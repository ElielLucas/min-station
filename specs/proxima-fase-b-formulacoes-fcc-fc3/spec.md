# Next Phase B — Connected-Configuration Formulations F-CC and F-C3 (MIN-STATION) Specification

Scope: tasks F1, F2, F3 and gate **GF1** of `docs/technical/plans/plano-proxima-fase.md`. This
spec decides, cheaply and on small instances only, whether the two alternative formulations F-CC and
F-C3 strengthen the lower bound in the compatibility regime (`Γ > 0`) enough to justify investing in
methods at scale. It contains **no column generation** and **no benchmark instance**.

Evidence vocabulary: **[Fato]**, **[Conferido]**, **[Evid.]**, **[Hipótese]**, **[Sugestão]** as in
the plan. Every mathematical statement in this spec carries one of the F2 labels: `PROVEN`,
`COMPUTATIONALLY VERIFIED`, `HYPOTHESIS`, `OPEN`. Nothing labelled `HYPOTHESIS` or `OPEN` may be used
as a fact when interpreting F3.

---

## Relationship with the other next-phase specs

| Spec | Relation |
|---|---|
| A — Foundation | Depends on **R1** only (renamed formulation files, status headers, F-OD removed). Independent of R2–R4 |
| C — Diagnosis | G1 recommends method M-F only if this spec's **GF1 = PASS**. Spec C's plateau anatomy (R7) tests hypothesis H-desc, which motivates F-CC; neither spec waits for the other |
| D — Special-class certifiers | Supplies small spiders with exact OPT as **optional** F3 instances. Not blocking |

---

## Current State (audited 2026-10-04, read-only)

| Item | Status | Evidence |
|---|---|---|
| F-CC definition document | PARTIAL | `formulacao-fcc-configuracoes-conectadas.md` (renomeado por Spec A R1): complete definition, exactness argument in prose |
| F-C3 definition document | PARTIAL | `formulacao-fc3-consistencia-trios.md` (renomeado por Spec A R1): a chat-style summary; trio networks described informally; menção à formulação intermediária descartada removida; links an external proof document that is **not** in the repository |
| F-C3 full proof document (`MIN-STATION-formulacao-componentes-consistencia-trios.md`) | BLOCKED (external) | Not in the repository |
| Claimed values (20-vertex family; 1.5g vs 2g; 15-vertex counterexample) | NEEDS VERIFICATION | Never measured; instances not defined in the repository |
| Code for F-CC, F-C3 or an enumerator of connected sets | NOT STARTED | Exhaustive `grep` over `experiments/` and `src/` finds none |
| Any LP value of F-CC or F-C3 | NOT STARTED | — |
| F-OD | OBSOLETE | Discarded by user decision (2026-10-03) |

**Reusable infrastructure [Fato]:** `experiments/cuts/independent_validator.py`
(`opt_por_enumeracao`, `viavel`), `baseline.py` (`construir_modelo_baseline`), `harness.measure_lp`,
`harness.prepare_cuts` with C1+C2+C4, the core solvers (`medir.py:nucleo`), the generators of TR,
BP, HB and SC (`experiments/structural/`), and the gadgets of `experiments/cuts/synthetic.py`.

---

## Problem Statement

The core of covering (IP in `y` with C1+C2+C4-DM) fails where collective compatibility matters: E12
measured a plateau of infeasible core optima (in `cc9-2p` the CBI LB stayed at the core value 27 for
860 iterations while COMP proved 30). F-CC encodes compatibility directly — stations used by a group
of robots must form a connected set in the reach graph `H = G^r` — and F-C3 adds trio consistency
between assignments. The planning analysis re-derived that F-CC is exact and dominates the baseline
LP, but also that in the pure covering regime (SC-GF2) F-CC has the same set-cover gap as the core.
Its value, if any, is in the regime `Γ > 0`. No line of code, no proof written in the repository and
no measured LP exists for either formulation, and the F-C3 numbers come from a document that is not
in the repository. Before any expensive method (column generation, branch-and-price) is considered,
the project needs a cheap, pre-registered answer: on small instances with `Γ > 0`, do F-CC or F-C3
give a stronger bound than what already exists?

## Goals

- [ ] F-CC and F-C3 are defined in the repository unambiguously, or each ambiguous point is marked
      `OPEN`.
- [ ] Every structural property used later is classified `PROVEN`, `COMPUTATIONALLY VERIFIED`,
      `HYPOTHESIS` or `OPEN`, with a written proof for each `PROVEN`.
