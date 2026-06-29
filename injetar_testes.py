import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Projeto_Sistema_Interno_MB_SV.settings')
django.setup()

from django.db import connection
from produtos.models import Produto
from tags.models import TagPreco
from anuncios.models import AnuncioML
from anuncios.signals import recalcular_tudo

OK   = '\033[92m✓\033[0m'
FAIL = '\033[91m✗\033[0m'
SEP  = '=' * 60

# ================================================
# 1. COLETA DE DADOS DO BANCO
# ================================================
print(f'\n{SEP}')
print('1. COLETANDO DADOS DO BANCO')
print(SEP)

produto = Produto.objects.first()
if not produto:
    print(f'{FAIL} Nenhum produto encontrado.')
    exit(1)
print(f'{OK} Produto base: {produto.sku} — {produto.titulo[:50]}')

tags = list(TagPreco.objects.filter(ativo=True).order_by('tipo', 'valor_pct'))
print(f'{OK} Tags encontradas: {len(tags)}')
for t in tags:
    print(f'     id={t.id} → {t}')

# ================================================
# 2. DEFINIÇÃO DAS COMBINAÇÕES
# ================================================
print(f'\n{SEP}')
print('2. GERANDO 176 COMBINAÇÕES')
print(SEP)

tipos_anuncio  = ['gold_special', 'gold_pro']
tipos_logistico= ['flex', 'fulfillment']
catalogos      = [False, True]
tag_ids        = [None] + [t.id for t in tags]  # None + 10 tags = 11
travados       = [False, True]

# Remove TST anteriores
removidos = AnuncioML.objects.filter(mlb__startswith='TST').delete()
print(f'   Anúncios TST anteriores removidos: {removidos[0]}')

# ================================================
# 3. GERAÇÃO E EXECUÇÃO DO SQL
# ================================================
print(f'\n{SEP}')
print('3. EXECUTANDO SQL')
print(SEP)

nomes_tipos    = {'gold_special': 'Clássico', 'gold_pro': 'Premium'}
nomes_logistic = {'flex': 'Flex', 'fulfillment': 'FULL'}

inserts = []
counter = 0

for tipo_anuncio in tipos_anuncio:
    for tipo_logistico in tipos_logistico:
        for catalogo in catalogos:
            for tag_id in tag_ids:
                for travado in travados:
                    counter += 1
                    mlb   = f'TST{counter:04d}'
                    cat_str = 'Cat' if catalogo else 'SemCat'
                    tag_str = next((t.nome for t in tags if t.id == tag_id), 'SemTag')
                    trav_str= 'Trav' if travado else 'Livre'
                    titulo  = (
                        f'[TESTE] {nomes_tipos[tipo_anuncio]} '
                        f'{nomes_logistic[tipo_logistico]} '
                        f'{cat_str} | {tag_str} | {trav_str}'
                    )[:255]

                    tag_val  = str(tag_id) if tag_id else 'NULL'
                    cat_val  = '1' if catalogo else '0'
                    trav_val = '1' if travado else '0'

                    inserts.append(f"""(
                        '{mlb}', NULL, '{produto.sku}', '{titulo}',
                        '{tipo_anuncio}', '{tipo_logistico}', {cat_val},
                        'active', 10, 0, 75, 'gold', {trav_val}, {tag_val},
                        NULL, NULL, NULL, NULL, NULL, NULL,
                        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                        NULL, NULL
                    )""")

# Executa em lote
sql = """
INSERT INTO anuncios_anuncioml (
    mlb, mlbu, produto_id, titulo_anuncio,
    tipo_anuncio, tipo_logistico, catalogo,
    status, estoque, qtd_vendas, score, nivel, preco_travado, tag_preco_id,
    frete_da_planilha, frete_calculado,
    preco_classico_da_planilha, preco_classico_calculado,
    preco_premium_da_planilha, preco_premium_calculado,
    margem_classico_da_planilha, margem_classico_valor_da_planilha,
    margem_classico_calculado, margem_classico_calculado_baseado_na_planilha,
    margem_premium_da_planilha, margem_premium_valor_da_planilha,
    margem_premium_calculado, margem_premium_calculado_baseado_na_planilha,
    preco_atacado_2, preco_atacado_3
) VALUES """ + ',\n'.join(inserts) + ';'

with connection.cursor() as cursor:
    cursor.execute(sql)

print(f'{OK} {counter} anúncios TST inseridos via SQL')

# ================================================
# 4. RECALCULO COMPLETO
# ================================================
print(f'\n{SEP}')
print('4. RECALCULANDO PREÇOS')
print(SEP)

from anuncios.signals import recalcular_todas_combinacoes_do_produto
recalcular_todas_combinacoes_do_produto(produto)
print(f'{OK} Recálculo concluído')

# ================================================
# 5. VERIFICAÇÃO
# ================================================
print(f'\n{SEP}')
print('5. VERIFICAÇÃO')
print(SEP)

total    = AnuncioML.objects.filter(mlb__startswith='TST').count()
com_preco= AnuncioML.objects.filter(mlb__startswith='TST', preco_classico_calculado__isnull=False).count()
com_preco+= AnuncioML.objects.filter(mlb__startswith='TST', preco_premium_calculado__isnull=False).count()
com_tag  = AnuncioML.objects.filter(mlb__startswith='TST', tag_preco__isnull=False).count()
travados_n= AnuncioML.objects.filter(mlb__startswith='TST', preco_travado=True).count()

print(f'{OK} Total inseridos:       {total}')
print(f'{OK} Com preço calculado:   {com_preco}')
print(f'{OK} Com tag aplicada:      {com_tag}')
print(f'{OK} Com preço travado:     {travados_n}')
print(f'\nAcesse a tela de anúncios para verificar visualmente.')
print(f'Para remover: AnuncioML.objects.filter(mlb__startswith="TST").delete()\n')