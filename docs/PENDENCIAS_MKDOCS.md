# Pendências de Documentação — MkDocs

Lista do que precisa ser documentado futuramente.
Não precisa seguir ordem — só não esquecer.

---

## 05 — Estrutura Física (espelho vivo)

Arquivos novos que precisam de página espelho:

- `core/` — pasta inteira com todos os arquivos
  - `__init__.py`
  - `admin.py`
  - `apps.py`
  - `middleware.py`
  - `models.py`
  - `tests.py`
  - `urls.py`
  - `views.py`
  - `migrations/__init__.py`
  - `management/__init__.py`
  - `management/commands/__init__.py`
  - `management/commands/start.py`
- `static/base_compartilhada/css/layout_global.css`
- `static/base_compartilhada/css/layout_base_grid_card.css`
- `static/base_compartilhada/css/layout_datatables.css`
- `static/base_compartilhada/js/script_global.js`
- `static/base_compartilhada/js/script_datatables.js`
- `static/pagina_home/css/layout_home.css`
- `static/pagina_home/js/home.js`
- `static/pagina_login/css/layout_login.css`
- `static/pagina_precificacao/css/layout_precificacao.css`
- `static/pagina_precificacao/img/` — logos dos marketplaces
- `static/pagina_produtos/css/layout_produtos.css`
- `static/pagina_produtos/js/script_produtos.js`
- `static/pagina_tabela_frete_ml/css/layout_tabela_frete_ml.css`
- `static/pagina_tabela_frete_ml/js/script_tabela_frete_ml.js`
- `templates/base_compartilhada/estrutura_base_global.html`
- `templates/base_compartilhada/estrutura_base_grid_card.html`
- `templates/pagina_home/estrutura_home.html`
- `templates/pagina_login/estrutura_login.html`
- `templates/pagina_mercado_livre/estrutura_mercado_livre.html`
- `templates/pagina_precificacao/estrutura_precificacao.html`
- `templates/pagina_produtos/estrutura_produtos.html`
- `templates/pagina_produtos/parciais/estrutura_parcial_painel_produto.html`
- `templates/pagina_tabela_frete_ml/estrutura_tabela_frete_ml.html`
- `templates/pagina_tabela_frete_ml/parciais/estrutura_parcial_resultado_frete_ml.html`
- `precificacao_marketplaces/` — pasta inteira com todos os arquivos
  - `__init__.py`
  - `admin.py`
  - `apps.py`
  - `models.py`
  - `tests.py`
  - `urls.py`
  - `views.py`
  - `migrations/__init__.py`
  - `management/__init__.py`
  - `management/commands/__init__.py`
  - `management/commands/importar_frete_ml.py`
- `produtos/` — pasta inteira com todos os arquivos
  - `__init__.py`
  - `admin.py`
  - `apps.py`
  - `models.py`
  - `tests.py`
  - `urls.py`
  - `views.py`
  - `migrations/__init__.py`
  - `management/__init__.py`
  - `management/commands/__init__.py`
  - `management/commands/importar_produtos.py`
  - `management/commands/importar_produtos_erp.py`

Atualizar `05__Estrutura_Fisica_do_Projeto/index.md` com a árvore completa.

---

## 03 — Django

### App `core`
App responsável pela base do sistema: login, logout, homepage e middleware de autenticação. Contém o `middleware.py` que verifica a variável `LOGIN_REQUIRED` do `.env` para controlar se o sistema exige autenticação. O management command `start.py` é usado para inicializar o ambiente de desenvolvimento.

### App `precificacao_marketplaces`
App que centraliza tudo relacionado à precificação por marketplace. Contém o model `FreteML` que armazena a tabela de frete do Mercado Livre como uma matriz (cada célula = uma linha no banco: peso_min, peso_max, preco_min, preco_max, valor). O command `importar_frete_ml.py` lê uma planilha Excel e popula o banco via `update_or_create`. A calculadora de frete usa HTMX: POST com peso e preço → Django busca no banco → retorna template parcial com resultado e destaque visual em "L" na tabela.

