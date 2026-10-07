# Next Phase N2 — Certified Compatibility Bound (MIN-STATION) Specification

**Status:** `CONDITIONAL — IMPLEMENT ONLY AFTER N1 SELECTS THE REPRESENTATION`
(created 2026-10-07, branch `novos_testes`, HEAD `0f16925`). **BLOCKED BY N1.**
**Authority:** `docs/technical/plans/historico/Analise-consolidada-MIN-STATION-2026-10-07.md`, §8, §13 Q1,
§14 (R8 `REORDER`, R10 `MERGE`), §16, §17 N2, §19.

## Scope

N2 answers, for the **single** representation selected by the N1 decision record: can that
information produce a **globally valid** lower bound for MIN-STATION that is strong enough and cheap
enough, without enumerating the whole formulation? It is a decision of **strength × certification ×
cost**, at the **root only**. It is not a branch-and-price decision.

Nothing in this spec may be implemented, measured or pre-registered with instance results until the
activation condition holds. Writing this spec now freezes the certification rules and the success
threshold before any N1 number exists.

Claim vocabulary and notation (F-C3, C3-cut, K, COMP, core IP, `B0`) are those of the N1 spec
(`specs/proxima-fase-n1-informacao-compatibilidade/spec.md`).

---

## Relationship with Previous Specs

| Spec | Relation |
|---|---|
| A — Foundation | Official baseline, budget unit (`WorkLimit`) and partition by origin reused unchanged |
| B — F-CC/F-C3 | GF1 = PASS justified investigating F-CC; it did **not** authorize R8 by itself. Spec B's "Future conditional work" (R8 prefix `CG-*`) is superseded by this spec |
| C — Gap/plateau | G1 is an operational gate toward LB research. Spec C's "released" R8/R10 lines are superseded: R8 and R10 are one question here, with one path |
| D — Special-class certifiers | `CONFIRMED DIVERGENCE`; no literal R11 procedure validates N2 results |
| N1 | **Hard dependency.** Its decision record selects the path and supplies full-enumeration LP values for regression |
| N3 | Not created; sketched below as `BLOCKED — DO NOT IMPLEMENT` |
| N4 | Not created; independent of N2 |

---

## Current State (audited 2026-10-07, read-only)

| Item | State | Evidence |
|---|---|---|
| N1 decision record | OPEN | N1 not executed |
| Pricing, reduced cost, F-CC dual | OPEN | No code, no document (`grep` over `*.py`/`*.md`) |
| Column generation / restricted master | OPEN | None |
| Farley or Lagrangian bound for an F-CC master | OPEN | None; the old baseline Lagrangian is a different object |
| Projected compatibility inequality | OPEN | None; C6 (first-hop Hall) valid but insufficient (`tecnico/c6-hall-primeiro-salto.md`) |
| Full-enumeration F-CC LP on small instances | DONE for 15 F3 rows | `results/alternative-formulations/f3-fcc.csv`; SC-GF2-k3 `NOT MEASURED` |
| Enumeration limit | Reached | SC-GF2 (21 vertices) exceeds 200 000 connected sets |
| R9 (branch-and-price) | BLOCKED | Requires a useful certified N2 |

---

## Problem Statement

F-CC's LP is stronger than the available bounds on small `Γ > 0` instances, but its connected sets
explode before reaching the hard benchmark instances. A restricted set of columns, or a projected
family of inequalities, might keep part of the strength at controlled cost. However, a restricted
master of a minimization problem can overstate the bound, heuristic pricing proves nothing, and
simplifications of pricing can silently change the problem. N2 must decide whether the representation
chosen by N1 yields a certified bound worth using, before any tree search is considered.

## Scientific Question

> Can the information selected in N1 generate a globally valid lower bound for MIN-STATION that is
> sufficiently strong and sufficiently cheap without enumerating the whole formulation?

## Hypotheses

| ID | Hypothesis | Status |
|---|---|---|
| H-N2-1 | Only part of the configurations, or a projected family of inequalities, is needed to recover a useful share of the N1 gain | `HYPOTHESIS` |
| H-N2-2 | Certifying that share requires treating the remaining columns implicitly (exact pricing or a derived dual bound) | `HYPOTHESIS` |

## Goals

