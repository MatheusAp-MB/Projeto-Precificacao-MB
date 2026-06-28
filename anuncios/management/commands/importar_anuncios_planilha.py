# * [RESUMO] → Comando Django para importar anúncios ML da planilha de precificação.
#              Cria 2 anúncios por produto: Clássico e Premium.
#              Uso: python manage.py importar_anuncios_planilha <caminho_do_arquivo>
#              Campos do JSON ficam em branco — serão preenchidos futuramente.

import openpyxl
from decimal import Decimal
from django.core.management.base import BaseCommand
from produtos.models import Produto
from anuncios.models import AnuncioML


class Command(BaseCommand):
    help = 'Importa anúncios ML da planilha de precificação'

    def add_arguments(self, parser):
        parser.add_argument(
            'arquivo',
            type=str,
            help='Caminho completo para o arquivo Excel de precificação'
        )

    def handle(self, *args, **options):
        arquivo = options['arquivo']
        self.stdout.write(f'Lendo arquivo: {arquivo}')

        try:
            wb = openpyxl.load_workbook(
                arquivo, read_only=True, data_only=True)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao abrir arquivo: {e}'))
            return

        ws = wb['Planilha1']
        criados = 0
        atualizados = 0
        ignorados = 0
        erros = 0
        contador = 1

        def seguro(val):
            # * [EXPLICAÇÃO] → Retorna None se o valor for erro de fórmula.
            if val is None:
                return None
            if isinstance(val, str) and val.strip().startswith('#'):
                return None
            return val

        def dec(val, max_val=99999):
            # * [EXPLICAÇÃO] → Descarta valores negativos ou absurdamente grandes —
            #                  indicam fórmula inválida na planilha.
            if val is None:
                return None
            try:
                resultado = Decimal(str(round(float(val), 2)))
                if resultado < 0 or resultado > max_val:
                    return None
                return resultado
            except:
                return None
            
        eans_processados = set()
        for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):

            if not any(v is not None for v in row[:5]):
                ignorados += 1
                continue

            try:
                ean = str(seguro(row[3])).strip() if seguro(row[3]) else None

                if not ean:
                    ignorados += 1
                    continue
                if ean in eans_processados:
                    ignorados += 1
                    continue
                eans_processados.add(ean)

                # * [EXPLICAÇÃO] → Busca o produto pelo EAN para obter o SKU.
                try:
                    produto = Produto.objects.get(ean=ean)
                except Produto.DoesNotExist:
                    self.stdout.write(
                        f'  [IGNORADO] Linha {i+2}: produto EAN {ean} não encontrado no banco')
                    ignorados += 1
                    continue

                preco_classico = dec(seguro(row[60]))
                frete_real = dec(seguro(row[72]))
                preco_real_premium = dec(seguro(row[73]))
                margem_real_classico = dec(seguro(row[71]))
                margem_real_premium = dec(seguro(row[78]))

                mlb_classico = f'TEMP{contador:04d}C'
                mlb_premium = f'TEMP{contador:04d}P'

                # * [EXPLICAÇÃO] → Cria ou atualiza o anúncio Clássico.
                _, criado = AnuncioML.objects.update_or_create(
                    mlb=mlb_classico,
                    defaults={
                        'produto':         produto,
                        'tipo_anuncio':    AnuncioML.TipoAnuncio.CLASSICO,
                        'tipo_logistico':  AnuncioML.TipoLogistico.FLEX,
                        'preco':           preco_classico,
                        'frete_real':      frete_real,
                        'margem_real_classico': margem_real_classico,
                        'margem_real_premium':  margem_real_premium,
                        'preco_real_premium':   preco_real_premium,
                    }
                )
                criados += 1 if criado else 0
                atualizados += 0 if criado else 1

                # * [EXPLICAÇÃO] → Cria ou atualiza o anúncio Premium.
                _, criado = AnuncioML.objects.update_or_create(
                    mlb=mlb_premium,
                    defaults={
                        'produto':         produto,
                        'tipo_anuncio':    AnuncioML.TipoAnuncio.PREMIUM,
                        'tipo_logistico':  AnuncioML.TipoLogistico.FLEX,
                        'frete_real':      frete_real,
                        'preco':                preco_real_premium,
                        'preco_real_premium':   preco_real_premium,
                        'margem_real_classico': margem_real_classico,
                        'margem_real_premium':  margem_real_premium,
                    }
                )
                criados += 1 if criado else 0
                atualizados += 0 if criado else 1

                contador += 1

            except Exception as e:
                erros += 1
                self.stdout.write(self.style.ERROR(
                    f'  [ERRO] Linha {i+2}: {e}'))

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(
            f'Importação concluída!\n'
            f'  Criados:     {criados}\n'
            f'  Atualizados: {atualizados}\n'
            f'  Ignorados:   {ignorados}\n'
            f'  Erros:       {erros}'
        ))
