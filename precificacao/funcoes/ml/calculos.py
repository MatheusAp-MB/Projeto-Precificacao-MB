import math
from django.db.models import Q


def arredondar_para_90(v: float) -> float:
    """Arredonda para cima até o menor valor terminado em ,90 >= v."""
    eps = 0.0000001
    k = math.ceil(v - 0.9 - eps)
    return k + 0.9


def calcular_custo_final(custo_com_boni, ipi_pct, frete_cif_pct, st_valor):
    """Custo Final = K + K×IPI + K×FreteEntrada + ST"""
    ipi = ipi_pct / 100
    frete = frete_cif_pct / 100
    return custo_com_boni + (custo_com_boni * ipi) + (custo_com_boni * frete) + st_valor


def calcular_peso_cubado(altura_cm, largura_cm, profundidade_cm):
    return (altura_cm * largura_cm * profundidade_cm) / 6000


def calcular_metro_cubico(altura_cm, largura_cm, profundidade_cm):
    return (altura_cm / 100) * (largura_cm / 100) * (profundidade_cm / 100)


def buscar_frete_ml(peso_lookup, preco):
    from ...models import FreteML
    frete = FreteML.objects.filter(
        peso_min__lte=peso_lookup,
        preco_min__lte=preco,
    ).filter(
        Q(peso_max__gte=peso_lookup) | Q(peso_max__isnull=True)
    ).filter(
        Q(preco_max__gte=preco) | Q(preco_max__isnull=True)
    ).first()
    return float(frete.valor) if frete else 0.0


def calcular_margem_ml(preco, custo_final, custo_bruto, comissao_pct,
                       icms_saida_pct, icms_entrada_pct, pis_cofins_pct,
                       frete, coleta, armazenagem):
    if preco <= 0:
        return 0.0
    comissao = preco * (comissao_pct / 100)
    icms = (preco * icms_saida_pct / 100) - \
        (custo_bruto * icms_entrada_pct / 100)
    pis = (preco - custo_bruto) * (pis_cofins_pct / 100)
    margem_valor = preco - custo_final - comissao - \
        icms - pis - frete - coleta - armazenagem
    return (margem_valor / preco) * 100


def calcular_preco_ideal_ml(custo_bruto, custo_com_boni, ipi_pct, frete_cif_pct,
                            st_valor, icms_entrada_pct, icms_saida_media_pct,
                            pis_cofins_pct, peso_kg, altura_cm, largura_cm,
                            profundidade_cm, comissao_pct, meta_margem_pct,
                            fator_coleta=72.0, armazenagem_diaria=0.015,
                            periodo_armazenagem=30, max_iter=10):
    comm = comissao_pct / 100
    m = meta_margem_pct / 100
    icmsv = icms_saida_media_pct / 100
    icmsc = icms_entrada_pct / 100
    pis_r = pis_cofins_pct / 100

    cf = calcular_custo_final(custo_com_boni, ipi_pct, frete_cif_pct, st_valor)
    metro_cubico = calcular_metro_cubico(
        altura_cm, largura_cm, profundidade_cm)
    peso_cubado = calcular_peso_cubado(altura_cm, largura_cm, profundidade_cm)
    peso_lookup = max(peso_kg, peso_cubado)
    coleta = metro_cubico * fator_coleta
    armazenagem = armazenagem_diaria * periodo_armazenagem

    denom = m - 1 + comm + icmsv + pis_r
    if abs(denom) < 0.0001:
        return {'erro': 'Denominador zero — verifique os parâmetros.', 'preco': None}

    frete = 0.0
    preco_bruto = 0.0
    for _ in range(max_iter):
        L = frete + coleta + armazenagem
        numerador = custo_bruto * (icmsc + pis_r) - cf - L
        preco_bruto = numerador / denom
        if preco_bruto <= 0:
            return {'erro': 'Preço calculado negativo — custo superior ao preço viável.', 'preco': None}
        frete_novo = buscar_frete_ml(peso_lookup, preco_bruto)
        if abs(frete_novo - frete) < 0.01:
            frete = frete_novo
            break
        frete = frete_novo

    preco_final = arredondar_para_90(preco_bruto)
    margem = calcular_margem_ml(
        preco=preco_final, custo_final=cf, custo_bruto=custo_bruto,
        comissao_pct=comissao_pct, icms_saida_pct=icms_saida_media_pct,
        icms_entrada_pct=icms_entrada_pct, pis_cofins_pct=pis_cofins_pct,
        frete=frete, coleta=coleta, armazenagem=armazenagem,
    )

    return {
        'preco':       preco_final,
        'margem_pct':  round(margem, 2),
        'custo_final': round(cf, 2),
        'frete':       round(frete, 2),
        'coleta':      round(coleta, 4),
        'armazenagem': round(armazenagem, 4),
        'peso_cubado': round(peso_cubado, 3),
        'peso_lookup': round(peso_lookup, 3),
        'erro':        None,
    }


def produto_para_dict(produto):
    return {
        'custo_bruto':          float(produto.custo),
        'custo_com_boni':       float(produto.custo_com_boni or produto.custo),
        'ipi_pct':              float(produto.ipi),
        'frete_cif_pct':        float(produto.frete_cif_fob or 0),
        'st_valor':             float(produto.st_valor or 0),
        'icms_entrada_pct':     float(produto.icms_entrada),
        'icms_saida_media_pct': float(produto.icms_saida_media),
        'pis_cofins_pct':       float(produto.pis_cofins),
        'peso_kg':              float(produto.peso),
        'altura_cm':            float(produto.altura),
        'largura_cm':           float(produto.largura),
        'profundidade_cm':      float(produto.profundidade),
    }


def config_para_dict(config):
    if config is None:
        return {'fator_coleta': 72.0, 'armazenagem_diaria': 0.015, 'periodo_armazenagem': 30}
    return {
        'fator_coleta':        float(config.fator_coleta),
        'armazenagem_diaria':  float(config.armazenagem_diaria),
        'periodo_armazenagem': config.periodo_armazenagem,
    }
