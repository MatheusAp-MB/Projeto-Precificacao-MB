# * [RESUMO] → Views do app de anúncios.
#              Cada view corresponde a uma tela do módulo.

from django.urls import reverse
from django.shortcuts import render
from .models import AnuncioML


# ================================================
# ANÚNCIOS — GRID DE MARKETPLACES
# ================================================

def view_anuncios(request):
    # * [EXPLICAÇÃO] → Tela inicial do módulo de anúncios.
    #                  Exibe um grid com os marketplaces disponíveis.
    return render(request, 'pagina_anuncios/estrutura_anuncios.html')


# ================================================
# ANÚNCIOS — MERCADO LIVRE
# ================================================

def view_anuncios_ml(request):
    # * [EXPLICAÇÃO] → Tela inicial do módulo de anúncios.
    #                  Passa as URLs dos marketplaces com tela de anúncios disponível.
    return render(request, 'pagina_anuncios/estrutura_anuncios.html', {
        'urls_marketplaces': {
            'mercado_livre': reverse('anuncios_ml'),
        }
    })
