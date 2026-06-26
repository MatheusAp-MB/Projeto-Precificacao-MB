# * [RESUMO] → Registro dos models no Django Admin.
#              Permite gerenciar os dados pelo painel em /admin/

from django.contrib import admin
from .models import Produto


# * [EXPLICAÇÃO] → Registra o Produto no admin com as colunas mais relevantes.
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):

    list_display  = ['ean', 'titulo', 'curva', 'custo', 'peso', 'peso_cubado']
    search_fields = ['ean', 'titulo']
    list_filter   = ['curva']