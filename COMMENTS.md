# Convenção de Comentários — Projeto Precificação MB

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

## Exemplos de uso

### Status simples
```python
# + [STATUS: APROVADO] → Testado e aprovado o cálculo de preço ideal ML
# ! [STATUS: ATENÇÃO] → Não funciona com valores negativos de custo
# ~ [STATUS: EM TESTE] → Testando integração com a tabela de fretes
# # [STATUS: DESENVOLVIMENTO] → Módulo Amazon — incompleto, não usar
```

### Explicações e resumos
```python
# * [RESUMO] → Este arquivo contém as funções de cálculo de preço ideal ML.
#              Todas as funções recebem valores simples (float/int),
#              sem dependência de models do Django.

# * [EXPLICAÇÃO] → A função abaixo usa iteração para convergir o frete,
#                  pois o frete depende do preço e o preço depende do frete.

# * [IMPORTANTE] → Não alterar a ordem dos parâmetros — outros módulos dependem disso.
```

### Combinações
```python
# ~ [STATUS: EM TESTE] → Testando a view calcular_produto_ml
# * [EXPLICAÇÃO] → Recebe os campos do painel via POST e recalcula em tempo real

# ! [STATUS: ATENÇÃO] → O campo custo_com_boni chega com vírgula do frontend
# * [IMPORTANTE] → Usar .replace(',', '.') antes de converter para float
```

---

## Regras do projeto

1. **Nunca poupar comentários** — código sem comentário não existe neste projeto
2. **Todo arquivo começa com** `# * [RESUMO]` descrevendo seu propósito
3. **Toda função/método tem** pelo menos um `# * [EXPLICAÇÃO]`
4. **Todo bloco com problema** recebe `# ! [STATUS: ATENÇÃO]`
5. **Código em desenvolvimento** recebe `# # [STATUS: DESENVOLVIMENTO]` até ser aprovado
6. **Após teste e aprovação** o status muda para `# + [STATUS: APROVADO]`

---

## Ciclo de vida de um código

```
# # [STATUS: DESENVOLVIMENTO]  →  em construção
         ↓
# ~ [STATUS: EM TESTE]         →  implementado, sendo validado
         ↓
# + [STATUS: APROVADO]         →  testado, funcionando, pronto para produção
```

Se um código aprovado apresentar problema:
```
# + [STATUS: APROVADO]  →  # ! [STATUS: ATENÇÃO]  →  corrigir  →  # ~ [STATUS: EM TESTE]  →  # + [STATUS: APROVADO]
```

---

*Documento criado em Junho/2026 — seguir rigorosamente em todo o projeto.*
