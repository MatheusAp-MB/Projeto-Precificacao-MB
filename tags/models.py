# * [RESUMO] → Models do app de tags.
#              Define TagPreco — tags aplicáveis a anúncios para modificar
#              o preço calculado pelo CardapioPrecos.
#              Transversal a todos os marketplaces.

from django.db import models


class TagPreco(models.Model):
    # * [EXPLICAÇÃO] → Tag de modificação de preço aplicável a qualquer anúncio.
    #                  desconto  → reduz o preco_em_uso (ex: promoção)
    #                  acrescimo → aumenta o preco_em_uso (ex: alta demanda)
    #                  O sistema reaplica a tag a cada recálculo do CardapioPrecos,
    #                  exceto quando o anúncio tem preco_travado = True.

    class Tipo(models.TextChoices):
        DESCONTO  = 'desconto',  'Desconto'
        ACRESCIMO = 'acrescimo', 'Acréscimo'

    nome      = models.CharField(max_length=50)
    tipo      = models.CharField(max_length=10, choices=Tipo.choices)
    valor_pct = models.DecimalField(max_digits=5, decimal_places=2)
    cor       = models.CharField(max_length=7, default='#64748b')
    ativo     = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Tag de Preço'
        verbose_name_plural = 'Tags de Preço'
        ordering            = ['tipo', 'valor_pct']

    def __str__(self):
        simbolo = '-' if self.tipo == 'desconto' else '+'
        return f'{self.nome} ({simbolo}{self.valor_pct}%)'