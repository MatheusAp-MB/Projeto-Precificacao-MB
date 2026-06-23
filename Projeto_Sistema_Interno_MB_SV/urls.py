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
]