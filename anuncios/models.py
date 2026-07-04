# * [RESUMO] → Models do app de anúncios.
#              Define AnuncioML (dados do anúncio no Mercado Livre) e
#              BaseDeCalculo (registro detalhado de cada etapa do cálculo de precificação).
#
#              Convenção de nomenclatura adotada no projeto:
#              - Sufixo "_da_planilha"              → valor importado diretamente da planilha (auditoria/comparação)
#              - Sufixo "_calculado"                → valor gerado pelo sistema (Goal Seek ou signal)
#              - Sufixo "_baseado_na_planilha"      → calculado pelo sistema usando armazenagem da planilha como input
#              - As fórmulas sempre usam os campos "_calculado" — os "_da_planilha" são apenas para comparação.
#
#              Sobre os dois cálculos paralelos de margem:
#              - _calculado                    → faixa de armazenagem selecionada pelas dimensões do produto
#              - _calculado_baseado_na_planilha → usa armazenagem_planilha do produto (coluna BH) como input
#              Ver documentação completa em produtos/models.py (campo armazenagem_planilha).
from django.db import models
from produtos.models import Produto


# ================================================
# ANÚNCIO MERCADO LIVRE
# ================================================

class AnuncioML(models.Model):
    # * [EXPLICAÇÃO] → Representa um anúncio publicado no Mercado Livre.
    #                  Cada linha é um anúncio único identificado pelo MLB.
    #                  Um mesmo produto pode ter múltiplos anúncios (Clássico, Premium, variações).

    class TipoAnuncio(models.TextChoices):
        CLASSICO = 'gold_special', 'Clássico'
        PREMIUM  = 'gold_pro',     'Premium'

    class TipoLogistico(models.TextChoices):
        FULL     = 'fulfillment', 'FULL'
        ME_SEND  = 'me2',         'Manda tu'
        FLEX     = 'flex',        'Flex'
        DROPSHIP = 'drop_off',    'Drop-off'

    class Status(models.TextChoices):
        ATIVO               = 'active',           'Ativo'
        PAUSADO              = 'paused',            'Pausado'
        FECHADO               = 'closed',            'Encerrado'
        EM_REVISAO            = 'under_review',      'Em revisão'
        DEBITO_PENDENTE       = 'payment_required',  'Débito pendente'
        AGUARDANDO_ATIVACAO   = 'not_yet_active',    'Aguardando ativação'

    class Nivel(models.TextChoices):
        BOM     = 'good',    'Bom'
        REGULAR = 'regular', 'Regular'
        RUIM    = 'bad',     'Ruim'

    # ================================================
    # IDENTIFICADORES
    # ================================================

    mlb    = models.CharField(max_length=20, unique=True)
    mlbu   = models.CharField(max_length=20, blank=True, null=True)

    # * [EXPLICAÇÃO] → SKU exatamente como veio da API do ML (seller_custom_field),
    #                  sem nenhum tratamento. Serve para detectar divergência
    #                  entre o que o ML tem cadastrado e o que o Produto/ERP tem —
    #                  a regra é que sejam iguais; se divergirem, é erro de
    #                  cadastro do anúncio, não falha do sistema.
    sku_ml = models.CharField(max_length=30, blank=True, null=True)

    # * [EXPLICAÇÃO] → Ligação com o produto via SKU — regra do projeto.
    #                  Se o SKU do anúncio não bater com o Produto, está errado.
    produto = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anuncios_ml',
        to_field='sku'
    )

    titulo_anuncio = models.CharField(max_length=255, blank=True, null=True)

    # ================================================
    # TIPO
    # ================================================

    tipo_anuncio   = models.CharField(max_length=20, choices=TipoAnuncio.choices,   blank=True, null=True)
    tipo_logistico = models.CharField(max_length=20, choices=TipoLogistico.choices, blank=True, null=True)
    catalogo       = models.BooleanField(default=False)

    # ================================================
    # CLASSIFICAÇÃO DE CATÁLOGO — dados brutos da API
    # ================================================
    # * [EXPLICAÇÃO] → Usados pela lógica de classificação (Simples/Base/Catálogo)
    #                  e pela árvore de agrupamento por Página de Catálogo.
    #                  Regra: catalog_product_id vazio → Simples
    #                         catalog_listing = True   → Anúncio de Catálogo
    #                         catalog_listing = False  → Anúncio Base
    catalog_product_id = models.CharField(max_length=30, blank=True, null=True)
    catalog_listing     = models.BooleanField(null=True, blank=True)
    item_relations      = models.JSONField(blank=True, null=True)

    # ================================================
    # ESTADO
    # ================================================

    status    = models.CharField(max_length=20, choices=Status.choices, blank=True, null=True)
    estoque   = models.IntegerField(default=0)
    score     = models.IntegerField(blank=True, null=True)
    nivel     = models.CharField(max_length=10, choices=Nivel.choices, blank=True, null=True)
    qtd_vendas = models.IntegerField(default=0)
    permalink  = models.URLField(max_length=500, blank=True, null=True)

    data_criacao_ml       = models.DateTimeField(blank=True, null=True)
    ultima_atualizacao_ml = models.DateTimeField(blank=True, null=True)

    # ================================================
    # PRECIFICAÇÃO — FRETE
    # ================================================

    # * [EXPLICAÇÃO] → frete_da_planilha → importado da planilha (coluna BF), mantido para comparação.
    #                  frete_calculado   → calculado pelo sistema via tabela FreteML.
    frete_da_planilha = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    frete_calculado   = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # ================================================
    # PRECIFICAÇÃO — PREÇO CLÁSSICO
    # ================================================

    # * [EXPLICAÇÃO] → preco_classico_da_planilha → importado da planilha (resultado do Goal Seek do Excel).
    #                  preco_classico_calculado   → calculado pelo sistema via Goal Seek analítico.
    #                  Todas as fórmulas do sistema usam preco_classico_calculado.
    preco_classico_da_planilha = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    preco_classico_calculado   = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # ================================================
    # PRECIFICAÇÃO — PREÇO PREMIUM
    # ================================================

    # * [EXPLICAÇÃO] → preco_premium_da_planilha → importado da planilha.
    #                  preco_premium_calculado   → calculado pelo sistema via RoundUpTo90(preco_classico × acrescimo).
    preco_premium_da_planilha = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    preco_premium_calculado   = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


    # ================================================
    # PRECIFICAÇÃO — MARGEM CLÁSSICA
    # ================================================

    # * [EXPLICAÇÃO] → margem_classico_da_planilha                    → importado da planilha (%) — coluna BT.
    #                  margem_classico_valor_da_planilha               → importado da planilha (R$) — coluna BQ.
    #                  margem_classico_calculado                       → calculado pelo sistema (faixa dinâmica por dimensão).
    #                  margem_classico_calculado_baseado_na_planilha   → calculado pelo sistema usando armazenagem da planilha.
    margem_classico_da_planilha                  = models.DecimalField(max_digits=6,  decimal_places=2, blank=True, null=True)
    margem_classico_valor_da_planilha            = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    margem_classico_calculado                    = models.DecimalField(max_digits=6,  decimal_places=2, blank=True, null=True)
    margem_classico_calculado_baseado_na_planilha = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)



    # ================================================
    # PRECIFICAÇÃO — MARGEM PREMIUM
    # ================================================

    # * [EXPLICAÇÃO] → margem_premium_da_planilha                    → importado da planilha (%) — coluna CA.
    #                  margem_premium_valor_da_planilha               → importado da planilha (R$) — coluna BX.
    #                  margem_premium_calculado                       → calculado pelo sistema (faixa dinâmica por dimensão).
    #                  margem_premium_calculado_baseado_na_planilha   → calculado pelo sistema usando armazenagem da planilha.
    margem_premium_da_planilha                  = models.DecimalField(max_digits=6,  decimal_places=2, blank=True, null=True)
    margem_premium_valor_da_planilha            = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    margem_premium_calculado                    = models.DecimalField(max_digits=6,  decimal_places=2, blank=True, null=True)
    margem_premium_calculado_baseado_na_planilha = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    # * [EXPLICAÇÃO] → preco_travado = True → signal não sobrescreve o preço.
    #                  Pode ser ativado pelo usuário para congelar o preço atual
    #                  (seja ele calculado pelo sistema ou digitado manualmente).
    #                  O sistema ainda recalcula e exibe a margem resultante,
    #                  mas o preço em si não muda.
    preco_travado = models.BooleanField(default=False)

    # * [EXPLICAÇÃO] → Tag de modificação de preço aplicada a este anúncio.
    #                  desconto  → preco_final = roundUp90(preco_em_uso × (1 - valor_pct/100))
    #                  acrescimo → preco_final = roundUp90(preco_em_uso × (1 + valor_pct/100))
    #                  Reaplicada automaticamente a cada recálculo do CardapioPrecos.
    #                  Ignorada quando preco_travado = True.
    tag_preco = models.ForeignKey(
        'tags.TagPreco',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anuncios'
    )

    # * [EXPLICAÇÃO] → Cópias locais dos preços de atacado vindos do CardapioPrecos.
    #                  Recalculados sobre o preco_em_uso quando o CardapioPrecos atualiza.
    #                  Se preco_manual = True, recalculados sobre o preço manual do anúncio.
    preco_atacado_2 = models.DecimalField(max_digits=10, decimal_places=2,
                                          null=True, blank=True)
    preco_atacado_3 = models.DecimalField(max_digits=10, decimal_places=2,
                                          null=True, blank=True)
    
    # ================================================
    # META
    # ================================================

    class Meta:
        verbose_name        = 'Anúncio ML'
        verbose_name_plural = 'Anúncios ML'
        ordering            = ['mlb']

    def __str__(self):
        return f'{self.mlb} — {self.titulo_anuncio}'