- [ ] One path (A or B) implemented at the root, as selected by N1.
- [ ] Every reported LB certified by a rule written before measurement.
- [ ] Agreement with the full-enumeration LP on all small instances of N1.
- [ ] A cost-decomposed curve of certified LB against total work on two structure types and two size levels.
- [ ] A pre-registered verdict `N2 PASS` or `N2 FAIL`.

## Out of Scope

| Item | Reason |
|---|---|
| Full branch-and-price, branching rules, node pricing | Analysis §16: postpone until the root shows value |
| Price-and-branch presented as exact | Heuristic unless certified |
| Implementing both paths at once | One path only; at most one justified change |
| F-C3 at scale or a broad F-C3 campaign | Only as path B trio variant, if N1 selects it |
| Spatial decomposition, classical Benders, the old baseline Lagrangian | Not stronger / different objects |
| Primal heuristics (R12), confirmation (R13) | Blocked |
| Running the whole benchmark-v1 | N3 territory, after N2 PASS |
| Changing baseline U, COMP or the core | They are the references |
| New synthetics to obtain timeouts | Instances answer the N2 question only |
| Moving instances between development and evaluation | Partition frozen |
| Literal R11 procedures as oracle | `CONFIRMED DIVERGENCE` |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Spec created before N1 | Allowed as `CONDITIONAL`; no path chosen | User decision 2026-10-07 | y |
| Path mapping from N1 | Projected inequality → path A; F-CC + K → path B; F-C3 → path B trio variant | N1 frozen tie-break | y |
| Recovery threshold | `≥ 50%` of the positive increment of the full-enumeration LP over `B0`, on cases where that LP is known | Analysis §17 N2; frozen now, before measurement | y |
| Reference bound for "gain" | `B0 = max(z_COMP^LP, z_core^IP)` on the same instance, same budget accounting | N1 metric | y |
| Size levels and structure types | Chosen in task N2-T1 after activation, before any N2 measurement, from N1 instances (level 1) and development-partition or structural instances above the enumeration cap (level 2) | N1 decides which structures carry the mechanism | y |
| Budget unit | `WorkLimit` as frozen by Spec A, plus wall time and memory recorded; all subsolves count | Analysis §19 | y |
| Integer rounding | Certified LB `L` reported with `⌈L − 1e-6⌉` as valid integer bound (objective is integer) | Objective counts stations | y |
| Representation changes | At most one, justified by a written diagnosis | Analysis §17 N2 | y |
| Trio variant pricing | Requires its own derivation of how trio networks interact with generated columns before any code | No derivation exists | y |

**Open questions:** none — every pending decision is recorded above with its default; the choice of
path is not open but delegated to the N1 decision record.

## Decisions

| ID | Decision |
|---|---|
| D-N2-1 | Root only; no branching |
| D-N2-2 | One initial path, chosen by N1, never by preference |
| D-N2-3 | No value is called "LB do MIN-STATION" without certification status `CERTIFIED` |
| D-N2-4 | No commit without explicit user approval |

---

## Mathematical Preconditions

1. N1 decision record exists and is not `NO INCREMENTAL TARGET FOUND`.
2. P1, P2, P7 `PROVEN` (N1 story 1); for the trio variant, MR-F3 accepted.
3. Path A: written validity proof of the inequality for every installation, including `S∩T`,
   permanence and terminals as relays.
4. Path B: written primal and dual of the master (F-CC + K, columns `W` with marginals or `(W,I,J)`),
   reduced-cost formula, and formal pricing problem, all reviewed before code.
5. Any bound under incomplete pricing: derivation specific to this master (Farley, Lagrangian or
   equivalent), reviewed before code.

---

## User Stories

### P1: Story 1 — Activation and pre-registration (task N2-T1) ⭐ MVP

**User Story**: As the owner of the program, I want N2 to start only from an N1 decision and with its
instances and thresholds frozen, so that N2 tests one representation without post-hoc choices.

**Why P1**: Prevents R8 from being treated as automatically authorized.

**Acceptance Criteria**:

1. WHILE the N1 decision record is absent or reads `NO INCREMENTAL TARGET FOUND` the system SHALL NOT write N2 code, measure, or pre-register instance results.
2. WHEN N1 names a representation THEN the system SHALL select exactly one path by the frozen mapping and record it.
3. The system SHALL write, before any N2 measurement, the pre-registration: path, two structure types, two size levels, instances per level, reference bounds, budget, threshold `≥ 50%`, certification rule and stop rule.
4. IF a second path is considered THEN the system SHALL require a written diagnosis of the first path's failure and SHALL allow at most one such change.

