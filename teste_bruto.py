import django, os, random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Projeto_Sistema_Interno_MB_SV.settings')
django.setup()

from django.db.models import Q
from produtos.models import Produto
from anuncios.models import AnuncioML, CardapioPrecos
from marketplaces.models import TipoAnuncioML, ConfiguracaoLogisticaML, FaixaArmazenagem
from precificacao_marketplaces.models import FreteML
from anuncios.signals import recalcular_combinacao

OK   = '\033[92m✓\033[0m'
FAIL = '\033[91m✗\033[0m'
SEP  = '=' * 75

# ================================================
# 1. SELECIONAR 5 PRODUTOS
# ================================================
print(f'\n{SEP}')
print('1. SELECIONANDO 5 PRODUTOS')
print(SEP)

produtos = list(Produto.objects.all()[:5])
if len(produtos) < 5:
    print(f'{FAIL} Menos de 5 produtos. Encontrados: {len(produtos)}')
    exit(1)

for p in produtos:
    print(f'   → {p.sku} — custo=R${p.custo} | peso={p.peso}kg | {p.titulo[:40]}')

# ================================================
# 2. DEFINIR MARGENS E ACRÉSCIMOS ÚNICOS POR TIPO
# ================================================
print(f'\n{SEP}')
print('2. CONFIGURANDO VALORES ÚNICOS POR TIPO')
print(SEP)

tipos = list(TipoAnuncioML.objects.filter(marketplace__sigla='ML'))
classicos = sorted([t for t in tipos if t.tipo_anuncio == 'gold_special'], key=lambda t: t.pk)
premiums  = sorted([t for t in tipos if t.tipo_anuncio == 'gold_pro'],     key=lambda t: t.pk)
tipos_ordenados = classicos + premiums

# Valores únicos aleatórios — nenhum se repete entre os 8 tipos
minimas  = random.sample(range(5,  13), 8)
padraos  = random.sample(range(14, 23), 8)
maximas  = random.sample(range(24, 38), 8)
acresci_premium = random.sample(range(3, 16), 4)

# Salva originais
originais = {t.pk: {
    'margem_minima':   t.margem_minima,
    'margem_padrao':   t.margem_padrao,
    'margem_maxima':   t.margem_maxima,
    'acrescimo_preco': t.acrescimo_preco,
} for t in tipos}

# Aplica novos valores
print(f'\n   {"Tipo":<30} {"Comissão":>8} {"Acréscimo":>9} {"Mín":>5} {"Padrão":>7} {"Máx":>5}')
print(f'   {"-"*30} {"-"*8} {"-"*9} {"-"*5} {"-"*7} {"-"*5}')

for i, tipo in enumerate(tipos_ordenados):
    is_premium = tipo.tipo_anuncio == 'gold_pro'
    acr = Decimal(str(acresci_premium[premiums.index(tipo)])) if is_premium else Decimal('0')
    TipoAnuncioML.objects.filter(pk=tipo.pk).update(
        margem_minima  = Decimal(str(minimas[i])),
        margem_padrao  = Decimal(str(padraos[i])),
        margem_maxima  = Decimal(str(maximas[i])),
        acrescimo_preco= acr,
    )
    tipo.refresh_from_db()
    print(f'   {tipo.nome:<30} {float(tipo.comissao):>7.1f}% {float(acr):>8.1f}% '
          f'{minimas[i]:>4}% {padraos[i]:>6}% {maximas[i]:>4}%')

# ================================================
# 3. CRIAR 40 ANÚNCIOS DE TESTE
# ================================================
print(f'\n{SEP}')
print('3. CRIANDO 40 ANÚNCIOS DE TESTE (5 produtos × 8 tipos)')
print(SEP)

AnuncioML.objects.filter(mlb__startswith='BRUTO').delete()
CardapioPrecos.objects.filter(produto__in=produtos).delete()

for i, produto in enumerate(produtos):
    for j, tipo in enumerate(tipos_ordenados):
        mlb = f'BRUTO{i+1:02d}{j+1:02d}'
        AnuncioML.objects.get_or_create(
            mlb=mlb,
            defaults={
                'produto':        produto,
                'titulo_anuncio': f'BRUTO {produto.sku} {tipo.nome}',
                'tipo_anuncio':   tipo.tipo_anuncio,
                'tipo_logistico': tipo.tipo_logistico,
                'catalogo':       tipo.catalogo,
                'status':         'active',
                'preco_manual':   False,
            }
        )

print(f'   {OK} 40 anúncios criados')

# ================================================
# 4. CALCULAR CARDÁPIO
# ================================================
print(f'\n{SEP}')
print('4. CALCULANDO CARDÁPIO (5 × 8 = 40 combinações)')
print(SEP)

tipos_db = list(TipoAnuncioML.objects.filter(marketplace__sigla='ML'))
for produto in produtos:
    for tipo in tipos_db:
        recalcular_combinacao(produto, tipo)

print(f'   {OK} CardapioPrecos calculado para todas as combinações')

# ================================================
# 5. VERIFICAÇÃO MATEMÁTICA COMPLETA
# ================================================
print(f'\n{SEP}')
print('5. VERIFICAÇÃO MATEMÁTICA — 40 ANÚNCIOS')
print(f'   Tolerância: proporcional ao preço — max_uplift = (R$0,90 / preço) × (1 - taxas)')
print(SEP)

logistica    = ConfiguracaoLogisticaML.objects.filter(marketplace__sigla='ML').first()
fator_coleta = logistica.fator_coleta if logistica else Decimal('0')
periodo_armaz= logistica.periodo_armazenagem if logistica else 0

