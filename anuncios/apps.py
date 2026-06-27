# * [RESUMO] → Configuração do app de anúncios.

from django.apps import AppConfig


class AnunciosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'anuncios'

    def ready(self):
        # * [EXPLICAÇÃO] → Importa os signals ao iniciar o app.
        #                  Sem isso, os signals não são registrados e não disparam.
        import anuncios.signals