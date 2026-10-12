# AS05 — Interpretação do diagnóstico

**Natureza:** investigação exploratória pós-piloto, sem homologação independente.

**Encaminhamento:** `INVESTIGATE_FURTHER`.

O diagnóstico ainda contém cortes, braços ou políticas censurados

## Perfil dos cortes K

| Instância | Status | Fase dominante | Cortes únicos |
|---|---|---|---:|
| puc-w3c571-seed-r1 | TIMEOUT_PREPARATION | — | — |
| vienna-I056-regiao-f4 | PROFILED | validation_cached_s | 101 |

## Retestes das instâncias censuradas

| Instância | U | U+K | A2+K | Efeito A |
|---|---|---|---|---|
| puc-w3c571-seed-r1 | OPTIMAL_NUMERIC | TIMEOUT_PREPARATION | WORKER_ERROR | NOT_COMPARABLE |
| vienna-I056-regiao-f4 | OPTIMAL_NUMERIC | OPTIMAL_NUMERIC | WORKER_ERROR | NOT_COMPARABLE |

## Políticas de agrupamento (desenvolvimento)

| Instância | Política | Status | Ganho A2 relativo | Custo total A2/U+K |
|---|---|---|---:|---:|
| mapf-room-32-32-4-m10-f8 | reachability_degree | OPTIMAL_NUMERIC | 0.0000% | 1.361× |
| mapf-room-32-32-4-m10-f8 | balanced | OPTIMAL_NUMERIC | -0.0000% | 1.292× |
| mapf-room-32-32-4-m10-f8 | reachability_overlap | OPTIMAL_NUMERIC | 0.3788% | 1.252× |
| puc-bip42p-regiao-f2 | reachability_degree | OPTIMAL_NUMERIC | 0.0000% | 1.039× |
| puc-bip42p-regiao-f2 | balanced | OPTIMAL_NUMERIC | 0.0000% | 1.054× |
| puc-bip42p-regiao-f2 | reachability_overlap | OPTIMAL_NUMERIC | 0.0000% | 1.041× |
| puc-cc9-2p-seed-r1 | reachability_degree | OPTIMAL_NUMERIC | 0.0165% | 1.109× |
| puc-cc9-2p-seed-r1 | balanced | OPTIMAL_NUMERIC | 0.0165% | 1.088× |
| puc-cc9-2p-seed-r1 | reachability_overlap | OPTIMAL_NUMERIC | 0.0481% | 1.078× |
| pucn-cc3-10n-seed-r1 | reachability_degree | OPTIMAL_NUMERIC | 0.0000% | 1.252× |
| pucn-cc3-10n-seed-r1 | balanced | OPTIMAL_NUMERIC | 0.0000% | 1.243× |
| pucn-cc3-10n-seed-r1 | reachability_overlap | OPTIMAL_NUMERIC | 0.0000% | 1.258× |

## Limitações

- Não substitui o gate científico AS05 original
- Políticas novas avaliadas somente no conjunto de desenvolvimento
- Seleção da melhor política após observar resultados é exploratória
- Não reutilizar resultados nos casos de avaliação AS00 sem novo pré-registro
- Retomar reprodutibilidade/independência antes de promoção da AS06
