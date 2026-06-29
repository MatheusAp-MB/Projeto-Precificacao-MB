# * [RESUMO] → Signals do app de anúncios.
#              Garantem que preços e precificação estão sempre atualizados automaticamente,
#              independente de onde a mudança veio (import, admin, API, etc).
#
#              Arquitetura CardapioPrecos:
#              1. Goal Seek roda por (produto + TipoAnuncioML) — nunca por anúncio individual
#              2. CardapioPrecos armazena 3 preços (min, padrao, max) + atacado por combinação
#              3. AnuncioML lê do CardapioPrecos — nunca calcula, apenas copia
#              4. preco_manual = True → signal não sobrescreve o preço do anúncio
#
#              Escala: N anúncios × M produtos × 8 tipos = M × 8 chamadas de Goal Seek
#              Independente do número de anúncios.
#
#              Dois cálculos paralelos de margem:
#              - _calculado                     → armazenagem dinâmica por dimensão do produto
#              - _calculado_baseado_na_planilha  → armazenagem importada da coluna BH

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
# GOAL SEEK — FUNÇÃO GENÉRICA
# ================================================

# * [RESUMO] → Calcula o preco_base que entrega exatamente a margem_meta
#              para uma combinação produto + TipoAnuncioML.
#              Roda para qualquer tipo de anúncio (Clássico, Premium, etc).
#              Não depende de anúncio — opera na camada do CardapioPrecos.
#
#              Fórmula direta (derivada da fórmula de margem):
#                  FIXO        = coleta + armazenagem + custo_final - custo*(icms_entrada + pis)
#                  denominador = 1 - comissao - icms_saida - pis - margem_meta
#                  P_exato     = (FIXO + frete_da_faixa) / denominador
#                  P_base      = round_up_to_90(P_exato)
#
#              O frete é resolvido por busca linear nas faixas — sem solver numérico.
#              Começa pela faixa que contém o custo do produto (piso de preço).
#              Máximo de 8 verificações no ML. Na prática: 2 a 4.

def goal_seek_preco_base(produto, tipo_anuncio, margem_meta: Decimal) -> Decimal | None:
    from marketplaces.models import ConfiguracaoLogisticaML, FaixaArmazenagem
    from precificacao_marketplaces.models import FreteML

    if not produto:
        return None

    logistica = ConfiguracaoLogisticaML.objects.filter(
        marketplace=tipo_anuncio.marketplace
    ).first()
    fator_coleta  = logistica.fator_coleta        if logistica else Decimal('0')
    periodo_armaz = logistica.periodo_armazenagem  if logistica else 0

    # --- Armazenagem dinâmica ---
    faixa_armazenagem = FaixaArmazenagem.objects.filter(
        marketplace=tipo_anuncio.marketplace,
        ativo=True,
        max_altura__gte=produto.altura,
        max_largura__gte=produto.largura,
        max_profundidade__gte=produto.profundidade
    ).order_by('ordem').first()

    if not faixa_armazenagem:
        faixa_armazenagem = FaixaArmazenagem.objects.filter(
            marketplace=tipo_anuncio.marketplace, ativo=True
        ).order_by('-ordem').first()

    faixa_valor = faixa_armazenagem.valor_diario if faixa_armazenagem else Decimal('0')
    armazenagem = faixa_valor * periodo_armaz

    # --- Parâmetros fiscais e de custo ---
    custo          = produto.custo
    custo_com_boni = produto.custo_com_boni or custo
    ipi            = (produto.ipi            or Decimal('0')) / 100
    frete_cif_fob  = (produto.frete_cif_fob  or Decimal('0')) / 100
    st_valor       = produto.st_valor or Decimal('0')
    icms_entrada   = (produto.icms_entrada    or Decimal('0')) / 100
    icms_saida     = (produto.icms_saida_media or Decimal('0')) / 100
    pis            = (produto.pis_cofins      or Decimal('0')) / 100
    comissao       = tipo_anuncio.comissao / 100

    # --- FIXO e denominador — calculados uma única vez ---
    metro_cubico = (produto.altura / 100) * (produto.largura / 100) * (produto.profundidade / 100)
    custo_final  = custo_com_boni + (custo_com_boni * ipi) + (custo_com_boni * frete_cif_fob) + st_valor
    coleta       = metro_cubico * fator_coleta
    fixo         = coleta + armazenagem + custo_final - custo * (icms_entrada + pis)
    denominador  = Decimal('1') - comissao - icms_saida - pis - margem_meta

    if denominador <= 0:
        logger.warning(
            f'[GOAL SEEK] {produto.sku} / {tipo_anuncio.nome} → '
            f'denominador={denominador:.4f} <= 0, '
            f'margem {margem_meta * 100:.1f}% inalcancavel com as taxas atuais'
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
            f'[GOAL SEEK] {produto.sku} / {tipo_anuncio.nome} → '
            f'nenhuma faixa de frete para peso={peso}kg'
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
                f'[GOAL SEEK] {produto.sku} / {tipo_anuncio.nome} / '
                f'margem={margem_meta * 100:.1f}% → '
                f'faixa=[R${preco_min}, R${preco_max}] | '
                f'frete=R${frete_faixa} | p_base=R${p_90}'
            )
            return p_90

    logger.warning(
        f'[GOAL SEEK] {produto.sku} / {tipo_anuncio.nome} → '
        f'nenhuma faixa gerou solucao valida'
    )
    return None


