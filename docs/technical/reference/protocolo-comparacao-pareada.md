# Protocolo de comparação pareada

**Data:** 2026-10-03
**Orçamento:** a decisão de `docs/technical/reference/decisao-orcamento-worklimit.md`. Comparação de métodos usa `WorkLimit`. Lote com prazo de parede usa `TimeLimit`. Os dois não se misturam no mesmo veredito.

Este protocolo vale para experimento confirmatório. Um piloto pode explorar configuração; o relatório desse piloto não fecha veredito de método.

`PYTHONHASHSEED` continua como proteção extra nos runners que já a fixam. O mecanismo de ordem estável é a ordenação dos cortes e dos vértices (T6), não a semente de hash.

## Checklist

Antes de comparar um braço de controle com um braço experimental:

1. Declarar a variável experimental e o controle. Um fator muda. O resto da configuração é o mesmo: formulação, família de cortes, instância, hash da instância, commit, versão do gerador de cortes, seed, threads e orçamento.
2. Se dois fatores mudam ao mesmo tempo, ou existe um braço que isola cada um, ou o relatório declara que o efeito medido é conjunto e não atribui o resultado a um fator só.
3. Se o veredito depende de uma margem de 1 ou 2 estações, usar pelo menos 3 seeds. Uma seed não fecha esse veredito.
4. Se o veredito é sobre a busca (nós, incumbente, bound ao longo da árvore), registrar `NodeCount`. O campo já sai de `measure_mip`. Tempo de primeiro incumbente, melhor incumbente e prova saem quando `coletar_incumbente=True`.
5. O orçamento é o mesmo nos dois braços, no sentido da decisão de orçamento: `WorkLimit` igual na comparação de métodos, ou `TimeLimit` igual no lote de parede. Não comparar um braço por trabalho com outro por parede.
6. Cada braço registra hash da instância, versão da família de cortes, commit, seed, threads e a fonte do certificado (solver, método ou prova).

## Retrospectiva do E13

`run_e13.py` tem um braço `focus600`: `MIPFocus=1` com o mesmo `TimeLimit` de 600 s do controle. Esse braço isola a ênfase.

A fase longa (`fase_longo`, linhas 164–166) muda dois fatores juntos: `TimeLimit` passa de 600 s para 1800 s e `MIPFocus=1` continua ligado. Não há braço com 1800 s e `MIPFocus` padrão.

O checklist acima barra um veredito que atribua o efeito dessa fase só ao prazo ou só à ênfase. O efeito, se for citado, é conjunto. O relatório `resultados-e13-pli.md` §5 registra essa ressalva. Nenhum `run_e*.py` histórico foi reescrito por este protocolo.
