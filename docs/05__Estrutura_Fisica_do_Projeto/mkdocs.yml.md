# mkdocs.yml

## O que é?

Arquivo de configuração do MkDocs. Define o nome do site, o tema visual,
a estrutura de navegação e configurações gerais da documentação.

---

## Por que existe?

O MkDocs precisa desse arquivo para saber como construir o site de documentação.
Sem ele, o comando `mkdocs serve` não funciona.

---

## Estrutura do arquivo

| Seção | O que configura |
|---|---|
| `site_name` | Nome exibido no header do site |
| `site_description` | Descrição do site |
| `docs_dir` | Pasta onde estão os arquivos `.md` |
| `dev_addr` | Endereço e porta do servidor local |
| `nav` | Estrutura de navegação do site |
| `theme` | Tema visual, cores, fontes e funcionalidades |
| `extra_css` | Arquivos CSS customizados |

---

## Porta padrão

O MkDocs está configurado para rodar na porta `8001` — diferente do Django
que usa a `8000`. Isso permite rodar os dois ao mesmo tempo sem conflito.

---

## Devo editar esse arquivo?

Sim — sempre que:
- Criar um arquivo `.md` novo que deve aparecer na navegação
- Remover uma página da documentação
- Ajustar o visual ou as configurações do site