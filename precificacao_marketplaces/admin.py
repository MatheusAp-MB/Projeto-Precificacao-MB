# * [RESUMO] → Registro dos models no Django Admin.
#              Permite gerenciar os dados pelo painel em /admin/

from django.contrib import admin
from .models import FreteML


# * [EXPLICAÇÃO] → Registra o FreteML no admin com configurações
#                  para facilitar a visualização e edição da matriz.
@admin.register(FreteML)
class FreteMLAdmin(admin.ModelAdmin):

    # * [EXPLICAÇÃO] → Colunas exibidas na listagem do admin.
    list_display = ['peso_min', 'peso_max', 'preco_min', 'preco_max', 'valor']

    # * [EXPLICAÇÃO] → Campos pelo qual é possível ordenar clicando no cabeçalho.
    ordering = ['peso_min', 'preco_min']