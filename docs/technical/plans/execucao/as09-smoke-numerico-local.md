# AS09 — Smoke numérico local (não homologatório)

**Ambiente:** execução local do patch em SciPy/HiGHS (sem Gurobi disponível), em uma única instância `puc-cc9-2p-seed-r1` carregada com o manifesto original. Não é benchmark e não substitui o piloto com Gurobi.

| Modelo | Variáveis | Restrições | LP numérico |
|---|---:|---:|---:|
| U | 5.120 | 1.536 | 1,25 |
| C | 5.696 | 1.568 | 1,25 |
| U+K | 5.120 | 1.603 | 27,026785714285705 |
| C+K | 5.696 | 1.635 | 27,02678571428571 |

A mesma preparação K produziu 67 cortes em cada modelo comparado. Concordância numérica dos quatro LPs e casos pequenos amostrados é **evidência exploratória**, não prova analítica da equivalência de projeções. Nesta instância, C tem **mais variáveis e restrições** que U, consistente com a triagem de regime esparso.

O protótipo não altera históricos N1/N2/FC/AS-08. Validação independente formal ainda é obrigatória para o gate T1.
