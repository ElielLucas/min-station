# AS29 — Envelope de limites históricos e estado de reconciliação

**Versão do envelope:** `AS29-r1` (revisão independente de 17/10/2026). A versão `AS29-r0` (mesma data, autor da implementação original) está registrada na §2 e não foi apagada.
**Escopo:** 31 casos `principal/desenvolvimento` + 5 casos `principal/legado` (controle histórico). **Nenhum resultado da partição `avaliacao` foi aberto ou incorporado** (os arquivos AS09 de avaliação são filtrados pelo nome antes de qualquer leitura; ver teste `test_reserved_results_are_never_opened`).
**Fontes incorporadas ao envelope:** `results/benchmark/linha_base.csv` (Spec A R4), checkpoints `as06-mip-replication-001`, arquivos MIP e LP de `as09-expanded-600s-001` e a **exportação posterior** `results/benchmark/as29-physical-ub-001/` (§2, Rev. 2). **Fonte exibida lado a lado, sem fusão:** colunas `lb`, `ub`, `lb_melhor`, `ub_melhor` e respectivas fontes de `instances/manifest.csv` (§4.1).
**Artefatos derivados:** `as29-envelope-proveniencia.csv` (338 linhas: uma por braço/fonte/modo), `as29-envelope-casos.csv` (36 casos), script `experiments/benchmark/reconcile_as29.py`.
**Classificação da etapa:** `AS29_COMPLETE` com limitações menores (§4). **G0 pelo contrato vigente:** `G0_CANDIDATE_PASS`: 31/31 casos de desenvolvimento com UB física revalidada pelo oráculo independente. A aprovação do gate continua com o pesquisador. A emenda A1 (§6) deixou de ser necessária e **não foi adotada**.

## 1. Semântica dos números

- **LB\* Spec A:** `ceil(max(mip_bound entre base/comp/nucleo) − 1e-6)` da linha de base (`WorkLimit=164`, 4 threads, 3 seeds em D/A e 1 em F/M/legados). Valor histórico preservado; não é editado por resultados posteriores.
- **LB envelope:** maior `ceil(bound − 1e-6)` entre registros **admissíveis** de Spec A, AS06, AS09 e da exportação posterior. Admissíveis: braços `U` (base), `U_K` (COMP+K) e `K_IP` (núcleo inteiro, relaxação). Os braços `C`/`C_K` do AS09 ficam na proveniência com `lb_admissible=false`, porque a formulação C está em `PROOF_REVIEW_REQUIRED` (`specs/as-09-formulacao-c-cumulativa/implementation-status.md`). O teto inteiro é convenção numérica, não certificado racional.
- **UB numérica:** menor incumbente reportada por `U`/`U_K` em qualquer fonte (`SOLVER_ONLY`). O objetivo do `K_IP` **nunca** entra como UB.
- **UB física (oráculo AS29):** a fonte guardou `physical_validated_ub`, o vetor `installed` de mesmo tamanho e `invalid_incumbents=0`, **e** a AS29 reexecutou o oráculo independente `experiments/cuts/independent_validator.viavel` sobre a instância com SHA conferido e `r` do manifesto (estados vértice-bateria no grafo original + emparelhamento S→T, sem usar o modelo MIP, `A_r` ou K). Rejeita duplicatas e vértices fora de `V`.
- **LP U / LP U_K:** ótimo LP numérico do AS09 (`OPTIMAL_NUMERIC`), coluna separada; nunca misturado ao LB MIP.
- **Estados por caso:**

| Estado | Regra | Uso permitido |
|---|---|---|
| `OPT_NUMERIC_PHYSICAL` | LB envelope = UB física revalidada | OPT de referência; certificação numérica (solver) + oráculo |
| `OPEN_PHYSICAL_UB` | UB física revalidada > LB envelope | LB e UB físicas de referência |
| `OPT_NUMERIC_SOLVER_ONLY` | LB envelope = UB numérica; sem instalação arquivada | LB de referência; OPT/UB apenas numéricos do solver |
| `OPEN_SOLVER_UB_ONLY` | UB numérica > LB envelope; sem instalação arquivada | LB de referência; UB apenas numérica |
| `INCONSISTENT` | LB > alguma UB, oráculo rejeitou instalação reportada, ou sem LB admissível | bloqueia G0 |
| `INCOMPLETE` | nenhuma UB disponível (nem física nem numérica) | bloqueia G0; nunca se estima o valor |
| `INTEGRITY_BLOCKED` | SHA do arquivo não confere | bloqueia G0 |

