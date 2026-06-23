# Visão Geral do Projeto

## O que é o Projeto - Sistema Interno MB/SV?

Sistema modular de gestão interna que centraliza múltiplas aplicações em uma única
plataforma com banco de dados unificado. O objetivo é eliminar o uso de planilhas
isoladas e integrar processos como precificação, gestão de produtos e anúncios
em marketplaces em um único lugar.

---

## Por que este projeto existe?

A empresa utilizava planilhas Excel para diversas operações internas — especialmente
para precificação de produtos em marketplaces. Esse processo era manual, propenso
a erros, difícil de manter e impossível de escalar.

A primeira versão do sistema foi desenvolvida rapidamente para **apresentação e
aprovação** da diretoria. Após ser aceita, o projeto entrou em uma nova fase:
desenvolvimento estruturado, com calma, planejamento e qualidade.

---

## O reset — por que recomeçamos do zero?

A primeira versão (`old_dev`) foi construída com foco em velocidade — mostrar
resultado rápido. Isso gerou:

- Código sem comentários
- CSS sem padrão ou variáveis
- Templates HTML desorganizados
- Ausência de testes
- Ausência de documentação
- Decisões técnicas tomadas sem planejamento

Com o projeto aprovado e se tornando algo real, foi necessário recomeçar com
a estrutura correta desde o início. A `old_dev` foi preservada como referência
e a `dev` foi criada do zero.

---

## Como o projeto está sendo desenvolvido?

O desenvolvimento segue os seguintes princípios:

- **Planejamento antes de código** — nenhuma linha é escrita sem entender o porquê
- **Didático** — o desenvolvedor principal precisa entender tudo que está sendo feito
- **Documentação junto com o código** — MkDocs e código caminham juntos
- **Testes antes de avançar** — nada avança sem ser validado
- **Padrões desde o início** — comentários, commits, CSS, HTML seguem convenções definidas

---

## Quem desenvolve?

Projeto individual, desenvolvido pelo analista responsável com suporte de IA (Claude).