# ================================================
# CARDÁPIO DE PREÇOS
# ================================================

def calcular_cardapio_precos(produto, tipo_anuncio):
    # * [EXPLICAÇÃO] → Calcula o cardápio completo de preços para uma combinação
    #                  produto + TipoAnuncioML. Roda o Goal Seek 3 vezes (min, padrao, max).
    #                  Aplica o acréscimo do tipo sobre o preco_base de cada margem.
    #                  Calcula preco_em_uso conforme preferencia_preco salva.
    #                  Calcula preços de atacado sobre preco_em_uso.
    #                  Salva/atualiza o registro em CardapioPrecos.
    #                  Retorna o CardapioPrecos atualizado ou None se falhar.
    from anuncios.models import CardapioPrecos

    acrescimo = tipo_anuncio.acrescimo_preco / 100

    def aplicar_acrescimo(preco_base: Decimal) -> Decimal:
        # * [EXPLICAÇÃO] → Para acrescimo = 0% (Clássico): preco_final = preco_base.
        #                  Para acrescimo = 8% (Premium): preco_final = roundUp90(preco_base × 1.08).
        return round_up_to_90(preco_base * (1 + acrescimo))

    # Goal Seek para cada margem — 3 chamadas por combinação
    base_padrao = goal_seek_preco_base(produto, tipo_anuncio, tipo_anuncio.margem_padrao / 100)
    base_minima = goal_seek_preco_base(produto, tipo_anuncio, tipo_anuncio.margem_minima / 100)
    base_maxima = goal_seek_preco_base(produto, tipo_anuncio, tipo_anuncio.margem_maxima / 100)

    if not base_padrao:
        logger.warning(
            f'[CARDAPIO] {produto.sku} / {tipo_anuncio.nome} → '
            f'Goal Seek falhou para margem_padrao — cardapio nao atualizado'
        )
        return None

    preco_margem_padrao = aplicar_acrescimo(base_padrao)
    preco_margem_minima = aplicar_acrescimo(base_minima) if base_minima else None
    preco_margem_maxima = aplicar_acrescimo(base_maxima) if base_maxima else None

    # Busca ou cria o registro — preserva a preferencia_preco já salva
    cardapio, _ = CardapioPrecos.objects.get_or_create(
        produto=produto,
        tipo_anuncio=tipo_anuncio,
        defaults={'preferencia_preco': CardapioPrecos.PreferenciaPreco.MARGEM_PADRAO}
    )

    # Determina preco_em_uso conforme preferencia atual
    if cardapio.preferencia_preco == CardapioPrecos.PreferenciaPreco.MARGEM_MINIMA:
        preco_em_uso = preco_margem_minima or preco_margem_padrao
    elif cardapio.preferencia_preco == CardapioPrecos.PreferenciaPreco.MARGEM_MAXIMA:
        preco_em_uso = preco_margem_maxima or preco_margem_padrao
    else:
        preco_em_uso = preco_margem_padrao

    # Preços de atacado — sempre sobre preco_em_uso
    desconto_2 = tipo_anuncio.desconto_atacado_2 / 100
    desconto_3 = tipo_anuncio.desconto_atacado_3 / 100
    preco_atacado_2 = round_up_to_90((2 * preco_em_uso) * (1 - desconto_2))
    preco_atacado_3 = round_up_to_90((3 * preco_em_uso) * (1 - desconto_3))

    # Atualiza o cardápio preservando a preferencia_preco
    CardapioPrecos.objects.filter(pk=cardapio.pk).update(
        preco_base          = base_padrao,
        preco_margem_padrao = preco_margem_padrao,
        preco_margem_minima = preco_margem_minima,
        preco_margem_maxima = preco_margem_maxima,
        preco_em_uso        = preco_em_uso,
        preco_atacado_2     = preco_atacado_2,
        preco_atacado_3     = preco_atacado_3,
        valido              = True,
    )
    cardapio.refresh_from_db()

    logger.info(
        f'[CARDAPIO] {produto.sku} / {tipo_anuncio.nome} → '
        f'padrao=R${preco_margem_padrao} | '
        f'minima=R${preco_margem_minima} | '
        f'maxima=R${preco_margem_maxima} | '
        f'em_uso=R${preco_em_uso}'
    )
    return cardapio


