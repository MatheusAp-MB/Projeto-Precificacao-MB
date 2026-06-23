# Quickstart — Configuração em um PC novo

Guia rápido para colocar o projeto rodando do zero.

---

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

| Ferramenta | Função |
|---|---|
| Python 3.12 | Linguagem do projeto |
| Poetry | Gerenciador de dependências |
| Git | Controle de versão |
| GitHub Desktop | Interface visual do Git |
| VSCode | Editor de código |
| MySQL 8.x | Banco de dados |
| MySQL Workbench | Interface visual do banco |

---

## Passo a passo

**1. Clonar o repositório**

Pelo GitHub Desktop: `File → Clone Repository`
Selecione `Projeto-Precificacao-MB` e escolha a pasta de destino.
Após clonar, mude para a branch `dev`.

---

**2. Instalar as dependências**

No terminal do VSCode:

```bash
poetry install
```

> Esse comando cria o ambiente virtual e instala todas as dependências.
> O passo seguinte mostra como ativá-lo.

**3. Ativar o ambiente virtual**

```bash
poetry env activate
```

Copie e execute o comando retornado. O terminal deve mostrar o nome
do ambiente virtual entre parênteses.

---

**4. Criar o arquivo `.env`**

Na raiz do projeto, crie um arquivo chamado `.env` com o conteúdo:

```env
SECRET_KEY=sua-chave-secreta-aqui
DB_NAME=precificacao
DB_USER=root
DB_PASSWORD=sua-senha-mysql
DB_HOST=localhost
DB_PORT=3306
LOGIN_REQUIRED=False
```

> Este arquivo nunca vai para o Git — cada PC tem o seu próprio.

---

**5. Criar o banco de dados**

No MySQL Workbench, conecte e execute:

```sql
CREATE DATABASE precificacao CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

**6. Aplicar as migrações**

```bash
python manage.py migrate
```

---

**7. Criar o superusuário**

```bash
python manage.py createsuperuser
```

---

**8. Rodar o projeto**

```bash
python manage.py runserver
```

Acesse `http://127.0.0.1:8000` no navegador.

---

## Após a configuração

- Acesse `/admin` para verificar se o banco está conectado
- Popule os dados iniciais pelo admin (Marketplace, TipoAnuncioML, ConfiguracaoLogisticaML)
- Para rodar a documentação: `mkdocs serve` → `http://127.0.0.1:8001`

---

## Uso diário

Quando o projeto já está configurado e você quer apenas rodar:

```bash
python manage.py runserver
mkdocs serve
```

Ou quando o comando `start` estiver implementado:

```bash
python manage.py start
```

> O comando `start` sobe o Django e o MkDocs juntos automaticamente.
> **Status:** planejado — ainda não implementado.

- Acesse a documentação em: `http://127.0.0.1:8001/`

- Acesse o servidor em: `http://127.0.0.1:8000/`
