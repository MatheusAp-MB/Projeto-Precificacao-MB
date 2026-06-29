# * [RESUMO] → Signals do app de anúncios.
#              Garantem que frete e precificação estão sempre atualizados automaticamente,
#              independente de onde a mudança veio (import, admin, API, etc).
#
#              Fluxo de cálculo:
#              1. Goal Seek analítico → calcula preco_classico_calculado diretamente
#              2. Todas as fórmulas usam preco_classico_calculado (nunca o _da_planilha)
#              3. preco_premium_calculado = RoundUpTo90(preco_classico_calculado × acréscimo)
#              4. Dois cálculos paralelos de margem são salvos:
#                 - _dinamico:  armazenagem selecionada por faixa dinâmica (dimensão do produto)
#                 - _planilha:  armazenagem importada da coluna BH da planilha
#
#              Sobre os dois cálculos:
#              _dinamico  → tecnicamente correto, independente da planilha
#              _planilha  → replica a planilha exatamente, usado para validação e comparação
#              Ver documentação completa em produtos/models.py (campo armazenagem_planilha).
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


# ================================================
# UTILITÁRIOS
# ================================================

def round_up_to_90(v: Decimal) -> Decimal:
    k = math.ceil(float(v) - 0.90 - 1e-7)
    return Decimal(str(k)) + Decimal('0.90')


# ================================================
# CÁLCULO DE FRETE
# ================================================

def calcular_frete_para_anuncio(anuncio):
    from precificacao_marketplaces.models import FreteML

    if not anuncio.produto or not anuncio.preco_classico_calculado:
        logger.info(
            f'[FRETE] {anuncio.mlb} → ignorado (sem produto ou preço calculado)')
        return None

    produto = anuncio.produto
    peso = max(produto.peso, produto.peso_cubado)
    preco = anuncio.preco_classico_calculado

    frete = FreteML.objects.filter(
        peso_min__lte=peso,
        preco_min__lte=preco
    ).filter(
        Q(peso_max__gte=peso) | Q(peso_max__isnull=True)
    ).filter(
        Q(preco_max__gte=preco) | Q(preco_max__isnull=True)
    ).first()

    novo_valor = frete.valor if frete else None
    type(anuncio).objects.filter(pk=anuncio.pk).update(
        frete_calculado=novo_valor)
    logger.info(
        f'[FRETE] {anuncio.mlb} → peso={peso}kg | preco=R${preco} | frete=R${novo_valor}')
    return novo_valor


# ================================================
# GOAL SEEK
# ================================================

# * [RESUMO] → Calcula o preco_classico_calculado que entrega exatamente a margem_padrao
#              definida no cadastro do TipoAnuncioML.
#              Replica o VBA Executar_Atingir_Meta de forma analítica — sem iteração numérica.
#
#              Fórmula direta (derivada da fórmula de margem):
#                  FIXO        = coleta + armazenagem + custo_final - custo*(icms_entrada + pis)
#                  denominador = 1 - comissao - icms_saida - pis - margem_padrao
#                  P_exato     = (FIXO + frete_da_faixa) / denominador
#                  P_final     = round_up_to_90(P_exato)
#
#              O frete é resolvido por busca linear nas faixas — sem solver numérico.
#              Começa pela faixa que contém o custo do produto (piso de preço).
#              Máximo de 8 verificações no ML. Na prática: 2 a 4.