**Independent Test**: the pre-registration timestamp precedes every N2 result file.

---

### P1: Story 2A — Path A: projected compatibility inequality (task N2-T2A)

**User Story**: As a researcher, I want the inequality selected by N1 formalized, proven and separated
with an independent check, so that adding it can only produce valid bounds.

**Why P1**: Applies only if N1 selects path A.

**Acceptance Criteria**:

1. WHERE path A is selected the system SHALL state the inequality family formally and SHALL provide a written validity proof for every installation `C`.
2. WHERE path A is selected the system SHALL provide an independent validator that checks every generated inequality against all installations `C ⊆ V` on instances with `n ≤ 12`.
3. WHERE path A is selected the system SHALL implement a separation routine and SHALL label it exact or heuristic.
4. WHERE path A is selected the system SHALL report the LP with the separated inequalities as a valid lower bound only because each added inequality is valid, and SHALL record the separation status at termination.

**Independent Test**: the validator reports zero installations cut that are feasible by `viavel`.

---

### P1: Story 2B — Path B: F-CC column generation at the root (task N2-T2B)

**User Story**: As a researcher, I want F-CC + K solved by column generation at the root with a
formally derived pricing problem, so that the strength of F-CC is obtained without full enumeration.

**Why P1**: Applies only if N1 selects path B.

**Acceptance Criteria**:

1. WHERE path B is selected the system SHALL document the primal master, its dual, and the reduced cost of a column before writing code.
2. WHERE path B is selected the system SHALL formalize pricing including connectivity of `W` in `H = G^r`, eligibility `S_W = S ∩ B(W)` and `T_W = T ∩ B(W)`, balance `|I| = |J| ≥ 1` (or CA4–CA5 in marginal form), the station linking rows and the duals of K.
3. WHERE path B is selected the system SHALL label each pricing call exact or heuristic and SHALL record its outcome.
4. IF pricing is heuristic THEN the system SHALL use its columns only to enlarge the master and SHALL NOT infer absence of improving columns from it.
5. WHERE path B is selected the system SHALL start from columns that make the master feasible (e.g. direct pairs and singleton/connected sets) and SHALL NOT branch.
6. WHERE the trio variant is selected the system SHALL first derive how trio networks couple with generated columns and SHALL NOT code it before that derivation is reviewed.

**Independent Test**: on every N1 small instance the converged master equals the full-enumeration
F-CC + K LP within `1e-6`.

---

### P1: Story 3 — Certification rule (task N2-T3)

**User Story**: As a reader of N2 results, I want every number marked with its certification status,
so that a restricted master is never mistaken for a lower bound.

**Why P1**: Central scientific risk of R8 (analysis §8, §19).

**Acceptance Criteria**:

1. The system SHALL NOT report the objective of a restricted master as a lower bound of MIN-STATION.
2. The system SHALL mark a bound `CERTIFIED` only when exact pricing proves no column with negative reduced cost beyond `1e-6`, or when a derived global bound valid under incomplete pricing is computed, or when (path A) every added inequality is valid.
3. WHERE a Farley, Lagrangian or equivalent bound is used the system SHALL derive it for this master in writing and SHALL NOT reuse the old baseline Lagrangian by analogy.
4. IF pricing is interrupted (budget, time, memory) THEN the system SHALL report the last certified bound, or `UNCERTIFIED` if none exists.
5. The system SHALL NOT fix the matching in advance, cover `S` and `T` separately without a proof of equivalence, remove `S∩T`, or treat terminals as free relays.
6. IF a simplification of the pricing problem is proposed THEN the system SHALL require a written proof that it preserves the master's LP before using it.

**Independent Test**: every row of the N2 CSV has a `certification_status` in
{`CERTIFIED`, `UNCERTIFIED`} and a non-empty justification field.

---

### P1: Story 4 — Regression against full enumeration (task N2-T4)

**User Story**: As a researcher, I want N2 reproduced against the full LP on small instances, so
that implementation errors cannot pass as bound gains.

**Why P1**: Main correctness regression.

**Acceptance Criteria**:

1. WHEN path B converges on an instance with known full F-CC (+K) LP THEN the system SHALL match it within `1e-6`.
2. WHEN path B does not converge THEN the system SHALL report a certified bound and SHALL show that it is at most the full LP within `1e-6`.
3. WHEN path A runs on an instance with known OPT THEN the system SHALL check that the bound does not exceed OPT by more than `1e-6`.
4. IF any regression fails THEN the system SHALL stop measurements at level 2 until it is resolved.

