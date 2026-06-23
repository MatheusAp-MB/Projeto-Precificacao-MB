# Tecnologias do Projeto

## Stack tecnológica

| Tecnologia | Versão | Função |
|---|---|---|
| Python | 3.12 | Linguagem principal do projeto |
| Django | 6.x | Framework web |
| MySQL | 8.x | Banco de dados relacional |
| Poetry | 2.x | Gerenciamento de dependências e ambiente virtual |
| HTMX | 1.9 | Interatividade no frontend sem JavaScript complexo |
| MkDocs Material | — | Documentação do projeto |
| Git | — | Controle de versão |

---

## Por que cada tecnologia foi escolhida?

**Python** — linguagem amplamente usada para sistemas web e automação.
Boa legibilidade e grande ecossistema de bibliotecas.

**Django** — framework completo que já vem com autenticação, painel admin,
ORM para banco de dados e sistema de templates. Evita reinventar a roda.

**MySQL** — banco de dados relacional robusto e amplamente utilizado.
Já estava disponível no ambiente da empresa.

**Poetry** — gerencia as dependências do projeto de forma isolada e reproduzível.
Garante que todos os ambientes (casa, escritório, produção) usem as mesmas versões.

**HTMX** — permite fazer requisições ao servidor e atualizar partes da página
sem recarregar tudo. Substitui JavaScript complexo em muitos casos.

**MkDocs Material** — gera um site de documentação a partir de arquivos Markdown.
Serve como enciclopédia e espelho vivo do projeto.

---

## Dependências do projeto

Todas as dependências estão definidas no `pyproject.toml` e travadas no `poetry.lock`.
Para instalar, basta rodar `poetry install`.

Ver documentação: [pyproject.toml](../05__Estrutura_Fisica_do_Projeto/pyproject.toml.md)