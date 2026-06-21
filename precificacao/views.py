from django.shortcuts import render, get_object_or_404
from django.db import models
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .funcoes.ml.calculos import (
    calcular_custo_final, calcular_preco_ideal_ml,
    calcular_margem_ml, arredondar_para_90,
    buscar_frete_ml, produto_para_dict, config_para_dict,
)

from .models import Produto, Marketplace, TipoAnuncioML, FreteML, Anuncio, ConfiguracaoLogisticaML


# Create your views here.


def lista_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'precificacao/lista_produtos.html', {'produtos': produtos})


def lista_marketplaces(request):
    marketplaces = Marketplace.objects.all()
    return render(request, 'precificacao/lista_marketplaces.html', {'marketplaces': marketplaces})


def lista_tipos_anuncio(request):
    tipos = TipoAnuncioML.objects.all()
    return render(request, 'precificacao/lista_tipos_anuncio.html', {'tipos': tipos})


def lista_anuncios(request):
    anuncios = Anuncio.objects.select_related('produto', 'tipo_anuncio').all()
    return render(request, 'precificacao/lista_anuncios.html', {'anuncios': anuncios})


def home(request):
    return render(request, 'precificacao/home.html')


def lista_frete_ml(request):
    from .models import FreteML

    # Busca todas as faixas de preço únicas (colunas)
    faixas_preco = FreteML.objects.values(
        'preco_min', 'preco_max'
    ).distinct().order_by('preco_min')

    # Busca todas as faixas de peso únicas (linhas)
    faixas_peso = FreteML.objects.values(
        'peso_min', 'peso_max'
    ).distinct().order_by('peso_min')

    # Monta dicionário de lookup: (peso_min, preco_min) -> valor
    fretes = FreteML.objects.all()
    lookup = {}
    for f in fretes:
        lookup[(float(f.peso_min), float(f.preco_min))] = f.valor

    # Monta as linhas da grade
    linhas = []
    for peso in faixas_peso:
        linha = {
            'peso_min': peso['peso_min'],
            'peso_max': peso['peso_max'],
            'valores': []
        }
        for preco in faixas_preco:
            valor = lookup.get(
                (float(peso['peso_min']), float(preco['preco_min'])), None)
            linha['valores'].append({
                'preco_min': preco['preco_min'],
                'valor': valor
            })
        linhas.append(linha)

    return render(request, 'precificacao/lista_frete_ml.html', {
        'faixas_preco': faixas_preco,
        'linhas': linhas,
    })


def calcular_frete_ml(request):
    if request.method == 'POST':
        from .models import FreteML
        from decimal import Decimal

        try:
            peso = Decimal(request.POST.get('peso', '0'))
            preco = Decimal(request.POST.get('preco', '0'))

            frete = FreteML.objects.filter(
                peso_min__lte=peso,
                preco_min__lte=preco
            ).filter(
                models.Q(peso_max__gte=peso) | models.Q(peso_max__isnull=True)
            ).filter(
                models.Q(preco_max__gte=preco) | models.Q(
                    preco_max__isnull=True)
            ).first()

            if frete:
                return render(request, 'parciais/resultado_frete.html', {
                    'valor': frete.valor,
                    'peso_min': frete.peso_min,
                    'preco_min': frete.preco_min,
                })
            else:
                return render(request, 'parciais/resultado_frete.html', {
                    'valor': None,
                })

        except Exception as e:
            return render(request, 'parciais/resultado_frete.html', {
                'valor': None,
                'erro': str(e),
            })


def _get_config_ml():
    """Retorna marketplace ML, tipos de anúncio e config logística."""
    marketplace = Marketplace.objects.get(sigla='ML')
    tipo_classico = TipoAnuncioML.objects.get(
        marketplace=marketplace, nome='Clássico')
    tipo_premium = TipoAnuncioML.objects.get(
        marketplace=marketplace, nome='Premium')
    try:
        config = marketplace.config_logistica
    except ConfiguracaoLogisticaML.DoesNotExist:
        config = None
    return marketplace, tipo_classico, tipo_premium, config


