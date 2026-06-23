# urls.py

## O que é?

O arquivo de roteamento principal do Django. Define quais URLs o projeto
reconhece e qual código responde a cada uma delas.

---

## Como funciona?

Quando um usuário acessa uma URL (ex: `/login`), o Django consulta
o `urls.py` para saber qual view (função Python) deve responder.

---

## Estrutura básica

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
]
```

O `urls.py` principal geralmente delega as rotas para os `urls.py`
de cada app — mantendo o arquivo principal limpo e organizado.

---

## Devo editar esse arquivo?

**Sim** — sempre que um novo app for criado e precisar registrar suas rotas.