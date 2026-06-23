# poetry.lock

## O que é?

Arquivo gerado automaticamente pelo Poetry que registra as versões
**exatas** de todas as dependências instaladas no projeto.

---

## Por que existe?

Garante que todos os ambientes (casa, escritório, produção) instalem
exatamente as mesmas versões das bibliotecas — evitando o problema
de "funciona na minha máquina".

---

## Devo editar esse arquivo?

**Nunca edite manualmente.** O Poetry gerencia esse arquivo automaticamente.

Ele é atualizado quando você roda:
- `poetry add pacote` — adiciona uma dependência
- `poetry remove pacote` — remove uma dependência
- `poetry update` — atualiza as dependências

---

## Devo commitar esse arquivo?

**Sim, sempre.** O `poetry.lock` deve estar no repositório para garantir
que todos os desenvolvedores usem as mesmas versões.