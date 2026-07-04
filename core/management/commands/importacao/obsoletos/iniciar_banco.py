# * [RESUMO] → Comando para popular a configuração inicial do banco de dados.
#              Deve ser executado uma vez após o migrate em qualquer PC novo.
#              Uso: python manage.py iniciar_banco
#              Usa get_or_create — seguro rodar múltiplas vezes, nunca duplica dados.

from django.core.management.base import BaseCommand
from decimal import Decimal


class Command(BaseCommand):
    help = 'Popula a configuração inicial do banco de dados'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando configuração do banco...\n')

        self._popular_ml()
        self._popular_tags()

        self.stdout.write(self.style.SUCCESS('\nBanco configurado com sucesso!'))

    def _popular_ml(self):
        from marketplaces.models import Marketplace, ConfiguracaoLogisticaML, TipoAnuncioML, FaixaArmazenagem

        self.stdout.write('  [ML] Marketplace...')
        ml, criado = Marketplace.objects.get_or_create(
            sigla='ML',
            defaults={'nome': 'Mercado Livre', 'ativo': True}
        )
        self.stdout.write(f'       {"criado" if criado else "já existe"}')

        # ================================================
        # CONFIGURAÇÃO LOGÍSTICA
        # ================================================

        self.stdout.write('  [ML] Configuração logística...')
        _, criado = ConfiguracaoLogisticaML.objects.get_or_create(
            marketplace=ml,
            defaults={
                'fator_coleta':        Decimal('72'),
                'periodo_armazenagem': 30,
            }
        )
        self.stdout.write(f'       {"criada" if criado else "já existe"}')

        # ================================================
        # TIPOS DE ANÚNCIO
        # ================================================

        self.stdout.write('  [ML] Tipos de anúncio...')
        tipos = [
            ('Clássico Flex',          'gold_special', 'flex',        False, 12, 0),
            ('Clássico Flex Catálogo', 'gold_special', 'flex',        True,  12, 0),
            ('Clássico FULL',          'gold_special', 'fulfillment', False, 12, 0),
            ('Clássico FULL Catálogo', 'gold_special', 'fulfillment', True,  12, 0),
            ('Premium Flex',           'gold_pro',     'flex',        False, 17, 8),
            ('Premium Flex Catálogo',  'gold_pro',     'flex',        True,  17, 8),
            ('Premium FULL',           'gold_pro',     'fulfillment', False, 17, 8),
            ('Premium FULL Catálogo',  'gold_pro',     'fulfillment', True,  17, 8),
        ]

        for nome, tipo_anuncio, tipo_logistico, catalogo, comissao, acrescimo in tipos:
            _, criado = TipoAnuncioML.objects.get_or_create(
                marketplace=ml,
                tipo_anuncio=tipo_anuncio,
                tipo_logistico=tipo_logistico,
                catalogo=catalogo,
                defaults={
                    'nome':               nome,
                    'comissao':           Decimal(str(comissao)),
                    'acrescimo_preco':    Decimal(str(acrescimo)),
                    'margem_padrao':      Decimal('15'),
                    'margem_minima':      Decimal('10'),
                    'margem_maxima':      Decimal('25'),
                    'desconto_atacado_2': Decimal('5'),
                    'desconto_atacado_3': Decimal('8'),
                }
            )
            self.stdout.write(f'       {nome}: {"criado" if criado else "já existe"}')

        # ================================================
        # FAIXAS DE ARMAZENAGEM
        # ================================================

        self.stdout.write('  [ML] Faixas de armazenagem...')
        faixas = [
            (1, 'Faixa 1 — Até 12×15×25cm',       Decimal('0.0070'),  12,   15,   25),
            (2, 'Faixa 2 — Até 28×36×51cm',       Decimal('0.0150'),  28,   36,   51),
            (3, 'Faixa 3 — Até 60×60×70cm',       Decimal('0.0500'),  60,   60,   70),
            (4, 'Faixa 4 — Maior que 60×60×70cm', Decimal('0.1070'), 9999, 9999, 9999),
        ]

        for ordem, nome, valor_diario, max_altura, max_largura, max_profundidade in faixas:
            _, criado = FaixaArmazenagem.objects.get_or_create(
                marketplace=ml,
                ordem=ordem,
                defaults={
                    'nome':             nome,
                    'valor_diario':     valor_diario,
                    'max_altura':       Decimal(str(max_altura)),
                    'max_largura':      Decimal(str(max_largura)),
                    'max_profundidade': Decimal(str(max_profundidade)),
                    'ativo':            True,
                }
            )
            self.stdout.write(f'       {nome}: {"criada" if criado else "já existe"}')



    def _popular_tags(self):
        from tags.models import TagPreco

        self.stdout.write('  [TAGS] Tags de preço...')
        tags = [
            # Descontos
            ('Promoção 5%',   'desconto',  Decimal('5'),  '#f59e0b'),
            ('Promoção 10%',  'desconto',  Decimal('10'), '#f97316'),
            ('Promoção 15%',  'desconto',  Decimal('15'), '#ef4444'),
            ('Promoção 20%',  'desconto',  Decimal('20'), '#dc2626'),
            ('Promoção 25%',  'desconto',  Decimal('25'), '#991b1b'),
            # Acréscimos
            ('Alta Demanda 5%',  'acrescimo', Decimal('5'),  '#34d399'),
            ('Alta Demanda 10%', 'acrescimo', Decimal('10'), '#10b981'),
            ('Alta Demanda 15%', 'acrescimo', Decimal('15'), '#059669'),
            ('Alta Demanda 20%', 'acrescimo', Decimal('20'), '#2563eb'),
            ('Alta Demanda 25%', 'acrescimo', Decimal('25'), '#1e3a5f'),
        ]

        for nome, tipo, valor_pct, cor in tags:
            _, criado = TagPreco.objects.get_or_create(
                nome=nome,
                defaults={
                    'tipo':      tipo,
                    'valor_pct': valor_pct,
                    'cor':       cor,
                    'ativo':     True,
                }
            )
            self.stdout.write(f'       {nome}: {"criada" if criado else "já existe"}')            