- **Censura:** status `16` (Spec A) e `TIME_LIMIT` (AS06/AS09) conservam bound e incumbente; nunca são convertidos em ótimo.
- **Nomenclatura:** Spec A `base`=`U`, `comp`=`U_K`, `nucleo`=`K_IP`; AS09 acrescenta `C`, `C_K`. Em E7–E14, `COMP` nomeia U+K (ver errata E-29-03).

## 2. Histórico da revisão (Rev. 0 → Rev. 1 → Rev. 2)

| Item | Rev. 0 (implementação original) | Rev. 1 (revisão independente) | Motivo |
|---|---|---|---|
| UB física | aceitava `physical_validated_ub` reportado sem reexecutar o oráculo | 67/67 instalações reexecutadas no oráculo independente; 0 rejeições | O próprio design exige "validação independente"; metadado não é validação |
| LB de `C`/`C_K` | entrava no LB histórico e na regra de OPT do mesmo braço | registrado, mas `lb_admissible=false` | Formulação C sem prova revisada; nenhum número do envelope mudou |
| LP | ausente | colunas `lp_u`, `lp_u_k` (AS09, 8 casos) | `design.md` exige três colunas distintas (LP, MIP bound, UB física); plano G0 lista LP |
| Casos fechados pelo solver | rotulados `UB_NUMERIC_ONLY`, igual aos abertos | `OPT_NUMERIC_SOLVER_ONLY` (15) vs `OPEN_SOLVER_UB_ONLY` (8) | Classe anterior escondia 15 ótimos numéricos |
| OPT | exigia bound e UB no mesmo braço | LB envelope = UB física (fontes distintas, mesmo SHA) | Ambos são limites válidos da mesma instância; proveniência de cada lado preservada |
| Consistência | só LB > UB física | LB > min(UB física, UB numérica) → `INCONSISTENT` | Detecta mistura de versões incompatíveis |
| Proveniência AS06/AS09 | `threads=4` e `wall_budget_s=540` fixos no código; seed AS09 vazia | lidos de `plan.json` (AS09: hash canônico conferido contra manifesto e cada registro; AS06: manifesto + sidecar) | Valor fixado no código não é proveniência; 540 era o tempo do solver, o orçamento por braço é 600 s |
| Gate | `G0_BLOCKED_EVIDENCE` se algum caso de desenvolvimento não tem UB física | mantido (`gate`); acrescenta `amendment_candidate` (emenda A1, §6) e bloqueio por `INCOMPLETE` | A regra Rev. 0 corresponde ao contrato vigente; mudar o critério depois dos resultados exige decisão explícita do pesquisador |
| Limites do manifesto | não lidos | colunas `manifest_*`, `lb_documented_max`, `ub_documented_min`; flag `DOCUMENTED_BOUND_OUTSIDE_ENVELOPE` | Spec P1.3: divergências entre documentos devem aparecer lado a lado (achado do Verifier) |
| Proveniência temporal | ausente | `source_versioned_in` (commit e data do git que versionou a fonte); `cuts_scope` distingue hash do gerador (Spec A) de hash de K por instância (AS06/AS09) | Plano G0 pede data/commit |

Resultado Rev. 0 preservado (os CSVs da Rev. 0 não eram versionados e foram sobrescritos; a paridade numérica abaixo foi conferida na sessão de revisão, antes da sobrescrita, e o Verifier recomputou os valores atuais de forma independente): `{"cases":36,"development":31,"provenance_rows":260,"by_status":{"UB_NUMERIC_ONLY":28,"OPTIMAL_NUMERIC_REPORTED":3,"PHYSICAL_UB_REPORTED":5},"development_with_physical_ub":8,"gate":"G0_BLOCKED_EVIDENCE"}`. Todos os valores numéricos de LB\* Spec A, LB histórico e UB física por caso são idênticos entre Rev. 0 e Rev. 1 (conferido caso a caso).

