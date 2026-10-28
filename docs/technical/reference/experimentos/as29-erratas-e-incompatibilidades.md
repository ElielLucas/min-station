# AS29 — Erratas e incompatibilidades documentadas

**Natureza:** anexo de reconciliação, sem alteração das fontes primárias. As correções abaixo são de **interpretação**, não substituições dos números originais.
**Revisão:** E-29-01 a E-29-07 são da Rev. 0. A Rev. 1 (revisão independente, 17/10/2026) acrescenta E-29-08 a E-29-11. A Rev. 2 (18/10/2026) registra a exportação posterior das instalações (E-29-12) e atualiza a tabela de pendências; o texto da Rev. 0 foi mantido, e as notas de atualização vêm marcadas como *[Rev. 1]*.

## E-29-01 — CC9: LB* antigo 30 e OPT numérico posterior 31

- Instância: `puc-cc9-2p-seed-r1.txt`, hash bruto `0312f43552cddc102081d9937465429e29797ddb86cf85a6871752d50aeec88c`.
- Spec A R4: `results/benchmark/linha_base.csv`, `WorkLimit=164`, seeds 42, 43, 44: `mip_bound=30`, `mip_obj=31` para `base` e `comp`; `nucleo` ótimo 27. O valor **LB*=30 está correto naquele experimento**.
- AS06: checkpoints `results/benchmark/as06-mip-replication-001/checkpoints/puc-cc9-2p-seed-r1/arm-{00,03,06}.json`: `U` com bound 31, UB física reportada 31, status `OPTIMAL_NUMERIC`; mesmo SHA físico. O histórico AS09 repetiu bound 31 e UB validada 31 em U/U_K.
- *[Rev. 1]* As 10 instalações de 31 estações de CC9 (AS06 e AS09) foram reexecutadas no oráculo independente e aceitas; remover qualquer estação da instalação de `arm-00` a torna inviável, o que é coerente com o LB 31 (teste `test_oracle_accepts_archived_installation_and_rejects_reduced_one`). Estado: `OPT_NUMERIC_PHYSICAL`.
- **Interpretação:** a instância foi resolvida numericamente como OPT=31 posteriormente; não corrigir o CSV de linha de base para 31, apenas registrar o certificado/resultado posterior com sua própria origem e orçamento. Essa prova é numérica (solver + oráculo físico reportado), não racional independente.

## E-29-02 — W3C571: LB* 669 contra bound histórico posterior 678

- Instância: `puc-w3c571-seed-r1.txt` (desenvolvimento).
- Spec A R4: LB*=669, proveniente de `comp` MIP; UB* numérica do modelo=1064.
- AS09 ampliada: há bound numérico 678, sob orçamento de 600 s, e UB física reportada de 1079 no subconjunto auditado; o bound 678 é posterior e não pertence ao protocolo Spec A.
- *[Rev. 1, correção de fonte]* O bound 678 vem do AS06 (`checkpoints/puc-w3c571-seed-r1/arm-07.json`, `U_K`, 600 s), não do AS09; o melhor bound `U_K` do AS09 é 664 e o de `C` é 581 (inadmissível, E-29-08). A UB física 1079 aparece no AS06 `arm-01` e no AS09 `U_K`, e as duas instalações foram revalidadas pelo oráculo. O registro AS09 `C_K` desta instância é `VALIDATION_FAIL` com 3 incumbentes inválidas e não entra no envelope.
- **Interpretação:** 678 é um bound histórico auditado **dentro das três fontes selecionadas**, não uma atualização retroativa da linha de base ou prova de superioridade sob `WorkLimit=164`. A UB numérica 1064 da linha de base não é substituída por 1079: são níveis de validação distintos e 1079 não é uma melhoria do objetivo.

## E-29-03 — Variação de nomenclatura COMP

- E7–E14 e fontes antigas: `COMP` frequentemente inclui C1+C2+C4-DM.
- Convenção AS04 em diante: `COMP=U` sem K; `COMP+K=U_K`.
- Spec A `base` corresponde a U; `comp` corresponde a U+K; `nucleo` corresponde ao IP de K sem COMP.
- A AS29 registra métodos canônicos em linhas separadas. Não atribuir ganho experimental a apenas uma troca de nome.

## E-29-04 — E9 antes da correção de C4-DM

- `docs/technical/reference/experimentos/resultados-e9-e10-pli.md`, §6, relata não determinismo por ordem de hash e geração de cortes inválidos para `S∩T ≠ ∅` no código anterior à correção de 26/09/2026.
- Resultados E9/E10 legados de K **não devem ser misturados diretamente** ao envelope Spec A/AS06/AS09, cuja identidade e versão são diferentes, sem reprodução/compatibilidade específica.
- O relatório antigo indica correções de interpretação em MAPF den312d-m50 e Room m25-rho; estas pertencem a instâncias e artefatos próprios, não ao comparador AS29, e **não foram reprocessadas**.

