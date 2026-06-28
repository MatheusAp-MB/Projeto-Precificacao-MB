# * [RESUMO] → Signals do app de anúncios.
#              Garantem que frete e precificação estão sempre atualizados automaticamente,
#              independente de onde a mudança veio (import, admin, API, etc).
#
#              Fluxo de cálculo:
#              1. preco_classico_real (da planilha) → copiado para preco_classico_calculado
#              2. Todas as fórmulas usam preco_classico_calculado (nunca o _real)
#              3. preco_premium_calculado = RoundUpTo90(preco_classico_calculado × acréscimo)
#              4. Margens calculadas e salvas em AnuncioML e BaseDeCalculo
#
#              Quando o Goal Seek for implementado, ele sobrescreverá preco_classico_calculado
#              com o valor otimizado — todo o resto do fluxo permanece igual.

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from decimal import Decimal
import logging
import math

logger = logging.getLogger(__name__)

# * [EXPLICAÇÃO] → Importações dentro das funções para evitar importação circular
#                  entre os apps anuncios, produtos, precificacao_marketplaces e marketplaces.


# ================================================
# UTILITÁRIOS
# ================================================

def round_up_to_90(v: Decimal) -> Decimal:
    # * [EXPLICAÇÃO] → Arredonda para o próximo valor terminado em ,90 (teto).
    #                  Equivalente ao RoundUpTo90() do VBA da planilha Excel.
    #                  Funciona deslocando a escala 0,90 para baixo, aplicando ceil()
    #                  sobre inteiros e devolvendo o deslocamento — fazendo os ,90
    #                  agirem como "inteiros" na escala deslocada.
    #
    #                  Exemplos:
    #                    108,50 → 108,90
    #                    105,98 → 106,90
    #                    108,89 → 108,90
    #                    110,91 → 111,90
    #
    #                  O epsilon (1e-7) evita imprecisão de ponto flutuante.
    k = math.ceil(float(v) - 0.90 - 1e-7)
    return Decimal(str(k)) + Decimal('0.90')


# ================================================
# CÁLCULO DE FRETE
# ================================================

