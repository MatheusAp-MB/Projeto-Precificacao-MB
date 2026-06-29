# * [RESUMO] → Views do app de marketplaces.

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import Marketplace, TipoAnuncioML, ConfiguracaoLogisticaML


# ================================================
# MARKETPLACES — GRID
# ================================================

def view_marketplaces(request):
    # * [EXPLICAÇÃO] → Tela inicial do módulo de marketplaces — grid de seleção.
    return render(request, 'pagina_marketplaces/estrutura_marketplaces.html', {
        'urls_marketplaces': {
            'mercado_livre': reverse('configuracoes_ml'),
        }
    })


# ================================================
# CONFIGURAÇÕES — MERCADO LIVRE
# ================================================

def view_configuracoes_ml(request):
    # * [EXPLICAÇÃO] → Tela de configurações do Mercado Livre.
    #                  Exibe parâmetros gerais, logística, faixas de armazenagem e os 8 tipos de anúncio.
    from .models import FaixaArmazenagem
    marketplace = get_object_or_404(Marketplace, sigla='ML')
    tipos       = TipoAnuncioML.objects.filter(marketplace=marketplace)
    logistica   = ConfiguracaoLogisticaML.objects.filter(marketplace=marketplace).first()
    faixas      = FaixaArmazenagem.objects.filter(marketplace=marketplace, ativo=True).order_by('ordem')

    return render(request, 'pagina_configuracoes_ml/estrutura_configuracoes_ml.html', {
        'marketplace': marketplace,
        'tipos':       tipos,
        'logistica':   logistica,
        'faixas':      faixas,
    })
