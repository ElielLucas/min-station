# karpathy-guidelines

Diretrizes comportamentais para reduzir erros comuns de IA ao escrever código, derivadas de observações públicas de Andrej Karpathy sobre armadilhas de LLMs em tarefas de codificação. A skill existe para corrigir um padrão recorrente: agentes que assumem contexto sem perguntar, produzem soluções superdimensionadas ou tocam código além do que foi pedido.

## O que faz

- Orienta o agente a explicitar suposições antes de implementar e perguntar quando houver incerteza ou múltiplas interpretações possíveis.
- Reforça simplicidade: implementar o mínimo necessário, sem abstrações, configurabilidade ou tratamento de erro especulativos.
- Restringe o escopo das alterações ao que foi solicitado — não "melhorar" código adjacente, não refatorar o que não está quebrado, remover apenas órfãos criados pela própria mudança.
- Exige critérios de sucesso verificáveis para cada tarefa (ex.: transformar "corrige o bug" em "escreve um teste que reproduz o bug, depois faz passar"), permitindo que o agente itere sozinho até confirmar o resultado.

## Quando usar

- Ao escrever, revisar ou refatorar código e quiser evitar overengineering.
- Ao precisar de mudanças cirúrgicas, sem efeitos colaterais em código não relacionado.
- Ao definir critérios de sucesso testáveis antes de iniciar uma tarefa.

Não use quando: a tarefa for trivial e o overhead de explicitar suposições/critérios não compensar — nesses casos a skill recomenda usar bom senso em vez de seguir o processo à risca.
