# AS16 — Resultado da campanha LP pareada COMP, K e H2

**Data da campanha:** 15/10/2026  
**Resultado produzido pelo analisador:** `INVESTIGATE` (preservado, **sem reclassificar**).  
**Decisão de pesquisa após inspeção dos dados:** **STOP — não promover H2 a COMP+K nem priorizar novas rodadas H2 dentro desta linha**.  
**Natureza da decisão:** encerramento por insuficiência de benefício observado, **não** prova de dominância matemática de K sobre H2 nem resultado `STOP` emitido pelo gate automático.  
**Commit de origem da execução:** `03431cf8cceafa20de354a160008c8fb84d4b54e` (informado no manifesto; conferir na máquina de execução).  
**Pré-registro SHA-256:** `4056fd08244a15085367a60a0c71fbfc3f44fc2d2f0a7686fdd31063b1de2dfe` (valor reportado pelo manifesto).  
**Evidências:** `results/benchmark/as16-lp-h2-001/` (`manifest.json`, `rows.json`, `analysis.json` e cinco arquivos de pool).

## Configuração e proveniência

- 6 instâncias de desenvolvimento em 6 grafos brutos identificados separadamente; 4 braços principais (`U`, `U_K`, `U_H2`, `U_K_H2`) e 2 controles de pool fixo (`U_FIXED_H2`, `U_K_FIXED_H2`): **36 registros**.
- Gurobi disponível na execução (`manifest.json`); limite de **90 segundos totais de parede por braço**, até 4 threads, seed 42, `Method=1`, `NumericFocus=1` e política de solver no manifesto.
- Os controles de pool são **post hoc**, válidos como diagnóstico em desenvolvimento, não como avaliação out-of-sample.
- Registro de testes informado pelo executor: `poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q` → **106 testes, OK**. Os testes não substituem revisão científica independente.

## Resultados LP e custo total

Os objetivos são limites inferiores da relaxação de um problema de minimização: valores maiores são melhores. Apresentam-se tempos *wall-clock* totais para comparação pareada (incluem preparação, seleção e certificação quando aplicáveis), não só tempo do solver. Censuras não são ótimos.

| Instância | U LB | U+K LB | U+H2 LB | U+K+H2 LB | U+K tempo | U+K+H2 tempo |
|---|---:|---:|---:|---:|---:|---:|
| `mapf-room-32-32-4-m10-f8` | 2.40000 | 13.20000 | 4.20000 | 13.20000 | 1.30 s | 1.74 s |
| `puc-bip42p-regiao-f2` | 1.00000 | 31.70605 | 1.00000 | 31.70605 | 13.77 s | 31.71 s |
| `puc-cc9-2p-seed-r1` | 1.25000 | 27.02679 | 1.25000 | 27.02679 | 1.69 s | 3.07 s |
| `puc-w3c571-seed-r1` | — | — | — | — | ≥90 s (cens.) | ≥90 s (cens.) |
| `pucn-cc3-10n-seed-r1` | 1.20000 | 16.93333 | 1.84889 | 16.93333 | 5.78 s | 23.95 s |
| `vienna-I056-regiao-f4` | 2.44000 | 8.50000 | — | 8.50000 | 88.17 s | 88.13 s |

### Constatações

1. **Incremento de H2 sobre U+K: zero nos cinco casos com ambos os ótimos** (PUC CC9, PUC BIP42, PUCN CC3, MAPF Room e Vienna I056); 0 de 6 grafos brutos com ganho certificado na análise atual. No sexto, não há resultado ótimo comparável.
2. **H2 sobre U isolado:** ganho em PUCN CC3 (`1.20000` → `1.84889`, cerca de 54,1%) e MAPF Room (`2.40000` → `4.20000`, 75%); isso mostra efeito sobre U, **não complementaridade com K**.
3. **Tempo total:** U+K+H2 foi mais lento que U+K nos quatro casos rápidos (PUC CC9: 3,07 vs. 1,69 s; BIP42: 31,71 vs. 13,77 s; PUCN: 23,95 vs. 5,78 s; MAPF: 1,74 vs. 1,30 s). Vienna apresentou tempos comparáveis (88,13 vs. 88,17 s), próximos do limite. Não inferir significância estatística sem repetições.
4. **Controle com mesmo pool:** nos cinco casos com controles ótimos, a aplicação do pool fixo sobre U+K não melhorou o limite LP. A disponibilidade do pool e a forma de criação são registradas nos `*-pool.json`.

## Censuras e gate automático

- **PUC W3C571:** U, U+K, U+H2, U+K+H2 encerraram com `TIME_LIMIT`; os dois braços de pool fixo estão `NOT_RUN`.
- **Vienna I056:** U+H2 encerrou com `TIME_LIMIT`; U, U+K, U+K+H2 e os controles tiveram `OPTIMAL`.
- Assim, **5 braços principais censurados e 2 controles não executados**. O analisador registra `INVESTIGATE`, porque a amostra integral exigida pelo pré-registro não está disponível (`complete_online_optima=false`, `all_same_pool_controls_complete=false`). **Não modificar o `analysis.json` para forçar `STOP`.**
- Regra pré-registrada de GO: melhoria relativa de LP ≥1% sobre U+K em **ao menos 2 grafos brutos independentes** e custo aceitável em ao menos 1. Nos cinco grafos ótimos para a comparação principal houve **0 ganhos**; portanto mesmo um ganho hipotético na única instância sem comparação ótima não atingiria 2. Isso justifica a **decisão humana STOP por impossibilidade de satisfazer o limiar de GO nesta amostra fixa**, sem fingir que o gate automático gerou STOP.

## Decisão e escopo do encerramento

**Decisão:** não promover H2 a COMP+K, não iniciar etapa MIP com H2 e encerrar a investigação H2 **neste protocolo de desenvolvimento**. Preservar implementação e evidências para reprodutibilidade; investigar novas famílias com hipótese explícita de ganho *marginal* sobre COMP+K. Reabertura de H2 somente mediante **novo plano pré-registrado** (instâncias/hipótese/seleção de suportes diferentes), jamais ajuste retrospectivo do gate.

**Limitações:** uma execução por braço; censuras e preparação de K significativa; comparação em seis grafos de desenvolvimento; cortes selecionados pelo procedimento testado, sem prova de redundância universal; ganho LP não implica ganho na raiz do MIP ou no desempenho do método inteiro. O campo `source_commit` descreve o código de execução e não deve ser substituído pelo hash do commit de documentação.

**Pendência de governança:** parecer externo de revisor diferente do autor não está evidenciado neste material. O encerramento documenta uma **decisão de priorização**; não representa aprovação de revisão científica independente.

## Reprodução e checagem

```bash
poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q
poetry run python experiments/cuts/analyze_h2_lp.py --run-dir results/benchmark/as16-lp-h2-001
```

Não rerodar o runner sobre o mesmo diretório: preservar os artefatos da campanha. Para repetição experimental, criar outro diretório e pré-registrar o plano.
