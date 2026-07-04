# * [RESUMO] → Comando Django para importar produtos do ERP via planilha Excel.
#              Uso: python manage.py importar_produtos_erp <caminho_do_arquivo>
#              Preenche dados de identificação, estoque e dimensões.
#              Dimensões: usa embalagem quando disponível, cai para produto como fallback.

import openpyxl
from decimal import Decimal
from datetime import datetime
from django.core.management.base import BaseCommand
from produtos.models import Produto
from django.utils import timezone

class Command(BaseCommand):
    help = 'Importa produtos do ERP via planilha Excel'

    def add_arguments(self, parser):
        # * [EXPLICAÇÃO] → Caminho completo para o arquivo .xlsx do ERP.
        #                  Exemplo: python manage.py importar_produtos_erp C:/erp.xlsx
        parser.add_argument(
            'arquivo',
            type=str,
            help='Caminho completo para o arquivo Excel do ERP'
        )

    def handle(self, *args, **options):
        arquivo = options['arquivo']
        self.stdout.write(f'Lendo arquivo: {arquivo}')

        try:
            wb = openpyxl.load_workbook(arquivo, read_only=True, data_only=True)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao abrir arquivo: {e}'))
            return

        ws          = wb['Planilha1']
        criados     = 0
        atualizados = 0
        ignorados   = 0
        erros       = 0

        def seguro(val):
            # * [EXPLICAÇÃO] → Retorna None se o valor for erro de fórmula ou vazio.
            if val is None:
                return None
            if isinstance(val, str) and val.strip().startswith('#'):
                return None
            return val

        def dec(val, casas=2):
            # * [EXPLICAÇÃO] → Converte valor para Decimal com n casas decimais.
            if val is None:
                return None
            try:
                return Decimal(str(round(float(val), casas)))
            except:
                return None

        def metros_para_cm(val):
            # * [EXPLICAÇÃO] → Converte metros para centímetros (dimensões do produto no ERP).
            result = dec(val, 2)
            if result is None:
                return None
            return result * 100

        def extrair_data(val):
            if val is None:
                return None
            if isinstance(val, datetime):
                return timezone.make_aware(val)
            try:
                texto = str(val).strip()
                data  = texto.split('(')[0].strip()
                dt    = datetime.strptime(data, '%d-%m-%Y')
                return timezone.make_aware(dt)
            except Exception:
                return None

        def dimensoes(emb, prod_metros):
            # * [EXPLICAÇÃO] → Usa dimensão da embalagem quando disponível e não zerada.
            #                  Cai para dimensão do produto (convertida de metros para cm).
            emb_val = dec(seguro(emb), 2)
            if emb_val and emb_val > 0:
                return emb_val
            return metros_para_cm(seguro(prod_metros))

        def peso(emb, prod):
            # * [EXPLICAÇÃO] → Usa peso da embalagem quando disponível e não zerado.
            #                  Cai para peso bruto do produto.
            emb_val = dec(seguro(emb), 3)
            if emb_val and emb_val > 0:
                return emb_val
            return dec(seguro(prod), 3)

        for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):

            if not any(v is not None for v in row[:5]):
                ignorados += 1
                continue

            try:
                ean = str(seguro(row[2])).strip() if seguro(row[2]) else None

                if not ean:
                    self.stdout.write(f'  [IGNORADO] Linha {i + 2}: ean={ean}, titulo={str(seguro(row[3]))[:50]}')
                    ignorados += 1
                    continue

                dados = {
                    'sku':               str(seguro(row[0])).strip() if seguro(row[0]) else None,
                    'cod_fabricante':    str(seguro(row[1])).strip() if seguro(row[1]) else None,
                    'titulo':            str(seguro(row[3])).strip() if seguro(row[3]) else None,
                    'estoque':           int(seguro(row[4])) if seguro(row[4]) is not None else 0,
                    'marca':             str(seguro(row[5])).strip() if seguro(row[5]) else None,
                    'categoria':         str(seguro(row[7])).strip() if seguro(row[7]) else None,
                    'altura':            dimensoes(row[12], row[9]),
                    'largura':           dimensoes(row[13], row[11]),
                    'profundidade':      dimensoes(row[14], row[10]),
                    'peso':              peso(row[15], row[8]),
                    'ultima_compra':     extrair_data(seguro(row[16])),
                    'cadastrado_erp_em': timezone.make_aware(seguro(row[17])) if seguro(row[17]) and isinstance(seguro(row[17]), datetime) else None,
                }

                # * [EXPLICAÇÃO] → Remove campos None para não sobrescrever dados
                #                  que já existem no banco com valores vazios.
                dados_limpos = {k: v for k, v in dados.items() if v is not None}

                _, criado = Produto.objects.update_or_create(
                    ean=ean,
                    defaults=dados_limpos,
                    create_defaults={**dados_limpos, 'custo': Decimal('0')}
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
            f'Importação ERP concluída!\n'
            f'  Criados:     {criados}\n'
            f'  Atualizados: {atualizados}\n'
            f'  Ignorados:   {ignorados}\n'
            f'  Erros:       {erros}'
        ))