# settings.py

## O que é?

O arquivo de configuração central do Django. Contém todas as definições
que controlam o comportamento do projeto.

---

## Por que é tão importante?

Pense nele como o "painel de controle" do sistema. Tudo que o Django
precisa saber para funcionar está aqui — banco de dados, apps instalados,
onde ficam os templates, arquivos estáticos, idioma, fuso horário, etc.

---

## Principais configurações

| Configuração | O que define |
|---|---|
| `SECRET_KEY` | Chave usada para assinar cookies e tokens — vem do `.env` |
| `DEBUG` | `True` em desenvolvimento, `False` em produção |
| `ALLOWED_HOSTS` | Domínios que podem acessar o sistema |
| `INSTALLED_APPS` | Lista de todos os apps ativos no projeto |
| `MIDDLEWARE` | Camadas que processam toda requisição e resposta |
| `DATABASES` | Configuração do banco de dados — vem do `.env` |
| `TEMPLATES` | Onde o Django procura os arquivos HTML |
| `STATIC_URL` | URL base para arquivos estáticos (CSS, JS, imagens) |
| `LANGUAGE_CODE` | Idioma do projeto — configurado para `pt-br` |
| `TIME_ZONE` | Fuso horário — configurado para `America/Sao_Paulo` |

---

## Informações sensíveis

Nunca coloque senhas ou chaves diretamente no `settings.py`.
Todas as informações sensíveis vêm do arquivo `.env` via `python-dotenv`.

---

## Devo editar esse arquivo?

**Sim** — sempre que:
- Instalar um novo app Django
- Alterar configurações de banco, templates ou arquivos estáticos
- Adicionar middleware novo