# Nomenclatura e Estrutura de Arquivos

## Por que padronizar?

Com o projeto crescendo, sem um padrão claro fica impossível saber onde
está cada arquivo. A padronização garante que qualquer pessoa — ou LLM —
consiga localizar qualquer coisa sem precisar procurar.

---

## Nomenclatura de arquivos

| Tipo | Prefixo | Exemplo |
|---|---|---|
| CSS | `layout_` | `layout_global.css` |
| HTML base | `estrutura_base_` | `estrutura_base_global.html` |
| HTML parcial | `estrutura_parcial_` | `estrutura_parcial_card.html` |
| HTML página | `estrutura_` | `estrutura_home.html` |
| JS | `script_` | `script_global.js` |

---

## Estrutura de pastas

### `static/`

```
static/
├── base_compartilhada/
│   ├── css/
│   │   └── layout_global.css
│   ├── js/
│   │   └── script_global.js
│   └── img/
│       └── logo.png
└── pagina_[nome]/
    ├── css/
    │   └── layout_[nome].css
    └── js/
        └── script_[nome].js
```

### `templates/`

```
templates/
├── base_compartilhada/
│   ├── estrutura_base_global.html
│   └── parciais/
│       └── estrutura_parcial_[nome].html
└── pagina_[nome]/
    ├── estrutura_[nome].html
    └── parciais/
        └── estrutura_parcial_[nome].html
```

---

## Parcial vs Base — qual a diferença?

**Base** — é o esqueleto que outras páginas herdam. Define a estrutura
global (head, sidebar, toolbar). Outras páginas estendem ela com
`{% extends %}`. Existe uma por tipo de layout.

**Parcial** — é um fragmento reutilizável incluído dentro de uma página
com `{% include %}`. Exemplos: um card, uma mensagem de erro, uma tabela.
Pode existir vários por página.

---

## Regras

1. Arquivos compartilhados entre páginas → `base_compartilhada/`
2. Cada página tem sua própria pasta em `static/` e `templates/`
3. Parciais globais → `base_compartilhada/parciais/`
4. Parciais específicas de uma página → `pagina_[nome]/parciais/`
5. Nunca misturar arquivos de páginas diferentes na mesma pasta