# Next Phase A — Foundation and Experimental Baseline (MIN-STATION) Specification

Scope: tasks R1–R4 of `docs/technical/plans/plano-proxima-fase.md` (the source of truth for the
current research program). This spec makes the repository clean, versioned and experimentally
comparable, and produces the official reference bounds `LB*` and `UB*` against which every later
claim of advance is measured.

It is **foundation, not a method experiment**: no new formulation, cut or heuristic is evaluated
here.

Evidence vocabulary (from the plan): **[Fato]** verified in this session; **[Conferido]** argument
re-derived but not yet written in the repository; **[Evid.]** measured result with its protocol
grade; **[Hipótese]** untested; **[Sugestão]** planning proposal.

---

## Relationship with the other next-phase specs

| Spec | Relation to this spec |
|---|---|
| B — `proxima-fase-b-formulacoes-fcc-fc3` | Depends only on **R1** (final file names and status headers). Does not need R2–R4 |
| C — `proxima-fase-c-diagnostico-gap-plato` | R5, R7 and the certified part of R6 depend only on **R1**. The D/A part of R6 depends on **R4** (`LB*`/`UB*`) |
| D — `proxima-fase-d-certificadores-classes-especiais` | Depends only on **R1** (renamed Pereira & Ravelo file) |

---

## Current State (audited 2026-10-04, read-only)

| Item | Status | Evidence |
|---|---|---|
| `plano-proxima-fase.md` saved | DONE | Header rewritten; rename applied; remaining R1 hygiene in `r1-changelog.md` |
| Renaming of `formulacao-min-station-alternativa-{1,2}.md` and the Pereira & Ravelo `.md` | DONE | `formulacao-fcc-configuracoes-conectadas.md`, `formulacao-fc3-consistencia-trios.md`, `pereira-ravelo-2026-aranhas.md` |
| Status headers on formulation files | DONE | Headers on F-CC and F-C3, 2026-10-04 |
| Removal of F-OD from the F-C3 file | DONE | `grep F-OD` on that file is empty; chain is `base ≤ F-CC ≤ F-C3 ≤ OPT` |
| `open-questions.md` | DONE | Q1 lists the 5 `principal` with `S∩T ≠ ∅`; Q3 closed by T5; Q6 = COMP; Q7 closed by H11 |
| `direcoes-pli-min-station.md` header | DONE | Header no longer claims every instance has `S∩T = ∅` |
| Partition of benchmark-v1 by origin graph | DONE | `regra-particao-origem.md`; 0 vazamento; `verify_t8_consolidacao.py` ok |
| 12 SC Phase-E instances in the manifest | DONE | 12 rows, `classe=estrutural`; manifesto com 149 linhas |
| Tag `benchmark-v1.0` | FROZEN, UNTAGGED | Sem autorização de commit |
| Protocol-compliant 3-seed baseline, `LB*`/`UB*` | DONE | 411 linhas em `results/benchmark/linha_base.csv`; tabela em `docs/technical/reference/resultados-linha-de-base.md` |
| AV-1..AV-4 thresholds | PENDING USER CONFIRMATION | Marked as pending in the plan §2 |

**Reusable infrastructure [Fato]:** `harness.measure_mip(coletar_incumbente=True)` (T9),
`cortes_ordenados` (T6), `WorkLimit` handling in `experiments/structural/piloto.py`, the
calibration procedure in `docs/technical/reference/piloto-fase-p.md`, core solvers
(`run_e12.py:nucleo`, `piloto.py:_resolver_nucleo`, `medir.py:nucleo`),
`experiments/benchmark/verify_t8_consolidacao.py`, `src/converters/build_manifest.py`
(`--so-grupos`), and `docs/technical/reference/protocolo-comparacao-pareada.md`.

---

## Problem Statement

The next research phase must measure a "considerable advance", but every headline number the
project has today is pre-protocol: E9–E14 ran with one seed, `TimeLimit`, before deterministic model
construction (T6), and on a development/evaluation partition that still leaks 11 origin graphs. In
addition, the documents that later specs depend on are out of date: the two formulations under
evaluation and the Pereira & Ravelo article carry provisional file names (one with spaces), the F-C3
file still cites the discarded F-OD formulation, and `open-questions.md` lists four questions with a
status that the evidence already settled. Without cleaning these up and producing an official,
protocol-compliant baseline, no later spec can state that a method improved anything.

## Goals

- [x] Every file and document the next-phase specs depend on has its final name, a status header
      where applicable, and no stale statement about closed questions.
- [x] The benchmark partition is assigned by origin graph with zero leakage, frozen as
      `benchmark-v1.0` (tag only with user authorization).
