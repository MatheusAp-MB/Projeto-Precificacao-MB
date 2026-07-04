# * [RESUMO] → Comando Django para popular Produto a partir de dados reais do ML.
#              Cruza detalhes_mlbs (lista de SKUs com anúncio real no ML) com
#              Produtos_do_ML_Sysemp (dados do ERP: EAN, título, marca, categoria,
#              estoque, imagem) — garantindo que todo produto realmente anunciado
#              no ML tenha uma linha correspondente em Produto.
#
#              Regras já definidas:
#              - SKU vem do detalhes_mlbs (fonte da lista de produtos reais)
#              - EAN, Cód. Fabricante, Título, Marca, Categoria, Estoque, Imagem vêm do ERP
#              - Preço é ignorado completamente (não interessa para Produto)
#              - Categoria do ML é ignorada — só a do ERP importa
#              - SKU sem EAN correspondente no ERP → não é importado, fica só logado
#
#              Uso: python manage.py importar_produtos_ml
#              (os caminhos dos arquivos são fixos abaixo, não são passados por parâmetro)

import pandas as pd
from django.core.management.base import BaseCommand
from produtos.models import Produto

# ================================================
# CAMINHOS DOS ARQUIVOS — ajuste aqui
# ================================================
CAMINHO_DETALHES = r'Arquivos_API\detalhes_mlbs.xlsx'
CAMINHO_ERP = r'Arquivos_API\Produtos_do_ML_Sysemp.xlsx'


class Command(BaseCommand):
    help = 'Popula Produto a partir do cruzamento entre detalhes_mlbs (ML) e Produtos_do_ML_Sysemp (ERP)'

    def handle(self, *args, **options):
        # ================================================
        # 1. LER DETALHES_MLBS — só a lista de SKUs reais
        # ================================================
        self.stdout.write(f'Lendo {CAMINHO_DETALHES}...')
        try:
            df_detalhes = pd.read_excel(
                CAMINHO_DETALHES, sheet_name='Detalhes')
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Erro ao abrir {CAMINHO_DETALHES}: {e}'))
            return

        total_linhas_ml = len(df_detalhes)
        df_skus = df_detalhes[['SKU']].drop_duplicates(
            subset='SKU', keep='first')
        self.stdout.write(
            f'  {total_linhas_ml} linhas totais → {len(df_skus)} SKUs únicos após dedupe')

        # ================================================
        # 2. LER PRODUTOS_DO_ML_SYSEMP — dados que vão popular o Produto
        # ================================================
        self.stdout.write(f'Lendo {CAMINHO_ERP}...')
        try:
            df_erp = pd.read_excel(CAMINHO_ERP)
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Erro ao abrir {CAMINHO_ERP}: {e}'))
            return

        df_erp = df_erp.rename(columns={'SKU na Plataforma': 'SKU'})

        # * [EXPLICAÇÃO] → Mantém só as colunas que de fato vão popular o Produto.
        #                  Preço é ignorado por decisão já tomada.
        df_erp = df_erp[[
            'SKU',
            'Código de Barras',
            'Código Fabricante',
            'Descrição do Produto',
            'Categoria',
            'Estoque',
            'Marca',
            'Imagem 1',
        ]]
        self.stdout.write(f'  {len(df_erp)} SKUs no arquivo do ERP')

        # ================================================
        # 3. MERGE — base é a lista de SKUs reais do ML
        # ================================================
        self.stdout.write(
            'Fazendo merge por SKU (left join — base é a lista de SKUs do ML)...')
        df_final = df_skus.merge(df_erp, on='SKU', how='left')

        # ================================================
        # 4. RENOMEIA PARA OS NOMES FINAIS DO PRODUTO
        # ================================================
        df_final = df_final.rename(columns={
            'SKU':                   'sku',
            'Código de Barras':      'ean',
            'Código Fabricante':     'cod_fabricante',
            'Descrição do Produto':  'titulo',
            'Categoria':             'categoria',
            'Estoque':               'estoque',
            'Marca':                 'marca',
            'Imagem 1':              'imagem_url',
        })

        # ================================================
        # 5. GRAVA NO BANCO — só quem tem EAN
        # ================================================
        criados = 0
        atualizados = 0
        sem_ean = 0

        for _, row in df_final.iterrows():
            sku = row['sku']
            ean = row['ean']

            if pd.isna(ean):
                self.stdout.write(
                    f'  [SEM EAN] SKU {sku} não encontrado no ERP — não importado')
                sem_ean += 1
                continue

            dados = {
                'ean':            str(ean).strip(),
                'cod_fabricante': str(row['cod_fabricante']).strip() if pd.notna(row['cod_fabricante']) else None,
                'titulo':         str(row['titulo']).strip() if pd.notna(row['titulo']) else sku,
                'categoria':      str(row['categoria']).strip() if pd.notna(row['categoria']) else None,
                'estoque':        int(row['estoque']) if pd.notna(row['estoque']) else 0,
                'marca':          str(row['marca']).strip() if pd.notna(row['marca']) else None,
                'imagem_url':     str(row['imagem_url']).strip() if pd.notna(row['imagem_url']) else None,
            }

            # * [EXPLICAÇÃO] → Produto.ean é a chave única real do model —
            #                  usa ean como identificador, sku como dado adicional.
            #                  create_defaults garante que custo/peso/altura/largura/
            #                  profundidade = 0 só é aplicado na CRIAÇÃO — nunca
            #                  sobrescreve valores reais de um produto que já existe
            #                  (populado por importar_produtos.py / importar_produtos_erp.py).
            #                  Esses campos são obrigatórios no model e ainda não são
            #                  conhecidos nesta etapa — ficam como placeholder até o
            #                  próximo comando da cadeia preencher com dado real.
            _, criado = Produto.objects.update_or_create(
                ean=dados['ean'],
                defaults={**dados, 'sku': sku},
                create_defaults={
                    **dados, 'sku': sku,
                    'custo': 0, 'peso': 0,
                    'altura': 0, 'largura': 0, 'profundidade': 0,
                }
            )

            if criado:
                criados += 1
            else:
                atualizados += 1

        # ================================================
        # 6. RESUMO FINAL
        # ================================================
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(
            f'Importação concluída!\n'
            f'  Criados:      {criados}\n'
            f'  Atualizados:  {atualizados}\n'
            f'  Sem EAN (não importados): {sem_ean}\n'
            f'  Total processado: {len(df_final)}'
        ))
