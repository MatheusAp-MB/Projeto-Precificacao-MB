# * [RESUMO] → Rotas do app de anúncios.

from django.urls import path
from . import views

urlpatterns = [
    # * [EXPLICAÇÃO] → Grid de marketplaces do módulo de anúncios.
    path('', views.view_anuncios, name='anuncios'),

    # * [EXPLICAÇÃO] → Tela de anúncios do Mercado Livre.
    path('mercado-livre/', views.view_anuncios_ml , name='anuncios_ml'),
]