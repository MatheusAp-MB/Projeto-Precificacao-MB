from django.shortcuts import render, get_object_or_404
from .models import Produto


def view_produtos(request):
    # * [EXPLICAÇÃO] → Busca todos os produtos ordenados por título
    #                  e passa para o template renderizar via DataTables.
    produtos = Produto.objects.all()
    return render(request, 'pagina_produtos/estrutura_produtos.html', {'produtos': produtos})


# ================================================
# PAINEL DO PRODUTO — HTMX
# ================================================

def view_painel_produto(request, produto_id):
    # * [EXPLICAÇÃO] → Endpoint HTMX — retorna o conteúdo do modal
    #                  com os dados completos do produto selecionado.
    produto = get_object_or_404(Produto, pk=produto_id)
    return render(request, 'pagina_produtos/parciais/estrutura_parcial_painel_produto.html', {
        'produto': produto,
    })