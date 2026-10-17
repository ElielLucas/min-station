# AS25.1 — Diagnóstico e otimização da separação FC-R — Validation

**Result:** **PASS**

**Data:** 2026-10-17
**Iteração:** re-verificação 1 de 3. A primeira passada deu FAIL com 7 mutantes sobreviventes; os testes foram corrigidos e não houve mudança em código de produção.
**Spec:** `specs/as-25-1-fcr-otimizacao-separacao/spec.md` (FCR251-01..25)
**Diff range:** working tree não commitado sobre `ee40fde` (branch `novos_testes`); todos os arquivos AS25.1 estão untracked.
**Verifier:** sub-agente independente (autor ≠ verificador), somente leitura; único arquivo escrito: este `validation.md`.

**Resumo.** O separador (`fcr_lp_policy_as251.py`) é matematicamente equivalente ao código auditado AS24/AS25. A correção de testes da iteração 1 mata os 24 mutantes, inclusive os 7 que sobreviviam no analisador e no runner. Os quatro arquivos de produção têm o mesmo SHA-256 da primeira passada:
- `fcr_lp_policy_as251.py`: `bc33d9ba…`
- `analyze_fcr_lp_as251.py`: `8be079a4…`
- `run_fcr_lp_as251.py`: `3c454ac6…`
- `diagnose_fcr_as251.py`: `4efe9ae1…`

**Desvios documentados (não contam como falha):**
- Não houve commits por tarefa. O `CLAUDE.md` proíbe commit automático, e o desvio está em `tasks.md:5` e na seção Assumptions da spec.
- A campanha real AS25.1 **não foi executada**: foi apenas pré-registrada (`docs/technical/plans/execucao/as251-preregistro-fcr-lp.{json,md}`). Isso está fora do escopo de T1–T7 e não é falha.

---

## Task Completion

| Task | Status | Notas |
|---|---|---|
| T1 Índice/linhas equivalentes | ✅ Done | Equivalência confirmada por leitura e pelo sensor. |
| T2 Seleção singleton-primeiro | ✅ Done | Mutantes de adiamento, duplicata, tolerância e status mortos. |
| T3 Diagnóstico reprodutível | ✅ Done | 34 JSONs `DIAGNOSTIC_POST_HOC` em `results/benchmark/as251-diagnostico-001/`. |
| T4 Pré-registro | ✅ Done | Mutações de hash agora testadas (`test_as251_fcr.py:380-392`). |
| T5 Runner | ✅ Done | Processo próprio + prazo rígido testados (`:466-476`); cobertura adiada testada (`:460-463`). |
| T6 Analisador | ✅ Done | Digest de assinatura, 2ª rodada, tolerância, fronteiras e teto testados (`:578-616`). |
| T7 Relatório | ✅ Done | Spec corrigida: `deficit` em CC9 = +0,005 p.p. (`spec.md:43`), coerente com o JSON. |

---

## Spec-Anchored Acceptance Criteria

Arquivo de testes: `experiments/cuts/test_as251_fcr.py` (abreviado `T`, 40 testes).

