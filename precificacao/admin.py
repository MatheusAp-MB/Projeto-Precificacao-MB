from django.contrib import admin
from .models import Produto, FreteML, Marketplace, TipoAnuncioML, Anuncio, ConfiguracaoLogisticaML


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['sku', 'titulo', 'custo', 'estoque', 'curva']
    search_fields = ['sku', 'titulo', 'ean']
    list_filter = ['curva']


@admin.register(Marketplace)
class MarketplaceAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sigla', 'ativo']
    search_fields = ['nome', 'sigla']
    list_filter = ['ativo']


@admin.register(TipoAnuncioML)
class TipoAnuncioMLAdmin(admin.ModelAdmin):
    list_display = ['nome', 'marketplace',
                    'comissao', 'acrescimo_preco', 'meta_margem']
    search_fields = ['nome']
    list_filter = ['marketplace']


@admin.register(FreteML)
class FreteMLAdmin(admin.ModelAdmin):
    list_display = ['peso_min', 'peso_max', 'preco_min', 'preco_max', 'valor']
    ordering = ['peso_min', 'preco_min']


@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ['produto', 'tipo_anuncio', 'tipo_envio',
                    'catalogo', 'preco_atual', 'preco_ideal', 'status']
    search_fields = ['produto__sku', 'produto__titulo', 'id_marketplace']
    list_filter = ['tipo_anuncio', 'tipo_envio', 'catalogo', 'status']

@admin.register(ConfiguracaoLogisticaML)
class ConfiguracaoLogisticaMLAdmin(admin.ModelAdmin):
    list_display = ['marketplace', 'fator_coleta', 'armazenagem_diaria', 'periodo_armazenagem', 'atualizado_em']