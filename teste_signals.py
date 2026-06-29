import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Projeto_Sistema_Interno_MB_SV.settings')
django.setup()

from anuncios.models import AnuncioML, CardapioPrecos
from anuncios.signals import recalcular_combinacao
from marketplaces.models import TipoAnuncioML

print('\n=== TESTE CLÁSSICO ===')
classico = AnuncioML.objects.filter(tipo_anuncio='gold_special', produto__isnull=False).first()
tipo_classico = TipoAnuncioML.objects.get(
    marketplace__sigla='ML',
    tipo_anuncio=classico.tipo_anuncio,
    tipo_logistico=classico.tipo_logistico,
    catalogo=classico.catalogo
)
recalcular_combinacao(classico.produto, tipo_classico)
classico.refresh_from_db()
cardapio = CardapioPrecos.objects.get(produto=classico.produto, tipo_anuncio=tipo_classico)
print(f'Produto: {classico.produto.sku}')
print(f'Tipo: {tipo_classico.nome}')
print(f'preco_margem_minima:  R${cardapio.preco_margem_minima}')
print(f'preco_margem_padrao:  R${cardapio.preco_margem_padrao}')
print(f'preco_margem_maxima:  R${cardapio.preco_margem_maxima}')
print(f'preco_em_uso:         R${cardapio.preco_em_uso}')
print(f'preco_atacado_2:      R${cardapio.preco_atacado_2}')
print(f'preco_atacado_3:      R${cardapio.preco_atacado_3}')
print(f'preco_classico_calculado: R${classico.preco_classico_calculado}')
print(f'margem_classico_calculado: {classico.margem_classico_calculado}%')

print('\n=== TESTE PREMIUM ===')
premium = AnuncioML.objects.filter(tipo_anuncio='gold_pro', produto__isnull=False).first()
tipo_premium = TipoAnuncioML.objects.get(
    marketplace__sigla='ML',
    tipo_anuncio=premium.tipo_anuncio,
    tipo_logistico=premium.tipo_logistico,
    catalogo=premium.catalogo
)
recalcular_combinacao(premium.produto, tipo_premium)
premium.refresh_from_db()
cardapio_p = CardapioPrecos.objects.get(produto=premium.produto, tipo_anuncio=tipo_premium)
print(f'Produto: {premium.produto.sku}')
print(f'Tipo: {tipo_premium.nome}')
print(f'preco_margem_minima:  R${cardapio_p.preco_margem_minima}')
print(f'preco_margem_padrao:  R${cardapio_p.preco_margem_padrao}')
print(f'preco_margem_maxima:  R${cardapio_p.preco_margem_maxima}')
print(f'preco_em_uso:         R${cardapio_p.preco_em_uso}')
print(f'preco_atacado_2:      R${cardapio_p.preco_atacado_2}')
print(f'preco_atacado_3:      R${cardapio_p.preco_atacado_3}')
print(f'preco_premium_calculado: R${premium.preco_premium_calculado}')
print(f'margem_premium_calculado: {premium.margem_premium_calculado}%')