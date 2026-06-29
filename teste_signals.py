import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Projeto_Sistema_Interno_MB_SV.settings')
django.setup()

from anuncios.models import AnuncioML, CardapioPrecos
from anuncios.signals import recalcular_combinacao
from marketplaces.models import TipoAnuncioML
from tags.models import TagPreco

print('\n=== TAGS CADASTRADAS ===')
for tag in TagPreco.objects.all():
    print(f'  {tag}')

print('\n=== TESTE SEM TAG ===')
anuncio = AnuncioML.objects.filter(tipo_anuncio='gold_special', produto__isnull=False).first()
tipo = TipoAnuncioML.objects.get(
    marketplace__sigla='ML',
    tipo_anuncio=anuncio.tipo_anuncio,
    tipo_logistico=anuncio.tipo_logistico,
    catalogo=anuncio.catalogo
)
recalcular_combinacao(anuncio.produto, tipo)
anuncio.refresh_from_db()
cardapio = CardapioPrecos.objects.get(produto=anuncio.produto, tipo_anuncio=tipo)
print(f'  preco_em_uso (cardapio): R${cardapio.preco_em_uso}')
print(f'  preco_classico_calculado: R${anuncio.preco_classico_calculado}')
print(f'  margem: {anuncio.margem_classico_calculado}%')

print('\n=== TESTE COM TAG DESCONTO 15% ===')
tag_desconto = TagPreco.objects.get(nome='Promoção 15%')
AnuncioML.objects.filter(pk=anuncio.pk).update(tag_preco=tag_desconto)
anuncio.tag_preco = tag_desconto
recalcular_combinacao(anuncio.produto, tipo)
anuncio.refresh_from_db()
print(f'  tag aplicada: {anuncio.tag_preco}')
print(f'  preco_em_uso (cardapio): R${cardapio.preco_em_uso}')
print(f'  preco_classico_calculado: R${anuncio.preco_classico_calculado}')
print(f'  margem com desconto: {anuncio.margem_classico_calculado}%')
esperado = round(float(cardapio.preco_em_uso) * 0.85, 2)
print(f'  esperado aprox: R${esperado:.2f}')

print('\n=== TESTE COM TAG ACRÉSCIMO 10% ===')
tag_acrescimo = TagPreco.objects.get(nome='Alta Demanda 10%')
AnuncioML.objects.filter(pk=anuncio.pk).update(tag_preco=tag_acrescimo)
anuncio.tag_preco = tag_acrescimo
recalcular_combinacao(anuncio.produto, tipo)
anuncio.refresh_from_db()
print(f'  tag aplicada: {anuncio.tag_preco}')
print(f'  preco_em_uso (cardapio): R${cardapio.preco_em_uso}')
print(f'  preco_classico_calculado: R${anuncio.preco_classico_calculado}')
print(f'  margem com acréscimo: {anuncio.margem_classico_calculado}%')

print('\n=== TESTE preco_travado ===')
AnuncioML.objects.filter(pk=anuncio.pk).update(preco_travado=True)
preco_antes = anuncio.preco_classico_calculado
recalcular_combinacao(anuncio.produto, tipo)
anuncio.refresh_from_db()
print(f'  preco_travado=True → preço alterado? {"SIM ✗" if anuncio.preco_classico_calculado != preco_antes else "NÃO ✓ (correto)"}')

print('\n=== LIMPEZA ===')
AnuncioML.objects.filter(pk=anuncio.pk).update(tag_preco=None, preco_travado=False)
recalcular_combinacao(anuncio.produto, tipo)
print('  tag removida, preco_travado=False, preço restaurado')