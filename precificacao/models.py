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
    ipi = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    icms_entrada = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    icms_saida_sp = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    icms_saida_media = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    pis_cofins = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    mva = models.DecimalField(max_digits=5, decimal_places=4, default=0, blank=True, null=True)
    st_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    frete_cif_fob = models.DecimalField(max_digits=5, decimal_places=4, default=0, blank=True, null=True)

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