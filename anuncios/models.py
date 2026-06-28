# * [RESUMO] → Models do app de anúncios.
#              Define AnuncioML (dados do anúncio no Mercado Livre) e
#              BaseDeCalculo (registro detalhado de cada etapa do cálculo de precificação).
#
#              Convenção de nomenclatura adotada no projeto:
#              - Campos com sufixo "_real"      → valor importado da planilha (fonte da verdade externa)
#              - Campos com sufixo "_calculado" → valor gerado pelo sistema (signal ou Goal Seek)
#              - As fórmulas sempre usam os campos "_calculado" — os "_real" são apenas para auditoria/comparação.

from django.db import models
from produtos.models import Produto


# ================================================
# ANÚNCIO MERCADO LIVRE
# ================================================

class AnuncioML(models.Model):
    # * [EXPLICAÇÃO] → Representa um anúncio publicado no Mercado Livre.
    #                  Cada linha é um anúncio único identificado pelo MLB.
    #                  Um mesmo produto pode ter múltiplos anúncios (Clássico, Premium, variações).

    class TipoAnuncio(models.TextChoices):
        CLASSICO = 'gold_special', 'Clássico'
        PREMIUM  = 'gold_pro',     'Premium'

    class TipoLogistico(models.TextChoices):
        FULL     = 'fulfillment', 'FULL'
        ME_SEND  = 'me2',         'Manda tu'
        FLEX     = 'flex',        'Flex'
        DROPSHIP = 'drop_off',    'Drop-off'

    class Status(models.TextChoices):
        ATIVO   = 'active',  'Ativo'
        PAUSADO = 'paused',  'Pausado'
        FECHADO = 'closed',  'Fechado'

    class Nivel(models.TextChoices):
        BOM     = 'good',    'Bom'
        REGULAR = 'regular', 'Regular'
        RUIM    = 'bad',     'Ruim'

    # ================================================
    # IDENTIFICADORES
    # ================================================

    mlb  = models.CharField(max_length=20, unique=True)
    mlbu = models.CharField(max_length=20, blank=True, null=True)

    # * [EXPLICAÇÃO] → Ligação com o produto via SKU — regra do projeto.
    #                  Se o SKU do anúncio não bater com o Produto, está errado.
    produto = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anuncios_ml',
        to_field='sku'
    )

    titulo_anuncio = models.CharField(max_length=255, blank=True, null=True)

    # ================================================
    # TIPO
    # ================================================

    tipo_anuncio   = models.CharField(max_length=20, choices=TipoAnuncio.choices,   blank=True, null=True)
    tipo_logistico = models.CharField(max_length=20, choices=TipoLogistico.choices, blank=True, null=True)
    catalogo       = models.BooleanField(default=False)

    # ================================================
    # ESTADO
    # ================================================

    status    = models.CharField(max_length=10, choices=Status.choices, blank=True, null=True)
    estoque   = models.IntegerField(default=0)
    score     = models.IntegerField(blank=True, null=True)
    nivel     = models.CharField(max_length=10, choices=Nivel.choices, blank=True, null=True)
    qtd_vendas = models.IntegerField(default=0)
    permalink  = models.URLField(max_length=500, blank=True, null=True)

    data_criacao_ml       = models.DateTimeField(blank=True, null=True)
    ultima_atualizacao_ml = models.DateTimeField(blank=True, null=True)

    # ================================================
    # PRECIFICAÇÃO — FRETE
    # ================================================

    # * [EXPLICAÇÃO] → frete_real      → importado da planilha para validação.
    #                  frete_calculado → calculado pelo sistema via tabela FreteML.
    # # [STATUS: DESENVOLVIMENTO] → frete_real será removido após validação aprovada.
    frete_real      = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    frete_calculado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # ================================================
    # PRECIFICAÇÃO — PREÇO CLÁSSICO
    # ================================================

    # * [EXPLICAÇÃO] → preco_classico_real      → importado da planilha (resultado do Goal Seek do Excel).
    #                  preco_classico_calculado → calculado pelo sistema (Goal Seek interno).
    #                  Por enquanto, preco_classico_calculado é uma cópia do real.
    #                  Todas as fórmulas do sistema usam preco_classico_calculado.
    preco_classico_real      = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    preco_classico_calculado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # ================================================
    # PRECIFICAÇÃO — PREÇO PREMIUM
    # ================================================

    # * [EXPLICAÇÃO] → preco_premium_real      → importado da planilha.
    #                  preco_premium_calculado → calculado pelo sistema via RoundUpTo90(preco_classico × 1.08).
    preco_premium_real      = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    preco_premium_calculado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # ================================================
    # PRECIFICAÇÃO — MARGEM CLÁSSICA
    # ================================================

    # * [EXPLICAÇÃO] → margem_classico_real      → importado da planilha (resultado do cálculo do Excel).
    #                  margem_classico_calculado → calculado pelo sistema a partir de preco_classico_calculado.
    margem_classico_real      = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    margem_classico_calculado = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    # ================================================
    # PRECIFICAÇÃO — MARGEM PREMIUM
    # ================================================

    # * [EXPLICAÇÃO] → margem_premium_real      → importado da planilha.
    #                  margem_premium_calculado → calculado pelo sistema a partir de preco_premium_calculado.
    margem_premium_real      = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    margem_premium_calculado = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    # ================================================
    # META
    # ================================================

    class Meta:
        verbose_name        = 'Anúncio ML'
        verbose_name_plural = 'Anúncios ML'
        ordering            = ['mlb']

    def __str__(self):
        return f'{self.mlb} — {self.titulo_anuncio}'


