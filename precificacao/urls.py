from django.urls import path
from . import views

urlpatterns = [
    path('produtos/', views.lista_produtos, name='lista_produtos'),
    path('marketplaces/', views.lista_marketplaces, name='lista_marketplaces'),
    path('tipos-anuncio/', views.lista_tipos_anuncio, name='lista_tipos_anuncio'),
    path('frete-ml/', views.lista_frete_ml, name='lista_frete_ml'),
    path('anuncios/', views.lista_anuncios, name='lista_anuncios'),
    path('', views.home, name='home'),
    path('frete-ml/calcular/', views.calcular_frete_ml, name='calcular_frete_ml'),
    path('precificacao/ml/', views.precificacao_ml, name='precificacao_ml'),
    path('precificacao/ml/produto/<int:produto_id>/painel/',
         views.painel_produto_ml, name='painel_produto_ml'),
    path('precificacao/ml/calcular/',
         views.calcular_produto_ml, name='calcular_produto_ml'),
    path('precificacao/ml/salvar/', views.salvar_precificacao_ml,
         name='salvar_precificacao_ml'),
    path('precificacao/ml/recalcular-tudo/',
         views.recalcular_tudo_ml, name='recalcular_tudo_ml'),
]