### Rev. 2 — exportação posterior de instalações (18/10/2026)

A Rev. 1 deixou 23 casos de desenvolvimento sem instalação arquivada. Em vez de adotar a emenda A1, o pesquisador autorizou a opção de obter essas instalações. Script: `experiments/benchmark/export_as29_installations.py`.

- **Configuração:** a da Spec A (`WorkLimit=164`, 4 threads, guarda de 1800 s, sem MIP start, seed 42) nos braços `U` e `U_K`, com o mesmo gerador de cortes. Gurobi 12.0.3, commit gravado em cada JSON.
- **Cobertura:** 23 casos × 2 braços = 46 solves, em 2 processos paralelos. Saída em pasta nova, com sidecar SHA-256 por arquivo; nenhuma fonte existente foi tocada.
- **Resultado:** 27 `OPTIMAL_NUMERIC` e 19 `WORK_LIMIT`. As 46 instalações foram aceitas pelo oráculo independente, na execução e de novo no auditor.
- **Reprodução:** as 46 linhas coincidem com a linha de base de seed 42 (`mip_obj` igual e `mip_bound` dentro de 0,01), de modo que a UB física validada é a própria incumbente histórica daquela seed. Teste: `test_posterior_export_reproduces_historical_seed42_rows`.
- **Natureza:** evidência obtida depois da AS29 original e depois dos resultados da Rev. 0/1. Cada linha traz `source=AS29_POSTERIOR_EXPORT`.
- **Limite:** nos casos D/A que tinham 3 seeds, só a seed 42 foi reexecutada. Em 4 deles a UB física (seed 42) é maior do que o menor objetivo numérico da Spec A (outra seed, sem instalação): `puc-cc10-2u-seed-r1` 58 contra 57, `puc-cc11-2u-seed-r1` 104 contra 101, `puc-cc12-2u-seed-r1` 198 contra 193 e `puc-w23c23-seed-r1` 158 contra 156. O mesmo vale para `puc-w3c571-seed-r1` (1079 contra 1064, já na Rev. 1). O envelope usa a UB física validada; a UB numérica menor fica na coluna própria e não é promovida.

## 3. Envelope por caso

Tabelas geradas de `as29-envelope-casos.csv`; nenhum número digitado à mão. **Não são comparação pareada**: misturam campanhas com orçamento, seeds e versões distintos (Spec A `WorkLimit=164`; AS06 600 s × 3 seeds; AS09 600 s × seed 42).

### desenvolvimento

