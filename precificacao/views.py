from django.shortcuts import render

from .models import Produto, Marketplace, TipoAnuncioML, FreteML

# Create your views here.


def lista_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'precificacao/lista_produtos.html', {'produtos': produtos})


def lista_marketplaces(request):
    marketplaces = Marketplace.objects.all()
    return render(request, 'precificacao/lista_marketplaces.html', {'marketplaces': marketplaces})


def lista_tipos_anuncio(request):
    tipos = TipoAnuncioML.objects.all()
    return render(request, 'precificacao/lista_tipos_anuncio.html', {'tipos': tipos})


def lista_frete_ml(request):
    fretes = FreteML.objects.all()
    return render(request, 'precificacao/lista_frete_ml.html', {'fretes': fretes})