def goal_seek_preco_classico(anuncio) -> Decimal | None:
    # * [EXPLICAÇÃO] → Só executa para anúncios Clássico (gold_special).
    #                  Premium não tem Goal Seek próprio — seu preço é derivado do Clássico.
    if anuncio.tipo_anuncio != 'gold_special':
        return None

    from marketplaces.models import TipoAnuncioML, ConfiguracaoLogisticaML, FaixaArmazenagem
    from precificacao_marketplaces.models import FreteML

    produto = anuncio.produto
    if not produto:
        return None

    # --- Configurações de marketplace ---
    try:
        tipo_classico = TipoAnuncioML.objects.select_related('marketplace').get(
            marketplace__sigla='ML',
            tipo_anuncio='gold_special',
            tipo_logistico=anuncio.tipo_logistico,
            catalogo=anuncio.catalogo
        )
    except TipoAnuncioML.DoesNotExist:
        logger.warning(f'[GOAL SEEK] {anuncio.mlb} → TipoAnuncioML nao encontrado')
        return None

    logistica = ConfiguracaoLogisticaML.objects.filter(marketplace__sigla='ML').first()
    fator_coleta  = logistica.fator_coleta        if logistica else Decimal('0')
    periodo_armaz = logistica.periodo_armazenagem  if logistica else 0

    # --- Armazenagem _dinamico ---
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

    faixa_valor  = faixa_armazenagem.valor_diario if faixa_armazenagem else Decimal('0')
    armazenagem  = faixa_valor * periodo_armaz

    # --- Parâmetros fiscais e de custo ---
    custo          = produto.custo
    custo_com_boni = produto.custo_com_boni or custo
    ipi            = (produto.ipi            or Decimal('0')) / 100
    frete_cif_fob  = (produto.frete_cif_fob  or Decimal('0')) / 100
    st_valor       = produto.st_valor or Decimal('0')
    icms_entrada   = (produto.icms_entrada    or Decimal('0')) / 100
    icms_saida     = (produto.icms_saida_media or Decimal('0')) / 100
    pis            = (produto.pis_cofins      or Decimal('0')) / 100
    comissao       = tipo_classico.comissao / 100
    margem_meta    = tipo_classico.margem_padrao / 100

    # --- FIXO e denominador — calculados uma única vez ---
    metro_cubico = (produto.altura / 100) * (produto.largura / 100) * (produto.profundidade / 100)
    custo_final  = custo_com_boni + (custo_com_boni * ipi) + (custo_com_boni * frete_cif_fob) + st_valor
    coleta       = metro_cubico * fator_coleta
    fixo         = coleta + armazenagem + custo_final - custo * (icms_entrada + pis)
    denominador  = Decimal('1') - comissao - icms_saida - pis - margem_meta

    if denominador <= 0:
        logger.warning(
            f'[GOAL SEEK] {anuncio.mlb} → denominador={denominador:.4f} <= 0, '
            f'margem_padrao de {margem_meta * 100}% inalcancavel com as taxas atuais'
        )
        return None

    # --- Busca nas faixas de frete a partir da faixa do custo ---
    # * [EXPLICAÇÃO] → Busca todas as faixas de preço para o peso do produto,
    #                  ordenadas do menor para o maior preco_min.
    #                  Começa pela faixa que contém o custo (piso de preço)
    #                  e avança até encontrar consistência entre P_90 e o range da faixa.
    peso = max(produto.peso, produto.peso_cubado)

    faixas = list(
        FreteML.objects.filter(
            peso_min__lte=peso
        ).filter(
            Q(peso_max__gte=peso) | Q(peso_max__isnull=True)
        ).order_by('preco_min')
    )

    if not faixas:
        logger.warning(
            f'[GOAL SEEK] {anuncio.mlb} → nenhuma faixa de frete encontrada para peso={peso}kg'
        )
        return None

    # Encontra o índice da faixa que contém o custo do produto
    idx_inicial = 0
    for i, faixa in enumerate(faixas):
        preco_min = faixa.preco_min or Decimal('0')
        preco_max = faixa.preco_max
        if preco_min <= custo and (preco_max is None or preco_max >= custo):
            idx_inicial = i
            break

    # Percorre as faixas a partir da faixa do custo
    for faixa in faixas[idx_inicial:]:
        preco_min   = faixa.preco_min or Decimal('0')
        preco_max   = faixa.preco_max
        frete_faixa = faixa.valor

        p_exato = (fixo + frete_faixa) / denominador
        p_90    = round_up_to_90(p_exato)

        dentro_do_min = p_90 >= preco_min
        dentro_do_max = (preco_max is None) or (p_90 <= preco_max)

        if dentro_do_min and dentro_do_max:
            logger.info(
                f'[GOAL SEEK] {anuncio.mlb} → '
                f'faixa=[R${preco_min}, R${preco_max}] | '
                f'frete=R${frete_faixa} | '
                f'p_exato=R${p_exato:.4f} | '
                f'p_90=R${p_90}'
            )
            return p_90

    logger.warning(
        f'[GOAL SEEK] {anuncio.mlb} → nenhuma faixa gerou solucao valida'
    )
    return None

# ================================================
# CÁLCULO DE PRECIFICAÇÃO
# ================================================