| Caso | SHA | LB* Spec A | LB envelope (braço) | UB numérica | UB física (oráculo AS29) | OPT numérico | LP U_K | Manifesto LB/UB melhor | Estado |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `b-b06-intercalado-f2` | `abdcdf3d6a52` | 1 | 1 (U) | 1 | 1 | 1 | — | 1/1 | `OPT_NUMERIC_PHYSICAL` |
| `b-b06-regiao-f2` | `5af5c7735536` | 3 | 3 (U) | 3 | 3 | 3 | — | 3/3 | `OPT_NUMERIC_PHYSICAL` |
| `b-b12-intercalado-f2` | `a7c590788ff9` | 7 | 7 (U) | 7 | 7 | 7 | — | 7/7 | `OPT_NUMERIC_PHYSICAL` |
| `b-b12-regiao-f2` | `34abce24950c` | 3 | 3 (U) | 3 | 3 | 3 | — | 3/3 | `OPT_NUMERIC_PHYSICAL` |
| `b-b18-intercalado-f2` | `5ce1a43892f1` | 1 | 1 (U) | 1 | 1 | 1 | — | 1/1 | `OPT_NUMERIC_PHYSICAL` |
| `b-b18-regiao-f2` | `ae469341762e` | 2 | 2 (U) | 2 | 2 | 2 | 2 | 2/2 | `OPT_NUMERIC_PHYSICAL` |
| `lin-lin06-intercalado-f2` | `baa0bafa1ef5` | 3 | 3 (U) | 3 | 3 | 3 | — | 3/3 | `OPT_NUMERIC_PHYSICAL` |
| `lin-lin06-regiao-f4` | `a35ffd710c97` | 7 | 7 (U) | 7 | 7 | 7 | — | 7/7 | `OPT_NUMERIC_PHYSICAL` |
| `mapf-room-32-32-4-m10-f8` | `78be3e1261f3` | 16 | 16 (U_K) | 18 | 18 | — | 13.200 | 16/18 | `OPEN_PHYSICAL_UB` |
| `pace18-t2-061-regiao-f4` | `37cf3679a3c4` | 7 | 7 (U_K) | 7 | 7 | 7 | 6.786 | 7/7 | `OPT_NUMERIC_PHYSICAL` |
| `pace18-t2-141-regiao-f4` | `9bb701cdf35b` | 10 | 10 (U) | 12 | 12 | — | — | 10/12 | `OPEN_PHYSICAL_UB` |
| `pace18-t2-199-regiao-f4` | `98d42c0bac95` | 7 | 7 (U_K) | 7 | 7 | 7 | — | 7/7 | `OPT_NUMERIC_PHYSICAL` |
| `puc-bip42p-regiao-f2` | `d7c535965224` | 35 | 35 (K_IP) | 43 | 43 | — | 31.706 | 33/43 | `OPEN_PHYSICAL_UB` |
| `puc-bip42p-seed-r1` | `2593a7cbca59` | 35 | 35 (K_IP) | 43 | 43 | — | — | 33/43 | `OPEN_PHYSICAL_UB` |
| `puc-cc10-2u-regiao-f2` | `512b6f1f16c6` | 2 | 2 (U) | 2 | 2 | 2 | — | 2/2 | `OPT_NUMERIC_PHYSICAL` |
| `puc-cc10-2u-seed-r1` | `f47b1dd56c29` | 53 | 53 (U) | 57 | 58 | — | — | 53/60 | `OPEN_PHYSICAL_UB` |
| `puc-cc11-2u-seed-r1` | `00cf9fd0946e` | 92 | 92 (U) | 101 | 104 | — | — | 92/102 | `OPEN_PHYSICAL_UB` |
| `puc-cc12-2u-seed-r1` | `4f2938667fcf` | 165 | 165 (U) | 193 | 198 | — | — | 165/204 | `OPEN_PHYSICAL_UB` |
| `puc-cc6-3p-seed-r1` | `b404ea3598e6` | 32 | 32 (U) | 32 | 32 | 32 | — | 32/32 | `OPT_NUMERIC_PHYSICAL` |
| `puc-cc9-2p-seed-r1` | `0312f43552cd` | 30 | 31 (U) | 31 | 31 | 31 | 27.027 | 30/31 | `OPT_NUMERIC_PHYSICAL` |
| `puc-w23c23-intercalado-f2-rho` | `e09ff5393ebf` | 128 | 128 (U_K) | 128 | 128 | 128 | — | 128/128 | `OPT_NUMERIC_PHYSICAL` |
| `puc-w23c23-seed-r1` | `2d66a9d3e0ce` | 140 | 140 (U_K) | 156 | 158 | — | — | 140/156 | `OPEN_PHYSICAL_UB` |
| `puc-w3c571-seed-r1` | `e85ced7daef7` | 669 | 678 (U_K) | 1064 | 1079 | — | 432.934 | 666/1131 | `OPEN_PHYSICAL_UB` |
| `pucn-cc3-10n-seed-r1` | `9123c0e46228` | 18 | 18 (K_IP) | 26 | 26 | — | 16.933 | 17/26 | `OPEN_PHYSICAL_UB` |
| `pucn-cc3-5n-seed-r1` | `7a50d215268f` | 8 | 8 (U_K) | 8 | 8 | 8 | — | 8/8 | `OPT_NUMERIC_PHYSICAL` |
| `pucn-cc5-3n-seed-r1` | `bc5ebcabf468` | 15 | 15 (U) | 15 | 15 | 15 | — | 15/15 | `OPT_NUMERIC_PHYSICAL` |
| `pucn-cc6-2n-seed-r1` | `0bb5c20e2f2d` | 6 | 6 (U) | 6 | 6 | 6 | — | 6/6 | `OPT_NUMERIC_PHYSICAL` |
| `urb-mindelo-m25-f4` | `a3e9ec1503a1` | 4 | 4 (U) | 4 | 4 | 4 | — | 4/4 | `OPT_NUMERIC_PHYSICAL` |
| `vienna-I056-regiao-f4` | `645da5115a0e` | 9 | 9 (U_K) | 11 | 11 | — | 8.500 | 9/11 | `OPEN_PHYSICAL_UB` |
| `vienna-I065-intercalado-f2` | `8d90458140a3` | 16 | 16 (U_K) | 20 | 20 | — | — | 17/19 † | `OPEN_PHYSICAL_UB` |
| `vienna-I065-regiao-f4` | `1f5d6b6c1294` | 14 | 14 (U_K) | 20 | 20 | — | — | 14/17 † | `OPEN_PHYSICAL_UB` |

