# AS23 — Design técnico: Revisão matemática independente de FC-R

**Spec:** `spec.md`; **Status:** Implemented for AS23; exact rational audit passed; formal technical gate VALIDATED after independent review and test corrections; final local commit/provenance pending.

## Architecture Overview

Estabelecer validade formal da FC-R/FC-R-T, confirmar separação exata de Q para região L fixa e reproduzir independentemente a testemunha racional declarada pelo Astra, antes de escrever um separador para benchmarks.

**Fluxo:** AS22 concluída experimentalmente; parecer Astra registrado; COMP+K, C6, C8 e validador físico existentes.

## Code Reuse Analysis

| Artefato atual | Reuso permitido |
|---|---|
| `experiments/alternative-formulations/as02_model_a.py` | Compilação de COMP e variáveis contínuas de fluxo. |
| `experiments/cuts/cuts.py` | Geradores K (C1/C2/C4-DM), sem mudanças no baseline. |
| `experiments/cuts/run_hl_lp_as22.py` | Convenções de orçamento, hashes e telemetria experimental. |
| `experiments/cuts/test_as22_hl_poly.py` | Padrões de testes de cortes e uso do compilador. |
| `docs/technical/reference/baseline-e-metodo/protocolo-comparacao-pareada.md` | Princípios de comparabilidade e censura. |

## Components

| Componente | Local | Contrato pretendido |
|---|---|---|
| Reprodução da testemunha | `experiments/cuts/verify_fcr_witness.py` | Constrói o grafo declarado, recupera os K reais e executa checagens racionais sem ajustar o modelo ao objetivo esperado. |
| Prova independente | `docs/technical/reference/tecnico/as23-prova-fcr.md` | Registra hipóteses, demonstração, simetria de destino, relação com C8 e precedentes. |
| Relatório de validação | `docs/technical/reference/experimentos/as23-validacao-fcr.md` | Registra coeficientes, certificados verificáveis, divergências, e decisão de gate. |

## Data Models e evidências

- Entradas: hash do grafo físico e do dígrafo `H`, conjuntos `S/T`, autonomia e configuração de solver versionada.
- Saídas experimentais: JSON determinístico com `status`, `schema_version`, `source_commit`, identidade de instância, parâmetros, linhas/certificados, contagens, tempos e razões de abstenção.
- Cada resultado produzido deve indicar se é prova algébrica, microcaso, execução LP/MIP real, resultado censurado ou hipótese externa.
- Não sobrescrever resultados AS16–AS22 nem tratar verificador independente como sinônimo de execução do autor.

## Error Handling Strategy

Apenas verificações locais. Se houver falha de geração C6/C8, não ajustar a restrição manualmente; registrar a divergência e interromper a conclusão.

## Risks & Concerns

| Risco | Impacto | Mitigação |
|---|---|---|
| Terminais e S∩T | A prova pode falhar se Q incluir destinos para FC-R ou origens para FC-R-T | Exclusões explícitas e microcontraexemplos. |
| Circulações | Simplificações de caminho podem eliminar fluxos válidos | Provar com balanço e capacidades sem assumir aciclicidade. |
| Testemunha declarada | Valores exatos ainda não verificados independentemente | Aritmética racional, enumeração de 0/1 estação e relatório de discrepâncias. |
| Literatura | Atribuir novidade não demonstrada | Levantar fixed-charge flow e disjunctive cuts antes de sugerir contribuição. |

## Tech Decisions

| Decisão | Escolha | Justificativa |
|---|---|---|
| Aprovação científica | Exigir relatório e artefatos verificáveis com `VALIDATED`/`BLOCKED` | Evita começar AS24 em cima de uma alegação não reproduzida. |
| Escopo | Nenhuma alteração a COMP/K/C6/C8 | Preserva baseline e histórico. |

## Critério de entrada na execução

Gate `VALIDATED` somente se duas provas, testemunha física e racional independente, relação C6/C8 e verificação bibliográfica forem documentadas sem divergência bloqueante. `BLOCKED` em caso contrário.

**Proveniência:** este design antecede a execução. A implementação AS23 e seu fechamento pós-revisão estão rastreados em `validation.md`; fonte de código rastreada por `source_commit`, `source_commit_note` e `source_sha256`.
