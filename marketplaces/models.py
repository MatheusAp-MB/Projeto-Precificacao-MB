# * [RESUMO] → Models do app de marketplaces.
#              Define a estrutura de configuração de cada marketplace do sistema.
#              Adaptado da old_dev com expansão para margens, atacado e tipos logísticos.
#              Inclui FaixaArmazenagem para seleção dinâmica de custo por dimensão de produto.

from django.db import models


# ================================================
# MARKETPLACE
# ================================================

class Marketplace(models.Model):
    # * [EXPLICAÇÃO] → Entidade base genérica para todos os marketplaces do sistema.
    #                  Outros apps (anuncios, precificacao) referenciam daqui.

    nome  = models.CharField(max_length=100)
    sigla = models.CharField(max_length=20, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Marketplace'
        verbose_name_plural = 'Marketplaces'
        ordering            = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.sigla})'


# ================================================
# TIPO DE ANÚNCIO ML
# ================================================

class TipoAnuncioML(models.Model):
    # * [EXPLICAÇÃO] → Define os parâmetros de cada tipo de anúncio do ML.
    #                  Cada combinação de tipo, logística e catálogo vira um registro.
    #                  Ex: "Clássico FULL Catálogo", "Premium Flex", etc.

    class TipoAnuncio(models.TextChoices):
        CLASSICO = 'gold_special', 'Clássico'
        PREMIUM  = 'gold_pro',     'Premium'

    class TipoLogistico(models.TextChoices):
        FULL    = 'fulfillment', 'FULL'
        FLEX    = 'flex',        'Flex'
        PADRAO  = 'me2',         'Padrão'

    marketplace    = models.ForeignKey(
        Marketplace,
        on_delete=models.PROTECT,
        related_name='tipos_anuncio'
    )

    # Identificação do tipo
    nome           = models.CharField(max_length=100)
    tipo_anuncio   = models.CharField(max_length=20, choices=TipoAnuncio.choices)
    tipo_logistico = models.CharField(max_length=20, choices=TipoLogistico.choices)
    catalogo       = models.BooleanField(default=False)

    # Comissão e ajuste de preço
    # * [EXPLICAÇÃO] → comissao = % cobrado pelo marketplace sobre o preço de venda.
    #                  acrescimo_preco = % adicionado ao preço base (ex: Premium = +8%).
    comissao        = models.DecimalField(max_digits=5, decimal_places=2)
    acrescimo_preco = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Margens
    # * [EXPLICAÇÃO] → margem_padrao = meta de margem desejada.
    #                  margem_minima = limite inferior aceitável.
    #                  margem_maxima = limite superior para não perder competitividade.
    margem_padrao = models.DecimalField(max_digits=5, decimal_places=2)
    margem_minima = models.DecimalField(max_digits=5, decimal_places=2)
    margem_maxima = models.DecimalField(max_digits=5, decimal_places=2)

    # Atacado
    # * [EXPLICAÇÃO] → Descontos aplicados para compras em quantidade.
    #                  Definidos por marketplace e tipo de anúncio.
    desconto_atacado_2 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    desconto_atacado_3 = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Tipo de Anúncio ML'
        verbose_name_plural = 'Tipos de Anúncio ML'
        ordering            = ['marketplace', 'tipo_anuncio', 'tipo_logistico']

    def __str__(self):
        catalogo_str = ' Catálogo' if self.catalogo else ''
        return f'{self.marketplace.sigla} — {self.nome}{catalogo_str}'


# ================================================
# CONFIGURAÇÃO LOGÍSTICA ML
# ================================================

class ConfiguracaoLogisticaML(models.Model):
    # * [EXPLICAÇÃO] → Parâmetros específicos da logística FULL do Mercado Livre.
    #                  OneToOne com Marketplace — um registro por marketplace.
    #                  fator_coleta: custo de coleta em R$ por m³.
    #                  armaz_faixa_*: tarifas diárias de armazenagem por faixa de tempo.
    #                  periodo_armazenagem: dias considerados no cálculo mensal.

    marketplace = models.OneToOneField(
        Marketplace,
        on_delete=models.CASCADE,
        related_name='config_logistica'
    )

    fator_coleta        = models.DecimalField(max_digits=8, decimal_places=2, default=72)
    periodo_armazenagem = models.IntegerField(default=30)

    # * [EXPLICAÇÃO] → 4 faixas de armazenagem diária (R$/m³/dia).
    #                  Faixas correspondem a diferentes períodos de permanência no armazém.
    armaz_faixa_1 = models.DecimalField(max_digits=8, decimal_places=4, default=0.0070)
    armaz_faixa_2 = models.DecimalField(max_digits=8, decimal_places=4, default=0.0150)
    armaz_faixa_3 = models.DecimalField(max_digits=8, decimal_places=4, default=0.0500)
    armaz_faixa_4 = models.DecimalField(max_digits=8, decimal_places=4, default=0.1070)

    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Configuração Logística ML'
        verbose_name_plural = 'Configurações Logísticas ML'

    def __str__(self):
        return f'Config Logística {self.marketplace.sigla}'
    
# ================================================
# FAIXA DE ARMAZENAGEM
# ================================================

class FaixaArmazenagem(models.Model):
    # * [EXPLICAÇÃO] → Define as faixas de custo de armazenagem por tamanho de produto.
    #                  A faixa correta é selecionada dinamicamente pelas dimensões do produto:
    #                  itera em ordem crescente e usa a primeira onde TODAS as dimensões cabem.
    #                  Se nenhuma comportar o produto, usa a maior (fallback).

    marketplace      = models.ForeignKey(Marketplace, on_delete=models.PROTECT, related_name='faixas_armazenagem')
    nome             = models.CharField(max_length=50)
    valor_diario     = models.DecimalField(max_digits=8, decimal_places=4)
    max_altura       = models.DecimalField(max_digits=6, decimal_places=2)
    max_largura      = models.DecimalField(max_digits=6, decimal_places=2)
    max_profundidade = models.DecimalField(max_digits=6, decimal_places=2)
    ordem            = models.PositiveIntegerField(default=1)
    ativo            = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Faixa de Armazenagem'
        verbose_name_plural = 'Faixas de Armazenagem'
        ordering            = ['marketplace', 'ordem']

    def __str__(self):
        return f'{self.marketplace.sigla} — {self.nome} (R${self.valor_diario}/dia)'