### legado

| Caso | SHA | LB* Spec A | LB envelope (braço) | UB numérica | UB física (oráculo AS29) | OPT numérico | LP U_K | Manifesto LB/UB melhor | Estado |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `bip42p` | `fffb7ecf020b` | 35 | 35 (K_IP) | 43 | — | — | — | —/— | `OPEN_SOLVER_UB_ONLY` |
| `hc10p` | `8cd73be105f5` | 56 | 56 (K_IP) | 77 | — | — | — | —/— | `OPEN_SOLVER_UB_ONLY` |
| `hc11p` | `7d4c55a4deb3` | 97 | 97 (K_IP) | 161 | — | — | — | —/— | `OPEN_SOLVER_UB_ONLY` |
| `hc12p` | `01ed34bb2b99` | 171 | 171 (U_K) | 376 | — | — | — | —/— | `OPEN_SOLVER_UB_ONLY` |
| `hc9u` | `1f2d51b5734e` | 32 | 32 (U_K) | 41 | — | — | — | 32/38 † | `OPEN_SOLVER_UB_ONLY` |

† = limite documentado no manifesto fora do envelope (§4.1).

## 4. Cobertura e evidências

- **31/31** casos de desenvolvimento e **5/5** legados com SHA-256 do arquivo igual ao manifesto; nenhum caso `avaliacao`.
- **338** registros de proveniência: 192 Spec A (128 `U`/`U_K`, 64 `K_IP`), 36 AS06, 32 AS09 MIP, 32 AS09 LP e 46 da exportação posterior (Rev. 2).
- **113** instalações revalidadas pelo oráculo independente: 36 AS06 + 31 AS09 + 46 da exportação posterior. **113 aceitas, 0 rejeitadas.** O registro `puc-w3c571 C_K` do AS09 é `VALIDATION_FAIL` e não tem vetor.
- **15** registros MIP `C`/`C_K` com bound ficaram inadmissíveis como LB. Nenhum deles superava o LB dos braços admissíveis.
- **Consistência cruzada:** nenhum caso tem LB envelope acima de qualquer UB (física ou numérica).
- **Desenvolvimento por estado:** 18 `OPT_NUMERIC_PHYSICAL` e 13 `OPEN_PHYSICAL_UB`; nenhum caso fica sem UB física. Os 5 legados, fora do gate, seguem `OPEN_SOLVER_UB_ONLY`.
- **`S∩T`:** apenas `puc-w23c23-intercalado-f2-rho` (28 terminais em `S∩T`) tem interseção não vazia. Com a Rev. 2 o seu ótimo 128 passou a ter instalação validada pelo oráculo (`OPT_NUMERIC_PHYSICAL`), o que fecha a lacuna que a Rev. 1 apontava no único caso com `S∩T`.
- **Limitações que restam:** versão do Gurobi da Spec A desconhecida e `commit=9b93650-dirty` nessa fonte; LP só em 8/31 casos (AS09); a data disponível nas linhas é a de versionamento git, não a de execução; as UBs físicas dos casos D/A de 3 seeds vêm só da seed 42 (§2, Rev. 2); e `OPT_NUMERIC_PHYSICAL` é igualdade entre LB numérico do solver e UB validada, não certificado racional.

### 4.1 Limites documentados fora do envelope (lado a lado, não fundidos)