- [ ] LP values of base, base+C1+C2+C4, core IP, F-CC and F-C3 are measured against an independent
      OPT on a pre-registered set of small instances.
- [ ] GF1 is decided by a rule written before measurement.

## Out of Scope

| Item | Reason |
|---|---|
| Column generation, pricing, branch-and-price (R8, R9) | BLOCKED until GF1 = PASS; created as a separate future spec |
| Compatibility inequalities derived from F-CC/F-C3 (R10) | BLOCKED until G1 (Spec C) and, for projections, GF1 |
| Any benchmark-v1 instance | F3 is restricted to small instances by design |
| F-OD | Discarded by user decision |
| Changing the baseline formulation | The baseline stays; these are formulations under evaluation |
| Performance claims (time, nodes) | This spec measures relaxation strength only; LP strength is never presented as computational superiority |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Missing F-C3 proof document | Not blocking: F2 re-derives what it can; claimed values stay `HYPOTHESIS` until reproduced | Plan F1; user was asked and it is not required | n |
| F-C3 trio networks cannot be fixed unambiguously from the summary | F-C3 arm marked `OPEN` and GF1 evaluated on F-CC alone | The summary does not define what a "stage" of the 8-state network is; implementing a guessed version would test the guess, not F-C3 | n — PENDING USER CONFIRMATION |
| Enumeration caps for F3 | Pre-registered before measurement: a maximum `n` and a maximum number of connected sets `W`; an instance over a cap is excluded and listed | Enumeration of connected subsets of a dense `H` explodes; caps must not be chosen after seeing values | n |
| Source of OPT | `independent_validator.opt_por_enumeracao` where `2^n` subsets are tractable; otherwise the baseline MIP solved to optimality, certified by the T5 equivalence; the source is recorded per instance | Independent where possible; never F-CC/F-C3 itself | n |
| Which instances count as "`Γ > 0` types" in GF1 | Determined by measurement in F3 (core IP < OPT), never assumed | The plan listed TR and F2 among the `Γ > 0` instruments, but Appendix B gives core = OPT for both (see Inconsistencies) | n |
| Computing F-CC via the separated form `λ_W, α, β` | Allowed only after F2 classifies the equivalence `(W,I,J) ↔ λ_W/α/β` as `PROVEN`; before that, F-CC is computed in its original `(W,I,J)` form on the smallest instances only | Prevents using an unproven reformulation as if it were F-CC | n |

**Open questions:** none — every pending decision is recorded above with its default.

---

## Definitions (to be written in full by F1)

**Common data.** `G = (V,E)` simple, connected, undirected; `S, T ⊆ V`, `|S| = |T| = m`; `r ∈ ℤ>0`;
`d` = hop distance. `H = (V, E_r)` with `E_r = {{u,v} : u ≠ v, d(u,v) ≤ r}`. For non-empty `W ⊆ V`,
`B(W) = W ∪ {v : ∃ w ∈ W, {v,w} ∈ E_r}`. Direct pairs `D = {(s,t) ∈ S×T : d(s,t) ≤ r}`; since
`d(s,s) = 0`, `D` contains the permanence pairs of `S∩T`.

**F-CC.** Configurations `q = (W,I,J)` with `W` non-empty and connected in `H`, `I ⊆ S ∩ B(W)`,
`J ⊆ T ∩ B(W)`, `|I| = |J| ≥ 1`. Variables `y_v ∈ {0,1}` for all `v ∈ V`, `λ_q ≥ 0`, `d_st ≥ 0`.
Objective `min Σ y_v`. R1: `Σ_{q: s∈I_q} λ_q + Σ_{t:(s,t)∈D} d_st = 1` for every `s ∈ S`. R2: the
symmetric equation for every `t ∈ T`. R3: `Σ_{q: v∈W_q} λ_q ≤ y_v` for every `v ∈ V`.

**F-C3.** Separated variables `λ_W ≥ 0` (connected `W`), `α_sW ≤ λ_W`, `β_tW ≤ λ_W`,
`Σ_s α_sW = Σ_t β_tW`, linking `Σ_{W ∋ v} λ_W ≤ y_v`, direct `d_st`, plus, for every trio of
origins and every trio of destinations, an auxiliary 8-state network whose flows must agree with
`λ, α, β, d`. **The exact structure of these networks (what a stage is, which arcs exist, how the
agreement constraints are written) is `OPEN`** until F1 fixes it or declares it not fixable.

---

## Propositions to classify (F2)

