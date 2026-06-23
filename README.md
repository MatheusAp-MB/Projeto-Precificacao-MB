# INSTRUÇÃO PARA A LLM — LEIA ANTES DE QUALQUER COISA

Se você é uma LLM lendo este arquivo:

1. SEMPRE pergunte ao usuário em qual branch estamos trabalhando antes de qualquer ação
2. SEMPRE sincronize o repositório com a branch correta antes de analisar ou gerar código
3. A branch de trabalho atual é a `dev` — mas confirme com o usuário

```
git fetch origin
git checkout dev
git reset --hard origin/dev
```

---

# Projeto — Sistema Interno MB/SV

## O que é este projeto?

Sistema modular de gestão interna que centraliza múltiplas aplicações em uma única
plataforma com banco de dados unificado — eliminando o uso de planilhas isoladas e
integrando processos como precificação, gestão de produtos e anúncios em marketplaces.

> Uma plataforma construída de dentro para fora — pensada por quem usa, para quem usa.
> O Projeto - Sistema Interno MB/SV reúne em um só lugar todas as ferramentas que a
> equipe precisa no dia a dia, com dados sempre atualizados, processos automatizados
> e uma interface que faz sentido.

---

## README vs MkDocs — qual usar?

| | README | MkDocs |
|---|---|---|
| **O que é** | Lista de regras e instruções críticas | Enciclopédia e espelho vivo do projeto |
| **Para que serve** | O que não pode esquecer | Conhecimento, explicações, documentação |
| **Quando consultar** | Antes de começar qualquer sessão | Para entender como algo funciona |

---

## REGRAS QUE NÃO PODEM SER ESQUECIDAS

### MkDocs e o projeto caminham juntos
- Nunca crie um arquivo no projeto sem criar o espelho no MkDocs
- Nunca remova um arquivo do projeto sem remover o espelho no MkDocs
- Nunca crie uma pasta no projeto sem criar a pasta espelho no MkDocs
- Todo commit deve incluir tanto o arquivo do projeto quanto sua documentação no MkDocs

### MkDocs é um espelho vivo do projeto
A pasta `docs/` replica exatamente a estrutura física do projeto no VSCode:
- Cada pasta do projeto → pasta equivalente no `docs/`
- Cada arquivo do projeto → arquivo de documentação equivalente no `docs/`
- O arquivo de documentação explica o que o arquivo real faz
- Não é uma cópia do código — é uma explicação do código

---

## Estrutura de branches

| Branch | Função | Pode mexer? |
|--------|--------|-------------|
| `main` | Produção — código estável e aprovado | Nunca |
| `dev` | Desenvolvimento atual — branch de trabalho | Sempre |
| `old_dev` | Referência — versão anterior do projeto | Só consulta |

### Regras de branch
- Todo desenvolvimento acontece na `dev`
- Nada vai direto para `main` — só via merge após aprovação
- `old_dev` existe para consulta e referência — nunca alterar

---

## Para que serve a `old_dev`?

A `old_dev` contém a primeira versão do projeto — desenvolvida rapidamente para
apresentação e aprovação. Ela serve como:

- Referência de lógica de negócio (cálculos, models, imports)
- Consulta de código que já funcionou
- Base para reescrever com qualidade na `dev`

**Não copie código da `old_dev` sem entender o que está copiando.**

---

## Stack tecnológica

| Tecnologia | Versão | Função |
|-----------|--------|--------|
| Python | 3.12 | Linguagem principal |
| Django | 6.x | Framework web |
| MySQL | 8.x | Banco de dados |
| Poetry | 2.x | Gerenciamento de dependências |
| HTMX | 1.9 | Interatividade sem JavaScript complexo |
| MkDocs Material | — | Documentação do projeto |
| Git | — | Controle de versão |

---

## Ambiente de desenvolvimento

### Configuração inicial (novo PC)

```bash
# 1. Clonar o repositório
git clone https://github.com/MatheusAp-MB/Projeto-Precificacao-MB.git
cd Projeto-Precificacao-MB
git checkout dev

# 2. Instalar dependências
poetry install

# 3. Ativar ambiente virtual
poetry env activate
# copiar e executar o comando retornado

# 4. Criar o arquivo .env na raiz do projeto (ver seção abaixo)

# 5. Criar o banco de dados no MySQL
# No MySQL Workbench:
# CREATE DATABASE precificacao CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 6. Aplicar migrações
python manage.py migrate

# 7. Criar superusuário (primeiro acesso)
python manage.py createsuperuser

# 8. Rodar o servidor
python manage.py runserver
```

### Arquivo .env

Criar na raiz do projeto. **Nunca commitar este arquivo.**

```env
SECRET_KEY=sua-chave-secreta-aqui
DB_NAME=precificacao
DB_USER=root
DB_PASSWORD=sua-senha-mysql
DB_HOST=localhost
DB_PORT=3306
LOGIN_REQUIRED=False
```

> `LOGIN_REQUIRED=False` durante desenvolvimento para não pedir senha a cada acesso.
> Em produção, alterar para `True`.

---

## Convenção de comentários

Ver arquivo `COMMENTS.md` na raiz do projeto.

Cada tipo de arquivo tem sua própria sintaxe de comentário:

| Tipo de arquivo | Sintaxe |
|---|---|
| `.py` | `#` |
| `.html` | `<!-- -->` |
| `.js` | `//` |
| `.css` | `/* */` |
| `.yml` | `#` |
| `.sql` | `--` |

Arquivos `.md` não precisam de comentários.

**Tudo que envolve banco de dados deve ser comentado com atenção especial.**

Tags disponíveis:

```python
# + [STATUS: APROVADO]          → Testado e funcionando
# ! [STATUS: ATENÇÃO]           → Falha, erro ou problema
# ~ [STATUS: EM TESTE]          → Aguardando validação
# # [STATUS: DESENVOLVIMENTO]   → Incompleto, não usar
# * [IMPORTANTE] / [EXPLICAÇÃO] / [RESUMO] → Detalhe crítico ou explicação
```

---

## Módulos do sistema

> Esta seção será atualizada conforme os módulos forem sendo construídos.

| Módulo | Status | Descrição |
|--------|--------|-----------|
| Autenticação | Em construção | Login, logout, controle de acesso |
| Home | Em construção | Painel principal com cards de módulos |
| Precificação ML | Planejado | Cálculo de preço ideal para Mercado Livre |

---

## Convenções de commit

| Prefixo | Quando usar |
|---------|-------------|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `chore:` | Configuração, dependências |
| `docs:` | Documentação |
| `refactor:` | Reorganização sem mudar comportamento |
| `test:` | Testes |
| `style:` | Formatação, CSS, visual |

---

## Notas importantes

- O banco de dados é local em cada máquina — não é compartilhado
- Cada PC precisa do seu próprio `.env`
- O MySQL deve estar rodando antes de iniciar o servidor
- O sistema é desenvolvido e testado em casa em um monitor QHD 27"
- Deve ser testado e aprovado para toda e qualquer resolução de computadores
- Mobile não é necessário considerar

---

*Documento interno — não publicar.*