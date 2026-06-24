# * [RESUMO] → Views do app de precificação por marketplace.
#              Cada view corresponde a uma tela do módulo.

from django.shortcuts import render


# ================================================
# PRECIFICAÇÃO — GRID PRINCIPAL
# ================================================

def view_precificacao(request):
    # * [EXPLICAÇÃO] → Tela inicial do módulo de precificação.
    #                  Exibe um grid com os marketplaces disponíveis.
    return render(request, 'pagina_precificacao/estrutura_precificacao.html')


# ================================================
# MERCADO LIVRE — GRID DE OPÇÕES
# ================================================

def view_mercado_livre(request):
    # * [EXPLICAÇÃO] → Tela do Mercado Livre — exibe um grid
    #                  com as opções disponíveis para o marketplace.
    return render(request, 'pagina_mercado_livre/estrutura_mercado_livre.html')


# ================================================
# TABELA DE FRETE ML
# ================================================

def view_tabela_frete_ml(request):
    # * [EXPLICAÇÃO] → Tela da tabela de frete do Mercado Livre.
    #                  Por enquanto exibe os dados estáticos da old_dev.
    #                  Futuramente virá do banco de dados.
    # # [STATUS: DESENVOLVIMENTO] → Dados ainda estáticos — banco não configurado
    return render(request, 'pagina_tabela_frete_ml/estrutura_tabela_frete_ml.html')