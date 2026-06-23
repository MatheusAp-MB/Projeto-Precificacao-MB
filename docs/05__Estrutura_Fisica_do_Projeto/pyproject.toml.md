# pyproject.toml

## O que é?

Arquivo de configuração do Poetry. Define as dependências do projeto,
a versão do Python exigida e metadados gerais.

---

## Por que existe?

É o arquivo principal de configuração do ambiente Python do projeto.
O Poetry usa ele para saber quais pacotes instalar e em quais versões.

---

## Estrutura do arquivo

| Seção | O que define |
|---|---|
| `[tool.poetry]` | Nome, versão e descrição do projeto |
| `[tool.poetry.dependencies]` | Dependências de produção |
| `[tool.poetry.group.dev.dependencies]` | Dependências só de desenvolvimento |
| `[build-system]` | Como o Poetry deve construir o projeto |

---

## Dependências de produção vs desenvolvimento

**Produção** — vão para o servidor. Exemplo: `django`, `mysqlclient`.

**Desenvolvimento** — só na máquina local. Exemplo: `pytest`, `mkdocs-material`.

---

## Como adicionar uma dependência?

```bash
poetry add nome-do-pacote          # produção
poetry add --group dev nome-do-pacote  # desenvolvimento
```

**Nunca use `pip install` diretamente** — use sempre o Poetry para
manter o `pyproject.toml` e o `poetry.lock` atualizados.