def calcular_precificacao_anuncio(anuncio, frete_valor):
    from anuncios.models import BaseDeCalculo
    from marketplaces.models import TipoAnuncioML, ConfiguracaoLogisticaML, FaixaArmazenagem

    if not anuncio.produto or not anuncio.preco_classico_calculado:
        logger.info(
            f'[PRECIF] {anuncio.mlb} → ignorado (sem produto ou preco calculado)')
        return

    produto = anuncio.produto

    try:
        tipo_classico = TipoAnuncioML.objects.select_related('marketplace').get(
            marketplace__sigla='ML',
            tipo_anuncio='gold_special',
            tipo_logistico=anuncio.tipo_logistico,
            catalogo=anuncio.catalogo
        )
    except TipoAnuncioML.DoesNotExist:
        logger.warning(
            f'[PRECIF] {anuncio.mlb} → TipoAnuncioML Classico nao encontrado')
        return

    try:
        tipo_premium = TipoAnuncioML.objects.select_related('marketplace').get(
            marketplace__sigla='ML',
            tipo_anuncio='gold_pro',
            tipo_logistico=anuncio.tipo_logistico,
            catalogo=anuncio.catalogo
        )
    except TipoAnuncioML.DoesNotExist:
        logger.warning(
            f'[PRECIF] {anuncio.mlb} → TipoAnuncioML Premium nao encontrado')
        return

    logistica = ConfiguracaoLogisticaML.objects.filter(
        marketplace__sigla='ML').first()

    preco_classico = anuncio.preco_classico_calculado
    custo = produto.custo
    custo_com_boni = produto.custo_com_boni or produto.custo
    ipi = (produto.ipi or Decimal('0')) / 100
    frete_cif_fob = (produto.frete_cif_fob or Decimal('0')) / 100
    st_valor = produto.st_valor or Decimal('0')
    icms_entrada = (produto.icms_entrada or Decimal('0')) / 100
    icms_saida_media = (produto.icms_saida_media or Decimal('0')) / 100
    pis_cofins = (produto.pis_cofins or Decimal('0')) / 100
    comissao_classico_pct = tipo_classico.comissao / 100
    comissao_premium_pct = tipo_premium.comissao / 100
    acrescimo_premium = tipo_premium.acrescimo_preco / 100
    fator_coleta = logistica.fator_coleta if logistica else Decimal('0')
    periodo_armaz = logistica.periodo_armazenagem if logistica else 0

    # Armazenagem _dinamico
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

    faixa_valor = faixa_armazenagem.valor_diario if faixa_armazenagem else Decimal(
        '0')
    armazenagem_dinamico = faixa_valor * periodo_armaz

    # Armazenagem _planilha
    armazenagem_planilha = produto.armazenagem_planilha or Decimal('0')

    # * [EXPLICAÇÃO] → _planilha usa armazenagem importada da planilha (BH).
    #                  Os demais intermediários são calculados pelo sistema —
    #                  os valores intermediários da planilha têm cache corrompido
    #                  por dependências de arquivos externos (XLOOKUP).
    #                  preco_premium_planilha: busca do anúncio Premium irmão.
    from anuncios.models import AnuncioML
    anuncio_premium = AnuncioML.objects.filter(
        produto=anuncio.produto,
        tipo_anuncio='gold_pro'
    ).first()
    preco_premium_planilha = (
    anuncio_premium.preco_premium_da_planilha if anuncio_premium and anuncio_premium.preco_premium_da_planilha
    else round_up_to_90(preco_classico * (1 + acrescimo_premium))
    )
    # Intermediários comuns
    metro_cubico = (produto.altura / 100) * \
        (produto.largura / 100) * (produto.profundidade / 100)
    custo_final = custo_com_boni + \
        (custo_com_boni * ipi) + (custo_com_boni * frete_cif_fob) + st_valor
    coleta = metro_cubico * fator_coleta
    frete = frete_valor or Decimal('0')
    preco_premium = round_up_to_90(preco_classico * (1 + acrescimo_premium))
    comissao_classico_valor = preco_classico * comissao_classico_pct
    comissao_premium_valor = preco_premium * comissao_premium_pct
    icms_classico = (preco_classico * icms_saida_media) - \
        (custo * icms_entrada)
    icms_premium = (preco_premium * icms_saida_media) - (custo * icms_entrada)
    pis_cofins_classico = (preco_classico - custo) * pis_cofins
    pis_cofins_premium = (preco_premium - custo) * pis_cofins

    # Resultados _dinamico
    margem_valor_classico_din = (preco_classico - frete - coleta - armazenagem_dinamico -
                                 custo_final - comissao_classico_valor - icms_classico - pis_cofins_classico)
    margem_pct_classico_din = (margem_valor_classico_din /
                               preco_classico * 100) if preco_classico else Decimal('0')
    margem_valor_premium_din = (preco_premium - frete - coleta - armazenagem_dinamico -
                                custo_final - comissao_premium_valor - icms_premium - pis_cofins_premium)
    margem_pct_premium_din = (
        margem_valor_premium_din / preco_premium * 100) if preco_premium else Decimal('0')

    # * [EXPLICAÇÃO] → _planilha: mesmos intermediários do _dinamico,
    #                  exceto armazenagem que vem da planilha (BH).
    #                  Diferença entre _dinamico e _planilha = impacto da faixa de armazenagem.
    margem_valor_classico_pla = (
        preco_classico - frete - coleta - armazenagem_planilha
        - custo_final - comissao_classico_valor
        - icms_classico - pis_cofins_classico
    )
    margem_pct_classico_pla = (
        margem_valor_classico_pla / preco_classico * 100
    ) if preco_classico else Decimal('0')

    margem_valor_premium_pla = (
        preco_premium_planilha - frete - coleta - armazenagem_planilha
        - custo_final - comissao_premium_valor
        - icms_premium - pis_cofins_premium
    )
    margem_pct_premium_pla = (
        margem_valor_premium_pla / preco_premium_planilha * 100
    ) if preco_premium_planilha else Decimal('0')
    # Salva em AnuncioML
    type(anuncio).objects.filter(pk=anuncio.pk).update(
        preco_premium_calculado=preco_premium,
        margem_classico_calculado=round(margem_pct_classico_din, 2),
        margem_premium_calculado=round(margem_pct_premium_din, 2),
        margem_classico_calculado_baseado_na_planilha=round(margem_pct_classico_pla, 2),
        margem_premium_calculado_baseado_na_planilha=round(margem_pct_premium_pla, 2),
    )

    # Salva na BaseDeCalculo
    BaseDeCalculo.objects.update_or_create(
        anuncio=anuncio,
        defaults={
            'entrada_custo':                    custo,
            'entrada_custo_com_boni':            custo_com_boni,
            'entrada_ipi':                       produto.ipi or Decimal('0'),
            'entrada_frete_cif_fob':             produto.frete_cif_fob or Decimal('0'),
            'entrada_st_valor':                  st_valor,
            'entrada_icms_entrada':              produto.icms_entrada or Decimal('0'),
            'entrada_icms_saida_media':          produto.icms_saida_media or Decimal('0'),
            'entrada_pis_cofins':                produto.pis_cofins or Decimal('0'),
            'entrada_peso':                      produto.peso,
            'entrada_peso_cubado':               produto.peso_cubado,
            'entrada_altura':                    produto.altura,
            'entrada_largura':                   produto.largura,
            'entrada_profundidade':              produto.profundidade,
            'entrada_comissao_classico':         tipo_classico.comissao,
            'entrada_acrescimo_premium':         tipo_premium.acrescimo_preco,
            'entrada_fator_coleta':              fator_coleta,
            'entrada_armazenagem_faixa_valor':   faixa_valor,
            'entrada_armazenagem_periodo':       periodo_armaz,
            'entrada_armazenagem_da_planilha':   armazenagem_planilha,
            'calc_metro_cubico':                 round(metro_cubico, 6),
            'calc_custo_final':                  round(custo_final, 2),
            'calc_coleta':                       round(coleta, 2),
            'calc_armazenagem':                  round(armazenagem_dinamico, 2),
            'calc_armazenagem_baseada_na_planilha': round(armazenagem_planilha, 2),
            'calc_preco_premium':                round(preco_premium, 2),
            'calc_comissao_classico':            round(comissao_classico_valor, 2),
            'calc_comissao_premium':             round(comissao_premium_valor, 2),
            'calc_icms_classico':                round(icms_classico, 2),
            'calc_icms_premium':                 round(icms_premium, 2),
            'calc_pis_cofins_classico':          round(pis_cofins_classico, 2),
            'calc_pis_cofins_premium':           round(pis_cofins_premium, 2),
            'resultado_margem_classico_valor':   round(margem_valor_classico_din, 2),
            'resultado_margem_classico_pct':     round(margem_pct_classico_din, 2),
            'resultado_margem_premium_valor':    round(margem_valor_premium_din, 2),
            'resultado_margem_premium_pct':      round(margem_pct_premium_din, 2),
            'resultado_margem_classico_valor_baseado_na_planilha': round(margem_valor_classico_pla, 2),
            'resultado_margem_classico_pct_baseado_na_planilha':   round(margem_pct_classico_pla, 2),
            'resultado_margem_premium_valor_baseado_na_planilha':  round(margem_valor_premium_pla, 2),
            'resultado_margem_premium_pct_baseado_na_planilha':    round(margem_pct_premium_pla, 2),

        }
    )

    logger.info(
        f'[PRECIF] {anuncio.mlb} → R${round(preco_classico, 2)} | '
        f'din={round(margem_pct_classico_din, 2)}% | '
        f'pla={round(margem_pct_classico_pla, 2)}%'
    )


