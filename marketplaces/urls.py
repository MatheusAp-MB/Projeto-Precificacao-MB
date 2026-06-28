# * [RESUMO] → Rotas do app de marketplaces.

from django.urls import path
from . import views

urlpatterns = [
    # * [EXPLICAÇÃO] → Grid de marketplaces.
    path('', views.view_marketplaces, name='marketplaces'),

    # * [EXPLICAÇÃO] → Configurações do Mercado Livre.
    path('mercado-livre/', views.view_configuracoes_ml, name='configuracoes_ml'),

]