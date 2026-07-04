# * [RESUMO] → Comando mestre de importação.
#              Orquestra todos os comandos de importação individuais, na ordem
#              correta e documentada — elimina a dependência de "lembrar a ordem".
#              Grava um arquivo de log por execução em logs/importacoes/,
#              com timestamp, duração e resultado de cada etapa.
#
#              Para na primeira falha — a ordem é sequencial por dependência real
#              (ex: importar_produtos_erp depende de produtos já existirem),
#              então continuar após uma falha só acumularia erros em cascata.
#
#              Uso: python manage.py importar_tudo

import time
import traceback
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand
from django.core.management import call_command

# ================================================
# SEQUÊNCIA DE IMPORTAÇÃO — ordem fixa e documentada
# ================================================
# * [EXPLICAÇÃO] → Cada etapa é (nome_do_comando, args). Args vazio quando o
#                  comando já tem os caminhos fixos no próprio arquivo.
SEQUENCIA = [
    ('iniciar_banco', []),
    ('importar_produtos_ml', []),
    ('importar_produtos_erp', ['Planilha_ERP.xlsx']),
    ('importar_produtos', ['Planilha_Importar_Pos_Macro.xlsm']),
    ('importar_frete_ml', []),
]

PASTA_LOGS = Path('logs/importacoes')


class Command(BaseCommand):
    help = 'Roda todos os comandos de importação na ordem correta, com log em arquivo'

    def handle(self, *args, **options):
        PASTA_LOGS.mkdir(parents=True, exist_ok=True)
        agora = datetime.now()
        caminho_log = PASTA_LOGS / f'{agora.strftime("%Y-%m-%d_%H-%M-%S")}.log'

        linhas_log = []

        def log(linha):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            texto = f'[{timestamp}] {linha}'
            linhas_log.append(texto)
            self.stdout.write(texto)
            # Grava incrementalmente — se travar no meio, o log até aqui não se perde
            with open(caminho_log, 'w', encoding='utf-8') as f:
                f.write('\n'.join(linhas_log) + '\n')

        inicio_total = time.time()
        log('INICIANDO importar_tudo')
        log('')

        for nome_comando, args_comando in SEQUENCIA:
            log(f'→ {nome_comando}')
            inicio_etapa = time.time()

            try:
                call_command(nome_comando, *args_comando)
                duracao = time.time() - inicio_etapa
                log(f'  ✓ concluído em {duracao:.1f}s')
                log('')

            except Exception as e:
                duracao = time.time() - inicio_etapa
                log(f'  ✗ FALHOU em {duracao:.1f}s')
                log(f'  ERRO: {e}')
                log('')
                log(traceback.format_exc())
                log('')
                log(f'PARADO — {nome_comando} falhou, etapas seguintes não foram executadas')

                duracao_total = time.time() - inicio_total
                log(f'\nFINALIZADO COM ERRO em {duracao_total:.1f}s')

                self.stdout.write(self.style.ERROR(
                    f'\nImportação interrompida em "{nome_comando}". Log completo em: {caminho_log}'
                ))
                return

        duracao_total = time.time() - inicio_total
        log(f'FINALIZADO em {duracao_total:.1f}s — 0 erros')

        self.stdout.write(self.style.SUCCESS(
            f'\nImportação completa. Log salvo em: {caminho_log}'
        ))