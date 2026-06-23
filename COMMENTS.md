# Convenção de Comentários — Projeto Sistema Interno MB/SV

Este documento define o padrão de comentários adotado em todo o projeto.
Utiliza a extensão **Better Comments** no VSCode para colorização automática.

---

## Formato padrão

```
[símbolo de comentário da linguagem][símbolo de cor][TAG] → [Mensagem]
```

---

## Tags disponíveis

| Símbolo | Tag | Cor | Quando usar |
|---|---|---|---|
| `+` | `[STATUS: APROVADO]` | Verde | Código testado e funcionando corretamente |
| `!` | `[STATUS: ATENÇÃO]` | Vermelho | Falha, erro, problema identificado ou risco |
| `~` | `[STATUS: EM TESTE]` | Amarelo | Implementado, aguardando validação |
| `#` | `[STATUS: DESENVOLVIMENTO]` | Laranja | Incompleto, não usar em produção |
| `*` | `[IMPORTANTE]` / `[EXPLICAÇÃO]` / `[RESUMO]` | Azul claro | Detalhe crítico, explicação ou visão geral |

---

## Sintaxe por tipo de arquivo

Cada linguagem tem seu próprio símbolo de comentário.
As tags são sempre as mesmas — só o símbolo muda.

| Tipo de arquivo | Sintaxe | Exemplo |
|---|---|---|
| `.py` | `#` | `# * [RESUMO] → Este arquivo faz...` |
| `.html` | `<!-- -->` | `<!-- * [EXPLICAÇÃO] → Este bloco faz... -->` |
| `.js` | `//` | `// ! [STATUS: ATENÇÃO] → Cuidado com...` |
| `.css` | `/* */` | `/* * [RESUMO] → Estilos da página... */` |
| `.yml` | `#` | `# * [IMPORTANTE] → Não alterar...` |
| `.sql` | `--` | `-- * [EXPLICAÇÃO] → Esta query faz...` |

**Arquivos `.md` não precisam de comentários** — eles já são explicações em si.

---

## Atenção especial — Banco de dados

Tudo que envolve banco de dados deve ser **muito bem comentado e explicado**.
Isso inclui:

- `models.py` — onde definimos a estrutura das tabelas
- `migrations/` — arquivos gerados pelo Django que alteram o banco
- Qualquer view ou função que consulte o banco (`filter`, `get`, `annotate`, etc.)
- `admin.py` — onde registramos os models para o painel administrativo
- Arquivos `.sql` externos

**Regra:** se envolve banco de dados, comente mais do que acha necessário.

---

## Exemplos de uso

### Python
```python
# * [RESUMO] → Este arquivo contém as funções de cálculo de preço ideal ML.

# * [EXPLICAÇÃO] → A função abaixo usa iteração para convergir o frete,
#                  pois o frete depende do preço e o preço depende do frete.

# + [STATUS: APROVADO] → Testado e aprovado o cálculo de preço ideal ML
# ! [STATUS: ATENÇÃO] → Não funciona com valores negativos de custo
# ~ [STATUS: EM TESTE] → Testando integração com a tabela de fretes
# # [STATUS: DESENVOLVIMENTO] → Módulo Amazon — incompleto, não usar
```

### Banco de dados
```python
# * [EXPLICAÇÃO] → Busca todos os produtos ativos ordenados por título.
#                  O filter(ativo=True) garante que produtos inativos
#                  não apareçam para o usuário.
produtos = Produto.objects.filter(ativo=True).order_by('titulo')

# * [IMPORTANTE] → O select_related('marketplace') evita N+1 queries.
#                  Sem ele, o Django faria uma query extra para cada anúncio.
anuncios = Anuncio.objects.select_related('marketplace').all()
```

### HTML
```html
<!-- * [RESUMO] → Template base do painel administrativo -->
<!-- * [EXPLICAÇÃO] → Este bloco define a navbar lateral -->
<!-- ! [STATUS: ATENÇÃO] → Não remover — usado por todos os templates filhos -->
```

### CSS
```css
/* * [RESUMO] → Estilos globais da tela de precificação ML */
/* * [IMPORTANTE] → As variáveis de cor estão definidas no :root */
```

### JavaScript
```javascript
// * [RESUMO] → Funções de controle do painel de edição de produtos
// * [EXPLICAÇÃO] → Esta função recalcula o preço em tempo real via HTMX
// ! [STATUS: ATENÇÃO] → Depende do csrftoken nos cookies
```

---

## Ciclo de vida de um código

```
[STATUS: DESENVOLVIMENTO] → em construção
          ↓
[STATUS: EM TESTE]        → implementado, sendo validado
          ↓
[STATUS: APROVADO]        → testado, funcionando, pronto para produção
```

Se um código aprovado apresentar problema:
```
[APROVADO] → [ATENÇÃO] → corrigir → [EM TESTE] → [APROVADO]
```

---

## Regras do projeto

1. Arquivos `.md` não precisam de comentários
2. Todo arquivo de código começa com um `[RESUMO]` no topo
3. Toda função tem pelo menos um `[EXPLICAÇÃO]`
4. Todo bloco com problema recebe `[STATUS: ATENÇÃO]`
5. Tudo que envolve banco de dados recebe comentário extra detalhado
6. Nunca poupar comentários — código sem comentário não existe neste projeto

---

*Documento interno — não publicar.*