- [x] A pre-registered baseline (base U, COMP, core) is executed under the paired protocol and
      produces official `LB*` and `UB*` per instance.

## Out of Scope

| Item | Reason |
|---|---|
| Implementing or measuring F-CC / F-C3 | Spec B |
| Measuring `Γ`, primal-slack test, plateau anatomy | Spec C |
| Paths / cycles / spiders algorithms | Spec D |
| R8 column generation, R9 branch-and-price, R10 compatibility inequalities, R12 matheuristic, R13 confirmation | Conditional on gates GF1, G1, G2 — **BLOCKED**, no spec yet |
| Rewriting any historical result or report (E0–E14, Blocks 1–4) | Results are history; only headers and pointers change |
| The "Passo posterior" edits of `overlap-ijcai2026-min-station.md` §7.1, benchmark licenses, datasheet | Deferred by the plan: no article is being written now |
| Commits and git tags | Only with explicit user authorization (`CLAUDE.md`) |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| New file names | `formulacao-fcc-configuracoes-conectadas.md`, `formulacao-fc3-consistencia-trios.md`, `pereira-ravelo-2026-aranhas.md` | Plan §6.4; matches `formulacao-*` and `desagregacao-por-origem.md`; no spaces | y (plan approved) |
| Partition rule | Deterministic: every variant of an `instancia_original` goes to the same side, chosen by a stable hash of `instancia_original` (e.g. SHA-256 of the string), targeting about 1/3 development and 2/3 evaluation per family | Removes leakage by construction; written before looking at any method result | n |
| `WorkLimit` for the baseline | Recalibrated for **4 threads** with the procedure of `piloto-fase-p.md` on one pre-declared instance, before any comparison is read | The existing value 297 was calibrated with 1 thread; reusing it would silently change the budget | n |
| Instances with `m ≥ 1000` | Run in the baseline but declared outside the advance evaluation (stagnated by scale, as in E12) | Avoids counting scale stagnation as structural difficulty | n |
| Seeds | 3 solver seeds on every D/A instance; 1 seed on F/M instances | Plan R3; margins of 1–2 units on D/A need 3 seeds (protocol item 3) | n |
| AV-1..AV-4 | Recorded verbatim from the plan §2 as **PENDING USER CONFIRMATION**; not treated as immutable requirements | The plan marks them as a pending user decision | n — PENDING USER CONFIRMATION |
| Commit and tag `benchmark-v1.0` | Prepared but not executed without explicit user authorization | `CLAUDE.md`: no automatic commits | n — user decision required |

**Open questions:** none — every pending user decision is recorded above with its default.

---

## Pre-registration (baseline, R3)

| Item | Value |
|---|---|
| Arms | **base U** (the formulation of `baseline.py`, no static cuts), **COMP** (U + C1+C2+C4, continuous `f`, the official comparison baseline), **core** (IP in `y` with C1+C2+C4-DM) |
| Instances | The 75 `classe = principal` rows of `instances/manifest.csv`; structural instances excluded |
| Budget | `WorkLimit` recalibrated for 4 threads; `TimeLimit` only as a wall guard, reported when it fires |
| Threads | 4 |
| MIP start | None in any arm |
| Seeds | 3 on D/A, 1 on F/M (seed values fixed in the pre-registration file) |
| Metrics | The T9 schema (`schema-instrumentacao-mip.md`): LB, UB, gap, status, `NodeCount`, time to first incumbent, time to best incumbent, time to proof, work |
| Provenance | Instance sha256, commit, cut-generator version, seed, threads, budget, certificate source |
| Control | The arms are the reference; there is no experimental arm in this spec |
| Decision gate | None scientific. Exit = official `LB*`/`UB*` frozen |

---

## User Stories

### P1: R1 — Minimal clean-up and renaming ⭐ MVP

**User Story**: As a researcher about to open three parallel specs, I want the files they depend on
renamed, annotated and free of stale claims, so that no spec builds on a document that contradicts
the current evidence.

**Why P1**: Specs B, C and D depend on it.

**Acceptance criteria:**

