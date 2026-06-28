# * [RESUMO] → Comando Django para importar produtos de uma planilha Excel.
#              Uso: python manage.py importar_produtos <caminho_do_arquivo>
#              Cada linha da planilha vira um registro na tabela Produto.

import openpyxl
from decimal import Decimal
from django.core.management.base import BaseCommand
from produtos.models import Produto


class Command(BaseCommand):
    help = 'Importa produtos de uma planilha Excel'

    def add_arguments(self, parser):
        # * [EXPLICAÇÃO] → O argumento 'arquivo' é o caminho para o .xlsx.
        #                  Exemplo: python manage.py importar_produtos C:/auxi.xlsx
        parser.add_argument(
            'arquivo',
            type=str,
            help='Caminho completo para o arquivo Excel'
        )

    def handle(self, *args, **options):
        arquivo = options['arquivo']
        self.stdout.write(f'Lendo arquivo: {arquivo}')

        try:
            wb = openpyxl.load_workbook(arquivo, read_only=True, data_only=True)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao abrir arquivo: {e}'))
            return

        ws       = wb['Planilha1']
        criados  = 0
        atualizados = 0
        ignorados = 0
        erros    = 0

        # * [EXPLICAÇÃO] → Converte decimal para percentual (0.04 → 4.00).
        #                  Campos fiscais da planilha estão em formato decimal.
        def pct(val):
            if val is None:
                return Decimal('0')
            return Decimal(str(round(float(val) * 100, 2)))

        # * [EXPLICAÇÃO] → Converte valor para Decimal com 2 casas.
        def dec(val, default='0'):
            if val is None:
                return Decimal(default)
            return Decimal(str(round(float(val), 2)))

        # * [EXPLICAÇÃO] → Converte valor para Decimal com 3 casas (para peso).
        def dec3(val, default='0'):
            if val is None:
                return Decimal(default)
            return Decimal(str(round(float(val), 3)))

        # * [EXPLICAÇÃO] → Retorna None se o valor for um erro de planilha (#N/A, #REF!, etc).
        #                  Evita que erros de fórmula quebrem a importação.
        def seguro(val):
            if val is None:
                return None
            if isinstance(val, str) and val.strip().startswith('#'):
                return None
            return val

        for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):

            # * [EXPLICAÇÃO] → Ignora linhas completamente vazias.
            if not any(v is not None for v in row[:10]):
                ignorados += 1
                continue

            try:
                ean    = str(row[3]).strip() if row[3] else None
                titulo = str(row[2]).strip() if row[2] else None

                if not ean or not titulo:
                    self.stdout.write(f'  [IGNORADO] Linha {i + 2}: ean={ean}, titulo={titulo}')
                    ignorados += 1
                    continue

                dados = {
                    'titulo':           titulo,
                    'curva':            str(seguro(row[0])).strip() if seguro(row[0]) else None,
                    'cod_fabricante':   str(seguro(row[1])).strip() if seguro(row[1]) else None,
                    'ncm':              str(seguro(row[4])).strip() if seguro(row[4]) else None,
                    'custo':            dec(seguro(row[9])),
                    'custo_com_boni':   dec(seguro(row[10])) if seguro(row[10]) else None,
                    'frete_cif_fob':    pct(seguro(row[11])) if seguro(row[11]) else Decimal('0'),
                    'mva':              dec(seguro(row[7])) if seguro(row[7]) else None,
                    'st_valor':         dec(seguro(row[8])) if seguro(row[8]) else None,
                    'icms_entrada':     pct(seguro(row[12])),
                    'ipi':              pct(seguro(row[13])),
                    'pis_cofins':       pct(seguro(row[14])),
                    'icms_saida_sp':    pct(seguro(row[15])),
                    'icms_saida_media': pct(seguro(row[16])),
                    'peso':             dec3(seguro(row[19])),
                    'altura':           dec(seguro(row[21])),
                    'profundidade':     dec(seguro(row[22])),
                    'largura':          dec(seguro(row[23])),
                    'coleta_planilha':      dec(seguro(row[58])) if seguro(row[58]) else None,
                    'custo_final_planilha': dec(seguro(row[17])) if seguro(row[17]) else None,
                    'custo_frete_ml_real': dec(seguro(row[57])) if seguro(row[57]) else None,

                    # * [EXPLICAÇÃO] → armazenagem_planilha: valor mensal de armazenagem
                    #                  importado diretamente da coluna BH da planilha.
                    #                  Usado no cálculo _planilha para replicar exatamente
                    #                  o comportamento da planilha, independente da faixa dinâmica.
                    #                  Ver documentação em produtos/models.py (campo armazenagem_planilha).
                    'armazenagem_planilha': dec(seguro(row[59])) if seguro(row[59]) else None,
                }

                _, criado = Produto.objects.update_or_create(
                    ean=ean,
                    defaults=dados
                )

                if criado:
                    criados += 1
                else:
                    atualizados += 1

            except Exception as e:
                erros += 1
                self.stdout.write(self.style.ERROR(f'  [ERRO] Linha {i + 2}: {e}'))

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(
            f'Importação concluída!\n'
            f'  Criados:     {criados}\n'
            f'  Atualizados: {atualizados}\n'
            f'  Ignorados:   {ignorados}\n'
            f'  Erros:       {erros}'
        ))
