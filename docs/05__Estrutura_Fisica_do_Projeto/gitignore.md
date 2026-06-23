# .gitignore

## O que é?

Arquivo de configuração do Git que define quais arquivos e pastas
**não** devem ser rastreados pelo controle de versão.

---

## Por que existe?

Alguns arquivos não devem ir para o repositório porque:

- Contêm informações sensíveis (senhas, chaves secretas)
- São gerados automaticamente e podem ser recriados
- São específicos de cada máquina e não fazem sentido para outros desenvolvedores

---

## O que está sendo ignorado e por quê?

| Arquivo / Pasta | Motivo |
|---|---|
| `.env` | Contém senhas e chaves secretas — nunca vai para o Git |
| `__pycache__/` | Gerado automaticamente pelo Python — recriado ao rodar o código |
| `*.pyc` | Arquivos compilados do Python — gerados automaticamente |
| `db.sqlite3` | Banco de dados local — cada máquina tem o seu |
| `site/` | Site gerado pelo MkDocs — recriado com `mkdocs build` |
| `.venv/` | Ambiente virtual — recriado com `poetry install` |

---

## Regra importante

Nunca remova o `.env` do `.gitignore`. Se isso acontecer acidentalmente
e o `.env` for commitado, as credenciais do banco estarão expostas
no histórico do Git — mesmo que você delete depois.