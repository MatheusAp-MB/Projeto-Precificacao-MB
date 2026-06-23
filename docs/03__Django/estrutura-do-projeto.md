# Estrutura do Projeto Django

## O que é o Django?

Django é um framework web Python de alto nível. Um framework é um conjunto de
ferramentas e convenções prontas que aceleram o desenvolvimento — você não
precisa construir tudo do zero.

O Django já vem com:

- Sistema de autenticação de usuários
- Painel administrativo pronto
- ORM — forma de interagir com o banco de dados usando Python, sem escrever SQL
- Sistema de templates HTML
- Gerenciamento de URLs
- Proteção contra ataques comuns (CSRF, SQL Injection, XSS)

---

## Por que o Django foi escolhido?

- Completo — tem tudo que o projeto precisa nativamente
- Maduro — existe desde 2005, amplamente testado e documentado
- Python — mesma linguagem usada no restante do projeto
- Admin gratuito — painel administrativo pronto sem escrever código

---

## O comando `startproject`

Para iniciar um projeto Django, rodamos:

```bash
django-admin startproject Projeto_Sistema_Interno_MB_SV .
```

O ponto `.` no final instrui o Django a criar os arquivos na pasta atual,
sem criar uma pasta extra desnecessária.

Esse comando é rodado **uma única vez**, no início do projeto.
Ele gera a estrutura base — o esqueleto — sobre o qual todo o sistema é construído.

---

## Visão geral da estrutura gerada

```
Projeto_Sistema_Interno_MB_SV/
    __init__.py
    settings.py
    urls.py
    asgi.py
    wsgi.py
manage.py
```

De forma resumida:

- **`manage.py`** — o controle remoto do Django. Usado para rodar o servidor,
  aplicar migrações, criar usuários, entre outros comandos.
- **`settings.py`** — todas as configurações do projeto em um único arquivo.
- **`urls.py`** — o mapa de rotas. Define qual código responde a cada URL.
- **`asgi.py` e `wsgi.py`** — usados em produção. Ignorados durante desenvolvimento.
- **`__init__.py`** — arquivo vazio que diz ao Python que a pasta é um módulo.

---

## Explicação detalhada de cada arquivo

A descrição completa de cada arquivo gerado — o que faz, por que existe,
e o que não deve ser alterado — está na seção de estrutura física do projeto:

[05 - Estrutura Física do Projeto](../05__Estrutura_Fisica_do_Projeto/index.md)