**Independent Test**: regression script exits 0 on all N1 instances within caps.

---

### P1: Story 5 — Evidence and cost accounting (task N2-T5)

**User Story**: As the owner of the program, I want strength and full cost recorded together, so that
the decision weighs both.

**Why P1**: A bound that costs more than it gains is a negative result.

**Acceptance Criteria**:

1. The system SHALL record per run: certified LB, continuous LB, valid integer rounding, `WorkLimit` used, wall time, time in assembly, master, pricing/separation, number of columns, number of cuts, pricing calls, pricing gaps, peak memory and certification status.
2. The system SHALL include every subsolve (distances, enumeration, pricing, separation, validation) in the total cost.
3. The system SHALL report the curve of certified LB against total work per instance.

**Independent Test**: total cost equals the sum of recorded phase costs within rounding.

---

### P1: Story 6 — N2 gate (task N2-T6)

**User Story**: As the owner of the program, I want a pre-registered PASS/FAIL, so that N3 is
specified only if the root bound is useful.

**Why P1**: Releases or keeps blocked N3.

**Acceptance Criteria**:

1. The system SHALL issue `N2 PASS` only if certification is correct on all controls, the certified LB exceeds the reference on at least two structure types, the gain reproduces on two size levels, and on cases with known full LP the method recovers at least 50% of the positive increment over `B0` within the reserved budget.
2. IF the bound cannot be certified, or pricing/separation consumes the budget without useful gain, or the gain disappears on both levels, or cost eliminates the advantage, or the representation does not scale minimally THEN the system SHALL issue `N2 FAIL`.
3. WHEN `N2 PASS` is issued THEN the system SHALL record that N3 may be specified and SHALL NOT start N3 work in this spec.
4. WHEN `N2 FAIL` is issued THEN the system SHALL keep F-CC as theoretical and diagnostic result, document the observed scalability limit, and SHALL NOT open branch-and-price to compensate.

**Independent Test**: a reader applying the rule to the N2 CSV reaches the same verdict.

---

## Tasks

| Task | Story | Depends on | Output |
|---|---|---|---|
| N2-T1 | 1 | N1-T7 | Path record, N2 pre-registration |
| N2-T2A or N2-T2B | 2A or 2B | N2-T1 | Formal document, code, validator |
| N2-T3 | 3 | N2-T2* | Certification logic and justification fields |
| N2-T4 | 4 | N2-T3 | Regression output |
| N2-T5 | 5 | N2-T4 | N2 CSV and cost report |
| N2-T6 | 6 | N2-T5 | Gate record |

Only one of N2-T2A / N2-T2B is executed initially.

---

## Validation Strategy

- Mathematics first: master/dual/pricing (path B) or validity proof (path A) reviewed before code.
- Small-instance regression against full enumeration from N1 before any level-2 run.
- Every bound carries its certification status; uncertified values are never aggregated with
  certified ones.

## Experimental Pre-registration

Not written now. Task N2-T1 writes it after activation and before measurement. Fixed now:
threshold `≥ 50%` of the positive increment over `B0`; two structure types; two size levels;
certification rule of story 3; at most one representation change; root only.

## Required Tests

| Test | Checks |
|---|---|
| Regression vs full LP | Story 4 |
| Validity check (path A) | All `C ⊆ V` on `n ≤ 12` |
| Pricing exactness check (path B) | Exact pricing vs enumeration of all columns on N1 small instances: same minimum reduced cost |
| Certification field check | Every row has status and justification |
| Forbidden simplifications | Review checklist against story 3 criterion 5 |

## Evidence to Produce

Path record; formal documents (inequality proof or master/dual/pricing derivation and bound
derivation); code; regression output; N2 CSV with the fields of story 5; LB-versus-work curves;
gate record.

## Dependencies

N1 decision record; N1 full-enumeration LP values; P1/P2/P7 proven; Spec A budget and partition.

---

## Gate / Promotion Criteria

See story 6. `N2 PASS` ⇒ N3 may be specified (not started). `N2 FAIL` ⇒ F-CC stays theoretical and
diagnostic; scalability limit documented; no branch-and-price.

## Stop Criteria

