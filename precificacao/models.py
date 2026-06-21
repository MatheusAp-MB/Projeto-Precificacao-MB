from django.db import models

# Create your models here.

from django.db import models


class Produto(models.Model):

    class Curva(models.TextChoices):
        A = 'A', 'A'
        B = 'B', 'B'
        C = 'C', 'C'

    # Identificadores
    titulo = models.CharField(max_length=255)
    ean = models.CharField(max_length=20, unique=True, blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True)
    cod_fabricante = models.CharField(max_length=50, blank=True, null=True)

    # Classificação
    curva = models.CharField(
        max_length=1,
        choices=Curva.choices,
        blank=True,
        null=True
    )

    # Estoque
    estoque = models.IntegerField(default=0)

    # Financeiro
    custo = models.DecimalField(max_digits=10, decimal_places=2)
    custo_com_boni = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    # Tributário
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
    peso = models.DecimalField(max_digits=8, decimal_places=3)
    altura = models.DecimalField(max_digits=8, decimal_places=2)
    largura = models.DecimalField(max_digits=8, decimal_places=2)
    profundidade = models.DecimalField(max_digits=8, decimal_places=2)

    # Controle
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['titulo']

    def __str__(self):
        return f'{self.sku} — {self.titulo}'


class Marketplace(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=20, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Marketplace'
        verbose_name_plural = 'Marketplaces'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.sigla})'


class TipoAnuncioML(models.Model):
    marketplace = models.ForeignKey(
        Marketplace,
        on_delete=models.PROTECT,
        related_name='tipos_anuncio'
    )
    nome = models.CharField(max_length=50)
    comissao = models.DecimalField(max_digits=5, decimal_places=2)
    acrescimo_preco = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    meta_margem = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tipo de Anúncio ML'
        verbose_name_plural = 'Tipos de Anúncio ML'

    def __str__(self):
        return f'{self.marketplace.sigla} — {self.nome}'


class FreteML(models.Model):
    peso_min = models.DecimalField(max_digits=8, decimal_places=3)
    peso_max = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True
    )
    preco_min = models.DecimalField(max_digits=10, decimal_places=2)
    preco_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Frete ML'
        verbose_name_plural = 'Fretes ML'
        ordering = ['peso_min', 'preco_min']

    def __str__(self):
        return f'Peso {self.peso_min}-{self.peso_max}kg | Preço {self.preco_min}-{self.preco_max} → R${self.valor}'
    
class Anuncio(models.Model):

    class TipoEnvio(models.TextChoices):
        FLEX = 'FLEX', 'Flex'
        FULL = 'FULL', 'Full'

    class Status(models.TextChoices):
        ATIVO    = 'ATIVO',    'Ativo'
        PAUSADO  = 'PAUSADO',  'Pausado'
        INATIVO  = 'INATIVO',  'Inativo'

    # Conexões
    produto      = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='anuncios'
    )
    tipo_anuncio = models.ForeignKey(
        TipoAnuncioML,
        on_delete=models.PROTECT,
        related_name='anuncios'
    )

    # Identificação
    id_marketplace = models.CharField(max_length=50, unique=True)
    titulo         = models.CharField(max_length=255)

    # Tipo
    tipo_envio = models.CharField(max_length=10, choices=TipoEnvio.choices)
    catalogo   = models.BooleanField(default=False)

    # Preços
    preco_atual  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preco_ideal  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Estoque
    estoque = models.IntegerField(default=0)

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ATIVO
    )

    # Controle
    criado_em     = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    calculado_em  = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = 'Anúncio'
        verbose_name_plural = 'Anúncios'
        ordering            = ['produto', 'tipo_anuncio', 'tipo_envio']

    def __str__(self):
        return f'{self.produto.sku} — {self.tipo_anuncio.nome} {self.tipo_envio}'
    

class ConfiguracaoLogisticaML(models.Model):
    marketplace = models.OneToOneField(
        Marketplace,
        on_delete=models.CASCADE,
        related_name='config_logistica'
    )
    fator_coleta = models.DecimalField(
        max_digits=8, decimal_places=2, default=72,
        help_text='R$ por metro cúbico (coleta FULL)'
    )
    armazenagem_diaria = models.DecimalField(
        max_digits=8, decimal_places=4, default=0.015,
        help_text='R$ por dia (faixa média)'
    )
    periodo_armazenagem = models.IntegerField(
        default=30,
        help_text='Dias de armazenagem a considerar'
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração Logística ML'
        verbose_name_plural = 'Configurações Logísticas ML'

    def __str__(self):
        return f'Config Logística {self.marketplace.sigla}'