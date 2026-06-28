# * [RESUMO] → Registro dos models no Django Admin.

from django.contrib import admin
from .models import Marketplace, TipoAnuncioML, ConfiguracaoLogisticaML, FaixaArmazenagem

@admin.register(Marketplace)
class MarketplaceAdmin(admin.ModelAdmin):
    list_display  = ['nome', 'sigla', 'ativo']
    list_filter   = ['ativo']


@admin.register(TipoAnuncioML)
class TipoAnuncioMLAdmin(admin.ModelAdmin):
    list_display  = ['marketplace', 'nome', 'tipo_anuncio', 'tipo_logistico', 'catalogo', 'comissao', 'margem_padrao']
    list_filter   = ['marketplace', 'tipo_anuncio', 'tipo_logistico', 'catalogo']


@admin.register(ConfiguracaoLogisticaML)
class ConfiguracaoLogisticaMLAdmin(admin.ModelAdmin):
    list_display  = ['marketplace', 'fator_coleta', 'periodo_armazenagem', 'armaz_faixa_2']

@admin.register(FaixaArmazenagem)
class FaixaArmazenagemAdmin(admin.ModelAdmin):
    list_display  = ['marketplace', 'nome', 'valor_diario', 'max_altura', 'max_largura', 'max_profundidade', 'ordem', 'ativo']
    list_filter   = ['marketplace', 'ativo']
    ordering      = ['marketplace', 'ordem']