# ================================================
# FUNÇÃO PRINCIPAL
# ================================================

def calcular_tudo_para_anuncio(anuncio):
    # * [EXPLICAÇÃO] → Goal Seek substitui a cópia simples do preco_classico_da_planilha.
    #                  Para anúncios Clássico: calcula o preço ideal via goal_seek_preco_classico().
    #                  Para anúncios Premium:  goal seek retorna None → fallback usa preco_classico_da_planilha.
    #                  Se goal seek falhar por qualquer motivo (sem marketplace configurado,
    #                  denominador <= 0, etc.), o fallback garante que o fluxo não trava.
    preco_goal_seek = goal_seek_preco_classico(anuncio)

    if preco_goal_seek:
        type(anuncio).objects.filter(pk=anuncio.pk).update(
            preco_classico_calculado=preco_goal_seek
        )
        anuncio.preco_classico_calculado = preco_goal_seek

    elif not anuncio.preco_classico_calculado and anuncio.preco_classico_da_planilha:
        # * [EXPLICAÇÃO] → Fallback: se goal seek não encontrar solução,
        #                  usa preco_classico_da_planilha para não travar o fluxo.
        type(anuncio).objects.filter(pk=anuncio.pk).update(
            preco_classico_calculado=anuncio.preco_classico_da_planilha
        )
        anuncio.preco_classico_calculado = anuncio.preco_classico_da_planilha

    frete_valor = calcular_frete_para_anuncio(anuncio)
    calcular_precificacao_anuncio(anuncio, frete_valor)