### App `produtos`
App de catálogo de produtos — espelho do ERP, somente leitura pela interface. O model `Produto` tem dois conjuntos de dados: identificação (EAN como chave única, SKU, cód. fabricante, marca, categoria), financeiro (custo, custo com bonificação), fiscal (NCM, IPI, ICMS, PIS/COFINS, MVA, ST, frete CIF/FOB), dimensões (peso, altura, largura, profundidade) e controle (criado_em no DB, atualizado_em no DB, cadastrado_erp_em, ultima_compra). O campo `peso_cubado` é um `GeneratedField` — calculado automaticamente pelo banco com a fórmula `(altura × largura × profundidade) / 6000`, nunca inserido manualmente. Há dois commands de importação: `importar_produtos.py` lê a planilha de precificação (com custo e dados fiscais) e `importar_produtos_erp.py` lê a planilha do ERP (com dimensões, estoque, marca, categoria). Ambos usam `update_or_create` com EAN como identificador.

### Middleware
O `core/middleware.py` intercepta todas as requisições e verifica se `LOGIN_REQUIRED=True` no `.env`. Se sim, redireciona para login caso o usuário não esteja autenticado. Durante desenvolvimento, `LOGIN_REQUIRED=False` permite acesso sem senha.

### GeneratedField
Campo do Django que delega o cálculo ao banco de dados via SQL. Usado no `peso_cubado` do model `Produto`. Vantagem: sempre consistente, nunca desatualizado. Limitação: somente leitura e só pode usar campos do mesmo model (sem joins). Disponível a partir do Django 5.0.

### Management Commands
Comandos customizados executados via `python manage.py <nome>`. No projeto existem: `importar_frete_ml` (lê planilha de frete e popula FreteML), `importar_produtos` (lê planilha de precificação e popula Produto com dados financeiros e fiscais) e `importar_produtos_erp` (lê planilha do ERP e atualiza Produto com dimensões, estoque e dados de identificação). Todos usam `openpyxl` com `data_only=True` para ler valores calculados de fórmulas, a função `seguro()` para tratar erros de fórmula como `#N/A`, e `update_or_create` para evitar duplicatas.

### Autenticação
Sistema padrão do Django com login e logout. Controlado pelo middleware customizado via variável de ambiente `LOGIN_REQUIRED`. Em desenvolvimento mantém `False` para agilidade. Em produção deve ser `True`.

---

## 04 — Padrões

### Padrão de telas com DataTables
Toda tela de listagem usa DataTables com uma estrutura padrão: o CSS compartilhado fica em `layout_datatables.css` (base_compartilhada), o JS compartilhado em `script_datatables.js` com as funções `inicializar_tabela`, `mudar`, `fnShowHide`, `opcoes_exibicao` e o comparador `pt-string` (ordenação sem acentos). Cada página tem seu próprio `script_[pagina].js` com a chamada `inicializar_tabela` e as colunas específicas. O SearchPanes é ativado via `dom: 'Plfrtip'` e exibe filtros para todas as colunas. A linha de filtros ativos mostra dinamicamente quais filtros estão aplicados no formato `Coluna = Valor`. O painel de colunas visíveis agrupa os botões por categoria (Identificação, Financeiro, Fiscal, Dimensões, Controle).

### Padrão de modal de detalhes via HTMX
Clicar em uma linha da tabela dispara um `hx-get` para um endpoint Django que retorna um template parcial com os dados do registro. O Bootstrap Modal abre com o conteúdo injetado pelo HTMX. Os modais são somente leitura — o ERP é a fonte da verdade e o sistema não permite edição pela interface. Os campos são agrupados por categoria em cards com cabeçalho azul escuro e fundo azul claro.

### Atualizar `comentarios.md`
Adicionar seção sobre tags Django em comentários HTML: usar espaço interno `{ % %}` para evitar que o Django processe as tags dentro de comentários.

---

## Novos arquivos a criar no MkDocs

- `03__Django/apps-e-modulos.md`
- `03__Django/autenticacao.md`
- `03__Django/middleware.md`
- `03__Django/management-commands.md`
- `03__Django/campos-calculados.md`
- `04__Padroes/datatables.md`