# wsgi.py

## O que é?

Arquivo gerado automaticamente pelo `startproject`. Define o ponto de entrada
**WSGI** (Web Server Gateway Interface) para o projeto.

---

## Para que serve?

É usado quando o projeto é hospedado em um servidor de produção tradicional
como Gunicorn ou uWSGI. O servidor usa esse arquivo para saber como
iniciar a aplicação Django.

---

## Usamos isso agora?

**Não.** Durante o desenvolvimento usamos o `runserver` do Django, que não
depende do `wsgi.py`. Esse arquivo só entra em uso na configuração
de produção.

---

## Devo editar esse arquivo?

**Não por enquanto.** Pode ser configurado no futuro quando o projeto
for para produção.