| AC | Resultado definido na spec | `file:line` + asserção | Resultado |
|---|---|---|---|
| FCR251-01 | `fast_region_plan` == `choose_regions` | `T:126` — `assertEqual(choose_regions(ins, max_larger=cap, include_larger=larger), fast_region_plan(...))` (testemunha + 40 aleatórias, caps 0/3/12, com e sem maiores) | ✅ PASS |
| FCR251-02 | Linha == `construct_row(instance,L,Q,direction)` | `T:136` — `assertEqual(row, construct_row(ins, row.region, row.q, row.direction))` com `audit_rows=True`; `T:144` para todo `Q` de tamanho ≤2 | ✅ PASS |
| FCR251-03 | Mesmas assinaturas, termos e contadores que `IndexedFCR` | `T:114-118` (`assertSameSeparation`) em `T:156` e `T:158` (caps 0/2/64, com `exclude_signatures`) | ✅ PASS |
| FCR251-04 | `Q` com LHS mínimo por enumeração exaustiva, nas duas direções | `T:174` — `assertAlmostEqual(deficit, float(demand-best), places=9)`; `T:177` — `assertEqual(directions, {'origin','destination'})`; `T:178-180` | ✅ PASS |
| FCR251-05 | Reuso == índice novo | `T:207` — `assertSameSeparation(fresh, reused)`; `T:208` — `assertEqual(fresh['events'], reused['events'])` | ✅ PASS |
| FCR251-06 | `PARTIAL_SINGLETONS`, `singleton_complete=False` | `T:213` — `assertEqual(result['status'], 'PARTIAL_SINGLETONS')`; `T:214` | ✅ PASS |
| FCR251-07 | `CUT_CAP_REACHED`, `capped>0`, `global_region_separation=False` | `T:220`, `T:222`, `T:223` | ✅ PASS |
| FCR251-08 | Adia maiores, `larger_deferred=True` | `T:230` — `assertTrue(result['stats']['larger_deferred'])`; `T:231` — `larger_checked == 0` | ✅ PASS |
| FCR251-09 | Sem singleton novo, todas as maiores examinadas | `T:241` — `assertEqual(...['larger_checked'], len(index.plan.larger))`; `T:243` | ✅ PASS |
| FCR251-10 | `COMPLETE_SINGLETONS_LARGER_DEFERRED` | `T:248-249`; `T:250` (com teto → `CUT_CAP_REACHED`) | ✅ PASS |
| FCR251-11 | Assinatura excluída → `DUPLICATE`, não emitida | `T:257`; `T:259` — `assertEqual(event['decision'], 'DUPLICATE')` | ✅ PASS |
| FCR251-12 | déficit ≤ tolerância → `NO_VIOLATION_IN_FIXED_REGION` | `T:270` — `assertEqual(at['deficit'], 0.25)`; `T:271` (fronteira exata); `T:274` | ✅ PASS |
| FCR251-13 | Índice: tempos AS25/AS25.1 + igualdade de plano | `T:307` — `assertTrue(row['plan_equal'])`; `T:309-310` | ✅ PASS |
| FCR251-14 | Trace por rodada: objetivo, violados, emitidos, nnz, separação, inserção, reotimização | `T:332-333` — `assertIn(key, result['rounds'][0])` para `separation_s, insertion_s, reoptimization_s, nnz, terms_digest`; `T:327`; `T:329` | ✅ PASS (residual menor: `violated` e `objective` por rodada não são asserted por nome; estão presentes nos JSONs reais) |
| FCR251-15 | `DIAGNOSTIC_POST_HOC`, fora de gate | `T:339`, `T:340` | ✅ PASS |
| FCR251-16 | Rejeita plano com casos, hashes, solver, 90 s, política, braços ou gate diferentes | `T:362-364`; `T:392` — `assertRaises(ValueError)` sobre 13 mutações, inclusive `as25_hash`, `as16_hash` e `source_hash` (`T:380-382`) | ✅ PASS |
| FCR251-17 | 4 braços, cada um em processo próprio com 90 s | `T:403` — `assertEqual(len(rows), 24)`; `T:473-475` — `run_arm` real (spawn) com orçamento de 1 s → `TIME_LIMIT`, `elapsed < 5` | ✅ PASS |
| FCR251-18 | Registro por rodada (objetivo, linhas, nnz, digests, tempos) | `T:449` — `assertIn` de `objective_after, signature_digest, terms_digest, nnz, emitted`; `T:452`; `T:453-456` INFRA == AS25 em LP real | ✅ PASS |
| FCR251-19 | Censura sem objetivo LP | `T:424` — `assertNotIn('lp_objective', conn.sent[0])`; `T:474` — `assertIsNone(result.get('lp_objective'))` | ✅ PASS |
| FCR251-20 | Diretório existente → recusa | `T:408` — `assertRaises(FileExistsError)` | ✅ PASS |
| FCR251-21 | Gate AS25 (≥1%, ≥2 grafos, custo ≤2×) no braço AS251 | `T:512-513` (A / `GO_CANDIDATE_REVIEW`); `T:519-520` (2,05× → C / `STOP`); `T:602` — `cost_multiple == 2.0` qualifica A; `T:606` — 0,99% não é A nem C | ✅ PASS |
| FCR251-22 | `infra_equivalent` só com ambos OPTIMAL e digests idênticos por rodada | `T:591` — `assertFalse(...['infra_equivalent'])` para digest de assinatura divergente, divergência só na 2ª rodada e objetivo +1e-4; `T:595` — `assertTrue` com +1e-6; `T:537` (terms) | ✅ PASS |
| FCR251-23 | A/B/C/D pela regra congelada | `T:512` (A), `T:519` (C), `T:525` (B), `T:535`/`T:543` (D); `T:616` — o teto no candidato impede A e mantém C; `T:462` — maiores adiadas contam como cobertas | ✅ PASS |
| FCR251-24 | Flow-only → ganho zero | `T:549` — `assertTrue(marginal['flow_only_zero_bound_gain'])`; `T:550` | ✅ PASS |
| FCR251-25 | `mip_automatically_authorized=False` | `T:575` | ✅ PASS |