## E-29-05 — UB do núcleo vs. UB física

- O `mip_obj` do IP de cobertura é ótimo/incumbente de uma **relaxação inteira**, não necessariamente um conjunto de estações viável para o MIN-STATION.
- O envelope de LB pode aproveitar seu `mip_bound` inteiro numérico; somente uma instalação fisicamente validada por oráculo independente fornece UB.
- `results/benchmark/linha_base.csv` não guarda, no próprio registro, o vetor instalado e o certificado de viabilidade independente: seu `mip_obj` de `base`/`comp` fica com rótulo **SOLVER_ONLY**, não UB física validada.

## E-29-06 — Proveniência incompleta e censuras

- O CSV Spec A registra `commit=9b93650-dirty` em suas linhas. Isso é proveniência de árvore potencialmente modificada; não inferir reprodutibilidade exata somente pelo hash do commit.
- Nem todo resultado AS09 contém seed/threads explicitamente no JSON individual; campos faltantes ficam vazios no CSV de proveniência até identificação segura por manifesto/protocolo.
- Status `WorkLimit` na linha de base conserva `mip_bound` e `mip_obj` numéricos, mas não prova ótimo. Os experimentos AS06/AS09 usam outro orçamento e não são comparação pareada com Spec A.
- Para 23/31 casos de desenvolvimento, as fontes AS06/AS09 auditadas não fornecem UB física reportada. O gate G0 exige essas evidências ou uma decisão científica explícita sobre escopo, não uma suposição.
- *[Rev. 1]* Decisão explícita registrada em `as29-envelope-lb-opt.md` §5–§6: nenhuma fonte versionada com identidade confirmada guarda instalações para esses 23 casos. Eles passam a ser referência de LB e de UB/OPT numérica (`SOLVER_ONLY`), não de UB física. Seed/threads/orçamento do AS09 agora vêm de `plan.json`, cujo hash canônico foi conferido; a versão do Gurobi da Spec A continua desconhecida.

## E-29-07 — Partição e identidade

- Foram auditados apenas os 31 casos de desenvolvimento e 5 legados de `classe=principal`. A partição `avaliacao` não foi usada para selecionar políticas, calcular envelope nem preencher lacunas.
- A identidade reprodutível é o hash SHA-256 do arquivo **com** parâmetros `r`, `m` e convenção de terminais. O identificador de família ou prefixo `puc` sozinho não define equivalência de instância.
- A comparação entre orçamentos diferentes deve permanecer descritiva, nunca um resultado pareado de performance.

## E-29-08 — Formulação C não é fonte admissível de LB *[Rev. 1]*

- A AS09 marca a equivalência U↔C como `PROOF_REVIEW_REQUIRED` (`specs/as-09-formulacao-c-cumulativa/implementation-status.md`, T1).
- Na Rev. 0, bounds de `C`/`C_K` entravam no "LB histórico" e na regra de OPT do mesmo braço (`b-b18-regiao` e `pace18-t2-061` tinham a fonte da UB/OPT apontando para `--C.json`).
- Rev. 1: os 15 registros MIP `C`/`C_K` com bound permanecem na proveniência com `lb_admissible=false`. Nenhum valor do envelope mudou, porque nenhum bound de C superava o de `U`/`U_K`/`K_IP`. As instalações produzidas por `C`/`C_K` continuam válidas como UB física quando o oráculo as aceita, porque a validade de uma instalação não depende do modelo que a gerou.

## E-29-09 — "UB física reportada" não era validação independente *[Rev. 1]*

- A Rev. 0 aceitava `physical_validated_ub` com base em metadados (`installed`, `invalid_incumbents=0`) sem reexecutar o oráculo.
- Rev. 1: o auditor reexecuta `experiments/cuts/independent_validator.viavel` sobre cada vetor `installed`, com a instância de SHA conferido e o `r` do manifesto. Resultado: 67/67 aceitas, 0 rejeitadas. Uma rejeição futura marca o caso como `INCONSISTENT` e bloqueia G0.

## E-29-10 — 15 ótimos numéricos estavam rotulados como "UB numérica apenas" *[Rev. 1]*

- Spec A fechou numericamente 15 casos de desenvolvimento (LB\* = UB\*, status 2), entre eles `b-b06-*`, `lin-lin06-*`, `puc-cc6-3p`, `puc-w23c23-intercalado-f2-rho` e `urb-mindelo`.
- A Rev. 0 os agrupava com os 8 casos abertos sob `UB_NUMERIC_ONLY`. A Rev. 1 os rotula `OPT_NUMERIC_SOLVER_ONLY`: ótimo numérico do solver, sem instalação arquivada e, portanto, sem UB física.
- `puc-w23c23-intercalado-f2-rho` é o único caso do escopo com `S∩T ≠ ∅` (28 terminais). Seu OPT numérico 128 vem de `U_K` (`comp`, status ótimo), enquanto `U` parou em `WorkLimit` com bound 125 e incumbente 132. É o caso prioritário para validação física se for usado como referência de OPT.