# ================================================
# BASE DE CÁLCULO
# ================================================

class BaseDeCalculo(models.Model):
    # * [EXPLICAÇÃO] → Registro completo de todos os valores que compõem o cálculo
    #                  de precificação de um anúncio. Serve como modo debug —
    #                  o usuário pode conferir cada etapa do cálculo em detalhe.
    #                  Relação OneToOne com AnuncioML — um registro por anúncio,
    #                  sempre sobrescrito quando o cálculo é refeito.

    anuncio      = models.OneToOneField(AnuncioML, on_delete=models.CASCADE, related_name='base_calculo')
    calculado_em = models.DateTimeField(auto_now=True)

    # ================================================
    # DADOS DE ENTRADA — PRODUTO
    # ================================================
    # * [EXPLICAÇÃO] → Cópia dos dados do produto no momento do cálculo.
    #                  Garante rastreabilidade mesmo se o produto for alterado depois.

    entrada_custo            = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    entrada_custo_com_boni   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    entrada_ipi              = models.DecimalField(max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_frete_cif_fob    = models.DecimalField(max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_st_valor         = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    entrada_icms_entrada     = models.DecimalField(max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_icms_saida_media = models.DecimalField(max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_pis_cofins       = models.DecimalField(max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_peso             = models.DecimalField(max_digits=8,  decimal_places=3, null=True, blank=True)
    entrada_peso_cubado      = models.DecimalField(max_digits=8,  decimal_places=3, null=True, blank=True)
    entrada_altura           = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)
    entrada_largura          = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)
    entrada_profundidade     = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)

    # ================================================
    # DADOS DE ENTRADA — ANÚNCIO E MARKETPLACE
    # ================================================

    entrada_preco_classico_real      = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    entrada_comissao_classico        = models.DecimalField(max_digits=5,  decimal_places=2, null=True, blank=True)
    entrada_acrescimo_premium        = models.DecimalField(max_digits=5,  decimal_places=2, null=True, blank=True)
    entrada_fator_coleta             = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)
    entrada_armazenagem_faixa_valor  = models.DecimalField(max_digits=8,  decimal_places=4, null=True, blank=True)
    entrada_armazenagem_periodo      = models.IntegerField(null=True, blank=True)

    # ================================================
    # FÓRMULAS — VALORES INTERMEDIÁRIOS
    # ================================================
    # * [EXPLICAÇÃO] → Cada etapa do cálculo é registrada com sua fórmula e valor resultante.
    #                  Permite auditar qualquer divergência entre o sistema e a planilha.

    formula_metro_cubico = models.CharField(
        max_length=200, blank=True,
        default='(Altura ÷ 100) × (Largura ÷ 100) × (Profundidade ÷ 100)'
    )
    calc_metro_cubico = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    formula_custo_final = models.CharField(
        max_length=200, blank=True,
        default='Custo c/ Boni + (Custo c/ Boni × IPI) + (Custo c/ Boni × Frete CIF/FOB) + ST Valor'
    )
    calc_custo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_coleta = models.CharField(
        max_length=200, blank=True,
        default='Metro Cúbico × Fator de Coleta'
    )
    calc_coleta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_armazenagem = models.CharField(
        max_length=200, blank=True,
        default='Tarifa Diária da Faixa × Período de Armazenagem'
    )
    calc_armazenagem = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_preco_premium = models.CharField(
        max_length=200, blank=True,
        default='RoundUpTo90(Preço Clássico Calculado × (1 + Acréscimo Premium))'
    )
    calc_preco_premium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_comissao_classico = models.CharField(
        max_length=200, blank=True,
        default='Preço Clássico Calculado × Comissão Clássico'
    )
    calc_comissao_classico = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_comissao_premium = models.CharField(
        max_length=200, blank=True,
        default='Preço Premium Calculado × Comissão Premium'
    )
    calc_comissao_premium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_icms_classico = models.CharField(
        max_length=200, blank=True,
        default='(Preço Clássico Calculado × ICMS Saída) - (Custo × ICMS Entrada)'
    )
    calc_icms_classico = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_icms_premium = models.CharField(
        max_length=200, blank=True,
        default='(Preço Premium Calculado × ICMS Saída) - (Custo × ICMS Entrada)'
    )
    calc_icms_premium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_pis_cofins_classico = models.CharField(
        max_length=200, blank=True,
        default='(Preço Clássico Calculado - Custo) × PIS/COFINS'
    )
    calc_pis_cofins_classico = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_pis_cofins_premium = models.CharField(
        max_length=200, blank=True,
        default='(Preço Premium Calculado - Custo) × PIS/COFINS'
    )
    calc_pis_cofins_premium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # ================================================
    # RESULTADOS FINAIS
    # ================================================

    formula_margem_classico = models.CharField(
        max_length=500, blank=True,
        default='Preço Clássico - Frete - Coleta - Armazenagem - Custo Final - Comissão Clássico - ICMS Clássico - PIS/COFINS Clássico'
    )
    resultado_margem_classico_valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    resultado_margem_classico_pct   = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)

    formula_margem_premium = models.CharField(
        max_length=500, blank=True,
        default='Preço Premium - Frete - Coleta - Armazenagem - Custo Final - Comissão Premium - ICMS Premium - PIS/COFINS Premium'
    )
    resultado_margem_premium_valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    resultado_margem_premium_pct   = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name        = 'Base de Cálculo'
        verbose_name_plural = 'Bases de Cálculo'

    def __str__(self):
        return f'Base de Cálculo — {self.anuncio.mlb}'