def _calcular_resultado_produto(d_produto, tipo_classico, tipo_premium, d_config):
    """Calcula preço ideal para Clássico e Premium."""
    res_c = calcular_preco_ideal_ml(
        comissao_pct=float(tipo_classico.comissao),
        meta_margem_pct=float(tipo_classico.meta_margem),
        **d_produto,
        **d_config,
    )

    res_p = None
    if res_c.get('preco'):
        acrescimo = float(tipo_premium.acrescimo_preco) / 100
        preco_p = arredondar_para_90(res_c['preco'] * (1 + acrescimo))
        frete_p = buscar_frete_ml(res_c['peso_lookup'], preco_p)
        margem_p = calcular_margem_ml(
            preco=preco_p,
            custo_final=res_c['custo_final'],
            custo_bruto=d_produto['custo_bruto'],
            comissao_pct=float(tipo_premium.comissao),
            icms_saida_pct=d_produto['icms_saida_media_pct'],
            icms_entrada_pct=d_produto['icms_entrada_pct'],
            pis_cofins_pct=d_produto['pis_cofins_pct'],
            frete=frete_p,
            coleta=res_c['coleta'],
            armazenagem=res_c['armazenagem'],
        )
        res_p = {
            'preco':      preco_p,
            'margem_pct': round(margem_p, 2),
            'frete':      round(frete_p, 2),
            'erro':       None,
        }

    return res_c, res_p


def precificacao_ml(request):
    from .funcoes.ml.calculos import calcular_custo_final, produto_para_dict, config_para_dict
    from django.core.paginator import Paginator

    marketplace, tipo_classico, tipo_premium, config = _get_config_ml()
    d_config = config_para_dict(config)

    busca = request.GET.get('busca', '').strip()
    produtos = Produto.objects.all().order_by('titulo')
    if busca:
        produtos = produtos.filter(
            models.Q(titulo__icontains=busca) |
            models.Q(sku__icontains=busca) |
            models.Q(cod_fabricante__icontains=busca)
        )

    paginator = Paginator(produtos, 25)
    pagina = request.GET.get('pagina', 1)
    page_obj = paginator.get_page(pagina)

    ids_pagina = [p.id for p in page_obj.object_list]

    anuncios_c = {
        a.produto_id: a
        for a in Anuncio.objects.filter(
            tipo_anuncio=tipo_classico,
            tipo_envio='FULL',
            produto_id__in=ids_pagina
        )
    }
    anuncios_p = {
        a.produto_id: a
        for a in Anuncio.objects.filter(
            tipo_anuncio=tipo_premium,
            tipo_envio='FULL',
            produto_id__in=ids_pagina
        )
    }

    lista = []
    for p in page_obj.object_list:
        d = produto_para_dict(p)
        cf = calcular_custo_final(
            d['custo_com_boni'], d['ipi_pct'], d['frete_cif_pct'], d['st_valor']
        )
        lista.append({
            'produto':          p,
            'custo_final':      round(cf, 2),
            'anuncio_classico': anuncios_c.get(p.id),
            'anuncio_premium':  anuncios_p.get(p.id),
        })

    contexto = {
        'lista':         lista,
        'page_obj':      page_obj,
        'busca':         busca,
        'tipo_classico': tipo_classico,
        'tipo_premium':  tipo_premium,
        'config':        config,
        'marketplace':   marketplace,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'parciais/card_tabela_ml.html', contexto)

    return render(request, 'precificacao/precificacao_ml.html', contexto)


def painel_produto_ml(request, produto_id):
    """HTMX — retorna o painel de edição expandido de um produto."""
    produto = get_object_or_404(Produto, pk=produto_id)
    marketplace, tipo_classico, tipo_premium, config = _get_config_ml()
    d_config = config_para_dict(config)
    d_produto = produto_para_dict(produto)

    res_c, res_p = _calcular_resultado_produto(
        d_produto, tipo_classico, tipo_premium, d_config)

    return render(request, 'parciais/painel_produto_ml.html', {
        'produto':       produto,
        'res_classico':  res_c,
        'res_premium':   res_p,
        'tipo_classico': tipo_classico,
        'tipo_premium':  tipo_premium,
    })