O manifesto guarda `lb`/`ub` do protocolo de dificuldade (regenerado no commit `dec8b78`, autoria 02/10/2026 e commit 05/10/2026, depois da correção do C4-DM) e `lb_melhor`/`ub_melhor` de campanhas posteriores. Esses números não têm artefato por execução com SHA da instância, por isso ficam fora do envelope. Mesmo assim, em três casos eles são melhores do que o envelope:

| Caso | Envelope LB / UB num. | Manifesto `lb`/`ub` (fonte) | Manifesto `lb_melhor`/`ub_melhor` (fonte) | Estado |
|---|---|---|---|---|
| `vienna-I065-intercalado-f2` | 16 / 20 | 16 / 21 (COMP, 600 s, seed 42) | **17 / 19** (E13, COMP C1+C2+C4, MIPFocus=1, 1800 s) | divergência aberta, não fundida |
| `vienna-I065-regiao-f4` | 14 / 20 | 14 / **19** (COMP, 600 s, seed 42) | 14 / **17** (E13) | divergência aberta, não fundida |
| `hc9u` (legado) | 32 / 41 | — | 32 / **38** (E3/E4, `resultados-e2-e4-pli.md`) | divergência histórica já registrada em `resultados-linha-de-base.md` |

Leitura: os arquivos I065 não mudam desde `d384ceb` (26/09/2026, 11:52). O E13 é de 27/09/2026, posterior à correção do C4-DM, e os dois casos têm `S∩T = ∅`, de modo que nada indica bound inválido. A identidade, porém, só é inferida pelo histórico git, sem SHA por linha. **Consequência para AS31+:** uma alegação de melhoria precisa superar `lb_documented_max` / `ub_documented_min`, e não apenas o envelope. No I065-intercalado, por exemplo, uma UB 19 de um método novo não é melhoria.

### Fontes examinadas e não incorporadas

| Fonte | Motivo |
|---|---|
| AS05 (fatorial, diagnóstico, piloto), AS06 screening, AS08 B/LB-probe | Mesmos 6 casos do núcleo AS05; LB ≤ e UB física ≥ às do AS06 replicação/AS09 (conferido): não alteram o envelope. Braços `A2/A4/B_K` não são formulações admissíveis do baseline |
| AS16/AS25/AS28 (LP) | Mesmos casos, orçamento de 90 s e políticas de corte; o LP U/U_K do AS09 cobre os mesmos 8 casos |
| E9–E14, `dificuldade_v1`, `e10b_starts`, R6/R7 | Sem SHA da instância por linha; parte é anterior à regeneração de `benchmark-v1` (`dec8b78`) ou à correção do C4-DM (E9/E10, errata E-29-04). Os resumos dessas campanhas que o manifesto adotou aparecem na §4.1 |

## 5. Análise do bloqueio G0 da Rev. 0 (Rev. 1)

Esta análise foi feita na Rev. 1, quando 23 casos não tinham instalação. Ela fica registrada porque motivou a Rev. 2.

1. **A spec exige instalação validada para todos os 31?** Não literalmente: o critério fala de casos "usados nos futuros gates". A Rev. 0 aplicou o requisito aos 31.
2. **Indispensável ao objetivo da AS29?** Não, porque o objetivo é reconciliar limites com proveniência. Mas a spec põe "Reexecutar linha de base" fora de escopo e a linha de base não guardava instalações, de modo que o critério lido como 31/31 era inalcançável dentro da etapa.
3. **Bounds numéricos bastam para o envelope?** Sim, como envelope histórico rotulado; a UB numérica só é usada onde um erro é conservador.
4. **Onde a UB física é necessária?** Em gates que usem o caso como referência de OPT ou aleguem igualdade/superação de UB (AS31–AS35).
5. **Decisão da Rev. 1: C (parcialmente correto), com componente D.** Os defeitos reais eram: UBs nunca revalidadas, bounds de formulação sem prova no LB, limites do manifesto invisíveis e caso sem UB não bloqueando.
6. **Desfecho:** a Rev. 1 propôs a emenda A1 para destravar o G0. O pesquisador preferiu obter as instalações; a emenda **não foi adotada** e não é mais necessária (§6).

## 6. G0

