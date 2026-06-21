import openpyxl
from django.core.management.base import BaseCommand
from precificacao.models import Produto


class Command(BaseCommand):
    help = 'Importa produtos de uma planilha Excel'

    def add_arguments(self, parser):
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

        ws = wb.active
        criados = 0
        atualizados = 0
        ignorados = 0
        erros = 0

        for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):

            # Ignora linhas completamente vazias
            if not any(v is not None for v in row[:10]):
                continue

            try:
                # Extrai colunas (índice 0 = coluna A)
                curva           = row[0]   # A
                cod_forn        = row[1]   # B - Cód Forn (usado como SKU)
                titulo          = row[2]   # C - Descrição
                ean             = row[3]   # D - Cód Barras
                ncm             = row[4]   # E - NCM
                mva             = row[7]   # H - MVA
                st_valor        = row[8]   # I - ST Valor
                custo           = row[9]   # J - Custo
                custo_com_boni  = row[10]  # K - Custo c/ Boni
                frete_cif_fob   = row[11]  # L - Frete CIF/FOB
                icms_entrada    = row[12]  # M - ICMS Entrada
                ipi             = row[13]  # N - IPI
                pis_cofins      = row[14]  # O - PIS/COFINS
                icms_saida_sp   = row[15]  # P - ICMS Saída SP
                icms_saida_media= row[16]  # Q - ICMS Saída Média
                peso            = row[19]  # T - Peso
                altura          = row[21]  # V - Alt.cm
                profundidade    = row[22]  # W - Comp.cm
                largura         = row[23]  # X - Larg.cm

                # Valida campos obrigatórios
                if not titulo or not custo or not cod_forn:
                    ignorados += 1
                    continue

                # Converte decimal para percentual (0.12 → 12.00)
                def pct(val):
                    if val is None:
                        return 0
                    return round(float(val) * 100, 2)

                # Converte para decimal com 2 casas
                def dec(val, default=0):
                    if val is None:
                        return default
                    return round(float(val), 2)

                dados = {
                    'titulo':           str(titulo).strip(),
                    'ean':              str(ean).strip() if ean else None,
                    'cod_fabricante':   str(cod_forn).strip() if cod_forn else None,
                    'curva':            str(curva).strip() if curva else None,
                    'custo':            dec(custo),
                    'custo_com_boni':   dec(custo_com_boni) if custo_com_boni else None,
                    'ncm':              str(ncm).strip() if ncm else None,
                    'ipi':              pct(ipi),
                    'icms_entrada':     pct(icms_entrada),
                    'icms_saida_sp':    pct(icms_saida_sp),
                    'icms_saida_media': pct(icms_saida_media),
                    'pis_cofins':       pct(pis_cofins),
                    'mva':              dec(mva) if mva else None,
                    'st_valor':         dec(st_valor) if st_valor else None,
                    'frete_cif_fob':    pct(frete_cif_fob) if frete_cif_fob else None,
                    'peso':             dec(peso) if peso else 0,
                    'altura':           dec(altura) if altura else 0,
                    'largura':          dec(largura) if largura else 0,
                    'profundidade':     dec(profundidade) if profundidade else 0,
                }

                sku = str(cod_forn).strip()

                produto, criado = Produto.objects.update_or_create(
                    sku=sku,
                    defaults=dados
                )

                if criado:
                    criados += 1
                    self.stdout.write(f'  [CRIADO]     {sku} — {titulo[:50]}')
                else:
                    atualizados += 1
                    self.stdout.write(f'  [ATUALIZADO] {sku} — {titulo[:50]}')

            except Exception as e:
                erros += 1
                self.stdout.write(self.style.ERROR(f'  [ERRO] Linha {i + 2}: {e}'))

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(
            f'Importação concluída!\n'
            f'  Criados:    {criados}\n'
            f'  Atualizados:{atualizados}\n'
            f'  Ignorados:  {ignorados}\n'
            f'  Erros:      {erros}'
        ))