def propagar_cardapio_para_anuncios(cardapio):
    # * [EXPLICAÇÃO] → Copia os preços do CardapioPrecos para todos os AnuncioML
    #                  que correspondem à mesma combinação produto + tipo de anúncio.
    #                  Respeita preco_manual = True — anúncios manuais não são tocados.
    from anuncios.models import AnuncioML

    tipo = cardapio.tipo_anuncio
    anuncios = AnuncioML.objects.filter(
        produto=cardapio.produto,
        tipo_anuncio=tipo.tipo_anuncio,
        tipo_logistico=tipo.tipo_logistico,
        catalogo=tipo.catalogo,
    ).select_related('produto')

    for anuncio in anuncios:
        if anuncio.preco_manual:
            logger.info(f'[PROPAGAR] {anuncio.mlb} → ignorado (preco_manual=True)')
            continue

        # Copia preços conforme tipo do anúncio
        is_classico = tipo.tipo_anuncio == 'gold_special'
        if is_classico:
            type(anuncio).objects.filter(pk=anuncio.pk).update(
                preco_classico_calculado = cardapio.preco_em_uso,
                preco_atacado_2          = cardapio.preco_atacado_2,
                preco_atacado_3          = cardapio.preco_atacado_3,
            )
            anuncio.preco_classico_calculado = cardapio.preco_em_uso
        else:
            type(anuncio).objects.filter(pk=anuncio.pk).update(
                preco_premium_calculado = cardapio.preco_em_uso,
                preco_atacado_2         = cardapio.preco_atacado_2,
                preco_atacado_3         = cardapio.preco_atacado_3,
            )
            anuncio.preco_premium_calculado = cardapio.preco_em_uso

        # Calcula frete e margens para este anúncio
        frete_valor = calcular_frete_para_anuncio(anuncio)
        calcular_margem_anuncio(anuncio, frete_valor)


# ================================================
# FRETE
# ================================================

def calcular_frete_para_anuncio(anuncio) -> Decimal | None:
    from precificacao_marketplaces.models import FreteML

    produto = anuncio.produto
    if not produto:
        return None

    # Usa o preço em uso do anúncio — classico ou premium
    preco = anuncio.preco_classico_calculado or anuncio.preco_premium_calculado
    if not preco:
        logger.info(f'[FRETE] {anuncio.mlb} → ignorado (sem preco calculado)')
        return None

    peso = max(produto.peso, produto.peso_cubado)

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
    logger.info(
        f'[FRETE] {anuncio.mlb} → peso={peso}kg | preco=R${preco} | frete=R${novo_valor}'
    )
    return novo_valor


# ================================================
# MARGEM
# ================================================

