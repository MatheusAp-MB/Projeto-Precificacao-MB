# * [RESUMO] → Registro dos models no Django Admin.

from django.contrib import admin
from .models import AnuncioML


# * [EXPLICAÇÃO] → Registra o AnuncioML no admin com as colunas mais relevantes.
@admin.register(AnuncioML)
class AnuncioMLAdmin(admin.ModelAdmin):
    list_display = ['mlb', 'produto', 'titulo_anuncio', 'tipo_anuncio', 'status', 'preco_classico_da_planilha', 'preco_classico_calculado', 'frete_calculado', 'frete_da_planilha']
    search_fields = ['mlb', 'mlbu', 'titulo_anuncio']
    list_filter   = ['tipo_anuncio', 'status', 'tipo_logistico', 'catalogo']