- No certified LB obtainable.
- Pricing or separation consumes the budget without useful gain.
- Gain disappears on both size levels.
- Total cost eliminates the advantage.
- The selected representation does not scale minimally beyond the enumeration cap.
- After one justified representation change, no further alternation between cuts, pricing and
  formulations.

## Risks

| Risk | Mitigation |
|---|---|
| Restricted master reported as LB | Story 3 criterion 1; status field |
| Heuristic pricing read as proof | Story 2B criterion 4 |
| Pricing simplified into a different problem | Story 3 criteria 5–6 |
| Old Lagrangian reused | Story 3 criterion 3 |
| Comparing master time with full COMP time | Story 5 criterion 2 |
| `WorkLimit` read as physical equality | Wall time and memory recorded too |
| Indefinite technique switching | One change maximum |
| Tree opened to rescue a weak root | Story 6 criterion 4 |

## Edge Cases

- WHEN heuristic pricing finds a negative-reduced-cost column THEN the system SHALL add it and SHALL still require exact pricing or a derived bound for certification.
- WHEN heuristic pricing finds no column THEN the system SHALL NOT mark the bound `CERTIFIED`.
- IF pricing is interrupted THEN the system SHALL report the last certified bound or `UNCERTIFIED`.
- IF the derived reduced-cost bound is not strong enough to improve on `B0` THEN the system SHALL report it as certified but not useful.
- WHEN `H` is dense THEN the system SHALL record pricing effort and SHALL NOT shrink `H` without proof.
- IF a candidate column has `W = ∅` THEN the system SHALL reject it.
- WHEN a terminal is shared (`S∩T`) THEN pricing SHALL keep origin and destination roles separate and SHALL allow `d_ss` up to 1.
- IF a column is balanced with `I = J = ∅` THEN the system SHALL exclude it (CA5).
- IF a pricing variant fixes a matching in advance THEN the system SHALL reject it as invalid.

---

## Requirement Traceability

| Requirement ID | Story | Plan origin | Current evidence | Status | Task | Test / verification | Artifact |
|---|---|---|---|---|---|---|---|
| COMPAT-BOUND-01 | 1 | §17 N2, §14 R8 | N1 not run | Pending | N2-T1 | Review | — |
| COMPAT-BOUND-02 | 1 | §17 N2 | — | Pending | N2-T1 | Review | Path record |
| COMPAT-BOUND-03 | 1 | §17 N2, §19 | — | Pending | N2-T1 | Timestamp order | Pre-registration |
| COMPAT-BOUND-04 | 1 | §17 N2 stop | — | Pending | N2-T1 | Review | Diagnosis record |
| COMPAT-BOUND-05 | 2A | §17 N2, §14 R10 | No family | Pending | N2-T2A | Proof review | Inequality document |
| COMPAT-BOUND-06 | 2A | §17 N2 | — | Pending | N2-T2A | Validity check | Validator |
| COMPAT-BOUND-07 | 2A | §17 N2 | — | Pending | N2-T2A | Review | Separator |
| COMPAT-BOUND-08 | 2A | §8 | — | Pending | N2-T2A | Review | CSV status |
| COMPAT-BOUND-09 | 2B | §8, §17 N2 | No dual | Pending | N2-T2B | Review | Master/dual document |
| COMPAT-BOUND-10 | 2B | §17 N2 | No pricing | Pending | N2-T2B | Pricing exactness check | Pricing document |
| COMPAT-BOUND-11 | 2B | §17 N2 | — | Pending | N2-T2B | Certification field check | CSV |
| COMPAT-BOUND-12 | 2B | §8 | — | Pending | N2-T2B | Review | — |
| COMPAT-BOUND-13 | 2B | §16 B&P | — | Pending | N2-T2B | Code review | — |
| COMPAT-BOUND-14 | 2B | §9 | MR-F3 pending | Pending | N2-T2B | Review | Trio derivation |
| COMPAT-BOUND-15 | 3 | §8, §19 | — | Pending | N2-T3 | Certification field check | CSV |
| COMPAT-BOUND-16 | 3 | §8 | — | Pending | N2-T3 | Review | Justification field |
| COMPAT-BOUND-17 | 3 | §6, §17 N2 | Old Lagrangian capped at base LP | Pending | N2-T3 | Review | Bound derivation |
| COMPAT-BOUND-18 | 3 | §17 N2 | — | Pending | N2-T3 | Review | CSV |
| COMPAT-BOUND-19 | 3 | §17 N2 | — | Pending | N2-T3 | Forbidden simplifications | Checklist |
| COMPAT-BOUND-20 | 3 | §17 N2 | — | Pending | N2-T3 | Review | Proof if any |
| COMPAT-BOUND-21 | 4 | §17 N2 | F3 LP values | Pending | N2-T4 | Regression | Regression output |
| COMPAT-BOUND-22 | 4 | §17 N2 | — | Pending | N2-T4 | Regression | Regression output |
| COMPAT-BOUND-23 | 4 | §19 | — | Pending | N2-T4 | Regression | Regression output |
| COMPAT-BOUND-24 | 4 | §19 | — | Pending | N2-T4 | Review | — |
| COMPAT-BOUND-25 | 5 | user §7.6 | — | Pending | N2-T5 | Schema check | N2 CSV |
| COMPAT-BOUND-26 | 5 | §19 | — | Pending | N2-T5 | Sum check | Cost report |
| COMPAT-BOUND-27 | 5 | §17 N2 | — | Pending | N2-T5 | Review | Curves |
| COMPAT-BOUND-28 | 6 | §17 N2 | — | Pending | N2-T6 | Reader re-derivation | Gate record |
| COMPAT-BOUND-29 | 6 | §17 N2 | — | Pending | N2-T6 | Review | Gate record |
| COMPAT-BOUND-30 | 6 | §17 N2/N3 | — | Pending | N2-T6 | Review | Gate record |
| COMPAT-BOUND-31 | 6 | §17 N2 | — | Pending | N2-T6 | Review | Gate record |