**Status:** 25/25 ACs com evidência que discrimina a falha. Fica uma observação residual menor de precisão em FCR251-14, que não bloqueia.

### Edge cases

- [x] Opções desconhecidas → `ValueError`: `T:286-289`.
- [x] `y`/`f` fora de `H` → `ValueError`: `T:291-293`.
- [x] `S∩T` sem singleton e isento de `Q`: `T:186`, `T:191-192`.
- [x] `r>1` usa arcos de `H`: `T:198`.

---

## Verificação matemática independente

Comparação de `fcr_lp_policy_as251.py` com `fcr_regions.py`, `fcr_rows.py` e `fcr_lp_policy.py`. Os hashes do código AS24/AS25 conferem com `results/benchmark/as25-fcr-lp-001/manifest.json`, e `git diff HEAD` em `fcr_rows.py`, `fcr_regions.py` e `fcr_separator.py` está vazio.

- **Plano** (`:41-66`). Os singletons têm `signed≠0`, o que exclui `S∩T`. Os pares candidatos são os arcos de `H` mais os pares do mesmo sinal com vizinho comum. A chave de ordenação é `(-|signed|, r)`. É idêntico a `choose_regions`.
- **Fronteira** (`:107-115`). Na origem, os arcos `(u,v)` com `u∈L, v∉L` e isenção de `T`. No destino, os arcos `(u,v)` com `v∈L, u∉L` e isenção de `S`. Isso coincide com `eligible_frontier`/`construct_row` (`fcr_rows.py:68-82,94-99`), calculado sobre `A_r` (dígrafo de alcance `H`).
- **Linha** (`:117-126`) e **Q exato** (`:128-138`). `Q = {v : agg_v > d·y_v}` minimiza LHS = total − Σ_{v∈Q}(agg_v − d·y_v). Os empates ficam fora, como na AS25.
- **Escalate** (`:162-166,214-227`). Com maiores adiadas, o status nunca é `COMPLETE_DECLARED_FAMILY`, e `global_region_separation` fica sempre `False`. Só violações novas adiam. Não há alegação falsa de completude.
- **Ressalva de risco baixo.** A ordem da soma em ponto flutuante em regiões de dois vértices difere da de `IndexedFCR`. Não houve efeito observado: digests AS25 = INFRA em todas as rodadas de CC9, BIP42, CC3 e MAPF.

---

## Discrimination Sensor

Cópia isolada (`rsync` sem `.git`) em `scratchpad/verifier/repo`. Antes da rodada, `test_as251_fcr.py` e `spec.md` foram atualizados na cópia; os arquivos de produção da cópia têm SHA-256 idêntico ao da árvore real. O baseline sem mutação deu 40/40 OK. Os testes rodaram com o Python do venv Poetry e cwd na cópia, e foi confirmado que nenhum módulo `fcr*` foi importado da árvore real. Cada mutante foi aplicado, testado e revertido.

| # | Arquivo:linha | Mutação | Passada 1 | Iteração 1 |
|---|---|---|---|---|
| M1 | `fcr_lp_policy_as251.py:59` | remove os pares de terminais | ✅ | ✅ Morto |
| M2 | `:114` | terminal isento elegível para `Q` | ✅ | ✅ Morto |
| M3 | `:136` | `>` → `>=` na escolha de `Q` | ✅ | ✅ Morto |
| M4 | `:179` | `<=` → `<` na tolerância | ✅ | ✅ Morto |
| M5 | `:164` | escalate nunca adia | ✅ | ✅ Morto |
| M6 | `:164` | duplicatas contam como novas | ✅ | ✅ Morto |
| M7 | `:153` | ignora `exclude_signatures` | ✅ | ✅ Morto |
| M8 | `:153` | `seen` vaza entre chamadas | ✅ | ✅ Morto |
| M9 | `:219` | adiado → `COMPLETE_DECLARED_FAMILY` | ✅ | ✅ Morto |
| M10 | `:120` | omite um termo de fluxo | ✅ | ✅ Morto |
| M23 | `:193` | `deficit` ascendente | ✅ | ✅ Morto |
| M24 | `:170` | ignora o limite de tempo | ✅ | ✅ Morto |
| M11 | `analyze_fcr_lp_as251.py:118` | remove o limiar de eficiência | ✅ | ✅ Morto |
| M12 | `:33` | ignora `terms_digest` | ✅ | ✅ Morto |
| M13 | `:32` | ignora `signature_digest` | ❌ | ✅ Morto |
| M14 | `:124-127` | troca a ordem C/B | ✅ | ✅ Morto |
| M15 | `:36` | ignora a tolerância de objetivo | ❌ | ✅ Morto |
| M16 | `:46` | cobertura ignora o teto de cortes | ❌ | ✅ Morto |
| M17 | `:31` | compara só a 1ª rodada | ❌ | ✅ Morto |
| M19 | `:89` | custo `<=` → `<` | ❌ | ✅ Morto |
| M20 | `:153` | MIP autorizado | ✅ | ✅ Morto |
| M18 | `run_fcr_lp_as251.py:64` | ignora os hashes AS25/AS16 | ❌ | ✅ Morto |
| M21 | `:42` | braço AS251 com `always` | ✅ | ✅ Morto |
| M22 | `:121` | adiadas não contam como cobertas | ❌ | ✅ Morto |

