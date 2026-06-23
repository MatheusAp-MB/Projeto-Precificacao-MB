# Git, GitHub e GitHub Desktop

## O que é cada um?

Esses três nomes se referem a coisas diferentes, mas que trabalham juntas:

**Git** — é o sistema de controle de versão. Ele roda localmente na sua máquina
e registra todo o histórico de alterações do projeto. Pense nele como uma
"máquina do tempo" do código — você pode voltar a qualquer ponto do histórico.

**GitHub** — é o serviço online onde o repositório fica armazenado na nuvem.
Serve como backup e como ponto central para sincronizar o projeto entre
diferentes máquinas (casa e escritório, por exemplo).

**GitHub Desktop** — é a interface visual para usar o Git sem precisar de
comandos no terminal. Neste projeto, **todo commit, push e gerenciamento de
branches é feito pelo GitHub Desktop**, exceto em situações específicas que
exigem comandos avançados no terminal.

---

## As branches do projeto

Uma branch é como uma "versão paralela" do projeto. Mudanças feitas em uma
branch não afetam as outras — até que você decida unificá-las.

| Branch | Função | Pode mexer? |
|---|---|---|
| `main` | Produção — código estável e aprovado | Nunca diretamente |
| `dev` | Desenvolvimento atual — branch de trabalho | Sempre |
| `old_dev` | Referência — versão anterior do projeto | Nunca — só consulta |

---

## Por que cada branch existe?

**`main`** — é a branch de produção. Só recebe código quando algo está
completamente testado e aprovado. Nada vai direto para ela — sempre
via merge da `dev`.

**`dev`** — é onde todo o desenvolvimento acontece. É a branch do dia a dia.
Todo commit novo vai para cá.

**`old_dev`** — foi criada quando o projeto foi reiniciado do zero. Ela preserva
a primeira versão do sistema — desenvolvida rapidamente para apresentação
e aprovação. Serve como referência de lógica de negócio e código que
já funcionou. **Nunca deve ser alterada.**

---

## Por que o projeto foi reiniciado?

A primeira versão (`old_dev`) foi construída com foco em velocidade.
Com o projeto aprovado e se tornando algo real, foi necessário recomeçar
com estrutura, padrões e qualidade desde o início.

A `dev` foi criada do zero — completamente limpa, sem histórico da versão anterior.

---

## Fluxo correto de trabalho

```
1. Sempre trabalhar na branch dev
2. Commitar pelo GitHub Desktop com título e descrição claros
3. Push para o GitHub após cada commit
4. Nunca commitar diretamente na main
5. Consultar a old_dev apenas como referência — nunca alterar
```

---

## Convenção de commits

Seguimos o padrão **Conventional Commits**:

| Prefixo | Quando usar |
|---|---|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `chore:` | Configuração, dependências |
| `docs:` | Documentação |
| `refactor:` | Reorganização sem mudar comportamento |
| `test:` | Testes |
| `style:` | Formatação, CSS, visual |