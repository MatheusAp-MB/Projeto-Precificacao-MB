# manage.py

## O que é?

É o **controle remoto** do Django. Um arquivo Python gerado automaticamente
pelo `startproject` que permite executar comandos de gerenciamento do projeto
pelo terminal.

---

## Por que existe?

O Django usa o `manage.py` como ponto de entrada para todos os comandos
administrativos. Sem ele, não é possível rodar o servidor, aplicar
migrações ou criar usuários pelo terminal.

---

## Comandos mais usados

| Comando | O que faz |
|---|---|
| `python manage.py runserver` | Sobe o servidor de desenvolvimento |
| `python manage.py migrate` | Aplica migrações pendentes no banco |
| `python manage.py makemigrations` | Gera arquivos de migração a partir dos models |
| `python manage.py createsuperuser` | Cria um usuário administrador |
| `python manage.py shell` | Abre o terminal interativo do Django |

---

## Devo editar esse arquivo?

**Não.** O `manage.py` não deve ser editado. Ele é gerado pelo Django
e não faz parte da lógica do projeto.

A única exceção é quando criamos **comandos de gestão customizados** —
mas esses ficam em `app/management/commands/`, não no `manage.py`.