1. WHEN R1 is executed THEN the system SHALL rename `formulacao-min-station-alternativa-1.md` to `formulacao-fcc-configuracoes-conectadas.md`, `formulacao-min-station-alternativa-2.md` to `formulacao-fc3-consistencia-trios.md`, and the Pereira & Ravelo `.md` to `pereira-ravelo-2026-aranhas.md`.
2. The system SHALL add to each formulation file a status header stating origin (external proposal), what was re-derived in the planning analysis, what is hypothesis, and what is missing (the F-C3 proof document), without changing the mathematical body.
3. The system SHALL remove every mention of F-OD from the F-C3 file and state the dominance chain as `base ≤ F-CC ≤ F-C3 ≤ OPT`.
4. The system SHALL register Pereira & Ravelo in `source-map.md` and list F-CC/F-C3 there as formulations under evaluation, never as the baseline.
5. The system SHALL update `open-questions.md` so that Q1's body reflects the 5 `principal` instances with `S∩T ≠ ∅`, Q3 is closed by T5, Q6 is closed with COMP as the official comparison baseline, and Q7 records the H11 decision.
6. The system SHALL correct the header of `direcoes-pli-min-station.md` that states `S∩T = ∅` for all instances.
7. The system SHALL mark `plano-pos-e13.md`, `plano-pos-e8-adiado.md` and `plano-benchmark-v1.md` as historical and point `backlog-continuacao.md` to `plano-proxima-fase.md`.
8. The system SHALL correct the stale header "Ação única ao aprovar" of `plano-proxima-fase.md` to describe what was actually done.
9. IF any edit would alter a reported number or verdict THEN the system SHALL NOT apply it.

**Required tests:** `grep` for the old file names and for `F-OD` returns nothing; `grep` confirms no
closed question remains marked open.

**Evidence to produce:** a short changelog listing every edited file and line range.

**Risks:** silently changing a historical statement. Criterion 9 forbids it.

**Dependencies:** none.

**Independent Test**: after R1, `git status` shows only renames and the listed documents.

---

### P1: R2 — Partition by origin graph and `benchmark-v1.0`

**User Story**: As a researcher who will claim an advance on the evaluation partition, I want no
origin graph to appear on both sides, so that development tuning cannot leak into evaluation.

**Why P1**: The baseline (R3/R4) and every later evaluation depend on the partition.

**Acceptance criteria:**

1. The system SHALL write the partition rule in a versioned document before reassigning any instance.
2. The system SHALL assign every variant of the same `instancia_original` to the same side.
3. The system SHALL NOT use any method result (LB, UB, gap, time, nodes) to decide the side of an instance.
4. WHEN the partition is regenerated THEN the system SHALL report zero groups with leakage in `instances/grupos_origem.csv`, verified by `experiments/benchmark/verify_t8_consolidacao.py`.
5. The system SHALL register the 12 SC Phase-E instances in `manifest.csv` with class `estrutural`.
6. The system SHALL preserve all manual corrections already in the manifest (C4-DM fixes, H17 columns).
7. IF the user authorizes a commit THEN the system SHALL create the tag `benchmark-v1.0` on that commit; otherwise the state is recorded as "frozen, untagged".

**Required tests:** `verify_t8_consolidacao.py` with zero leakage; a diff of the manifest restricted
to `particao` and the 12 new rows.

**Evidence to produce:** the rule, the before/after partition table per family, the verifier output.

**Risks:** the 1/3–2/3 target is approximate per family; small families may deviate. Record the
achieved ratio instead of forcing it.

**Dependencies:** R1.

**Independent Test**: re-running the rule twice produces the same partition byte for byte.

---

### P1: R3 — Baseline pre-registration

**User Story**: As a researcher who must not choose the budget after seeing results, I want the
baseline frozen in writing before the first solve.

**Why P1**: Without it the baseline is not protocol-compliant.

**Acceptance criteria:**

1. The system SHALL write the pre-registration (arms, instances, budget, threads, seeds, metrics, provenance) before any baseline solve.
2. WHEN the `WorkLimit` is calibrated THEN the system SHALL use 4 threads, one pre-declared instance, and the procedure of `piloto-fase-p.md`, and SHALL record the measured work rate.
3. The system SHALL declare the instances with `m ≥ 1000` as outside the advance evaluation before running them.
4. The system SHALL record AV-1..AV-4 verbatim from the plan with the status PENDING USER CONFIRMATION.
5. The system SHALL fill the checklist of `protocolo-comparacao-pareada.md` for the three arms.

**Required tests:** none; the check is the timestamp of the pre-registration preceding the first CSV
row.

**Evidence to produce:** `docs/technical/reference/linha-de-base-pre-registro.md` (name to confirm).

**Risks:** calibration on one instance may not represent all families; this is a documented property
of `WorkLimit`, not a reason to recalibrate per family.

**Dependencies:** R2.

**Independent Test**: a reader can rerun the whole baseline from the pre-registration alone.

---

### P1: R4 — Baseline execution

**User Story**: As a researcher who will compare future methods, I want official reference bounds per
instance with full provenance.

**Why P1**: `LB*`/`UB*` are the reference for AV-1..AV-4 and for the D/A part of Spec C.

**Acceptance criteria:**

