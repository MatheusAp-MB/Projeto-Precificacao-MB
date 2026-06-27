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
        PREMIUM  = 'gold_pro',     'Premium'

    class TipoLogistico(models.TextChoices):
        # * [EXPLICAÇÃO] → Tipos logísticos disponíveis no Mercado Livre.
        FULL      = 'fulfillment', 'FULL'
        ME_SEND   = 'me2',         'Manda tu'
        FLEX      = 'flex',        'Flex'
        DROPSHIP  = 'drop_off',    'Drop-off'

    class Status(models.TextChoices):
        ATIVO    = 'active',  'Ativo'
        PAUSADO  = 'paused',  'Pausado'
        FECHADO  = 'closed',  'Fechado'

    class Nivel(models.TextChoices):
        BOM      = 'good',    'Bom'
        REGULAR  = 'regular', 'Regular'
        RUIM     = 'bad',     'Ruim'

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
    preco          = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # ================================================
    # TIPO
    # ================================================

    tipo_anuncio  = models.CharField(max_length=20, choices=TipoAnuncio.choices, blank=True, null=True)
    tipo_logistico = models.CharField(max_length=20, choices=TipoLogistico.choices, blank=True, null=True)
    catalogo      = models.BooleanField(default=False)

    # ================================================
    # ESTADO
    # ================================================

    status  = models.CharField(max_length=10, choices=Status.choices, blank=True, null=True)
    estoque = models.IntegerField(default=0)
    score   = models.IntegerField(blank=True, null=True)
    nivel   = models.CharField(max_length=10, choices=Nivel.choices, blank=True, null=True)

    # ================================================
    # CONTROLE
    # ================================================

    data_criacao_ml        = models.DateTimeField(blank=True, null=True)
    ultima_atualizacao_ml  = models.DateTimeField(blank=True, null=True)
    qtd_vendas             = models.IntegerField(default=0)
    permalink              = models.URLField(max_length=500, blank=True, null=True)

    # ================================================
    # PRECIFICAÇÃO
    # ================================================

    # * [EXPLICAÇÃO] → frete_calculado → calculado pelo sistema via tabela FreteML.
    #                  frete_real      → importado da planilha para validação.
    # # [STATUS: DESENVOLVIMENTO] → frete_real removido após validação aprovada.
    frete_calculado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    frete_real      = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # ================================================
    # META
    # ================================================

    class Meta:
        verbose_name        = 'Anúncio ML'
        verbose_name_plural = 'Anúncios ML'
        ordering            = ['mlb']

    def __str__(self):
        return f'{self.mlb} — {self.titulo_anuncio}'