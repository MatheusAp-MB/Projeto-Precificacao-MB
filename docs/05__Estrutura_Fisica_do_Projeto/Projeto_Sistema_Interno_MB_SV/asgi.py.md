# asgi.py

## O que é?

Arquivo gerado automaticamente pelo `startproject`. Define o ponto de entrada
**ASGI** (Asynchronous Server Gateway Interface) para o projeto.

---

## Para que serve?

É usado quando o projeto é hospedado em um servidor de produção que suporta
comunicação assíncrona — como WebSockets e requisições em tempo real.

---

## Usamos isso agora?

**Não.** Durante o desenvolvimento usamos o `runserver` do Django, que não
depende do `asgi.py`. Esse arquivo só entra em uso na configuração
de produção com servidores como Daphne ou Uvicorn.

---

## Devo editar esse arquivo?

**Não por enquanto.** Pode ser configurado no futuro quando o projeto
for para produção.