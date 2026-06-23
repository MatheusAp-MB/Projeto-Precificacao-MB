# Convenção de Commits

## O que é Conventional Commits?

É um padrão de escrita para mensagens de commit. Define uma estrutura
clara e consistente que facilita entender o histórico do projeto sem
precisar abrir cada arquivo alterado.

---

## Formato

```
tipo: descrição curta do que foi feito

- detalhe 1
- detalhe 2
- detalhe 3
```

---

## Prefixos disponíveis

| Prefixo | Quando usar |
|---|---|
| `feat:` | Nova funcionalidade adicionada |
| `fix:` | Correção de bug ou comportamento errado |
| `chore:` | Configuração, dependências, manutenção |
| `docs:` | Documentação — MkDocs, README, COMMENTS |
| `refactor:` | Reorganização de código sem mudar comportamento |
| `test:` | Adição ou correção de testes |
| `style:` | Formatação, CSS, ajustes visuais sem mudar lógica |

---

## Exemplos

### Bom
```
feat: tela de login com autenticação Django

- Template login.html com campos usuário e senha
- View de login integrada ao sistema de auth do Django
- Redirecionamento para home após login bem sucedido
- Middleware de proteção ativado via LOGIN_REQUIRED no .env
```

```
fix: correção do cálculo de margem com valores zerados

- Adicionado tratamento para custo_com_boni nulo
- Substituído por custo_bruto quando não informado
```

### Ruim
```
ajustes
```
```
correções diversas
```
```
wip
```

---

## Regras do projeto

1. **Todo commit tem título e descrição** — nunca só o título
2. **A LLM sempre gera o título e descrição** antes de pedir o commit
3. **Título em português** — claro e objetivo
4. **Descrição em tópicos** — o que foi feito, não o que foi alterado
5. **Um commit por assunto** — não misturar funcionalidades diferentes

---

## Por que isso importa?

O histórico de commits junto com o MkDocs é o que permite que uma LLM
entenda o contexto do projeto em sessões futuras. Um commit bem descrito
poupa tempo de explicação e evita retrabalho.