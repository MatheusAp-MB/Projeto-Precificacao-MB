# * [RESUMO] → Views do app de produtos.

from django.shortcuts import render
from .models import Produto


# ================================================
# LISTAGEM DE PRODUTOS
# ================================================

def view_produtos(request):
    # * [EXPLICAÇÃO] → Busca todos os produtos ordenados por título
    #                  e passa para o template renderizar via DataTables.
    produtos = Produto.objects.all()
    return render(request, 'pagina_produtos/estrutura_produtos.html', {'produtos': produtos})