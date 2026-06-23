
# * [RESUMO] → Comando de gestão customizado do Django.
# *            Sobe o servidor Django e o MkDocs simultaneamente
# *            com um único comando: python manage.py start

import subprocess
import sys
import os

from django.core.management.base import BaseCommand
from django.core.management import call_command


# * [EXPLICAÇÃO] → BaseCommand é a classe base para todos os comandos
# *                de gestão do Django. Ao herdar dela, o Django reconhece
# *                essa classe como um comando válido do manage.py
class Command(BaseCommand):

    # * [EXPLICAÇÃO] → O atributo help é exibido quando o usuário roda
    # *                 python manage.py help start
    help = 'Sobe o servidor Django e o MkDocs simultaneamente'

    # * [EXPLICAÇÃO] → O método handle é executado automaticamente
    # *                quando o comando é chamado no terminal.
    # *                Tudo que o comando faz fica aqui.
    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS('Iniciando o sistema...'))

        # * [EXPLICAÇÃO] → Sobe o MkDocs em background e guarda a referência
        # *                do processo para poder encerrá-lo depois com o CTRL+C.
        # * [IMPORTANTE] → O MkDocs roda na porta 8001 — definida no mkdocs.yml.
        # *                Isso evita conflito com o Django que usa a porta 8000.
        self.stdout.write('Subindo MkDocs em http://127.0.0.1:8001 ...')
        mkdocs_processo = subprocess.Popen(
            ['mkdocs', 'serve'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        self.stdout.write('Subindo Django em http://127.0.0.1:8000 ...')
        self.stdout.write(self.style.SUCCESS('Sistema iniciado! Pressione CTRL+C para encerrar.'))

        try:
            # * [EXPLICAÇÃO] → O call_command bloqueia aqui até o Django ser encerrado.
            # *                Quando o usuário pressiona CTRL+C, o Django lança
            # *                KeyboardInterrupt, que capturamos para encerrar o MkDocs.
            call_command('runserver')

        except KeyboardInterrupt:
            # * [EXPLICAÇÃO] → Ao capturar o CTRL+C, encerra o processo do MkDocs
            # *                antes de sair, garantindo que nenhum processo fique
            # *                rodando em background sem necessidade.
            self.stdout.write(self.style.WARNING('\nEncerrando MkDocs...'))
            mkdocs_processo.terminate()
            mkdocs_processo.wait()
            self.stdout.write(self.style.SUCCESS('Sistema encerrado.'))
