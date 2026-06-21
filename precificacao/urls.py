from django.urls import path
from . import views

urlpatterns = [
    path('produtos/', views.lista_produtos, name='lista_produtos'),
    path('marketplaces/', views.lista_marketplaces, name='lista_marketplaces'),
    path('tipos-anuncio/', views.lista_tipos_anuncio, name='lista_tipos_anuncio'),
    path('frete-ml/', views.lista_frete_ml, name='lista_frete_ml'),
    path('anuncios/', views.lista_anuncios, name='lista_anuncios'),
    path('', views.home, name='home'),
]