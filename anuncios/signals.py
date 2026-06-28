# * [RESUMO] → Signals do app de anúncios.
#              Garantem que frete e precificação estão sempre atualizados automaticamente,
#              independente de onde a mudança veio.

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# * [EXPLICAÇÃO] → Importações dentro das funções para evitar importação circular
#                  entre os apps anuncios, produtos, precificacao_marketplaces e marketplaces.


# ================================================
# CÁLCULO DE FRETE
# ================================================

def calcular_frete_para_anuncio(anuncio):
    # * [EXPLICAÇÃO] → Calcula o frete via tabela FreteML usando peso efetivo e preço.
    #                  Usa update() para não disparar o signal novamente (evita loop).
    from precificacao_marketplaces.models import FreteML

    if not anuncio.produto or not anuncio.preco:
        logger.info(f'[FRETE] {anuncio.mlb} → ignorado (sem produto ou preço)')
        return None

    produto = anuncio.produto
    peso    = max(produto.peso, produto.peso_cubado)
    preco   = anuncio.preco

    frete = FreteML.objects.filter(
        peso_min__lte=peso,
        preco_min__lte=preco
    ).filter(
        Q(peso_max__gte=peso) | Q(peso_max__isnull=True)
    ).filter(
        Q(preco_max__gte=preco) | Q(preco_max__isnull=True)
    ).first()

    novo_valor = frete.valor if frete else None

    type(anuncio).objects.filter(pk=anuncio.pk).update(frete_calculado=novo_valor)
    logger.info(f'[FRETE] {anuncio.mlb} → peso={peso}kg | preço=R${preco} | frete=R${novo_valor}')

    return novo_valor


# ================================================
# CÁLCULO DE PRECIFICAÇÃO
# ================================================