# ================================================
# BASE DE CÁLCULO
# ================================================

class BaseDeCalculo(models.Model):
    # * [EXPLICAÇÃO] → Registro completo de todos os valores que compõem o cálculo
    #                  de precificação de um anúncio. Serve como modo debug —
    #                  o usuário pode conferir cada etapa do cálculo em detalhe.
    #                  Relação OneToOne com AnuncioML — um registro por anúncio,
    #                  sempre sobrescrito quando o cálculo é refeito.
    #
    #                  Campos com sufixo _dinamico → usam faixa de armazenagem por dimensão do produto
    #                  Campos sem sufixo           → são os campos _dinamico (nomenclatura herdada)
    #                  Campos com sufixo _planilha → usam armazenagem importada da coluna BH da planilha

    anuncio      = models.OneToOneField(AnuncioML, on_delete=models.CASCADE, related_name='base_calculo')
    calculado_em = models.DateTimeField(auto_now=True)

    # ================================================
    # DADOS DE ENTRADA — PRODUTO
    # ================================================
    # * [EXPLICAÇÃO] → Cópia dos dados do produto no momento do cálculo.
    #                  Garante rastreabilidade mesmo se o produto for alterado depois.

    entrada_custo            = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    entrada_custo_com_boni   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    entrada_ipi              = models.DecimalField(max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_frete_cif_fob    = models.DecimalField(max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_st_valor         = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    entrada_icms_entrada     = models.DecimalField(max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_icms_saida_media = models.DecimalField(max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_pis_cofins       = models.DecimalField(max_digits=6,  decimal_places=2, null=True, blank=True)
    entrada_peso             = models.DecimalField(max_digits=8,  decimal_places=3, null=True, blank=True)
    entrada_peso_cubado      = models.DecimalField(max_digits=8,  decimal_places=3, null=True, blank=True)
    entrada_altura           = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)
    entrada_largura          = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)
    entrada_profundidade     = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)

    # ================================================
    # DADOS DE ENTRADA — ANÚNCIO E MARKETPLACE
    # ================================================

    entrada_comissao_classico        = models.DecimalField(max_digits=5,  decimal_places=2, null=True, blank=True)
    entrada_acrescimo_premium        = models.DecimalField(max_digits=5,  decimal_places=2, null=True, blank=True)
    entrada_fator_coleta             = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)
    entrada_armazenagem_faixa_valor  = models.DecimalField(max_digits=8,  decimal_places=4, null=True, blank=True)
    entrada_armazenagem_periodo      = models.IntegerField(null=True, blank=True)

    # * [EXPLICAÇÃO] → Valor mensal de armazenagem importado da planilha (coluna BH).
    #                  Registrado aqui para rastreabilidade do cálculo baseado na planilha.
    entrada_armazenagem_da_planilha = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)


    # ================================================
    # FÓRMULAS — VALORES INTERMEDIÁRIOS
    # ================================================
    # * [EXPLICAÇÃO] → Cada etapa do cálculo é registrada com sua fórmula e valor resultante.
    #                  Permite auditar qualquer divergência entre o sistema e a planilha.

    formula_metro_cubico = models.CharField(
        max_length=200, blank=True,
        default='(Altura ÷ 100) × (Largura ÷ 100) × (Profundidade ÷ 100)'
    )
    calc_metro_cubico = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    formula_custo_final = models.CharField(
        max_length=200, blank=True,
        default='Custo c/ Boni + (Custo c/ Boni × IPI) + (Custo c/ Boni × Frete CIF/FOB) + ST Valor'
    )
    calc_custo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_coleta = models.CharField(
        max_length=200, blank=True,
        default='Metro Cúbico × Fator de Coleta'
    )
    calc_coleta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # * [EXPLICAÇÃO] → calc_armazenagem                  → faixa selecionada pelas dimensões do produto
    #                  calc_armazenagem_baseada_na_planilha → valor direto da coluna BH da planilha
    formula_armazenagem = models.CharField(
        max_length=200, blank=True,
        default='Tarifa Diária da Faixa × Período de Armazenagem'
    )
    calc_armazenagem                   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    calc_armazenagem_baseada_na_planilha = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_preco_premium = models.CharField(
        max_length=200, blank=True,
        default='RoundUpTo90(Preço Clássico Calculado × (1 + Acréscimo Premium))'
    )
    calc_preco_premium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_comissao_classico = models.CharField(
        max_length=200, blank=True,
        default='Preço Clássico Calculado × Comissão Clássico'
    )
    calc_comissao_classico = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_comissao_premium = models.CharField(
        max_length=200, blank=True,
        default='Preço Premium Calculado × Comissão Premium'
    )
    calc_comissao_premium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_icms_classico = models.CharField(
        max_length=200, blank=True,
        default='(Preço Clássico Calculado × ICMS Saída) - (Custo × ICMS Entrada)'
    )
    calc_icms_classico = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_icms_premium = models.CharField(
        max_length=200, blank=True,
        default='(Preço Premium Calculado × ICMS Saída) - (Custo × ICMS Entrada)'
    )
    calc_icms_premium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_pis_cofins_classico = models.CharField(
        max_length=200, blank=True,
        default='(Preço Clássico Calculado - Custo) × PIS/COFINS'
    )
    calc_pis_cofins_classico = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    formula_pis_cofins_premium = models.CharField(
        max_length=200, blank=True,
        default='(Preço Premium Calculado - Custo) × PIS/COFINS'
    )
    calc_pis_cofins_premium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # ================================================
    # RESULTADOS FINAIS — CÁLCULO _DINAMICO
    # ================================================
    # * [EXPLICAÇÃO] → Faixa de armazenagem selecionada automaticamente pelas dimensões do produto.
    #                  Considerado o cálculo tecnicamente correto.

    formula_margem_classico = models.CharField(
        max_length=500, blank=True,
        default='[_dinamico] Preço Clássico - Frete - Coleta - Armazenagem Dinâmica - Custo Final - Comissão Clássico - ICMS Clássico - PIS/COFINS Clássico'
    )
    resultado_margem_classico_valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    resultado_margem_classico_pct   = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)

    formula_margem_premium = models.CharField(
        max_length=500, blank=True,
        default='[_dinamico] Preço Premium - Frete - Coleta - Armazenagem Dinâmica - Custo Final - Comissão Premium - ICMS Premium - PIS/COFINS Premium'
    )
    resultado_margem_premium_valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    resultado_margem_premium_pct   = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)

    # ================================================
    # RESULTADOS FINAIS — CÁLCULO BASEADO NA PLANILHA
    # ================================================
    # * [EXPLICAÇÃO] → Usa armazenagem importada diretamente da coluna BH da planilha.
    #                  Existe para comparação com o cálculo dinâmico e identificação de inconsistências.
    #                  Ver documentação em produtos/models.py (campo armazenagem_planilha).

    resultado_margem_classico_valor_baseado_na_planilha = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    resultado_margem_classico_pct_baseado_na_planilha   = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)

    resultado_margem_premium_valor_baseado_na_planilha  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    resultado_margem_premium_pct_baseado_na_planilha    = models.DecimalField(max_digits=8,  decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name        = 'Base de Cálculo'
        verbose_name_plural = 'Bases de Cálculo'

    def __str__(self):
        return f'Base de Cálculo — {self.anuncio.mlb}'



class CardapioPrecos(models.Model):
    # * [RESUMO] → Armazena o cardápio de preços calculados para cada combinação
    #              produto + tipo de anúncio. O Goal Seek roda aqui — nunca diretamente
    #              no AnuncioML. Cada AnuncioML lê desta tabela e guarda uma cópia local.
    #              Uma linha por combinação — 10 anúncios do mesmo tipo = 1 cálculo.

    class PreferenciaPreco(models.TextChoices):
        MARGEM_PADRAO = 'margem_padrao', 'Margem Padrão'
        MARGEM_MINIMA = 'margem_minima', 'Margem Mínima'
        MARGEM_MAXIMA = 'margem_maxima', 'Margem Máxima'

    # Chave única
    produto      = models.ForeignKey(Produto, on_delete=models.CASCADE,
                                     related_name='cardapio_precos', to_field='sku')
    tipo_anuncio = models.ForeignKey('marketplaces.TipoAnuncioML',
                                     on_delete=models.PROTECT,
                                     related_name='cardapio_precos')

    # Preço base — resultado puro do Goal Seek, antes do acréscimo
    preco_base = models.DecimalField(max_digits=10, decimal_places=2,
                                     null=True, blank=True)

    # Cardápio — já com acréscimo + roundUp90 aplicados
    preco_margem_padrao = models.DecimalField(max_digits=10, decimal_places=2,
                                              null=True, blank=True)
    preco_margem_minima = models.DecimalField(max_digits=10, decimal_places=2,
                                              null=True, blank=True)
    preco_margem_maxima = models.DecimalField(max_digits=10, decimal_places=2,
                                              null=True, blank=True)

    # Decisão do usuário
    preferencia_preco = models.CharField(max_length=20,
                                         choices=PreferenciaPreco.choices,
                                         default=PreferenciaPreco.MARGEM_PADRAO)
    preco_em_uso      = models.DecimalField(max_digits=10, decimal_places=2,
                                            null=True, blank=True)

    # Atacado — derivados do preco_em_uso
    preco_atacado_2 = models.DecimalField(max_digits=10, decimal_places=2,
                                          null=True, blank=True)
    preco_atacado_3 = models.DecimalField(max_digits=10, decimal_places=2,
                                          null=True, blank=True)

    # Controle
    calculado_em = models.DateTimeField(auto_now=True)
    valido       = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.produto.sku} — {self.tipo_anuncio.nome}'

    class Meta:
            unique_together     = ['produto', 'tipo_anuncio']
            verbose_name        = 'Cardápio de Preços'
            verbose_name_plural = 'Cardápios de Preços'
            ordering            = ['produto', 'tipo_anuncio']