from django.contrib import admin

# Register your models here.
from .models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['sku', 'titulo', 'custo', 'estoque', 'curva']
    search_fields = ['sku', 'titulo', 'ean']
    list_filter = ['curva']