def calcular_frete_para_anuncio(anuncio):
    # * [EXPLICAÇÃO] → Calcula o frete via tabela FreteML usando peso efetivo e preço calculado.
    #                  Usa update() direto para não disparar o signal novamente (evita loop).
    from precificacao_marketplaces.models import FreteML

    if not anuncio.produto or not anuncio.preco_classico_calculado:
        logger.info(f'[FRETE] {anuncio.mlb} → ignorado (sem produto ou preço calculado)')
        return None

    produto = anuncio.produto
    peso    = max(produto.peso, produto.peso_cubado)
    preco   = anuncio.preco_classico_calculado

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
    # * [EXPLICAÇÃO] → Calcula todos os valores de precificação do anúncio e salva em:
    #                    - AnuncioML: preços e margens calculados (campos _calculado)
    #                    - BaseDeCalculo: registro completo de cada etapa (modo debug)
    #
    #                  Sempre usa preco_classico_calculado como base — nunca o _real.
    #                  Copia os dados de entrada no momento do cálculo para rastreabilidade.
    from anuncios.models import BaseDeCalculo
    from marketplaces.models import TipoAnuncioML, ConfiguracaoLogisticaML, FaixaArmazenagem

    if not anuncio.produto or not anuncio.preco_classico_calculado:
        logger.info(f'[PRECIF] {anuncio.mlb} → ignorado (sem produto ou preço calculado)')
        return

    produto = anuncio.produto

    # * [EXPLICAÇÃO] → Busca sempre os dois tipos (Clássico e Premium) independente do tipo do anúncio,
    #                  pois o cálculo gera os resultados de ambos de uma vez só.
    try:
        tipo_classico = TipoAnuncioML.objects.select_related('marketplace').get(
            marketplace__sigla='ML',
            tipo_anuncio='gold_special',
            tipo_logistico=anuncio.tipo_logistico,
            catalogo=anuncio.catalogo
        )
    except TipoAnuncioML.DoesNotExist:
        logger.warning(f'[PRECIF] {anuncio.mlb} → TipoAnuncioML Clássico não encontrado')
        return

    try:
        tipo_premium = TipoAnuncioML.objects.select_related('marketplace').get(
            marketplace__sigla='ML',
            tipo_anuncio='gold_pro',
            tipo_logistico=anuncio.tipo_logistico,
            catalogo=anuncio.catalogo
        )
    except TipoAnuncioML.DoesNotExist:
        logger.warning(f'[PRECIF] {anuncio.mlb} → TipoAnuncioML Premium não encontrado')
        return

    logistica = ConfiguracaoLogisticaML.objects.filter(marketplace__sigla='ML').first()

    # ================================================
    # DADOS DE ENTRADA
    # ================================================

    preco_classico        = anuncio.preco_classico_calculado
    custo                 = produto.custo
    custo_com_boni        = produto.custo_com_boni or produto.custo
    ipi                   = (produto.ipi or Decimal('0')) / 100
    frete_cif_fob         = (produto.frete_cif_fob or Decimal('0')) / 100
    st_valor              = produto.st_valor or Decimal('0')
    icms_entrada          = (produto.icms_entrada or Decimal('0')) / 100
    icms_saida_media      = (produto.icms_saida_media or Decimal('0')) / 100
    pis_cofins            = (produto.pis_cofins or Decimal('0')) / 100
    comissao_classico_pct = tipo_classico.comissao / 100
    comissao_premium_pct  = tipo_premium.comissao / 100
    acrescimo_premium     = tipo_premium.acrescimo_preco / 100

    fator_coleta  = logistica.fator_coleta if logistica else Decimal('0')
    periodo_armaz = logistica.periodo_armazenagem if logistica else 0

    # * [EXPLICAÇÃO] → Seleciona a faixa de armazenagem pelas dimensões do produto.
    #                  Itera em ordem crescente (ordem=1, 2, 3...) e usa a primeira
    #                  onde TODAS as dimensões cabem. Fallback: maior faixa cadastrada.
    faixa_armazenagem = FaixaArmazenagem.objects.filter(
        marketplace__sigla='ML',
        ativo=True,
        max_altura__gte=produto.altura,
        max_largura__gte=produto.largura,
        max_profundidade__gte=produto.profundidade
    ).order_by('ordem').first()

    if not faixa_armazenagem:
        faixa_armazenagem = FaixaArmazenagem.objects.filter(
            marketplace__sigla='ML', ativo=True
        ).order_by('-ordem').first()

    faixa_valor = faixa_armazenagem.valor_diario if faixa_armazenagem else Decimal('0')

    # ================================================
    # CÁLCULOS INTERMEDIÁRIOS
    # ================================================

    # Metro cúbico em m³ (dimensões do produto em cm → metros)
    metro_cubico = (produto.altura / 100) * (produto.largura / 100) * (produto.profundidade / 100)

    # Custo final = custo c/ bonificação + IPI + frete CIF/FOB + ST
    custo_final = custo_com_boni + (custo_com_boni * ipi) + (custo_com_boni * frete_cif_fob) + st_valor

    # Coleta proporcional ao volume | Armazenagem flat por faixa — ambas para todos os produtos
    coleta      = metro_cubico * fator_coleta
    armazenagem = faixa_valor * periodo_armaz

    frete = frete_valor or Decimal('0')

    # * [EXPLICAÇÃO] → Preço Premium = RoundUpTo90(Preço Clássico × (1 + Acréscimo)).
    #                  Equivalente ao cálculo do VBA: BV = BI × 1,08 → arredonda para ,90.
    preco_premium = round_up_to_90(preco_classico * (1 + acrescimo_premium))

    # Comissões
    comissao_classico_valor = preco_classico * comissao_classico_pct
    comissao_premium_valor  = preco_premium  * comissao_premium_pct

    # ICMS = (Preço × ICMS Saída) - (Custo × ICMS Entrada)
    icms_classico = (preco_classico * icms_saida_media) - (custo * icms_entrada)
    icms_premium  = (preco_premium  * icms_saida_media) - (custo * icms_entrada)

    # PIS/COFINS = (Preço - Custo) × alíquota
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
    # SALVA EM ANUNCIOML — campos _calculado
    # ================================================

    type(anuncio).objects.filter(pk=anuncio.pk).update(
        preco_premium_calculado   = preco_premium,
        margem_classico_calculado = round(margem_pct_classico, 2),
        margem_premium_calculado  = round(margem_pct_premium, 2),
    )

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
            'entrada_preco_classico_real':     preco_classico,
            'entrada_comissao_classico':       tipo_classico.comissao,
            'entrada_acrescimo_premium':       tipo_premium.acrescimo_preco,
            'entrada_fator_coleta':            fator_coleta,
            'entrada_armazenagem_faixa_valor': faixa_valor,
            'entrada_armazenagem_periodo':     periodo_armaz,
            # Intermediários
            'calc_metro_cubico':        round(metro_cubico, 6),
            'calc_custo_final':         round(custo_final, 2),
            'calc_coleta':              round(coleta, 2),
            'calc_armazenagem':         round(armazenagem, 2),
            'calc_preco_premium':       round(preco_premium, 2),
            'calc_comissao_classico':   round(comissao_classico_valor, 2),
            'calc_comissao_premium':    round(comissao_premium_valor, 2),
            'calc_icms_classico':       round(icms_classico, 2),
            'calc_icms_premium':        round(icms_premium, 2),
            'calc_pis_cofins_classico': round(pis_cofins_classico, 2),
            'calc_pis_cofins_premium':  round(pis_cofins_premium, 2),
            # Resultados finais
            'resultado_margem_classico_valor': round(margem_valor_classico, 2),
            'resultado_margem_classico_pct':   round(margem_pct_classico, 2),
            'resultado_margem_premium_valor':  round(margem_valor_premium, 2),
            'resultado_margem_premium_pct':    round(margem_pct_premium, 2),
        }
    )

    logger.info(
        f'[PRECIF] {anuncio.mlb} → '
        f'Clássico: R${round(preco_classico, 2)} → {round(margem_pct_classico, 2)}% | '
        f'Premium:  R${round(preco_premium, 2)} → {round(margem_pct_premium, 2)}%'
    )