def calcular_precificacao_anuncio(anuncio, frete_valor):
    # * [EXPLICAÇÃO] → Calcula todos os valores de precificação do anúncio e
    #                  salva na BaseDeCalculo. Copia os dados de entrada no momento
    #                  do cálculo para garantir rastreabilidade.
    from anuncios.models import BaseDeCalculo
    from marketplaces.models import TipoAnuncioML, ConfiguracaoLogisticaML

    if not anuncio.produto or not anuncio.preco:
        logger.info(f'[PRECIF] {anuncio.mlb} → ignorado (sem produto ou preço)')
        return

    produto = anuncio.produto

    # * [EXPLICAÇÃO] → Busca o tipo de anúncio correspondente no marketplace.
    try:
        tipo = TipoAnuncioML.objects.select_related('marketplace').get(
            marketplace__sigla='ML',
            tipo_anuncio=anuncio.tipo_anuncio,
            tipo_logistico=anuncio.tipo_logistico,
            catalogo=anuncio.catalogo
        )
    except TipoAnuncioML.DoesNotExist:
        logger.warning(f'[PRECIF] {anuncio.mlb} → TipoAnuncioML não encontrado')
        return

    # * [EXPLICAÇÃO] → Busca configuração logística apenas se FULL.
    logistica = None
    if anuncio.tipo_logistico == 'fulfillment':
        logistica = ConfiguracaoLogisticaML.objects.filter(
            marketplace__sigla='ML'
        ).first()

    # ================================================
    # DADOS DE ENTRADA
    # ================================================

    preco_classico    = anuncio.preco
    custo             = produto.custo
    custo_com_boni    = produto.custo_com_boni or produto.custo
    ipi               = (produto.ipi or Decimal('0')) / 100
    frete_cif_fob     = (produto.frete_cif_fob or Decimal('0')) / 100
    st_valor          = produto.st_valor or Decimal('0')
    icms_entrada      = (produto.icms_entrada or Decimal('0')) / 100
    icms_saida_media  = (produto.icms_saida_media or Decimal('0')) / 100
    pis_cofins        = (produto.pis_cofins or Decimal('0')) / 100
    comissao_pct      = tipo.comissao / 100
    acrescimo_premium = tipo.acrescimo_preco / 100

    fator_coleta  = logistica.fator_coleta if logistica else Decimal('0')
    armaz_faixa   = logistica.armaz_faixa_2 if logistica else Decimal('0')
    periodo_armaz = logistica.periodo_armazenagem if logistica else 0

    # ================================================
    # CÁLCULOS INTERMEDIÁRIOS
    # ================================================

    # * [EXPLICAÇÃO] → Metro cúbico em m³ — dimensões do produto em cm convertidas para metros.
    metro_cubico = (produto.altura / 100) * (produto.largura / 100) * (produto.profundidade / 100)

    # * [EXPLICAÇÃO] → Custo final inclui IPI, frete CIF/FOB e ST sobre o custo com bonificação.
    custo_final = custo_com_boni + (custo_com_boni * ipi) + (custo_com_boni * frete_cif_fob) + st_valor

    # * [EXPLICAÇÃO] → Coleta e armazenagem só se logística FULL.
    coleta      = metro_cubico * fator_coleta if logistica else Decimal('0')
    armazenagem = metro_cubico * armaz_faixa * periodo_armaz if logistica else Decimal('0')

    frete = frete_valor or Decimal('0')

    # * [EXPLICAÇÃO] → Preço Premium = Preço Clássico × (1 + acréscimo).
    preco_premium = preco_classico * (1 + acrescimo_premium)

    # Comissões
    comissao_classico_valor = preco_classico * comissao_pct
    comissao_premium_valor  = preco_premium  * comissao_pct

    # ICMS = (Preço × ICMS Saída) - (Custo × ICMS Entrada)
    icms_classico = (preco_classico * icms_saida_media) - (custo * icms_entrada)
    icms_premium  = (preco_premium  * icms_saida_media) - (custo * icms_entrada)

    # PIS/COFINS = (Preço - Custo) × PIS/COFINS
    pis_cofins_classico = (preco_classico - custo) * pis_cofins
    pis_cofins_premium  = (preco_premium  - custo) * pis_cofins

    # ================================================
    # RESULTADOS FINAIS
    # ================================================

    margem_valor_classico = (
        preco_classico - frete - coleta - armazenagem
        - custo_final - comissao_classico_valor
        - icms_classico - pis_cofins_classico
    )
    margem_pct_classico = (margem_valor_classico / preco_classico * 100) if preco_classico else Decimal('0')

    margem_valor_premium = (
        preco_premium - frete - coleta - armazenagem
        - custo_final - comissao_premium_valor
        - icms_premium - pis_cofins_premium
    )
    margem_pct_premium = (margem_valor_premium / preco_premium * 100) if preco_premium else Decimal('0')

    # ================================================
    # SALVA NA BASE DE CÁLCULO
    # ================================================

    BaseDeCalculo.objects.update_or_create(
        anuncio=anuncio,
        defaults={
            # Dados de entrada — produto
            'entrada_custo':            custo,
            'entrada_custo_com_boni':   custo_com_boni,
            'entrada_ipi':              produto.ipi or Decimal('0'),
            'entrada_frete_cif_fob':    produto.frete_cif_fob or Decimal('0'),
            'entrada_st_valor':         st_valor,
            'entrada_icms_entrada':     produto.icms_entrada or Decimal('0'),
            'entrada_icms_saida_media': produto.icms_saida_media or Decimal('0'),
            'entrada_pis_cofins':       produto.pis_cofins or Decimal('0'),
            'entrada_peso':             produto.peso,
            'entrada_peso_cubado':      produto.peso_cubado,
            'entrada_altura':           produto.altura,
            'entrada_largura':          produto.largura,
            'entrada_profundidade':     produto.profundidade,
            # Dados de entrada — anúncio e marketplace
            'entrada_preco_classico':    preco_classico,
            'entrada_comissao':          tipo.comissao,
            'entrada_acrescimo_premium': tipo.acrescimo_preco,
            'entrada_fator_coleta':      fator_coleta,
            'entrada_armaz_faixa':       armaz_faixa,
            'entrada_periodo_armaz':     periodo_armaz,
            # Intermediários
            'calc_metro_cubico':          round(metro_cubico, 6),
            'calc_custo_final':           round(custo_final, 2),
            'calc_coleta':                round(coleta, 2),
            'calc_armazenagem':           round(armazenagem, 2),
            'calc_preco_premium':         round(preco_premium, 2),
            'calc_comissao_classico':     round(comissao_classico_valor, 2),
            'calc_comissao_premium':      round(comissao_premium_valor, 2),
            'calc_icms_classico':         round(icms_classico, 2),
            'calc_icms_premium':          round(icms_premium, 2),
            'calc_pis_cofins_classico':   round(pis_cofins_classico, 2),
            'calc_pis_cofins_premium':    round(pis_cofins_premium, 2),
            # Resultados finais
            'resultado_margem_valor_classico': round(margem_valor_classico, 2),
            'resultado_margem_pct_classico':   round(margem_pct_classico, 2),
            'resultado_margem_valor_premium':  round(margem_valor_premium, 2),
            'resultado_margem_pct_premium':    round(margem_pct_premium, 2),
        }
    )

    logger.info(
        f'[PRECIF] {anuncio.mlb} → '
        f'Margem Clássico: R${round(margem_valor_classico, 2)} ({round(margem_pct_classico, 2)}%) | '
        f'Margem Premium: R${round(margem_valor_premium, 2)} ({round(margem_pct_premium, 2)}%)'
    )


