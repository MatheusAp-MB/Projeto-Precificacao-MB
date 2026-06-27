# * [RESUMO] → Views do app de precificação por marketplace.
#              Cada view corresponde a uma tela do módulo.

from django.shortcuts import render
from .models import FreteML
from django.urls import reverse

# ================================================
# PRECIFICAÇÃO — GRID PRINCIPAL
# ================================================

def view_precificacao(request):
    # * [EXPLICAÇÃO] → Tela inicial do módulo de precificação.
    #                  Passa as URLs dos marketplaces com tela de precificação disponível.
    return render(request, 'pagina_precificacao/estrutura_precificacao.html', {
        'urls_marketplaces': {
            'mercado_livre': reverse('mercado_livre'),
        }
    })

# ================================================
# MERCADO LIVRE — GRID DE OPÇÕES
# ================================================

def view_mercado_livre(request):
    # * [EXPLICAÇÃO] → Tela do Mercado Livre — exibe um grid
    #                  com as opções disponíveis para o marketplace.
    return render(request, 'pagina_mercado_livre/estrutura_mercado_livre.html')


# ================================================
# TABELA DE FRETE ML
# ================================================

def view_tabela_frete_ml(request):
    # * [EXPLICAÇÃO] → Busca as faixas de preço únicas para montar os cabeçalhos da tabela.
    faixas_preco = FreteML.objects.values(
        'preco_min', 'preco_max'
    ).distinct().order_by('preco_min')

    # * [EXPLICAÇÃO] → Busca as faixas de peso únicas para montar as linhas da tabela.
    faixas_peso = FreteML.objects.values(
        'peso_min', 'peso_max'
    ).distinct().order_by('peso_min')

    # * [EXPLICAÇÃO] → Monta um dicionário de lookup (peso_min, preco_min) → valor
    #                  para montar a matriz sem múltiplas queries ao banco.
    lookup = {
        (float(f.peso_min), float(f.preco_min)): f.valor
        for f in FreteML.objects.all()
    }

    linhas = []
    for peso in faixas_peso:
        linha = {
            'peso_min': peso['peso_min'],
            'peso_max': peso['peso_max'],
            'valores': [
                {
                    'preco_min': preco['preco_min'],
                    'preco_max': preco['preco_max'],
                    'valor': lookup.get((float(peso['peso_min']), float(preco['preco_min'])))
                }
                for preco in faixas_preco
            ]
        }
        linhas.append(linha)

    return render(request, 'pagina_tabela_frete_ml/estrutura_tabela_frete_ml.html', {
        'faixas_preco': faixas_preco,
        'linhas': linhas,
    })

def view_calcular_frete_ml(request):
    # * [EXPLICAÇÃO] → Endpoint HTMX — recebe peso e preço via POST,
    #                  busca a célula correta no banco e retorna o parcial com o resultado.
    from decimal import Decimal
    from django.db import models as db_models

    try:
        peso  = Decimal(request.POST.get('peso', '0'))
        preco = Decimal(request.POST.get('preco', '0'))

        frete = FreteML.objects.filter(
            peso_min__lte=peso,
            preco_min__lte=preco
        ).filter(
            db_models.Q(peso_max__gte=peso) | db_models.Q(peso_max__isnull=True)
        ).filter(
            db_models.Q(preco_max__gte=preco) | db_models.Q(preco_max__isnull=True)
        ).first()

        if frete:
            return render(request, 'pagina_tabela_frete_ml/parciais/estrutura_parcial_resultado_frete_ml.html', {
                'valor':     frete.valor,
                'peso_min':  frete.peso_min,
                'preco_min': frete.preco_min,
            })

        return render(request, 'pagina_tabela_frete_ml/parciais/estrutura_parcial_resultado_frete_ml.html', {
            'valor': None,
        })

    except Exception as e:
        return render(request, 'pagina_tabela_frete_ml/parciais/estrutura_parcial_resultado_frete_ml.html', {
            'valor': None,
            'erro':  str(e),
        })