**Profundidade:** expandida (24 mutantes). **Resultado:** 24/24 mortos — **PASS**.
**Isolamento:** o `git status --porcelain` da árvore real ficou idêntico ao baseline capturado no início da verificação. Este `validation.md` fica num diretório já untracked e por isso não altera a listagem.

---

## Gate Check

- **Quick:** `poetry run python -m unittest experiments.cuts.test_as251_fcr -q` → `Ran 40 tests in 4.250s — OK`
- **Full:** `poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q` → `Ran 244 tests in 35.353s — OK` (Gurobi 12, 0 skips)
- **Build** (passada 1, sem mudança desde então em `tasks.md`): `validate_spec.py` 0 erros; `validate_tasks.py` 0 erros e 2 avisos esperados (T4/T7 `Tests: none`).
- **Contagem:** 204 antes da feature → 244 (+40). Nenhum teste removido ou enfraquecido; a iteração 1 só acrescentou testes e asserções.

---

## Conferência do diagnóstico

Os 10 números de `as251-diagnostico-fcr.md` foram conferidos contra os JSONs na passada 1 e batem:
- tempos de índice de CC3 e MAPF e igualdade de plano;
- W3C571;
- fechos de 0,205%, 0,606%, 0% e 1,172%;
- MAPF com 16 e 37 rodadas, em 13,28;
- BIP42 na rodada 13 com 2.506 linhas e 79,1 s;
- MAPF parado em 13,247059;
- BIP42 com `deficit` 0,0007% e 167–180 linhas cortadas pelo teto;
- digests AS25 = INFRA;
- índice ocupando 48–90% do tempo de parede na AS25.

A divergência que existia na spec (+0,014 p.p.) foi corrigida para +0,005 p.p. (`spec.md:43`), que é o valor de `trace-puc-cc9-2p-deficit.json` (0,1143%) contra `as25` (0,1090%).

---

## Code Quality

| Princípio | Status |
|---|---|
| Código mínimo / sem escopo extra | ✅ |
| Mudanças cirúrgicas (AS24/AS25, COMP e K intocados; a iteração 1 mudou só testes e um número da spec) | ✅ |
| Segue os padrões existentes | ✅ |
| Spec-anchored outcome check | ✅ |
| Cobertura por camada | ✅ |
| Todo teste mapeado a AC, edge case ou Done-when | ✅ |
| Diretrizes `CLAUDE.md` / `docs/context-ai/code-guidelines.md` | ✅ |

---

## Gaps residuais (nenhum bloqueante)

1. **[Minor]** FCR251-14: `violated` e `objective` por rodada do `trace` não são asserted por nome (`T:332`). Estão presentes nos JSONs reais.
2. **[Minor]** O novo teste `T:466` depende do caso real Vienna I056 e de spawn de processo. É mais lento e sensível ao ambiente, mas foi aceito porque exercita o caminho real do prazo rígido.
3. **[Info, fora de escopo]** `plano-fcr-as23-as27.md` e `specs/as-25-fcr-lp-pareado/*` dizem que a campanha AS25 não foi executada, mas os resultados (`INVESTIGATE`) existem. O relatório AS25.1 §1 registra a divergência sem reconciliá-la, como o `CLAUDE.md` pede.
4. **[Info]** A campanha AS25.1 está pendente, depende de commit aprovado pelo pesquisador, e a expectativa pré-registrada é a classe B.

---

## Requirement Traceability Update

| Requirement | Anterior | Novo |
|---|---|---|
| FCR251-01..25 | Implemented (FCR251-16/22/23 em Needs Fix na passada 1) | ✅ Verified |

---

## Summary

**Overall:** ✅ Ready, no escopo de implementação e testes; a campanha está fora do escopo.
**Spec-anchored:** 25/25. **Sensor:** 24/24 mortos. **Gate:** 40/40 quick; 244/244 full.
**Próximo passo:** o pesquisador decide sobre o commit e, depois, executa a campanha pré-registrada.