## E-29-11 — Limites do manifesto fora do envelope *[Rev. 1, achado do Verifier]*

- `instances/manifest.csv` guarda `lb`/`ub` (protocolo de dificuldade, 600 s) e `lb_melhor`/`ub_melhor` (E13, 1800 s, MIPFocus=1; E3/E4 para `hc9u`). Em `vienna-I065-intercalado-f2` (17/19 contra 16/20 no envelope), `vienna-I065-regiao-f4` (UB 19 e 17 contra 20) e `hc9u` (UB 38 contra 41), esses valores são melhores do que o envelope.
- Não foram fundidos: as fontes não guardam SHA por linha. Agora aparecem lado a lado nas colunas `manifest_*`, `lb_documented_max` e `ub_documented_min`, com a flag `DOCUMENTED_BOUND_OUTSIDE_ENVELOPE`.
- Alegações de melhoria em AS31+ precisam superar esses valores documentados, e não apenas o envelope.

## E-29-12 — Exportação posterior de instalações *[Rev. 2]*

- Os 23 casos de desenvolvimento sem instalação arquivada foram reexecutados em `U` e `U_K` com a configuração da Spec A (seed 42, `WorkLimit=164`, 4 threads, Gurobi 12.0.3), por `experiments/benchmark/export_as29_installations.py`. Saída em `results/benchmark/as29-physical-ub-001/` (46 JSONs com sidecar SHA-256).
- As 46 instalações foram aceitas pelo oráculo independente. As 46 linhas reproduzem a linha de base de seed 42 (mesmo `mip_obj`, `mip_bound` dentro de 0,01).
- É evidência **posterior** (18/10/2026) à AS29 original e aos resultados da Rev. 0/1; não altera nenhuma fonte existente e fica identificada como `AS29_POSTERIOR_EXPORT`.
- Em 4 casos D/A de 3 seeds (`puc-cc10-2u-seed-r1`, `puc-cc11-2u-seed-r1`, `puc-cc12-2u-seed-r1`, `puc-w23c23-seed-r1`) a UB física da seed 42 é maior do que o menor objetivo numérico da Spec A (outra seed, sem instalação). A UB física validada entra no envelope; a numérica menor permanece na coluna `ub_numeric_envelope`.
- `puc-w23c23-intercalado-f2-rho`, único caso do escopo com `S∩T ≠ ∅`, passa a ter instalação validada para o ótimo 128.

## Pendências e decisão

| Item | Situação | Ação necessária |
|---|---|---|
| CC9 | Divergência interpretada | Manter Spec A 30 e adicionar ótimo numérico histórico 31 |
| W3C571 | Bound posterior distinto | Manter 669 da Spec A e 678 na coluna histórica |
| Modelos / nomenclatura | Normalizado nos CSVs | Verificar em qualquer experimento futuro |
| E9 pré-C4-DM | Isolado | Exigir evidência compatível antes de reutilizar |
| UB física de 23 casos | *[Rev. 2]* **Resolvido** por exportação posterior (E-29-12); na Rev. 1 era limitação sem artefato recuperável | Nenhuma para o escopo de desenvolvimento; os 5 legados seguem sem UB física (fora do gate) |
| UB física dos 8 casos AS06/AS09 | *[Rev. 1]* **Resolvido** | 67/67 instalações revalidadas pelo oráculo AS29 |
| LB de `C`/`C_K` | *[Rev. 1]* **Resolvido** | Inadmissível até o gate matemático da AS09 |
| Dados numéricos de solver | Somente prova numérica | Identificar versão/seed faltantes; não afirmar prova racional |
| Limites do manifesto (I065 ×2, hc9u) | *[Rev. 1]* **Exibidos lado a lado**, não fundidos | Usar `lb_documented_max`/`ub_documented_min` como régua de melhoria |
| Gate independente | *[Rev. 2]* Verifier em `validation.md` | Aprovação do gate pelo pesquisador |

**Decisão Rev. 0:** **G0_BLOCKED_EVIDENCE**. A implementação de AS29 pode ser utilizada como auditoria, mas não libera AS30–AS35 sem resolver os pré-requisitos do programa.

**Decisão Rev. 1:** `AS29_COMPLETE_WITH_LIMITATIONS`; G0 `G0_BLOCKED_EVIDENCE` (8/31) e emenda A1 proposta.

**Decisão Rev. 2:** G0 pelo contrato vigente, sem emendas: `G0_CANDIDATE_PASS` (31/31 com UB física revalidada). A emenda A1 **não foi adotada** e deixou de ser necessária. A aprovação do gate continua com o pesquisador.