erros = 0
sucessos = 0

for produto in produtos:
    print(f'\n  Produto: {produto.sku} — custo=R${produto.custo}')
    print(f'  {"Tipo":<28} {"Preço":>8} {"Margem":>8} {"Meta":>7} {"Tolerância":>11} {"Resultado":>10}')
    print(f'  {"-"*28} {"-"*8} {"-"*8} {"-"*7} {"-"*11} {"-"*10}')

    faixa_armaz = FaixaArmazenagem.objects.filter(
        marketplace__sigla='ML', ativo=True,
        max_altura__gte=produto.altura,
        max_largura__gte=produto.largura,
        max_profundidade__gte=produto.profundidade
    ).order_by('ordem').first()
    if not faixa_armaz:
        faixa_armaz = FaixaArmazenagem.objects.filter(
            marketplace__sigla='ML', ativo=True
        ).order_by('-ordem').first()

    armazenagem    = (faixa_armaz.valor_diario if faixa_armaz else Decimal('0')) * periodo_armaz
    metro_cubico   = (produto.altura / 100) * (produto.largura / 100) * (produto.profundidade / 100)
    custo_com_boni = produto.custo_com_boni or produto.custo
    ipi            = (produto.ipi or Decimal('0')) / 100
    frete_cif_fob  = (produto.frete_cif_fob or Decimal('0')) / 100
    st_valor       = produto.st_valor or Decimal('0')
    icms_entrada   = (produto.icms_entrada or Decimal('0')) / 100
    icms_saida     = (produto.icms_saida_media or Decimal('0')) / 100
    pis            = (produto.pis_cofins or Decimal('0')) / 100
    custo_final    = custo_com_boni + (custo_com_boni * ipi) + (custo_com_boni * frete_cif_fob) + st_valor
    coleta         = metro_cubico * fator_coleta
    peso           = max(produto.peso, produto.peso_cubado)

    for tipo in tipos_db:
        try:
            cardapio = CardapioPrecos.objects.get(produto=produto, tipo_anuncio=tipo)
        except CardapioPrecos.DoesNotExist:
            print(f'  {FAIL} {tipo.nome}: CardapioPrecos não encontrado')
            erros += 1
            continue

        preco = cardapio.preco_em_uso
        if not preco:
            print(f'  {FAIL} {tipo.nome}: preco_em_uso é None')
            erros += 1
            continue

        frete_obj = FreteML.objects.filter(
            peso_min__lte=peso, preco_min__lte=preco
        ).filter(
            Q(peso_max__gte=peso) | Q(peso_max__isnull=True)
        ).filter(
            Q(preco_max__gte=preco) | Q(preco_max__isnull=True)
        ).first()
        frete = frete_obj.valor if frete_obj else Decimal('0')

        comissao_pct   = tipo.comissao / 100
        comissao_valor = preco * comissao_pct
        icms_valor     = (preco * icms_saida) - (produto.custo * icms_entrada)
        pis_valor      = (preco - produto.custo) * pis
        margem_valor   = preco - frete - coleta - armazenagem - custo_final - comissao_valor - icms_valor - pis_valor
        margem_calc    = round(float(margem_valor / preco * 100), 2)
        margem_meta    = float(tipo.margem_padrao)

        # Tolerância proporcional: máximo uplift possível do roundUp90
        # roundUp90 pode adicionar no máximo R$0,90 ao preço exato.
        # Esse valor a mais contribui com (0.90/preco) × (1 - taxas) de margem adicional.
        taxas_pct     = float(comissao_pct + icms_saida + pis)
        tolerancia    = round((0.90 / float(preco)) * (1 - taxas_pct) * 100, 2)

        ok_minimo = margem_calc >= margem_meta - 0.05
        ok_maximo = margem_calc <= margem_meta + tolerancia + 0.05  # +0.05 para arredondamento decimal
        ok        = ok_minimo and ok_maximo

        simbolo   = OK if ok else FAIL
        resultado = 'OK' if ok else 'FALHOU'

        print(f'  {simbolo} {tipo.nome:<28} R${preco:>6.2f} {margem_calc:>7.2f}% {margem_meta:>6.2f}% '
              f'  ±{tolerancia:>5.2f}%   {resultado}')

        if ok:
            sucessos += 1
        else:
            erros += 1

# ================================================
# 6. RESUMO FINAL
# ================================================
print(f'\n{SEP}')
print('6. RESUMO FINAL')
print(SEP)
print(f'   {OK} Sucessos: {sucessos}/40')
if erros:
    print(f'   {FAIL} Erros:    {erros}/40')
else:
    print(f'   {OK} Nenhum erro — matemática validada para todas as combinações!')

# ================================================
# 7. LIMPEZA E RESTAURAÇÃO
# ================================================
print(f'\n{SEP}')
print('7. LIMPEZA E RESTAURAÇÃO')
print(SEP)

for tipo in tipos:
    TipoAnuncioML.objects.filter(pk=tipo.pk).update(**originais[tipo.pk])

AnuncioML.objects.filter(mlb__startswith='BRUTO').delete()
CardapioPrecos.objects.filter(produto__in=produtos).delete()

print(f'   {OK} Valores originais dos TipoAnuncioML restaurados')
print(f'   {OK} Anúncios BRUTO removidos')
print(f'   {OK} CardapioPrecos de teste removidos')
print(f'\nTeste concluído.\n')