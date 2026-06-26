# * [RESUMO] → Rotas do app de produtos.

from django.urls import path
from . import views

urlpatterns = [
    # * [EXPLICAÇÃO] → Listagem de produtos.
    path('', views.view_produtos, name='produtos'),
]