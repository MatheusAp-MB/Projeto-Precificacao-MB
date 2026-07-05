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

    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=20, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Marketplace'
        verbose_name_plural = 'Marketplaces'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.sigla})'


# ================================================
#          TIPO DE ANÚNCIO ML
# ================================================


class TipoAnuncioML(models.Model):
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE)

    class Status(models.TextChoices):
        ATIVO = 'active',           'Ativo'
        PAUSADO = 'paused',            'Pausado'
        FECHADO = 'closed',            'Encerrado'
        EM_REVISAO = 'under_review',      'Em revisão'
        DEBITO_PENDENTE = 'payment_required',  'Débito pendente'
        AGUARDANDO_ATIVACAO = 'not_yet_active',    'Aguardando ativação'

    class TipoAnuncio(models.TextChoices):
        CLASSICO = 'gold_special', 'Clássico'
        PREMIUM = 'gold_pro',     'Premium'

    class TipoLogistico(models.TextChoices):
        FULL = 'fulfillment',   'FULL'
        COLETA = 'cross_docking', 'Coleta'
        AGENCIA = 'xd_drop_off',   'Agência'
        FLEX_PURO = 'self_service',  'Flex Puro'
        LEGADO = 'not_specified', 'Legado'
        CORREIOS = 'drop_off',      'Correios'
        POR_NOSSA_CONTA = 'custom',        'Por nossa conta'

    status = models.CharField(max_length=20, choices=Status.choices)
    tipo_anuncio = models.CharField(max_length=20, choices=TipoAnuncio.choices)
    tipo_logistico = models.CharField(
        max_length=20, choices=TipoLogistico.choices)
    catalogo = models.BooleanField()
    flex = models.BooleanField()

    nome = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ['marketplace', 'status',
                           'tipo_anuncio', 'tipo_logistico', 'catalogo', 'flex']
        verbose_name = 'Tipo de Anúncio ML'
        verbose_name_plural = 'Tipos de Anúncio ML'

    def __str__(self):
        return self.nome or f'{self.status} / {self.tipo_anuncio} / {self.tipo_logistico} / catálogo={self.catalogo} / flex={self.flex}'


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

    fator_coleta = models.DecimalField(
        max_digits=8, decimal_places=2, default=72)
    periodo_armazenagem = models.IntegerField(default=30)

    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração Logística ML'
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

    marketplace = models.ForeignKey(
        Marketplace, on_delete=models.PROTECT, related_name='faixas_armazenagem')
    nome = models.CharField(max_length=50)
    valor_diario = models.DecimalField(max_digits=8, decimal_places=4)
    max_altura = models.DecimalField(max_digits=6, decimal_places=2)
    max_largura = models.DecimalField(max_digits=6, decimal_places=2)
    max_profundidade = models.DecimalField(max_digits=6, decimal_places=2)
    ordem = models.PositiveIntegerField(default=1)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Faixa de Armazenagem'
        verbose_name_plural = 'Faixas de Armazenagem'
        ordering = ['marketplace', 'ordem']

    def __str__(self):
        return f'{self.marketplace.sigla} — {self.nome} (R${self.valor_diario}/dia)'