| # | Proposition | Status before F2 | Source |
|---|---|---|---|
| P1 | F-CC is exact: for binary `y`, F-CC is feasible iff `C = {v : y_v = 1}` is feasible for MIN-STATION | [Conferido] sketch: a pair is realizable iff it is direct or both ends lie in `B(K)` for one component `K` of `H[C]`; bipartite matching integrality | Planning analysis |
| P2 | `z_LP(base) ≤ z_LP(F-CC)` | [Conferido] sketch: route `λ_q·|I_q|` through `W`; base activation holds since `m·y_v ≤ b_v + (m−b_v)·y_v` for `y_v ≤ 1` | Planning analysis |
| P3 | The LP of F-CC implies C1 | [Conferido] sketch | Planning analysis |
| P4 | The LP of F-CC implies C2 | [Conferido] sketch | Planning analysis |
| P5 | The LP of F-CC implies C4 only partially (`y(Z) ≥ δ/|S'|`) | `HYPOTHESIS` | Planning analysis |
| P6 | Relation between the LP of F-CC and `LP_cov` over the family `𝒵` | `OPEN` | — |
| P7 | The separated form `λ_W/α/β` has the same LP value as F-CC | [Conferido] sketch: `{(a,b) ∈ [0,1]^S × [0,1]^T : Σa = Σb}` has integral vertices | Planning analysis |
| P8 | `z_LP(F-CC) ≤ z_LP(F-C3) ≤ OPT` | `HYPOTHESIS` (needs the trio networks fixed) | External summary |
| P9 | In SC-GF2, the LP of F-CC equals the set-cover LP (≈ 2 vs OPT `k`) | [Conferido] sketch | Planning analysis |
| P10 | Permanence in `S∩T` is represented by `d_ss` | [Conferido] sketch | Planning analysis |
| P11 | 20-vertex family: base 1, F-CC 3, F-C3 4, OPT 4; general family F-CC 1.5g vs F-C3 2g; 15-vertex example F-C3 2.5 vs OPT 3 | `HYPOTHESIS`; instances not defined in the repository | External summary |

---

## Pre-registration (F3) and gate GF1

**Arms per instance:** LP of base; LP of base + C1+C2+C4; core IP (C1+C2+C4-DM); LP of F-CC; LP of
F-C3 (only if F1 fixes it); OPT (independent source, recorded).

**Instance set (fixed before measurement):**
- existing gadgets of `synthetic.py`;
- HB (Appendix B configurations) — expected `Γ > 0`;
- BP-"não" minimal cases — expected `Γ = 1`;
- Tri, Sec59 — `Γ` unknown, to be measured;
- TR (`k = 2, 3`) and F2 — expected `Γ = 0` (bound controls);
- SC-GF2 (`k = 3, 4`) — **negative control**;
- 20/15-vertex examples of the F-C3 summary, only if reconstructible from a definition;
- small spiders from Spec D with exact OPT, if available.

**Caps:** a maximum `n` and a maximum number of connected sets, written in the pre-registration
before measurement.

**GF1 rule (default from the plan, pre-registered):**
- **PASS** iff the LP of F-CC or of F-C3 is strictly above `max(LP base+C1+C2+C4, core IP)` on at
  least **2 instance types with measured `Γ > 0`**, **and** closes at least **50% of `Γ`** on at least
  one of them.
- Any gain on SC is treated as a suspected error and investigated before any positive reading.
- **FAIL** otherwise: column generation stays paused; F-CC is recorded as an exact characterization
  with a negative LP result.

---

## User Stories

### P1: F1 — Fix the definitions ⭐ MVP

**User Story**: As a researcher about to measure two formulations, I want them defined in the
repository without ambiguity, so that what I measure is the formulation and not my reading of a
summary.

**Why P1**: Everything else in this spec depends on it.

**Acceptance criteria:**

1. The system SHALL write the full F-CC definition in `formulacao-fcc-configuracoes-conectadas.md`, covering `y`, `λ_q`, `d_st`, `q = (W,I,J)`, connectivity in `H`, `B(W)`, direct pairs, R1–R3 and `S∩T`.
2. The system SHALL rewrite `formulacao-fc3-consistencia-trios.md` as a reference document (not a chat reply), with no mention of F-OD and with the chain `base ≤ F-CC ≤ F-C3 ≤ OPT`.
3. WHEN a part of F-C3 cannot be fixed unambiguously from the available text THEN the system SHALL mark that part `OPEN` and SHALL NOT implement a guessed version.
4. The system SHALL list each claimed numerical value of the F-C3 summary as `HYPOTHESIS`, with the condition under which it can be checked.

