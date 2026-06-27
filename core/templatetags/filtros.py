# * [RESUMO] → Filtros customizados de template para o sistema.

from django import template

register = template.Library()


@register.filter
def get_item(dicionario, chave):
    # * [EXPLICAÇÃO] → Permite acessar um dicionário por chave variável no template.
    #                  Uso: {{ dicionario|get_item:variavel }}
    return dicionario.get(chave)