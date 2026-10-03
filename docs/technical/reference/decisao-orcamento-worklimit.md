# Decisão de orçamento: `TimeLimit` e `WorkLimit`

**Data:** 2026-10-03
**Solver:** Gurobi 12.0.3
**Fonte da semântica:** [Parameter Reference, WorkLimit](https://docs.gurobi.com/projects/optimizer/en/12.0/reference/parameters.html), página da versão 12.0 consultada em 2026-10-03. Não é paráfrase de memória.

## O que `WorkLimit` mede

Parâmetro `double`, padrão infinito, mínimo 0. Limita o trabalho total em unidades de trabalho. Se o limite é ultrapassado, a otimização retorna status `WORK_LIMIT` (código 16 nesta instalação).

A documentação contrasta com `TimeLimit`: o limite de trabalho é determinístico. No mesmo hardware, com os mesmos parâmetros e atributos, a otimização de um modelo para no mesmo ponto. Uma unidade de trabalho corresponde, de forma muito aproximada, a um segundo em uma thread, e essa correspondência depende do hardware e do modelo.

A parada não é imediata. O solver espera um estado determinístico e ainda calcula os atributos da otimização interrompida. Por isso o atributo `Work` pode ficar acima do `WorkLimit` pedido. Repetir a otimização com `WorkLimit` igual ao `Work` observado pode executar trabalho adicional.

O parâmetro vale para otimização em geral. Os pontos de callback em que ele pode ser alterado incluem `SIMPLEX` e `BARRIER`, além de `MIP`. Nesta instalação, um LP contínuo da formulação base em `hc9u.txt` com `WorkLimit = 0.05` parou com status 16 e `Work = 0.050`. O limite se aplica ao LP, não só ao MIP.

## Experimento

Script: `experiments/cuts/verify_t7_orcamento.py`.

Duas instâncias, tamanhos diferentes: `hc9u.txt` (n = 512) e `mapf-empty-32-32-m25-f4.txt` (n = 1024). Formulação base, fluxo inteiro, sem cortes a priori. Seed 42, `Threads = 1`, `Heuristics = 0`, `Cuts = 0`, `Presolve = 0` (sem isso as duas fecham ou ficam na raiz antes de a busca ramificar). A carga são processos ocupando os núcleos da máquina; o solver continua com uma thread.

O `WorkLimit` de cada instância é o `Work` medido na corrida `TimeLimit = 3 s` sem carga. `TimeLimit` nessas corridas de trabalho fica em infinito.

| Condição | Instância | Status | Nós | Work | Parede (s) |
|---|---|---:|---:|---:|---:|
| TimeLimit sozinho | hc9u | 9 | 265 | 0,639 | 3,001 |
| TimeLimit com carga | hc9u | 9 | 107 | 0,329 | 3,001 |
| WorkLimit sozinho | hc9u | 16 | 265 | 0,639 | 2,679 |
| WorkLimit com carga | hc9u | 16 | 265 | 0,639 | 5,432 |
| TimeLimit sozinho | mapf-empty-32-32-m25-f4 | 9 | 1 | 0,854 | 3,003 |
| TimeLimit com carga | mapf-empty-32-32-m25-f4 | 9 | 1 | 0,427 | 3,005 |
| WorkLimit sozinho | mapf-empty-32-32-m25-f4 | 16 | 1 | 0,854 | 3,273 |
| WorkLimit com carga | mapf-empty-32-32-m25-f4 | 16 | 1 | 0,854 | 4,041 |

Status 9 é `TIME_LIMIT`. Status 16 é `WORK_LIMIT`.

Em `hc9u`, o mesmo `TimeLimit` de 3 s passou de 265 nós sem carga para 107 nós com carga. O mesmo `WorkLimit` manteve 265 nós e o mesmo `Work`; o tempo de parede passou de 2,679 s para 5,432 s. Em `mapf-empty`, a busca não saiu do nó raiz, então `NodeCount` não se move; o `Work` sob `TimeLimit` caiu de 0,854 para 0,427, e sob `WorkLimit` o trabalho ficou em 0,854 com parede maior.

Nesta execução, fixar `WorkLimit` no `Work` da corrida interrompida por tempo não produziu o trabalho extra que a documentação admite como possível. Isso é observação deste par de modelos, não garantia geral.

## Decisão

Os dois limites ficam, para propósitos diferentes.

- **Comparação de métodos**, quando a pergunta é o esforço de busca (`NodeCount`, bound, incumbente no mesmo ponto da árvore): `WorkLimit`. O experimento mostra que `TimeLimit` muda nós e trabalho quando a máquina está carregada, e `WorkLimit` não.
- **Lote com prazo de parede** (bateria noturna, fatia com horário de término): `TimeLimit`. Ele limita o relógio. `NodeCount` e `Work` dessa corrida não são comparáveis com outra máquina ou com a mesma máquina sob carga diferente.

Nenhum runner existente (`harness.py`, `bc_yspace.py`, `run_e*.py`) foi migrado para `WorkLimit` nesta decisão. Os experimentos já publicados continuam no orçamento com que foram executados. Um experimento novo que compare métodos declara o limite no protocolo pareado.
