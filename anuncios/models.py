# * [RESUMO] → Models do app de anúncios.
#              Define a estrutura de dados de um anúncio por marketplace.

from django.db import models
from produtos.models import Produto


# ================================================
# ANÚNCIO MERCADO LIVRE
# ================================================

class AnuncioML(models.Model):

    class TipoAnuncio(models.TextChoices):
        # * [EXPLICAÇÃO] → Tipos de anúncio do Mercado Livre.
        CLASSICO = 'gold_special', 'Clássico'
        PREMIUM = 'gold_pro',     'Premium'

    class TipoLogistico(models.TextChoices):
        # * [EXPLICAÇÃO] → Tipos logísticos disponíveis no Mercado Livre.
        FULL = 'fulfillment', 'FULL'
        ME_SEND = 'me2',         'Manda tu'
        FLEX = 'flex',        'Flex'
        DROPSHIP = 'drop_off',    'Drop-off'

    class Status(models.TextChoices):
        ATIVO = 'active',  'Ativo'
        PAUSADO = 'paused',  'Pausado'
        FECHADO = 'closed',  'Fechado'

    class Nivel(models.TextChoices):
        BOM = 'good',    'Bom'
        REGULAR = 'regular', 'Regular'
        RUIM = 'bad',     'Ruim'

    # ================================================
    # IDENTIFICADORES
    # ================================================

    mlb = models.CharField(max_length=20, unique=True)
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
    preco = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)

    # Valores reais — vindos da planilha
    preco_real_premium = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    margem_real_classico = models.DecimalField(
        max_digits=6,  decimal_places=2, null=True, blank=True)
    margem_real_premium = models.DecimalField(
        max_digits=6,  decimal_places=2, null=True, blank=True)

    # Valores calculados — gerados pelo signal
    preco_calculado_premium = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    # ================================================
    # TIPO
    # ================================================

    tipo_anuncio = models.CharField(
        max_length=20, choices=TipoAnuncio.choices, blank=True, null=True)
    tipo_logistico = models.CharField(
        max_length=20, choices=TipoLogistico.choices, blank=True, null=True)
    catalogo = models.BooleanField(default=False)

    # ================================================
    # ESTADO
    # ================================================

    status = models.CharField(
        max_length=10, choices=Status.choices, blank=True, null=True)
    estoque = models.IntegerField(default=0)
    score = models.IntegerField(blank=True, null=True)
    nivel = models.CharField(
        max_length=10, choices=Nivel.choices, blank=True, null=True)

    # ================================================
    # CONTROLE
    # ================================================

    data_criacao_ml = models.DateTimeField(blank=True, null=True)
    ultima_atualizacao_ml = models.DateTimeField(blank=True, null=True)
    qtd_vendas = models.IntegerField(default=0)
    permalink = models.URLField(max_length=500, blank=True, null=True)

    # ================================================
    # PRECIFICAÇÃO
    # ================================================

    # * [EXPLICAÇÃO] → frete_calculado → calculado pelo sistema via tabela FreteML.
    #                  frete_real      → importado da planilha para validação.
    # # [STATUS: DESENVOLVIMENTO] → frete_real removido após validação aprovada.
    frete_calculado = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    frete_real = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)

    # ================================================
    # META
    # ================================================

    class Meta:
        verbose_name = 'Anúncio ML'
        verbose_name_plural = 'Anúncios ML'
        ordering = ['mlb']

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
    #                  sempre atualizado quando o cálculo é refeito.

    anuncio = models.OneToOneField(
        AnuncioML,
        on_delete=models.CASCADE,
        related_name='base_calculo'
    )
    calculado_em = models.DateTimeField(auto_now=True)

    # ================================================
    # DADOS DE ENTRADA — PRODUTO
    # ================================================
    # * [EXPLICAÇÃO] → Cópia dos dados do produto no momento do cálculo.
    #                  Garante rastreabilidade mesmo se o produto for alterado.

    entrada_custo = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    entrada_custo_com_boni = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    entrada_ipi = models.DecimalField(
        max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_frete_cif_fob = models.DecimalField(
        max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_st_valor = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    entrada_icms_entrada = models.DecimalField(
        max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_icms_saida_media = models.DecimalField(
        max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_pis_cofins = models.DecimalField(
        max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_peso = models.DecimalField(
        max_digits=8,  decimal_places=3, null=True, blank=True)
    entrada_peso_cubado = models.DecimalField(
        max_digits=8,  decimal_places=3, null=True, blank=True)
    entrada_altura = models.DecimalField(
        max_digits=8,  decimal_places=2, null=True, blank=True)
    entrada_largura = models.DecimalField(
        max_digits=8,  decimal_places=2, null=True, blank=True)
    entrada_profundidade = models.DecimalField(
        max_digits=8,  decimal_places=2, null=True, blank=True)

    # ================================================
    # DADOS DE ENTRADA — ANÚNCIO E MARKETPLACE
    # ================================================

    entrada_preco_classico = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    entrada_comissao = models.DecimalField(
        max_digits=5,  decimal_places=2, null=True, blank=True)
    entrada_acrescimo_premium = models.DecimalField(
        max_digits=5,  decimal_places=2, null=True, blank=True)
    entrada_fator_coleta = models.DecimalField(
        max_digits=8,  decimal_places=2, null=True, blank=True)
    entrada_armaz_faixa = models.DecimalField(
        max_digits=8,  decimal_places=4, null=True, blank=True)
    entrada_periodo_armaz = models.IntegerField(null=True, blank=True)

    # ================================================
    # FÓRMULAS — VALORES INTERMEDIÁRIOS
    # ================================================

    formula_metro_cubico = models.CharField(
        max_length=200, blank=True,
        default='(Altura ÷ 100) × (Largura ÷ 100) × (Profundidade ÷ 100)'
    )
    calc_metro_cubico = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True)

    formula_custo_final = models.CharField(
        max_length=200, blank=True,
        default='Custo c/ Boni + (Custo c/ Boni × IPI) + (Custo c/ Boni × Frete CIF/FOB) + ST Valor'
    )
    calc_custo_final = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    formula_coleta = models.CharField(
        max_length=200, blank=True,
        default='Metro Cúbico × Fator de Coleta (apenas FULL)'
    )
    calc_coleta = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    formula_armazenagem = models.CharField(
        max_length=200, blank=True,
        default='Metro Cúbico × Tarifa de Armazenagem Diária × Período de Armazenagem (apenas FULL)'
    )
    calc_armazenagem = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    formula_preco_premium = models.CharField(
        max_length=200, blank=True,
        default='Preço Clássico × (1 + Acréscimo Premium)'
    )
    calc_preco_premium = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    formula_comissao_classico = models.CharField(
        max_length=200, blank=True,
        default='Preço Clássico × Comissão'
    )
    calc_comissao_classico = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    formula_comissao_premium = models.CharField(
        max_length=200, blank=True,
        default='Preço Premium × Comissão Premium'
    )
    calc_comissao_premium = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    formula_icms_classico = models.CharField(
        max_length=200, blank=True,
        default='(Preço Clássico × ICMS Saída) - (Custo × ICMS Entrada)'
    )
    calc_icms_classico = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    formula_icms_premium = models.CharField(
        max_length=200, blank=True,
        default='(Preço Premium × ICMS Saída) - (Custo × ICMS Entrada)'
    )
    calc_icms_premium = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    formula_pis_cofins_classico = models.CharField(
        max_length=200, blank=True,
        default='(Preço Clássico - Custo) × PIS/COFINS'
    )
    calc_pis_cofins_classico = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    formula_pis_cofins_premium = models.CharField(
        max_length=200, blank=True,
        default='(Preço Premium - Custo) × PIS/COFINS'
    )
    calc_pis_cofins_premium = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    # ================================================
    # RESULTADOS FINAIS
    # ================================================

    formula_margem_classico = models.CharField(
        max_length=500, blank=True,
        default='Preço Clássico - Frete - Coleta - Armazenagem - Custo Final - Comissão - ICMS - PIS/COFINS'
    )
    resultado_margem_valor_classico = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    resultado_margem_pct_classico = models.DecimalField(
        max_digits=8,  decimal_places=2, null=True, blank=True)

    formula_margem_premium = models.CharField(
        max_length=500, blank=True,
        default='Preço Premium - Frete - Coleta - Armazenagem - Custo Final - Comissão Premium - ICMS Premium - PIS/COFINS Premium'
    )
    resultado_margem_valor_premium = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    resultado_margem_pct_premium = models.DecimalField(
        max_digits=8,  decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Base de Cálculo'
        verbose_name_plural = 'Bases de Cálculo'

    def __str__(self):
        return f'Base de Cálculo — {self.anuncio.mlb}'
