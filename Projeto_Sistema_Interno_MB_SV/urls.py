# * [RESUMO] → Arquivo de URLs principal do projeto.
#              Centraliza todas as rotas e delega para os urls.py de cada app.

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # * [EXPLICAÇÃO] → Rota do painel administrativo do Django.
    #                  Acessível em /admin/
    path('admin/', admin.site.urls),

    # * [EXPLICAÇÃO] → Rotas do app core — login, logout e homepage.
    #                  O include() delega para o urls.py do app core.
    path('', include('core.urls')),
    
    # * [EXPLICAÇÃO] → Rotas do app de precificação por marketplace.
    #                  O prefixo 'precificacao/' agrupa todas as telas do módulo.
    path('precificacao/', include('precificacao_marketplaces.urls')),

    # * [EXPLICAÇÃO] → Rotas do app de produtos.
    path('produtos/', include('produtos.urls')),
]