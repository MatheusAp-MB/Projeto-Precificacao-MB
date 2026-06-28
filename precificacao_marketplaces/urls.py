# * [RESUMO] → Rotas do app de precificação por marketplace.

from django.urls import path
from . import views

urlpatterns = [
    # * [EXPLICAÇÃO] → Grid principal do módulo de precificação.
    path('', views.view_precificacao, name='precificacao'),

    # * [EXPLICAÇÃO] → Grid de opções do Mercado Livre.
    path('mercado-livre/', views.view_mercado_livre, name='mercado_livre'),

    # * [EXPLICAÇÃO] → Tabela de frete do Mercado Livre.
    path('mercado-livre/tabela-de-frete/', views.view_tabela_frete_ml, name='tabela_frete_ml'),

    # * [EXPLICAÇÃO] → Endpoint HTMX da calculadora de frete ML.
    path('mercado-livre/tabela-de-frete/calcular/', views.view_calcular_frete_ml, name='calcular_frete_ml'),

    # * [EXPLICAÇÃO] → Tela de precificação de anúncios do Mercado Livre.
    path('mercado-livre/precificar/', views.view_precificar_ml, name='precificar_ml'),

    path('mercado-livre/precificar/<int:anuncio_id>/painel/', views.view_painel_precificar_ml, name='painel_precificar_ml'),



]