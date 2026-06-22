from django.core.management.base import BaseCommand
from precificacao.models import Anuncio


class Command(BaseCommand):
    help = 'Zera preco_atual, preco_ideal e calculado_em de todos os anúncios ML'

    def handle(self, *args, **options):
        total = Anuncio.objects.update(
            preco_atual=None,
            preco_ideal=None,
            calculado_em=None,
        )
        self.stdout.write(self.style.SUCCESS(
            f'{total} anúncios resetados com sucesso.'
        ))