def calcular_margem_anuncio(anuncio, frete_valor):
    # * [EXPLICAÇÃO] → Calcula as margens para um anúncio específico.
    #                  Cada anúncio calcula apenas as margens do seu próprio tipo.
    #                  Mantém dois cálculos paralelos:
    #                  - dinâmico: armazenagem por faixa das dimensões do produto
    #                  - baseado_na_planilha: armazenagem importada da coluna BH
    from anuncios.models import BaseDeCalculo
    from marketplaces.models import TipoAnuncioML, ConfiguracaoLogisticaML, FaixaArmazenagem

    produto = anuncio.produto
    if not produto:
        return

    # Preço em uso deste anúncio
    preco = anuncio.preco_classico_calculado or anuncio.preco_premium_calculado
    if not preco:
        return

    # TipoAnuncioML correto para este anúncio
    try:
        tipo = TipoAnuncioML.objects.select_related('marketplace').get(
            marketplace__sigla='ML',
            tipo_anuncio=anuncio.tipo_anuncio,
            tipo_logistico=anuncio.tipo_logistico,
            catalogo=anuncio.catalogo
        )
    except TipoAnuncioML.DoesNotExist:
        logger.warning(f'[MARGEM] {anuncio.mlb} → TipoAnuncioML nao encontrado')
        return

    logistica = ConfiguracaoLogisticaML.objects.filter(marketplace__sigla='ML').first()
    fator_coleta  = logistica.fator_coleta        if logistica else Decimal('0')
    periodo_armaz = logistica.periodo_armazenagem  if logistica else 0

    # Armazenagem dinâmica
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

    faixa_valor          = faixa_armazenagem.valor_diario if faixa_armazenagem else Decimal('0')
    armazenagem_dinamico = faixa_valor * periodo_armaz
    armazenagem_planilha = produto.armazenagem_planilha or Decimal('0')

    # Parâmetros fiscais
    custo          = produto.custo
    custo_com_boni = produto.custo_com_boni or custo
    ipi            = (produto.ipi            or Decimal('0')) / 100
    frete_cif_fob  = (produto.frete_cif_fob  or Decimal('0')) / 100
    st_valor       = produto.st_valor or Decimal('0')
    icms_entrada   = (produto.icms_entrada    or Decimal('0')) / 100
    icms_saida     = (produto.icms_saida_media or Decimal('0')) / 100
    pis            = (produto.pis_cofins      or Decimal('0')) / 100
    comissao_pct   = tipo.comissao / 100

    metro_cubico   = (produto.altura / 100) * (produto.largura / 100) * (produto.profundidade / 100)
    custo_final    = custo_com_boni + (custo_com_boni * ipi) + (custo_com_boni * frete_cif_fob) + st_valor
    coleta         = metro_cubico * fator_coleta
    frete          = frete_valor or Decimal('0')
    comissao_valor = preco * comissao_pct
    icms_valor     = (preco * icms_saida) - (custo * icms_entrada)
    pis_valor      = (preco - custo) * pis

    # Margem dinâmica
    margem_valor_din = (
        preco - frete - coleta - armazenagem_dinamico
        - custo_final - comissao_valor - icms_valor - pis_valor
    )
    margem_pct_din = (margem_valor_din / preco * 100) if preco else Decimal('0')

    # Margem baseada na planilha
    margem_valor_pla = (
        preco - frete - coleta - armazenagem_planilha
        - custo_final - comissao_valor - icms_valor - pis_valor
    )
    margem_pct_pla = (margem_valor_pla / preco * 100) if preco else Decimal('0')

    # Salva no AnuncioML — campo correto conforme tipo
    is_classico = anuncio.tipo_anuncio == 'gold_special'
    if is_classico:
        type(anuncio).objects.filter(pk=anuncio.pk).update(
            margem_classico_calculado=round(margem_pct_din, 2),
            margem_classico_calculado_baseado_na_planilha=round(margem_pct_pla, 2),
        )
    else:
        type(anuncio).objects.filter(pk=anuncio.pk).update(
            margem_premium_calculado=round(margem_pct_din, 2),
            margem_premium_calculado_baseado_na_planilha=round(margem_pct_pla, 2),
        )

    # Salva BaseDeCalculo
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
            'entrada_comissao_classico':         tipo.comissao,
            'entrada_acrescimo_premium':         tipo.acrescimo_preco,
            'entrada_fator_coleta':              fator_coleta,
            'entrada_armazenagem_faixa_valor':   faixa_valor,
            'entrada_armazenagem_periodo':       periodo_armaz,
            'entrada_armazenagem_da_planilha':   armazenagem_planilha,
            'calc_metro_cubico':                 round(metro_cubico, 6),
            'calc_custo_final':                  round(custo_final, 2),
            'calc_coleta':                       round(coleta, 2),
            'calc_armazenagem':                  round(armazenagem_dinamico, 2),
            'calc_armazenagem_baseada_na_planilha': round(armazenagem_planilha, 2),
            'calc_preco_premium':                round(preco, 2),
            'calc_comissao_classico':            round(comissao_valor, 2) if is_classico else None,
            'calc_comissao_premium':             round(comissao_valor, 2) if not is_classico else None,
            'calc_icms_classico':                round(icms_valor, 2) if is_classico else None,
            'calc_icms_premium':                 round(icms_valor, 2) if not is_classico else None,
            'calc_pis_cofins_classico':          round(pis_valor, 2) if is_classico else None,
            'calc_pis_cofins_premium':           round(pis_valor, 2) if not is_classico else None,
            'resultado_margem_classico_valor':   round(margem_valor_din, 2) if is_classico else None,
            'resultado_margem_classico_pct':     round(margem_pct_din, 2) if is_classico else None,
            'resultado_margem_premium_valor':    round(margem_valor_din, 2) if not is_classico else None,
            'resultado_margem_premium_pct':      round(margem_pct_din, 2) if not is_classico else None,
            'resultado_margem_classico_valor_baseado_na_planilha': round(margem_valor_pla, 2) if is_classico else None,
            'resultado_margem_classico_pct_baseado_na_planilha':   round(margem_pct_pla, 2) if is_classico else None,
            'resultado_margem_premium_valor_baseado_na_planilha':  round(margem_valor_pla, 2) if not is_classico else None,
            'resultado_margem_premium_pct_baseado_na_planilha':    round(margem_pct_pla, 2) if not is_classico else None,
        }
    )

    logger.info(
        f'[MARGEM] {anuncio.mlb} → R${round(preco, 2)} | '
        f'din={round(margem_pct_din, 2)}% | pla={round(margem_pct_pla, 2)}%'
    )