**Coverage:** 31 total, 31 mapped to tasks, 0 unmapped (only one of path A / path B rows becomes
active after N2-T1).

---

## Success Criteria

- [ ] Exactly one path executed, selected by N1.
- [ ] Zero restricted-master values reported as LB.
- [ ] Regression against full enumeration passes on all small instances.
- [ ] Gate verdict issued by the frozen rule with the full cost decomposition.

---

## Inconsistencies Found

| # | Inconsistency | Class |
|---|---|---|
| 1 | Spec B "Future conditional work" requires GF1 and P1/P7 for R8 but does not mention certification of a restricted master explicitly as reporting rule | superseded by story 3 |
| 2 | Spec C lists R8/R9 as "released" under a "BLOCKED" heading | stale; R9 still depends on N2 |
| 3 | Spec D says its certifiers may validate R8/R9/R10 | superseded by `CONFIRMED DIVERGENCE` |
| 4 | Backlog and `direcoes` D-5 pause column generation generically, with an argument about pricing whole station sets | different object from F-CC configurations |
| 5 | `decisao-gf1.md:41` says column generation is no longer blocked by GF1 | true for GF1 only; N1 decision still required |

---

## Future conditional work — N3 Algorithmic Utility and Evaluation (BLOCKED — DO NOT IMPLEMENT)

No path, no requirement IDs yet (prefix `COMPAT-ALG` reserved). A future N3 spec may be written only
after `N2 PASS`, and must contain at least:

1. **Order:** development, then a development gate, then evaluation. Never evaluation directly after
   a small pilot.
2. **Development:** new method vs COMP vs the relevant core reference, comparable total budget, same
   data and protocol, three seeds when solver randomness matters, two size levels, aggregation by
   graph of origin; record LB, UB, gap, nodes, time to incumbent, time to proof, `WorkLimit`, wall
   time and auxiliary costs; SC as mechanism control; regressions reported.
3. **Exactness:** root columns followed by a restricted IP is a heuristic and certifies nothing;
   branch-and-price needs pricing compatible with branching and a valid bound at every relevant node.
4. **Advancement criterion:** one closed criterion frozen prospectively before the run (for example
   "close ≥ 3 D/A in ≥ 2 families" **or** "reduce median gap ≥ 25% in ≥ 2 families reproduced in the
   three seeds" — exactly one is chosen, never a post-hoc menu).
5. **Evaluation:** only with method and parameters frozen and development approved; partition by
   origin; no adaptation after observing results; negatives preserved; tuned results never
   re-presented as new.
6. **Edge cases:** gain in one seed only; gain only on a gadget; LB improves while UB worsens; root
   improves while the tree worsens; overhead larger than gain; fewer instances solved but better
   median gap; evaluation contradicting development.