# ================================================
# FUNÇÃO PRINCIPAL — CALCULA TUDO
# ================================================

def calcular_tudo_para_anuncio(anuncio):
    # * [EXPLICAÇÃO] → Ponto único de entrada para todos os cálculos de um anúncio.
    #                  Garante que frete e precificação são sempre calculados juntos,
    #                  pois são interdependentes.
    frete_valor = calcular_frete_para_anuncio(anuncio)
    calcular_precificacao_anuncio(anuncio, frete_valor)


# ================================================
# SIGNAL — ANUNCIO ML
# ================================================

@receiver(post_save, sender='anuncios.AnuncioML')
def signal_anuncio_ml_salvo(sender, instance, **kwargs):
    # * [EXPLICAÇÃO] → Dispara quando qualquer AnuncioML é salvo.
    #                  Recalcula frete e precificação automaticamente.
    calcular_tudo_para_anuncio(instance)


# ================================================
# SIGNAL — PRODUTO
# ================================================

@receiver(post_save, sender='produtos.Produto')
def signal_produto_salvo(sender, instance, **kwargs):
    # * [EXPLICAÇÃO] → Dispara quando um Produto é salvo.
    #                  Recalcula tudo para todos os anúncios vinculados.
    from anuncios.models import AnuncioML

    for anuncio in AnuncioML.objects.filter(produto=instance).select_related('produto'):
        calcular_tudo_para_anuncio(anuncio)


# ================================================
# SIGNAL — FRETE ML
# ================================================

@receiver(post_save, sender='precificacao_marketplaces.FreteML')
def signal_frete_ml_salvo(sender, instance, **kwargs):
    # * [EXPLICAÇÃO] → Dispara quando qualquer registro da tabela FreteML é salvo.
    #                  Recalcula tudo para TODOS os anúncios.
    from anuncios.models import AnuncioML

    for anuncio in AnuncioML.objects.select_related('produto').all():
        calcular_tudo_para_anuncio(anuncio)


# ================================================
# SIGNAL — TIPO DE ANÚNCIO ML
# ================================================

@receiver(post_save, sender='marketplaces.TipoAnuncioML')
def signal_tipo_anuncio_ml_salvo(sender, instance, **kwargs):
    # * [EXPLICAÇÃO] → Dispara quando um TipoAnuncioML é salvo.
    #                  Parâmetros como comissão ou margem mudaram —
    #                  recalcula todos os anúncios desse tipo.
    from anuncios.models import AnuncioML

    for anuncio in AnuncioML.objects.filter(
        tipo_anuncio=instance.tipo_anuncio,
        tipo_logistico=instance.tipo_logistico,
        catalogo=instance.catalogo
    ).select_related('produto'):
        calcular_tudo_para_anuncio(anuncio)


# ================================================
# SIGNAL — CONFIGURAÇÃO LOGÍSTICA ML
# ================================================

@receiver(post_save, sender='marketplaces.ConfiguracaoLogisticaML')
def signal_config_logistica_ml_salvo(sender, instance, **kwargs):
    # * [EXPLICAÇÃO] → Dispara quando a configuração logística do ML é alterada.
    #                  Parâmetros de coleta ou armazenagem mudaram —
    #                  recalcula todos os anúncios FULL do ML.
    from anuncios.models import AnuncioML

    for anuncio in AnuncioML.objects.filter(
        tipo_logistico='fulfillment'
    ).select_related('produto'):
        calcular_tudo_para_anuncio(anuncio)