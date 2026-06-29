# Create your models here.
# * [RESUMO] → Models do app de produtos.
#              Define a estrutura de dados de um produto no sistema.

from django.db import models
from django.db.models import GeneratedField, ExpressionWrapper, DecimalField, F


# ================================================
# PRODUTO
# ================================================

class Produto(models.Model):

    class Curva(models.TextChoices):
        A = 'A', 'A'
        B = 'B', 'B'
        C = 'C', 'C'

    # Identificação
    # * [EXPLICAÇÃO] → EAN é o código de barras — identificador único do produto.
    ean = models.CharField(max_length=20, unique=True)
    titulo = models.CharField(max_length=255)
    curva = models.CharField(
        max_length=1, choices=Curva.choices, blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    estoque = models.IntegerField(default=0)
    cod_fabricante = models.CharField(max_length=50, blank=True, null=True)
    categoria = models.CharField(max_length=100, blank=True, null=True)
    ultima_compra = models.DateTimeField(blank=True, null=True)
    # * [EXPLICAÇÃO] → Data de cadastro no ERP — distinto do criado_em que é a data de entrada no DB.
    cadastrado_erp_em = models.DateTimeField(blank=True, null=True)

    # Financeiro
    custo = models.DecimalField(max_digits=10, decimal_places=2)
    custo_com_boni = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)

    # Fiscal
    # * [EXPLICAÇÃO] → Campos tributários do produto — variam por NCM e origem.
    #                  São características do produto, não do anúncio ou marketplace.
    ncm = models.CharField(max_length=10, blank=True, null=True)
    ipi = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    icms_entrada = models.DecimalField(
        max_digits=6, decimal_places=2, default=0)
    icms_saida_sp = models.DecimalField(
        max_digits=6, decimal_places=2, default=0)
    icms_saida_media = models.DecimalField(
        max_digits=6, decimal_places=2, default=0)
    pis_cofins = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    mva = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, blank=True, null=True)
    st_valor = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    frete_cif_fob = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, blank=True, null=True)

    # Dimensões
    # * [EXPLICAÇÃO] → peso e peso_cubado em kg. Altura, largura e profundidade em cm.
    #                  peso_cubado = (altura * largura * profundidade) / 6000
    peso = models.DecimalField(max_digits=8, decimal_places=3)
    altura = models.DecimalField(max_digits=8, decimal_places=2)
    largura = models.DecimalField(max_digits=8, decimal_places=2)
    profundidade = models.DecimalField(max_digits=8, decimal_places=2)

    peso_cubado = GeneratedField(
        expression=ExpressionWrapper(
            (F('altura') * F('largura') * F('profundidade')) / 6000,
            output_field=DecimalField(max_digits=8, decimal_places=3)
        ),
        output_field=DecimalField(max_digits=8, decimal_places=3),
        db_persist=True
    )

    # ================================================
    # ARMAZENAGEM
    # ================================================

    
    # * [EXPLICAÇÃO] → armazenagem_planilha: valor mensal importado diretamente da coluna BH
    #                  da planilha de precificação. Representa o custo mensal de armazenagem
    #                  definido manualmente na planilha (ex: R$0,21 / R$0,45 / R$3,21).
    #
    #                  ATENÇÃO — INCONSISTÊNCIA DOCUMENTADA:
    #                  A planilha atribui faixas de armazenagem sem seguir uma regra clara
    #                  baseada nas dimensões do produto. Ex: calcanheiras (produto pequeno)
    #                  recebem Faixa 4 (R$3,21), enquanto palmilhas (produto longo mas fino)
    #                  recebem Faixa 1 (R$0,21). A lógica exata não foi confirmada —
    #                  possivelmente usa dimensão de embalagem ou atribuição manual.
    #
    #                  O sistema mantém dois cálculos paralelos:
    #                  - _dinamico: seleção automática de faixa pelas dimensões do produto
    #                  - _planilha: usa este campo diretamente (replica a planilha)
    #
    # # [STATUS: DESENVOLVIMENTO] → Remover quando a regra de faixas for padronizada
    #                               e validada com o criador da planilha.
    armazenagem_planilha = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)

    # Controle
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['titulo']

    def __str__(self):
        return f'{self.ean} — {self.titulo}'