**Estado formal (contrato vigente, sem emendas):** `G0_CANDIDATE_PASS`. Condições verificadas pelo auditor (`gate()` e testes):
- 31/31 casos de desenvolvimento com SHA conferido, LB admissível com fonte, UB física revalidada pelo oráculo independente e classe de status;
- 0 casos `INCONSISTENT`, `INCOMPLETE` ou `INTEGRITY_BLOCKED`;
- CC9 contextualizada (E-29-01): LB\* 30 da Spec A preservado, ótimo numérico 31 posterior com instalação validada;
- divergências abertas e exibidas lado a lado (E-29-11, §4.1).

**Isso é um candidato, não uma aprovação.** O plano exige que o pesquisador aprove o gate (plano §6). Itens que a decisão deve ponderar:
1. A evidência de UB física dos 23 casos é **posterior** à AS29 original e foi gerada na seed 42 apenas; está rotulada como `AS29_POSTERIOR_EXPORT`.
2. `OPT_NUMERIC_PHYSICAL` é numérico, não racional.
3. Em AS31+, alegações de melhoria devem superar também `lb_documented_max`/`ub_documented_min` do manifesto (I065 ×2 e `hc9u`, §4.1), e não apenas o envelope.
4. O envelope é histórico; comparação de desempenho exige corrida pareada (mesmo SHA, orçamento, seeds, solver e política).
5. Itens do G0 do plano que ficam como limitação declarada: LP em 8/31, versão do Gurobi da Spec A, commit `-dirty`, ausência de data de execução (§4).

## 7. Comparabilidade das próximas etapas Y-RBC

| Medida | Regra da AS29 | Uso futuro |
|---|---|---|
| LP | ótimo LP numérico com status `OPTIMAL_NUMERIC` e mesmo SHA; formulação admissível | Não comparar como bound MIP |
| MIP LB | `ceil(bound − 1e-6)` de `U`/`U_K`/`K_IP`, com seed, orçamento e status | Comparar pares em orçamento/instância idênticos |
| UB | conjunto de estações + oráculo independente reexecutado | Sem oráculo, só `SOLVER_ONLY`; núcleo nunca é UB |
| OPT | LB = UB física → `OPT_NUMERIC_PHYSICAL`; LB = UB numérica → `OPT_NUMERIC_SOLVER_ONLY` | Nenhum é certificado racional |
| Identidade | SHA do arquivo, `r` do manifesto, `m`, fonte e partição | Registro com outro SHA é excluído (`INSTANCE_SHA_MISMATCH`) |
| Fonte | caminho, hash do artefato, hash do plano, commit gravado e commit/data de versionamento | Preservar sem sobrescrita |
| Censura | status e limites parciais conservados | Nunca converter limite de tempo/trabalho em ganho zero |
| Formulação sem prova | registrada, inadmissível no envelope | Readmitir só após gate matemático próprio |
| Partições | desenvolvimento para políticas; legado só histórico | Não consumir `avaliacao` antes do freeze AS35 |

Limitações herdadas: a Spec A gravou `commit=9b93650-dirty` e não gravou a versão do Gurobi (`solver_version` vazio; não preenchido por suposição). AS06/AS09 registram Gurobi 12.0.3. `cuts_sha256` tem dois escopos: `generator` na Spec A (hash do gerador de cortes) e `instance_K` em AS06/AS09 (hash do conjunto K da instância).

## 8. Reproduzir

```bash
poetry run python experiments/benchmark/reconcile_as29.py
poetry run python -m unittest discover -s experiments/benchmark -p 'test_reconcile_as29.py' -q
```

O script não resolve MIP/LP. Ele lê as fontes versionadas, confere os hashes de instâncias, sidecars, manifestos e planos (AS06: plano contra manifesto e `report.json`; AS09: hash canônico contra manifesto e cada registro), reexecuta o oráculo físico independente (cerca de 30 s) e escreve os dois CSVs de forma determinística. A exportação posterior das instalações (necessita Gurobi, cerca de 1 h) é um passo separado: `poetry run python experiments/benchmark/export_as29_installations.py --shard i/N`, retomável, que escreve só em `results/benchmark/as29-physical-ub-001/`. `source_versioned_in` depende do histórico git e fica vazio fora de um clone. As fontes primárias permanecem inalteradas.

Ver erratas: [`as29-erratas-e-incompatibilidades.md`](as29-erratas-e-incompatibilidades.md).
