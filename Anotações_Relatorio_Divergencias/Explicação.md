# Guia de Leitura do Relatório — Precificação ML

---

## O que é esse relatório

É uma comparação entre **o que a planilha calcula** e **o que o sistema calcula** para cada produto. Cada linha é um produto, e você vê os dois lado a lado para identificar onde e quanto eles divergem.

---

## As colunas de Armazenagem

**Armazenagem Planilha (R$/mês)** e **Armazenagem Dinâmico (R$/mês)**

Esse é o coração do problema. A armazenagem é um custo fixo mensal que o Mercado Livre cobra para guardar o produto no galpão deles. Existem 4 faixas de preço:
- Faixa 1: R$0,21/mês → produtos muito pequenos
- Faixa 2: R$0,45/mês → produtos médios
- Faixa 3: R$1,50/mês → produtos grandes
- Faixa 4: R$3,21/mês → produtos muito grandes

**O problema:** a planilha escolheu uma faixa para cada produto, mas não está claro qual foi a regra usada. O sistema escolhe a faixa pela dimensão do produto (altura × largura × profundidade). Os dois nem sempre concordam.

**Exemplo real:** uma calcanheira pequena (2×9×14cm) está na Faixa 4 (R$3,21) na planilha, mas pelo tamanho do produto deveria ser Faixa 1 (R$0,21). Isso gera uma diferença de R$3,00 por mês no custo, o que impacta diretamente a margem.

**Δ Armazenagem** = a diferença em reais entre as duas. Se for positivo, a planilha está cobrando mais armazenagem que o sistema. Se for negativo, o contrário.

**O que perguntar:** "Como você definiu a faixa de armazenagem para cada produto? Foi pelo tamanho da caixa de embalagem, pelo peso, ou foi manual?"

---

## As colunas de Margem Clássica

**Margem Clássica Real (%)** → o que a planilha mostrou como margem final depois de rodar a macro. Esse é o valor que você vê no Excel.

**Margem Clássica Sistema-Planilha (%)** → o que o sistema calculou usando a armazenagem da planilha. Em teoria deveria ser igual ao Real. Se for diferente, tem algo errado na origem dos dados (custo, fiscal ou outra coisa).

**Margem Clássica Sistema-Dinâmico (%)** → o que o sistema calculou usando a faixa de armazenagem por dimensão do produto. Representa o que o sistema considera correto.

**Δ Clássico vs Planilha** → diferença entre o Real e o Sistema-Planilha. Deveria ser zero. Se não for, indica que algum dado da planilha está com cache antigo (um arquivo externo que não estava disponível quando a planilha calculou).

**Δ Clássico vs Dinâmico** → diferença entre o Real e o Sistema-Dinâmico. Essa é a comparação mais importante para a reunião — mostra o impacto de usar uma faixa de armazenagem diferente da planilha.

---

## As colunas de Margem Premium

Mesma lógica das colunas Clássicas, mas para o anúncio Premium. O preço Premium é sempre o preço Clássico + 8%, arredondado para o próximo centavo 90 (ex: R$122,90).

**Importante:** a margem Premium tende a ser maior que a Clássica porque a comissão do ML no Premium é 17% mas o preço é 8% maior, então sobra mais margem.

---

## As colunas de Frete

**Frete Real** → o frete que aparece na planilha para aquele produto.

**Frete Calculado** → o frete que o sistema calculou pela tabela oficial do ML (peso × preço).

**Δ Frete** → diferença entre os dois. Na grande maioria dos produtos isso é zero — o que significa que a tabela de frete do sistema bate 100% com a planilha. Se aparecer alguma diferença aqui, é raro e pequeno.

---

## As colunas de Dimensão

Altura, largura e profundidade em centímetros. Estão aqui exatamente para a conversa com o criador da planilha — você pode apontar e dizer "esse produto tem essas dimensões, por que você colocou na Faixa 4 sendo que ele é pequeno?"

---

## Por que a planilha e o sistema divergem

São basicamente 3 causas:

**Causa 1 — Faixa de armazenagem diferente**
A mais comum (102 produtos). A planilha escolheu uma faixa, o sistema escolheu outra. Nenhum dos dois está necessariamente errado — a regra simplesmente não está documentada. Isso resolve com uma conversa.

**Causa 2 — Cache de arquivo externo**
A planilha usa fórmulas que buscam dados em outro arquivo (estoque, ICMS, etc.) que não estava disponível quando você rodou a macro. Resultado: alguns valores ficaram travados com dados antigos. Isso afeta 4 produtos e não tem solução sem ter acesso ao arquivo externo original.

**Causa 3 — Arredondamento**
Diferenças de 0,01% a 0,05% que aparecem porque o sistema arredonda em momentos ligeiramente diferentes da planilha. Não tem impacto prático, pode ignorar.

---

## O que levar para a reunião

1. **Mostrar a aba Divergências** e perguntar: "Esses produtos aqui estão com faixas de armazenagem diferentes do que o sistema calcula pelas dimensões. Qual foi o critério usado?"

2. **Mostrar a coluna Δ Armazenagem** e explicar: "Essa diferença em reais aqui impacta diretamente a margem. Se a faixa estiver errada, estamos ou perdendo margem ou precificando errado."

3. **Mostrar a aba Convergências** e dizer: "Esses aqui batem perfeitamente. O sistema está correto para a maioria."

4. **Proposta de solução:** definir formalmente a regra de faixas (por dimensão de produto, por dimensão de embalagem, ou outra), documentar, e o sistema passa a usar essa regra para todos os produtos automaticamente — sem precisar de ajuste manual na planilha.