**Required tests:** none; review against the source documents.

**Evidence to produce:** the two rewritten documents and a list of `OPEN` points.

**Risks:** filling gaps of F-C3 by intuition. Criterion 3 forbids it.

**Dependencies:** Spec A R1.

**Independent Test**: a reader can build the F-CC model for a 6-vertex instance from the document
alone.

---

### P1: F2 — Independent theoretical verification

**User Story**: As a researcher interpreting an LP table, I want every property I rely on proven or
explicitly marked as unproven.

**Why P1**: F3's reading depends on it.

**Acceptance criteria:**

1. The system SHALL assign each of P1–P11 exactly one label among `PROVEN`, `COMPUTATIONALLY VERIFIED`, `HYPOTHESIS`, `OPEN`.
2. WHEN a proposition is labelled `PROVEN` THEN the system SHALL contain a written proof in the repository.
3. The system SHALL prove or refute the exactness of F-CC (P1), including permanence in `S∩T` and the bipartite matching integrality argument.
4. The system SHALL prove or refute the equivalence of the separated form (P7) before F3 computes F-CC through it.
5. IF a proposition is refuted THEN the system SHALL record the counterexample and SHALL update the dependent statements of this spec.

**Required tests:** for P1 and P7, a computational cross-check on the smallest instances (F-CC LP in
`(W,I,J)` form equals the separated form; F-CC with binary `y` agrees with `viavel` on every `C`).

**Evidence to produce:** a proofs document (name to confirm) with one section per proposition.

**Risks:** P5/P6 may stay `OPEN`; that is acceptable and must be stated.

**Dependencies:** F1.

**Independent Test**: each `PROVEN` label points to a proof section.

---

### P1: F3 — Small-instance LP diagnosis

**User Story**: As a researcher deciding whether to build column generation, I want the LP of F-CC
and F-C3 compared with the existing bounds on instances where the true gap is known.

**Why P1**: It is the cheapest decisive test in the program.

**Acceptance criteria:**

1. The system SHALL write the pre-registration (instances, caps, arms, OPT source, GF1 rule) before computing any F-CC or F-C3 value.
2. The system SHALL build F-CC and F-C3 by explicit enumeration of connected sets `W`, restricted to the pre-registered caps.
3. WHEN an instance exceeds a cap THEN the system SHALL exclude it and list it with the cap it exceeded.
4. The system SHALL report, per instance, the LP of base, the LP of base+C1+C2+C4, the core IP, the LP of F-CC, the LP of F-C3 (when defined), OPT, the source of OPT, and `Γ = OPT − core`.
5. The system SHALL determine membership in "`Γ > 0` types" from the measured `Γ`, not from the plan's expectation.
6. WHEN a claimed value from the F-C3 summary can be reconstructed THEN the system SHALL compare it with the measured value and record any divergence without adjusting either.
7. The system SHALL include SC-GF2 as a negative control and SHALL report its F-CC/F-C3 LP next to the set-cover LP.

**Required tests:** binary-`y` agreement of F-CC with `viavel`; LP(F-CC) ≥ LP(base) on every instance
(a violation is a bug or a refutation of P2).

**Evidence to produce:** the pre-registration, a CSV of all values, and a short report.

**Risks:** only two instance types are expected to have `Γ > 0` (HB, BP-"não"), and the planning
analysis expects no gain on BP-"não"; GF1 may be hard to pass. That is a legitimate outcome.

**Dependencies:** F2 for any use of the separated form; Spec D optionally.

**Independent Test**: the CSV can be regenerated from the pre-registration.

---

### P1: GF1 — Gate decision

**User Story**: As the owner of the program, I want a binary, pre-registered decision on whether the
formulation line continues to methods at scale.

**Why P1**: It releases or keeps blocked the future column-generation spec.

**Acceptance criteria:**

1. The system SHALL apply the GF1 rule exactly as pre-registered.
2. The system SHALL output `GF1 = PASS` or `GF1 = FAIL`, citing the rows that decided it.
3. IF SC shows any gain THEN the system SHALL investigate and document the cause before issuing GF1.
4. IF `GF1 = FAIL` THEN the system SHALL record F-CC as an exact characterization with a negative LP result and SHALL keep column generation paused.
5. The system SHALL NOT state that F-CC or F-C3 is computationally better on the basis of LP values alone.

