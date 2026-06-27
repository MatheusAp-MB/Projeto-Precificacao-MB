# * [RESUMO] → Context processors globais do sistema.
#              Injetam dados automaticamente em todos os templates.

# * [EXPLICAÇÃO] → Lista global de marketplaces do sistema.
#                  Define nome, logo e id de cada marketplace.
#                  O id é usado pelas views para mapear URLs específicas por módulo.
MARKETPLACES = [
    {'id': 'mercado_livre', 'nome': 'Mercado Livre', 'logo': 'pagina_precificacao/img/logo_mercado_livre.png'},
    {'id': 'shopee',        'nome': 'Shopee',        'logo': 'pagina_precificacao/img/logo_shopee.png'},
    {'id': 'magalu',        'nome': 'Magalu',        'logo': 'pagina_precificacao/img/logo_magalu.png'},
    {'id': 'amazon',        'nome': 'Amazon',        'logo': 'pagina_precificacao/img/logo_amazon.png'},
    {'id': 'tiktok_shop',   'nome': 'Tiktok Shop',   'logo': 'pagina_precificacao/img/logo_tiktok_shop.png'},
    {'id': 'mais_correios', 'nome': 'Mais Correios', 'logo': 'pagina_precificacao/img/logo_mais_correios.png'},
    {'id': 'raia',          'nome': 'Raia',          'logo': 'pagina_precificacao/img/logo_raia.png'},
    {'id': 'tudo_de_agro',  'nome': 'Tudo de Agro',  'logo': 'pagina_precificacao/img/logo_tudo_de_agro.png'},
]


def marketplaces(request):
    # * [EXPLICAÇÃO] → Injeta a lista de marketplaces em todos os templates.
    #                  Disponível como {{ marketplaces }} em qualquer template.
    return {'marketplaces': MARKETPLACES}