# ================================================
# FUNÇÃO PRINCIPAL — CALCULA TUDO
# ================================================

def calcular_tudo_para_anuncio(anuncio):
    # * [EXPLICAÇÃO] → Ponto único de entrada para todos os cálculos de um anúncio.
    #                  Garante a ordem correta: primeiro define o preço calculado,
    #                  depois calcula frete (que depende do preço) e por fim as margens.
    #
    #                  Sobre preco_classico_calculado:
    #                  Por enquanto é sempre uma cópia do preco_classico_real.
    #                  Quando o Goal Seek for implementado, ele sobrescreverá este campo
    #                  antes de chegar aqui — todo o resto do fluxo permanece igual.

    # Garante que preco_classico_calculado está definido
    if not anuncio.preco_classico_calculado and anuncio.preco_classico_real:
        type(anuncio).objects.filter(pk=anuncio.pk).update(
            preco_classico_calculado=anuncio.preco_classico_real
        )
        anuncio.preco_classico_calculado = anuncio.preco_classico_real

    frete_valor = calcular_frete_para_anuncio(anuncio)
    calcular_precificacao_anuncio(anuncio, frete_valor)


# ================================================
# SIGNAL — ANÚNCIO ML
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
    #                  Recalcula tudo para todos os anúncios vinculados ao produto.
    from anuncios.models import AnuncioML

    for anuncio in AnuncioML.objects.filter(produto=instance).select_related('produto'):
        calcular_tudo_para_anuncio(anuncio)


# ================================================
# SIGNAL — FRETE ML
# ================================================

@receiver(post_save, sender='precificacao_marketplaces.FreteML')
def signal_frete_ml_salvo(sender, instance, **kwargs):
    # * [EXPLICAÇÃO] → Dispara quando qualquer registro da tabela FreteML é salvo.
    #                  Uma mudança na tabela de frete pode afetar qualquer anúncio —
    #                  recalcula tudo.
    from anuncios.models import AnuncioML

    for anuncio in AnuncioML.objects.select_related('produto').all():
        calcular_tudo_para_anuncio(anuncio)


# ================================================
# SIGNAL — TIPO DE ANÚNCIO ML
# ================================================

@receiver(post_save, sender='marketplaces.TipoAnuncioML')
def signal_tipo_anuncio_ml_salvo(sender, instance, **kwargs):
    # * [EXPLICAÇÃO] → Dispara quando um TipoAnuncioML é salvo (comissão, acréscimo, margens).
    #                  Afeta apenas anúncios com a mesma combinação de logística e catálogo.
    from anuncios.models import AnuncioML

    for anuncio in AnuncioML.objects.filter(
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
    #                  Fator de coleta e período de armazenagem afetam todos os anúncios.
    from anuncios.models import AnuncioML

    for anuncio in AnuncioML.objects.select_related('produto').all():
        calcular_tudo_para_anuncio(anuncio)


# ================================================
# SIGNAL — FAIXA DE ARMAZENAGEM
# ================================================

@receiver(post_save, sender='marketplaces.FaixaArmazenagem')
def signal_faixa_armazenagem_salvo(sender, instance, **kwargs):
    # * [EXPLICAÇÃO] → Dispara quando qualquer faixa de armazenagem é alterada.
    #                  A faixa selecionada por dimensão pode mudar para qualquer produto —
    #                  recalcula todos os anúncios.
    from anuncios.models import AnuncioML

    for anuncio in AnuncioML.objects.select_related('produto').all():
        calcular_tudo_para_anuncio(anuncio)