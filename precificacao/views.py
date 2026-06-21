from django.shortcuts import render
from django.db import models

from .models import Produto, Marketplace, TipoAnuncioML, FreteML, Anuncio
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
