# * [RESUMO] → Comando Django para importar a tabela de frete do ML de uma planilha Excel.
#              Uso: python manage.py importar_frete_ml <caminho_do_arquivo>
#              Cada célula da matriz (peso × preço) vira uma linha no banco.

import openpyxl
from decimal import Decimal
from django.core.management.base import BaseCommand
from precificacao_marketplaces.models import FreteML


class Command(BaseCommand):
    help = 'Importa a tabela de frete do ML de uma planilha Excel'

    def add_arguments(self, parser):
        # * [EXPLICAÇÃO] → O argumento 'arquivo' é o caminho para o .xlsx.
        #                  Exemplo: python manage.py importar_frete_ml C:/tabela.xlsx
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

        ws       = wb.active
        rows     = list(ws.iter_rows(values_only=True))
        header   = rows[0]
        criados  = 0
        atualizados = 0
        erros    = 0

        # * [EXPLICAÇÃO] → Lê as faixas de preço do cabeçalho (colunas 1 a 8).
        #                  Exemplo: "R$ 0 - R$ 18,99" → (Decimal('0'), Decimal('18.99'))
        #                           "R$ 200 -"        → (Decimal('200'), None)
        faixas_preco = []
        for col_idx in range(1, 9):
            faixas_preco.append(self.parse_faixa_preco(str(header[col_idx])))

        # * [EXPLICAÇÃO] → Percorre cada linha da planilha (linha = faixa de peso).
        #                  Para cada linha, cria uma entrada no banco por faixa de preço.
        for row in rows[1:]:
            if not any(v is not None for v in row[:9]):
                continue

            try:
                # * [EXPLICAÇÃO] → Colunas 9 e 10 já têm os valores numéricos de peso.
                #                  A última faixa usa 1000000000 como sentinela — convertemos para None.
                peso_min     = Decimal(str(row[9]))
                peso_max_raw = row[10]

                if peso_max_raw is not None and float(peso_max_raw) >= 999999999:
                    peso_max = None
                elif peso_max_raw is not None:
                    peso_max = Decimal(str(peso_max_raw))
                else:
                    peso_max = None

                for col_idx, (preco_min, preco_max) in enumerate(faixas_preco):
                    valor = row[col_idx + 1]
                    if valor is None:
                        continue

                    valor = Decimal(str(round(float(valor), 2)))

                    # * [EXPLICAÇÃO] → update_or_create evita duplicatas.
                    #                  Se a combinação peso_min + preco_min já existir,
                    #                  atualiza o valor. Senão, cria uma nova linha.
                    _, criado = FreteML.objects.update_or_create(
                        peso_min=peso_min,
                        preco_min=preco_min,
                        defaults={
                            'peso_max': peso_max,
                            'preco_max': preco_max,
                            'valor': valor,
                        }
                    )

                    if criado:
                        criados += 1
                    else:
                        atualizados += 1

            except Exception as e:
                erros += 1
                self.stdout.write(self.style.ERROR(f'  [ERRO] Linha {row[0]}: {e}'))

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(
            f'Importação concluída!\n'
            f'  Criados:     {criados}\n'
            f'  Atualizados: {atualizados}\n'
            f'  Erros:       {erros}'
        ))
  
    def parse_faixa_preco(self, texto):
            import re
            # * [EXPLICAÇÃO] → Extrai todos os números do texto do cabeçalho.
            #                  Funciona independente do formato — com ou sem "R$", com
            #                  ponto de milhar, vírgula decimal ou traço solto no final.
            #                  Exemplo: "R$ 1.542,98 - R$ 2.000,00" → ['1.542,98', '2.000,00']
            #                           "R$ 200 -"                  → ['200']
            numeros = re.findall(r'[\d]+(?:[.,]\d+)?', texto)

            def to_decimal(s):
                return Decimal(s.replace('.', '').replace(',', '.'))

            preco_min = to_decimal(numeros[0]) if numeros else Decimal('0')
            preco_max = to_decimal(numeros[1]) if len(numeros) > 1 else None

            return preco_min, preco_max