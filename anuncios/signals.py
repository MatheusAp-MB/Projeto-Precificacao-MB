# * [RESUMO] → Signals do app de anúncios.
#              Garantem que frete_calculado está sempre atualizado automaticamente,
#              independente de onde a mudança veio — anúncio, produto ou tabela de frete.

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)


# * [EXPLICAÇÃO] → Importações dentro das funções para evitar importação circular
#                  entre os apps anuncios, produtos e precificacao_marketplaces.


def calcular_frete_para_anuncio(anuncio):
    from precificacao_marketplaces.models import FreteML

    if not anuncio.produto or not anuncio.preco:
        logger.info(f'[FRETE] {anuncio.mlb} → ignorado (sem produto ou preço)')
        return

    produto = anuncio.produto
    peso = max(produto.peso, produto.peso_cubado)
    preco = anuncio.preco

    frete = FreteML.objects.filter(
        peso_min__lte=peso,
        preco_min__lte=preco
    ).filter(
        Q(peso_max__gte=peso) | Q(peso_max__isnull=True)
    ).filter(
        Q(preco_max__gte=preco) | Q(preco_max__isnull=True)
    ).first()

    novo_valor = frete.valor if frete else None

    type(anuncio).objects.filter(pk=anuncio.pk).update(
        frete_calculado=novo_valor)
    logger.info(
        f'[FRETE] {anuncio.mlb} → peso={peso}kg | preço=R${preco} | frete=R${novo_valor}')


# ================================================
# SIGNAL — ANUNCIO ML
# ================================================

@receiver(post_save, sender='anuncios.AnuncioML')
def signal_anuncio_ml_salvo(sender, instance, **kwargs):
    # * [EXPLICAÇÃO] → Dispara quando qualquer AnuncioML é salvo.
    #                  Recalcula o frete do anúncio automaticamente.
    calcular_frete_para_anuncio(instance)


# ================================================
# SIGNAL — PRODUTO
# ================================================

@receiver(post_save, sender='produtos.Produto')
def signal_produto_salvo(sender, instance, **kwargs):
    # * [EXPLICAÇÃO] → Dispara quando um Produto é salvo.
    #                  Recalcula o frete de todos os anúncios vinculados a esse produto,
    #                  pois peso ou dimensões podem ter mudado.
    from anuncios.models import AnuncioML

    anuncios = AnuncioML.objects.filter(produto=instance)
    for anuncio in anuncios:
        calcular_frete_para_anuncio(anuncio)


# ================================================
# SIGNAL — FRETE ML
# ================================================

@receiver(post_save, sender='precificacao_marketplaces.FreteML')
def signal_frete_ml_salvo(sender, instance, **kwargs):
    # * [EXPLICAÇÃO] → Dispara quando qualquer registro da tabela FreteML é salvo.
    #                  Recalcula o frete de TODOS os anúncios — a tabela mudou.
    from anuncios.models import AnuncioML

    for anuncio in AnuncioML.objects.select_related('produto').all():
        calcular_frete_para_anuncio(anuncio)