1. The system SHALL run exactly the pre-registered arms, instances, budget and seeds, without adding an arm during the run.
2. The system SHALL persist, per run, the T9 metrics and the provenance fields of the pre-registration.
3. The system SHALL compute per instance `LB*` as the best LB and `UB*` as the best UB across arms and seeds, recording which arm and seed produced each.
4. The system SHALL compare the results with E9 and E12 only as context, stating which qualitative readings held and which changed.
5. IF a wall-clock guard fires before the work limit THEN the system SHALL mark that row and keep it in the table.

**Required tests:** row count equals the pre-registered design; every row has sha256 and commit.

**Evidence to produce:** CSV under `results/`, a report with the `LB*`/`UB*` table, and the E9/E12
context comparison.

**Risks:** machine load affects wall time but not work; report work as the budget measure.

**Dependencies:** R3.

**Independent Test**: one row can be reproduced from the pre-registration in a clean checkout.

---

## Stop Criteria

This is a foundation spec: it ends when R4's report exists. It is never extended with more time,
more arms or more seeds without a new pre-registration.

## Edge Cases

- IF an instance has no incumbent in any arm (as `puc-hc12p-seed-r1` in E12) THEN `UB*` SHALL be
  recorded as missing, not imputed.
- IF the hash rule leaves a family entirely on one side THEN the achieved ratio SHALL be reported
  and the rule SHALL NOT be changed after the fact.
- IF a renamed file is referenced by a document written after the audit THEN the reference SHALL be
  updated in the same edit.
- IF the user does not authorize a commit THEN the benchmark SHALL be recorded as frozen but
  untagged, and later specs SHALL cite the working-tree state explicitly.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| FOUND-01 | P1: R1 | Design | Pending |
| FOUND-02 | P1: R1 | Design | Pending |
| FOUND-03 | P1: R1 | Design | Pending |
| FOUND-04 | P1: R1 | Design | Pending |
| FOUND-05 | P1: R1 | Design | Pending |
| FOUND-06 | P1: R1 | Design | Pending |
| FOUND-07 | P1: R1 | Design | Pending |
| FOUND-08 | P1: R1 | Design | Pending |
| FOUND-09 | P1: R1 | Design | Pending |
| FOUND-10 | P1: R2 | Design | Pending |
| FOUND-11 | P1: R2 | Design | Pending |
| FOUND-12 | P1: R2 | Design | Pending |
| FOUND-13 | P1: R2 | Design | Pending |
| FOUND-14 | P1: R2 | Design | Pending |
| FOUND-15 | P1: R2 | Design | Pending |
| FOUND-16 | P1: R2 | Design | Pending |
| FOUND-17 | P1: R3 | Design | Pending |
| FOUND-18 | P1: R3 | Design | Pending |
| FOUND-19 | P1: R3 | Design | Pending |
| FOUND-20 | P1: R3 | Design | Pending |
| FOUND-21 | P1: R3 | Design | Pending |
| FOUND-22 | P1: R4 | Design | Pending |
| FOUND-23 | P1: R4 | Design | Pending |
| FOUND-24 | P1: R4 | Design | Pending |
| FOUND-25 | P1: R4 | Design | Pending |
| FOUND-26 | P1: R4 | Design | Pending |

**Coverage:** 26 total, 0 mapped to tasks (`tasks.md` not created in this round), 26 unmapped.

---

## Success Criteria

- [x] No document the next-phase specs depend on carries a provisional name, an F-OD mention or a
      stale question status.
- [x] Zero leakage by origin graph, verified by the existing verifier.
- [x] Pre-registration timestamped before the first baseline row.
- [x] Official `LB*`/`UB*` per instance with full provenance.

---

## Inconsistencies Found During Specification

| # | Inconsistency | Class |
|---|---|---|
| 1 | `plano-proxima-fase.md` says "Ação única ao aprovar: salvar + renomear", but only the copy was done | documentation stale |
| 2 | The plan's DAG places R7 after R4; R7 only needs certified OPT and the core | plan stricter than needed (handled in Spec C) |
| 3 | `WorkLimit = 297` was calibrated with 1 thread; the baseline uses 4 threads | plan ahead of implementation — recalibrate in R3 |
| 4 | F-OD still cited in `alternativa-2.md`; removed only in the plan | plan ahead of implementation |
| 5 | AV-1..AV-4 pending | user decision required |
| 6 | The tag `benchmark-v1.0` needs a commit; `CLAUDE.md` forbids automatic commits | user decision required |

---

## Future conditional work — BLOCKED

R8 (column generation), R9 (branch-and-price), R10 (compatibility inequalities), R12
(matheuristic) and R13 (confirmation) have **no spec**. They are created only when Spec B's GF1 or
Spec C's G1 releases them, and R13 only when a method passes G2. Nothing in this spec authorizes
them.
