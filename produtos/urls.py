# * [RESUMO] → Rotas do app de produtos.

from django.urls import path
from . import views

urlpatterns = [
    # * [EXPLICAÇÃO] → Listagem de produtos.
    path('', views.view_produtos, name='produtos'),

    # * [EXPLICAÇÃO] → Endpoint HTMX do modal de detalhes do produto.
    path('<int:produto_id>/painel/', views.view_painel_produto, name='painel_produto'),
]
