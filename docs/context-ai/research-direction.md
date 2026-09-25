---
type: context-ai
file: research-direction
title: "MIN-STATION — Direção da Pesquisa em Otimização"
---

# MIN-STATION — Direção da Pesquisa em Otimização

## 1. Papel deste arquivo

Este documento orienta agentes de IA sobre **como pensar novas contribuições** para o projeto sem confundir o baseline atual com o objetivo final da pesquisa.

## 2. Pergunta central

A pergunta ampla do projeto é:

> Como resolver o MIN-STATION de forma exata ou com melhores garantias computacionais por meio de formulações de PLI e técnicas de otimização que explorem a estrutura do problema?

A formulação base atual é apenas um ponto de referência para essa investigação.

## 3. Tipos de contribuição válidos

Uma nova contribuição pode atuar em uma ou mais dimensões:

- nova formulação matemática;
- reformulação equivalente mais forte ou compacta;
- fortalecimento da relaxação linear;
- desigualdades válidas e cortes;
- pré-processamento e redução de instâncias;
- decomposição do problema;
- relaxações estruturadas;
- estratégias específicas de branching ou integração com branch-and-cut;
- procedimentos híbridos que preservem a correção do método exato;
- análise computacional que explique por que determinada abordagem funciona ou falha.

Não assumir que uma técnica conhecida será automaticamente superior. O projeto é experimental e comparativo.

## 4. Regra de comparação com o baseline

Toda abordagem nova deve deixar claro:

1. qual problema está resolvendo;
2. se é equivalente ao baseline em termos de soluções viáveis e objetivo;
3. quais variáveis e restrições foram adicionadas, removidas ou substituídas;
4. qual efeito esperado sobre a relaxação ou a árvore de busca;
5. qual custo adicional de pré-processamento ou separação;
6. em quais instâncias foi comparada;
7. quais métricas sustentam a conclusão.

## 5. Resultados negativos

Tentativas que não melhoram desempenho não devem ser apagadas ou descritas como fracasso sem análise.

Quando uma abordagem for pior, registrar quando possível:

- onde o tempo é consumido;
- se o limite dual melhora ou piora;
- se o modelo cresce excessivamente;
- se há degenerescência ou simetria;
- se a técnica ajuda apenas em determinadas famílias de instâncias;
- se a implementação ou a ideia estrutural é a provável causa.

Esse histórico evita repetir experimentos sem aprendizado acumulado.

## 6. Cuidado com variantes

Não confundir avanço algorítmico com mudança do problema.

Adicionar custos heterogêneos, autonomias distintas ou elegibilidade origem-destino altera a variante estudada. Essas extensões podem ser interessantes, mas devem ser tratadas separadamente de técnicas destinadas a resolver melhor o MIN-STATION base.