@require_POST
def calcular_produto_ml(request):
    """HTMX — recalcula em tempo real quando um campo é alterado no painel."""
    def _f(key, default=0.0):
        try:
            return float(request.POST.get(key, default))
        except (ValueError, TypeError):
            return float(default)

    produto_id = request.POST.get('produto_id')
    produto = get_object_or_404(Produto, pk=produto_id)
    marketplace, tipo_classico, tipo_premium, config = _get_config_ml()
    d_config = config_para_dict(config)

    d_produto = {
        'custo_bruto':           _f('custo'),
        'custo_com_boni':        _f('custo_com_boni') or _f('custo'),
        'ipi_pct':               _f('ipi'),
        'frete_cif_pct':         _f('frete_cif_fob'),
        'st_valor':              _f('st_valor'),
        'icms_entrada_pct':      _f('icms_entrada'),
        'icms_saida_media_pct':  _f('icms_saida_media'),
        'pis_cofins_pct':        _f('pis_cofins'),
        'peso_kg':               _f('peso'),
        'altura_cm':             _f('altura'),
        'largura_cm':            _f('largura'),
        'profundidade_cm':       _f('profundidade'),
    }

    res_c, res_p = _calcular_resultado_produto(
        d_produto, tipo_classico, tipo_premium, d_config)

    return render(request, 'parciais/resultado_produto_ml.html', {
        'res_classico': res_c,
        'res_premium':  res_p,
    })


@require_POST
def salvar_precificacao_ml(request):
    """Salva todas as alterações da sessão no banco."""
    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido'}, status=400)

    marketplace, tipo_classico, tipo_premium, config = _get_config_ml()
    d_config = config_para_dict(config)

    # Salva parâmetros master
    params = dados.get('parametros', {})
    if params:
        if 'classico_comissao' in params:
            tipo_classico.comissao = params['classico_comissao']
        if 'classico_meta_margem' in params:
            tipo_classico.meta_margem = params['classico_meta_margem']
        tipo_classico.save()
        if 'premium_comissao' in params:
            tipo_premium.comissao = params['premium_comissao']
        if 'premium_meta_margem' in params:
            tipo_premium.meta_margem = params['premium_meta_margem']
        if 'premium_acrescimo' in params:
            tipo_premium.acrescimo_preco = params['premium_acrescimo']
        tipo_premium.save()
        if config:
            if 'fator_coleta' in params:
                config.fator_coleta = params['fator_coleta']
            if 'armazenagem_diaria' in params:
                config.armazenagem_diaria = params['armazenagem_diaria']
            if 'periodo_armazenagem' in params:
                config.periodo_armazenagem = params['periodo_armazenagem']
            config.save()

    # Salva alterações por produto
    salvos = 0
    for item in dados.get('produtos', []):
        try:
            produto = Produto.objects.get(pk=item['id'])
            for campo in ['custo', 'custo_com_boni', 'ipi', 'icms_entrada',
                          'icms_saida_media', 'icms_saida_sp', 'pis_cofins',
                          'frete_cif_fob', 'mva', 'st_valor',
                          'peso', 'altura', 'largura', 'profundidade']:
                if campo in item:
                    setattr(produto, campo, item[campo])
            produto.save()

            d = produto_para_dict(produto)
            res_c, res_p = _calcular_resultado_produto(
                d, tipo_classico, tipo_premium, d_config)

            if res_c.get('preco'):
                Anuncio.objects.filter(produto=produto, tipo_anuncio=tipo_classico).update(
                    preco_ideal=res_c['preco'], calculado_em=timezone.now())
            if res_p and res_p.get('preco'):
                Anuncio.objects.filter(produto=produto, tipo_anuncio=tipo_premium).update(
                    preco_ideal=res_p['preco'], calculado_em=timezone.now())
            salvos += 1
        except Produto.DoesNotExist:
            continue

    return JsonResponse({'ok': True, 'salvos': salvos})