# ================================================
# SIGNALS
# ================================================

@receiver(post_save, sender='anuncios.AnuncioML')
def signal_anuncio_ml_salvo(sender, instance, **kwargs):
    calcular_tudo_para_anuncio(instance)


@receiver(post_save, sender='produtos.Produto')
def signal_produto_salvo(sender, instance, **kwargs):
    from anuncios.models import AnuncioML
    for anuncio in AnuncioML.objects.filter(produto=instance).select_related('produto'):
        calcular_tudo_para_anuncio(anuncio)


@receiver(post_save, sender='precificacao_marketplaces.FreteML')
def signal_frete_ml_salvo(sender, instance, **kwargs):
    from anuncios.models import AnuncioML
    for anuncio in AnuncioML.objects.select_related('produto').all():
        calcular_tudo_para_anuncio(anuncio)


@receiver(post_save, sender='marketplaces.TipoAnuncioML')
def signal_tipo_anuncio_ml_salvo(sender, instance, **kwargs):
    from anuncios.models import AnuncioML
    for anuncio in AnuncioML.objects.filter(
        tipo_logistico=instance.tipo_logistico,
        catalogo=instance.catalogo
    ).select_related('produto'):
        calcular_tudo_para_anuncio(anuncio)


@receiver(post_save, sender='marketplaces.ConfiguracaoLogisticaML')
def signal_config_logistica_ml_salvo(sender, instance, **kwargs):
    from anuncios.models import AnuncioML
    for anuncio in AnuncioML.objects.select_related('produto').all():
        calcular_tudo_para_anuncio(anuncio)


@receiver(post_save, sender='marketplaces.FaixaArmazenagem')
def signal_faixa_armazenagem_salvo(sender, instance, **kwargs):
    from anuncios.models import AnuncioML
    for anuncio in AnuncioML.objects.select_related('produto').all():
        calcular_tudo_para_anuncio(anuncio)
