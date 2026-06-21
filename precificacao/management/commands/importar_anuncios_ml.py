import random
import openpyxl
from django.core.management.base import BaseCommand
from precificacao.models import Produto, TipoAnuncioML, Anuncio


class Command(BaseCommand):
    help = 'Importa anúncios ML a partir da planilha Excel'

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
            wb = openpyxl.load_workbook(
                arquivo, read_only=True, data_only=True)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao abrir arquivo: {e}'))
            return

        ws = wb.active

        # Busca os tipos de anúncio
        try:
            classico = TipoAnuncioML.objects.get(nome='Clássico')
            premium = TipoAnuncioML.objects.get(nome='Premium')
        except TipoAnuncioML.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(
                f'Tipo de anúncio não encontrado: {e}'))
            self.stdout.write(
                'Certifique-se de ter cadastrado Clássico e Premium no admin.')
            return

        criados = 0
        atualizados = 0
        ignorados = 0
        erros = 0

        def gerar_mlb():
            return f'MLB{random.randint(1000000000, 9999999999)}'

        for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):

            if not any(v is not None for v in row[:5]):
                continue

            try:
                ean = str(row[3]).strip() if row[3] else None
                sku = f"F{ean}.001" if ean else str(row[3]).strip()
                titulo = str(row[2]).strip() if row[2] else None
                preco_classico = row[60]   # coluna BI
                preco_premium = row[73]   # coluna BV

                if not sku or not titulo:
                    ignorados += 1
                    continue

                # Busca o produto pelo SKU
                try:
                    produto = Produto.objects.get(sku=sku)
                except Produto.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f'  [IGNORADO] SKU {sku} não encontrado no banco'))
                    ignorados += 1
                    continue

                # Define os 4 anúncios a criar
                anuncios = [
                    {
                        'tipo_anuncio': classico,
                        'tipo_envio':   'FLEX',
                        'preco':        preco_classico,
                        'sufixo':       'FLEX-C',
                    },
                    {
                        'tipo_anuncio': classico,
                        'tipo_envio':   'FULL',
                        'preco':        preco_classico,
                        'sufixo':       'FULL-C',
                    },
                    {
                        'tipo_anuncio': premium,
                        'tipo_envio':   'FLEX',
                        'preco':        preco_premium,
                        'sufixo':       'FLEX-P',
                    },
                    {
                        'tipo_anuncio': premium,
                        'tipo_envio':   'FULL',
                        'preco':        preco_premium,
                        'sufixo':       'FULL-P',
                    },
                ]

                for a in anuncios:
                    preco = round(float(a['preco']), 2) if a['preco'] else None

                    # ID único: SKU + sufixo (para poder fazer update_or_create)
                    id_interno = f'{sku}-{a["sufixo"]}'

                    # Verifica se já existe pelo id interno
                    existente = Anuncio.objects.filter(
                        produto=produto,
                        tipo_anuncio=a['tipo_anuncio'],
                        tipo_envio=a['tipo_envio']
                    ).first()

                    if existente:
                        existente.preco_atual = preco
                        existente.titulo = titulo
                        existente.save()
                        atualizados += 1
                        # self.stdout.write(
                        #     f'  [ATUALIZADO] {sku} — {a["tipo_anuncio"].nome} {a["tipo_envio"]}')
                    else:
                        Anuncio.objects.create(
                            produto=produto,
                            tipo_anuncio=a['tipo_anuncio'],
                            tipo_envio=a['tipo_envio'],
                            id_marketplace=gerar_mlb(),
                            titulo=titulo,
                            preco_atual=preco,
                            status='ATIVO',
                        )
                        criados += 1
                        # self.stdout.write(
                        #     f'  [CRIADO]     {sku} — {a["tipo_anuncio"].nome} {a["tipo_envio"]}')

            except Exception as e:
                erros += 1
                self.stdout.write(self.style.ERROR(
                    f'  [ERRO] Linha {i + 2}: {e}'))

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(
            f'Importação concluída!\n'
            f'  Criados:     {criados}\n'
            f'  Atualizados: {atualizados}\n'
            f'  Ignorados:   {ignorados}\n'
            f'  Erros:       {erros}'
        ))