**Required tests:** none.

**Evidence to produce:** a decision document citing F3.

**Risks:** the temptation to relax the rule after seeing values. The rule is frozen in F3's
pre-registration.

**Dependencies:** F3.

**Independent Test**: a reader applying the rule to the CSV reaches the same verdict.

---

## Stop Criteria

- The line stops at GF1 = FAIL: no further formulation work without a new hypothesis.
- F-C3 stops (stays `OPEN`) if its networks cannot be defined; GF1 then uses F-CC only (pending user
  confirmation).
- Never continue with larger instances, more time or other seeds to rescue a failed GF1.

## Edge Cases

- IF F-CC with binary `y` disagrees with `viavel` on any `C` THEN the system SHALL stop and debug
  before reporting any LP.
- IF LP(F-CC) < LP(base) on any instance THEN P2 is refuted or the implementation is wrong; the
  system SHALL resolve which before continuing.
- IF an instance has `S∩T ≠ ∅` THEN permanence SHALL be represented only through `d_ss`.
- IF the core IP equals OPT on every measured instance except one type THEN GF1 cannot pass; the
  system SHALL report it, not add instances to rescue it.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| FORM-01 | P1: F1 | Design | Pending |
| FORM-02 | P1: F1 | Design | Pending |
| FORM-03 | P1: F1 | Design | Pending |
| FORM-04 | P1: F1 | Design | Pending |
| FORM-05 | P1: F2 | Design | Pending |
| FORM-06 | P1: F2 | Design | Pending |
| FORM-07 | P1: F2 | Design | Pending |
| FORM-08 | P1: F2 | Design | Pending |
| FORM-09 | P1: F2 | Design | Pending |
| FORM-10 | P1: F3 | Design | Pending |
| FORM-11 | P1: F3 | Design | Pending |
| FORM-12 | P1: F3 | Design | Pending |
| FORM-13 | P1: F3 | Design | Pending |
| FORM-14 | P1: F3 | Design | Pending |
| FORM-15 | P1: F3 | Design | Pending |
| FORM-16 | P1: F3 | Design | Pending |
| FORM-17 | P1: GF1 | Design | Pending |
| FORM-18 | P1: GF1 | Design | Pending |
| FORM-19 | P1: GF1 | Design | Pending |
| FORM-20 | P1: GF1 | Design | Pending |
| FORM-21 | P1: GF1 | Design | Pending |

**Coverage:** 21 total, 0 mapped to tasks (`tasks.md` not created in this round), 21 unmapped.

---

## Success Criteria

- [ ] Both formulations defined in the repository; every ambiguity marked `OPEN`.
- [ ] P1–P11 labelled; every `PROVEN` label backed by a written proof.
- [ ] F3 CSV regenerable from the pre-registration; claimed values checked or left as `HYPOTHESIS`.
- [ ] GF1 issued by the pre-registered rule, with SC as negative control.

---

## Inconsistencies Found During Specification

| # | Inconsistency | Class |
|---|---|---|
| 1 | The plan lists TR and F2 among the `Γ > 0` instruments, but Appendix B of the assessment gives core = OPT for TR(k=2,3) (both 3) and C4 closes F2; both have `Γ = 0`. They remain bound controls (and TR remains a plateau instrument for Spec C) | conflicting evidence (plan error) |
| 2 | The plan writes the claimed 20-vertex values both as "1/3/4" (§6.2) and "1/3/3/4/4" (F3), the latter still including the discarded F-OD column | documentation stale |
| 3 | F-OD still cited in the F-C3 file | plan ahead of implementation (Spec A R1) |
| 4 | The F-C3 proof document is outside the repository | mathematical claim unverified |
| 5 | The F-C3 trio networks are not defined precisely enough to implement | user decision required (GF1 on F-CC only?) |

---

## Future conditional work — BLOCKED

- **R8, column generation of F-CC** (future spec, prefix `CG-*`): released only if **GF1 = PASS**,
  P1 and P7 are `PROVEN`, the pricing problem is formalized in `H = G^r` (connected subgraph with
  collected prize, balanced `I`/`J`), and a valid dual bound (Farley or Lagrangian) is defined. No LB
  reported without convergence or a valid bound.
- **R9, branch-and-price / price-and-branch**: released only after R8 passes its own gate.
- **R10, compatibility inequalities projected from F-CC/F-C3** (prefix `COMPAT-*`): released by
  Spec C's G1 and, for projections, by GF1.

Nothing in this spec authorizes them.
