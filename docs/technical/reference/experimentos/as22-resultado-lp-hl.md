# AS22 — HL poliédrica: campanha real e conclusão

**Status da execução:** campanha Gurobi executada no ambiente do pesquisador; 6 casos de desenvolvimento, 12 registros; gate do analisador **`INVESTIGATE`**. **Decisão científica:** encerrar a estratégia local AS20–AS22 para estes suportes, sem alegar redundância universal de HL; nenhum MIP autorizado.

## Proveniência e escopo

- Dados arquivados em `results/benchmark/as22-hl-lp-001/{manifest,rows,analysis}.json`, incluídos no snapshot recebido em 2026-10-16; esta atualização documental não reexecutou Gurobi.
- Braços `U_K` e `U_K_HL`; teto nominal 90 s totais por braço. O gate avalia ganho/custo somente quando os pares são comparáveis.
- O `source_commit` do manifesto pode representar um commit anterior à inclusão dos arquivos AS22; o SHA sozinho **não demonstra a identidade integral do código executado**. A origem dos resultados deve ser reconciliada antes de publicação.

## Pares da execução

| Instância | LP K | LP K+HL | Cortes adicionados | Parede K / K+HL (s) | Leitura |
|---|---:|---:|---:|---:|---|
| `puc-cc9-2p-seed-r1` | 27.026786 | 27.026786 | 0 | 1.803945 / 2.512203 | par ótimo |
| `puc-bip42p-regiao-f2` | 31.706052 | 31.706052 | 0 | 14.807924 / 16.950329 | par ótimo |
| `pucn-cc3-10n-seed-r1` | 16.933333 | 16.933333 | 0 | 5.826092 / 7.599916 | par ótimo |
| `mapf-room-32-32-4-m10-f8` | 13.200000 | 13.200000 | 0 | 1.289200 / 1.815300 | par ótimo |
| `vienna-I056-regiao-f4` | — | — | 0 | 87.977172 / 90.045223 | censurado / inconclusivo |
| `puc-w3c571-seed-r1` | — | — | 0 | 90.099362 / 90.099699 | censurado / inconclusivo |

## Diagnóstico dos suportes

Conforme os 12 registros, as quatro instâncias com separação concluída examinaram **16 suportes de tamanho 8**: 11 `K_PAIR_PROJECTION` e 5 `LARGE_K_PROJECTION`. Em cada suporte, o oráculo classificou como fisicamente viável o conjunto de estações externo `V\R` (padrão vazio dentro de `R`); as demais 255 configurações foram inferidas por monotonicidade. São **16 consultas físicas e 4.080 inferências**, não verificações independentes.

Sob monotonicidade de viabilidade por adição de estações, `VIABLE(V\R)` implica `conv(Φ_R)=[0,1]^R`. Portanto **nenhuma desigualdade válida escrita exclusivamente nas variáveis `y_R` separa pontos do cubo nesses 16 suportes** — independentemente de pesos. Isso **não demonstra** que todo suporte ou toda extensão de HL seja redundante.

## Decisão após revisão externa

O [parecer Astra de FC-R](../tecnico/parecer-astra-fcr-pos-as22.md) recomenda encerrar o mecanismo local “suporte pequeno/complemento inteiro disponível” e investigar cortes de cobertura de fluxo por regiões (FC-R), preservando COMP+K como baseline. A proposta será submetida a validação independente AS23 antes de ser tratada como contribuição.

**Não modificar** os JSON históricos; este documento atualiza somente a interpretação e a indicação de continuação.
