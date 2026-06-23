# __init__.py

## O que é?

Arquivo Python vazio gerado automaticamente pelo `startproject`.

---

## Por que existe se está vazio?

Em Python, para que uma pasta seja reconhecida como um **módulo**
(ou seja, para que outros arquivos possam importar coisas dela),
ela precisa conter um arquivo chamado `__init__.py`.

Sem ele, o Python não reconhece a pasta `Projeto_Sistema_Interno_MB_SV/`
como um módulo e os imports do Django não funcionam.

---

## Devo editar esse arquivo?

**Não.** Deve permanecer vazio. Sua simples existência já cumpre sua função.