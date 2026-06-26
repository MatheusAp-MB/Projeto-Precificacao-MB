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
- `static/base_compartilhada/js/script_global.js`
- `static/pagina_home/css/layout_home.css`
- `static/pagina_home/js/home.js`
- `static/pagina_login/css/layout_login.css`
- `static/pagina_precificacao/css/layout_precificacao.css`
- `static/pagina_precificacao/img/` — logos dos marketplaces
- `templates/base_compartilhada/estrutura_base_global.html`
- `templates/base_compartilhada/estrutura_base_grid_card.html`
- `templates/pagina_home/estrutura_home.html`
- `templates/pagina_login/estrutura_login.html`
- `templates/pagina_mercado_livre/estrutura_mercado_livre.html`
- `templates/pagina_precificacao/estrutura_precificacao.html`
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

Atualizar `05__Estrutura_Fisica_do_Projeto/index.md` com a árvore completa.

---

## 03 — Django

- Explicar o que é um app Django e para que serve
- Explicar o app `core` e sua função no projeto
- Explicar o app `precificacao_marketplaces` e sua função no projeto
- Explicar o que é middleware e como funciona
- Explicar o sistema de autenticação do Django
- Explicar o que são management commands e como usar

---

## 04 — Padrões

- Atualizar `comentarios.md` com o detalhe sobre tags Django em comentários HTML

---

## Novos arquivos a criar no MkDocs

- `03__Django/apps-e-modulos.md`
- `03__Django/autenticacao.md`
- `03__Django/middleware.md`
- `03__Django/management-commands.md`