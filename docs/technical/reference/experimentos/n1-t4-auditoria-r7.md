# N1-T4 — Auditoria dos pools R7 gravados

**Data:** 2026-10-07. **Status:** `COMPUTATIONALLY VERIFIED` para os 610 registros auditados. **Sem geração de novos pools.**

**Código reexecutável:** `python experiments/benchmark/audit_r7_n1.py` (somente biblioteca padrão Python; não requer Gurobi). Entradas: `results/benchmark/r7-plato.csv` e os cinco arquivos de instância congelados referenciados no script. `run_r7_plato.py`, `r7-plato.csv` e `r7-plato-resumo.csv` continuam inalterados.

## Métricas com significados distintos

- `z_freq_retorno`: número de linhas em que o oráculo **retornou** aquele mesmo `Z`.
- `z_n_instalacoes_cortadas`: número de instalações **gravadas** `C` do mesmo pool com `C∩Z=∅`, mesmo que o oráculo tenha retornado outro `Z` naquela linha. Instalações são contadas para **todos** os Z que violam.
- `n_origens_grau_zero`: número de origens sem destino incidente no grafo bipartido `B_C`.
- `n_origens_nao_emparelhadas`: `m−|M|`, para `M` um emparelhamento máximo; independente da escolha de `M`.
- `hall_deficit`: `|X|−|N(X)|` para o conjunto `X` recuperado por caminhos alternantes a partir das origens não emparelhadas. Não é o máximo de déficit entre todos os `X`: registra **uma testemunha válida**.

## Resultados recalculados

| Instância | C gravados | Truncado? | Máxima frequência | Máxima cobertura | Divergência oráculo × matching |
|---|---:|---|---:|---:|---:|
| TR-k2-L5-r2 | 8 | não | 2 | 2 | 0 |
| BP-não-[3,1]-q2 | 2 | não | 1 | 1 | 0 |
| mapf-maze-32-32-2-m10-f4 | 200 | sim | 49 | 49 | 0 |
| lin-lin03-regiao-f4 | 200 | sim | 17 | 17 | 0 |
| puc-cc9-2p-seed-r1 | 200 | sim | **21** | **27** | 0 |

A reprodução do máximo histórico de frequência 21 e a cobertura independente 27 em cc9 são os testes de regressão obrigatórios da N1. Frequência e cobertura coincidirem em outros quatro pools **não as torna a mesma métrica**.

## Classificação por obstrução, sem inferência causal indevida

Regra determinística exclusiva para cada `C` inviável: se alguma origem tem grau zero em `B_C`, classificar `sem_alcance_individual`; se não e o matching máximo é deficiente, classificar `deficiencia_Hall_sem_grau_zero`; na ausência de déficit mas com oráculo inviável, `inexplicado` e registrar discordância. `viavel` é controle fora das categorias de inviabilidade. O fato de `H[C]` ter várias componentes **não** é por si uma classe de inviabilidade, nem autoriza corte global de conectividade.

- TR: 2 viáveis, 6 inviáveis por ausência de alcance individual.
- BP: 2 inviáveis **sem origem de grau zero**, com deficiência de Hall. É um testemunho estrutural diferente de isolamento individual.
- Maze: 199 inviáveis por grau zero; 1 com Hall sem grau zero.
- Lin e cc9: 200 inviáveis cada por origem de grau zero.

`H-desc` do relatório antigo simplesmente implementa a caracterização de viabilidade por emparelhamento em `B_C`; sua confirmação não prova a causa individual da inviabilidade. Um conjunto Hall-deficiente identifica uma obstrução **daquela instalação**, não uma desigualdade global válida em `y`.

## Artefatos e limites

- `results/benchmark/n1-r7-cortes-corrigidos.csv`: uma linha por Z distinto em cada pool.
- `results/benchmark/n1-r7-testemunhas-hall.csv`: uma linha por instalação gravada, com os dois números separados e testemunha.
- `results/benchmark/n1-r7-auditoria-resumo.csv`: auditoria cruzada por instância.

Os pools de maze, lin e cc9 foram truncados em 200; suas taxas não estimam o platô completo. Os dados auditados não demonstram automaticamente uma nova família de cortes, força de LP ou vantagem de método. A classificação vale apenas para essas instalações e a caracterização de matching nelas reconstruída.