# ================================================
# ORQUESTRAÇÃO
# ================================================

def recalcular_combinacao(produto, tipo_anuncio):
    # * [EXPLICAÇÃO] → Ponto de entrada único para recálculo de uma combinação específica.
    #                  Calcula o CardapioPrecos e propaga para os AnuncioML.
    if not produto or not tipo_anuncio:
        return
    cardapio = calcular_cardapio_precos(produto, tipo_anuncio)
    if cardapio:
        propagar_cardapio_para_anuncios(cardapio)


def recalcular_todas_combinacoes_do_produto(produto):
    # * [EXPLICAÇÃO] → Recalcula todas as combinações de TipoAnuncioML para um produto.
    #                  Chamado quando o produto é alterado.
    from marketplaces.models import TipoAnuncioML
    tipos = TipoAnuncioML.objects.filter(marketplace__sigla='ML')
    for tipo in tipos:
        recalcular_combinacao(produto, tipo)


def recalcular_todas_combinacoes_do_tipo(tipo_anuncio):
    # * [EXPLICAÇÃO] → Recalcula todas as combinações de produto para um TipoAnuncioML.
    #                  Chamado quando o TipoAnuncioML é alterado.
    from produtos.models import Produto
    for produto in Produto.objects.all():
        recalcular_combinacao(produto, tipo_anuncio)


def recalcular_tudo():
    # * [EXPLICAÇÃO] → Recalcula todas as combinações existentes.
    #                  Chamado quando frete, logística ou armazenagem mudam.
    #                  Custo: M produtos × 8 tipos × 3 Goal Seeks = M × 24 operações.
    #                  Independente do número de anúncios.
    from produtos.models import Produto
    from marketplaces.models import TipoAnuncioML
    tipos = TipoAnuncioML.objects.filter(marketplace__sigla='ML')
    for produto in Produto.objects.all():
        for tipo in tipos:
            recalcular_combinacao(produto, tipo)


# ================================================
# SIGNALS
# ================================================

@receiver(post_save, sender='anuncios.AnuncioML')
def signal_anuncio_ml_salvo(sender, instance, **kwargs):
    # * [EXPLICAÇÃO] → Quando um anúncio é salvo, recalcula o CardapioPrecos
    #                  da sua combinação e propaga o resultado de volta para ele.
    if not instance.produto or not instance.tipo_anuncio:
        return
    from marketplaces.models import TipoAnuncioML
    try:
        tipo = TipoAnuncioML.objects.get(
            marketplace__sigla='ML',
            tipo_anuncio=instance.tipo_anuncio,
            tipo_logistico=instance.tipo_logistico,
            catalogo=instance.catalogo
        )
    except TipoAnuncioML.DoesNotExist:
        logger.warning(
            f'[SIGNAL] {instance.mlb} → TipoAnuncioML nao encontrado, ignorado'
        )
        return
    recalcular_combinacao(instance.produto, tipo)


@receiver(post_save, sender='produtos.Produto')
def signal_produto_salvo(sender, instance, **kwargs):
    recalcular_todas_combinacoes_do_produto(instance)


@receiver(post_save, sender='precificacao_marketplaces.FreteML')
def signal_frete_ml_salvo(sender, instance, **kwargs):
    recalcular_tudo()


@receiver(post_save, sender='marketplaces.TipoAnuncioML')
def signal_tipo_anuncio_ml_salvo(sender, instance, **kwargs):
    recalcular_todas_combinacoes_do_tipo(instance)


@receiver(post_save, sender='marketplaces.ConfiguracaoLogisticaML')
def signal_config_logistica_ml_salvo(sender, instance, **kwargs):
    recalcular_tudo()


@receiver(post_save, sender='marketplaces.FaixaArmazenagem')
def signal_faixa_armazenagem_salvo(sender, instance, **kwargs):
    recalcular_tudo()