# Next Phase C — Diagnosis of the Remaining Gap and of the Core Plateau (MIN-STATION) Specification

Scope: tasks R5, R6, R7 and gate **G1** of `docs/technical/plans/plano-proxima-fase.md`. This spec
determines whether the remaining gap is mainly on the lower-bound side (collective compatibility) or
on the upper-bound side (primal), measures the compatibility gap `Γ` exactly where possible and as an
interval elsewhere, and dissects why optimal core solutions are infeasible. It produces the evidence
that decides which method spec, if any, is opened next. **It implements no method.**

Evidence vocabulary: **[Fato]**, **[Conferido]**, **[Evid.]**, **[Hipótese]**, **[Sugestão]** as in
the plan. No sentence in this spec anticipates a result ("the gap is dual", "H-desc holds").

---

## Relationship with the other next-phase specs

| Spec | Relation |
|---|---|
| A — Foundation | **R5, R7 and the certified part of R6** depend only on A.R1 (a proven OPT is a certificate regardless of protocol). **The D/A part of R6** depends on A.R4 (`LB*`, `UB*`) and on A.R3's frozen `WorkLimit` |
| B — Formulations | G1 may recommend method M-F only if B's **GF1 = PASS** |
| D — Special-class certifiers | Not required |

This corrects the plan's DAG, which places R7 after R4: R7 needs only the core, the oracle and
instances whose `Γ` or plateau is already certified.

---

## Current State (audited 2026-10-04, read-only)

| Item | Status | Evidence |
|---|---|---|
| Plateau phenomenon | [Evid.] pre-protocol | E12 CSV: CBI LB stayed at the core value after 124–1334 iterations; `cc9-2p` 860 iterations at 27 vs COMP LB 30; master took 67–99% of the time |
| Core below OPT on certified F instances | [Evid.] | E9 §2.1 item 6: maze 5 vs 7, pace-001 2 vs 3, pucn-cc6-2n 4 vs 6, lin03 5 vs 7 |
| Certified `Γ` instruments | [Fato] | BP-"não": core `2n+q`, OPT `2n+q+1` (independent DP certificate); HB: core 1, OPT 2–3 (enumeration); SC-GF2: `Γ = 0`; TR(k=2,3): core = OPT = 3 (`Γ = 0`) but 8 and 27 core optima with only 2 and 3 feasible |
| Primal-slack evidence | [Evid.] confounded | E13 changed `TimeLimit` and `MIPFocus` together (`protocolo-comparacao-pareada.md`, retrospective); E14 0/4 certifications |
| `Γ` measurement, primal test, plateau anatomy | NOT STARTED | — |
| Official `LB*`/`UB*` | NOT STARTED | Produced by Spec A R4 |

**Reusable infrastructure [Fato]:** core solvers (`run_e12.py:nucleo`, `piloto.py:_resolver_nucleo`,
`medir.py:nucleo`), `cuts.integer_oracle` (returns a minimum cut `Z` for an infeasible `C`),
`independent_validator`, `harness.measure_mip(coletar_incumbente=True)`, the paired protocol.

---

## Problem Statement

The residual gap of the 31 D/A instances (about 10% to 44%) has never been attributed to the lower
or the upper bound: E13 confounded time with `MIPFocus`, and E14 certified no optimum. At the same
time, E12 exposed a mechanism on the dual side — the core has a plateau of optimal solutions that
are infeasible, and point-wise `𝒵` cuts remove them one at a time — but the structure of that plateau
was never examined. Without knowing (a) where the gap sits, (b) how large the compatibility gap
`Γ = OPT − OPT_core` is and where it concentrates, and (c) why core optima fail, any method opened
next (column generation, compatibility inequalities, primal matheuristic) would be chosen by
preference rather than by evidence.

## Goals

- [ ] `Γ` reported for every sampled instance in exactly one class: exact, lower bound, upper bound
      or unknown — an interval is never presented as a value.
- [ ] A single-factor primal-slack test (control vs `MIPFocus = 1`, same budget) with 3 seeds.
- [ ] A plateau anatomy on 3–5 representative instances, with hypothesis H-desc classified as
      CONFIRMED, PARTIALLY CONFIRMED or REFUTED.
- [ ] Gate G1 issued by a pre-registered rule.

## Out of Scope

| Item | Reason |
|---|---|
| Running CBI or BC-y as a method | Closed lines; only the infeasibility oracle is used, to explain the plateau |
| Implementing any method: column generation (R8), compatibility inequalities (R10), matheuristic (R12) | BLOCKED until G1 (and GF1 for R8) |
| Re-running E13 or E14 as such | The primal test here is a new single-factor design |
| Tuning any solver parameter beyond the single declared factor | Forbidden by the plan |
| New instance families | The plan rules them out; existing instruments suffice |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Definition of `Γ` | `Γ(I) = OPT(I) − OPT_core(I)`, with core = IP in `y` with C1+C2+C4-DM, as frozen by Spec A R3 | Relative to a fixed core; not an absolute property of the instance | y (plan) |
| `Γ` classes | exact (OPT proven); lower bound `max(0, LB* − OPT_core)`; upper bound `UB* − OPT_core`; unknown when the core itself is not solved to optimality | Avoids presenting intervals as values | n |
| Certified sample | F-class instances with proven OPT, the 5 legacy instances where OPT is proven, SC, BP-"não" (new generation seeds, DP certificate), HB | A proven OPT is a certificate regardless of protocol | n |
| Primal-slack test | Control vs `MIPFocus = 1`, same `WorkLimit` as Spec A R3, 4 threads, no start, 3 seeds, D/A development partition | Single factor; corrects the E13 confound | n |
| Plateau sample | 3–5 instances among `cc9-2p`, `cc11-2u`, one MAPF, one maze/lin F instance, TR, BP-"não" | Mix of real instances with measured gap and controlled instruments | n |
| Number of core optima recorded per instance | A pre-registered cap N (e.g. 200) | Prevents an open-ended enumeration | n |
| AV-1..AV-4 | Not used here; they are the program's success criteria, PENDING USER CONFIRMATION | Out of this spec's decision | n — PENDING USER CONFIRMATION |

**Open questions:** none — every pending decision is recorded above with its default.

---

## Pre-registration (R5)

| Item | Value |
|---|---|
| Arms (primal test) | **control**: COMP with default parameters; **experimental**: COMP with `MIPFocus = 1`. Only this factor differs |
| Budget | `WorkLimit` from Spec A R3 (4 threads); `TimeLimit` only as a wall guard |
| Threads / start / seeds | 4 / none / 3 seeds |
| Instances (primal test) | D/A instances of the development partition from Spec A R2, excluding `m ≥ 1000` |
| Metrics | T9 schema; UB trajectory (time to first and best incumbent) |
| `Γ` sample | As in Assumptions; the class of each instance recorded |
| Plateau sample and cap N | As in Assumptions |
| Provenance | sha256, commit, cut-generator version, seed, threads, budget |
| Decision gate | G1, rule below |

**G1 rule [Sugestão, frozen before measurement]:**
- **compatibility (LB) dominates** if, on the certified sample, `Γ > 0` occurs in at least two
  families **and** the primal test does not improve `UB` by at least the pre-registered threshold in
  at least two families → recommend M-A; recommend M-F only if Spec B's GF1 = PASS.
- **primal (UB) dominates** if the primal test improves `UB` by at least the threshold in at least
  two families, reproducing in 3 seeds, **and** `Γ` is zero or small on the certified sample →
  recommend M-B.
- **both** → recommend the LB-side method first, then M-B.
- **no clear signal** → no method is opened; the result is documented and the decision returns to
  the user.

The UB threshold is fixed in the pre-registration file before any run.

---

## User Stories

### P1: R5 — Diagnosis pre-registration ⭐ MVP

**User Story**: As a researcher who must not shape the diagnosis after seeing data, I want sample,
classes, primal test, caps and the G1 rule frozen in writing first.

**Why P1**: R6, R7 and G1 depend on it.

**Acceptance criteria:**

1. The system SHALL write the pre-registration (samples, `Γ` classes, primal test, seeds, budget, plateau cap N, G1 rule and UB threshold) before any measurement of this spec.
2. The system SHALL change exactly one factor between the arms of the primal test.
3. The system SHALL take the `WorkLimit` from Spec A R3 and SHALL NOT recalibrate it here.
4. The system SHALL define each `Γ` class operationally, including the case where the core is not solved to optimality.

**Required tests:** none; the check is the timestamp before the first row.

**Evidence to produce:** a pre-registration document (name to confirm).

**Risks:** choosing the UB threshold after seeing E13; it is fixed here from first principles.

**Dependencies:** Spec A R1 (certified part); Spec A R3 (budget for the primal test).

**Independent Test**: the document alone lets a reader run R6 and R7.

---

### P1: R6 — Measure `Γ` and primal slack

**User Story**: As a researcher deciding where to attack, I want to know how large `Γ` is and whether
better incumbents exist at equal work.

**Why P1**: It is one of the two inputs of G1.

**Acceptance criteria:**

1. The system SHALL report `Γ` for every instance of the certified sample with its class and the source of OPT.
2. WHILE `LB*` and `UB*` from Spec A R4 are not available, the system SHALL NOT report `Γ` intervals for D/A instances.
3. WHEN `LB*` and `UB*` are available THEN the system SHALL report for each D/A instance the interval `[max(0, LB* − OPT_core), UB* − OPT_core]`, never a single value.
4. The system SHALL run the primal test exactly as pre-registered and report UB, LB and `NodeCount` per arm and seed.
5. The system SHALL issue a per-family verdict (LB side, UB side, both, unclear) using only the pre-registered rule.

**Required tests:** core values reproduce the existing certified cases (BP-"não" core `2n+q`; SC-GF2
core = `k`; TR core = 3).

**Evidence to produce:** CSV and report with the `Γ` table and the primal-test table.

**Risks:** F-class instances are easy by selection; their `Γ` may underestimate the gap of D/A. The
report must state it.

**Dependencies:** R5; Spec A R4 for the D/A part.

**Independent Test**: the `Γ` table can be regenerated from the pre-registration.

---

### P1: R7 — Anatomy of the core plateau

**User Story**: As a researcher who wants a method that removes classes of infeasible solutions
instead of one at a time, I want to know what those infeasible core optima have in common.

**Why P1**: It is the source of hypotheses for compatibility inequalities and the test of H-desc,
which motivates F-CC.

**Acceptance criteria:**

1. The system SHALL record, for each plateau instance and up to the cap N, the infeasible optimal core solutions, the stations chosen, the components of `H[C]`, the minimum cut `Z` returned by the oracle, the unserved robots and the incompatible destinations.
2. The system SHALL test H-desc — "infeasible core optima fail because their stations do not form components of `H[C]` that connect the required origins and destinations collectively" — and classify it as CONFIRMED, PARTIALLY CONFIRMED or REFUTED, with counts.
3. The system SHALL measure, for each recorded `Z`, how many recorded optima it eliminates.
4. The system SHALL NOT run CBI or any iterative method; only the core and the oracle are used.
5. WHEN a repeatable structure is found THEN the system SHALL write it as a hypothesis of a valid inequality family, without implementing it.
6. IF no repeatable structure is found THEN the system SHALL record that outcome as a result.

**Required tests:** every recorded solution is confirmed infeasible by `independent_validator` as
well as by the oracle on instances small enough for it.

**Evidence to produce:** a report with the counts, the H-desc verdict and the written hypotheses.

**Risks:** the cap N may hide structure in very large plateaus; the report states the fraction of the
plateau covered when it can be estimated.

**Dependencies:** R5 (cap and sample); Spec A R1.

**Independent Test**: TR, where the plateau is known exactly (k^R optima, k feasible), reproduces the
known counts.

---

### P1: G1 — Gate decision

**User Story**: As the owner of the program, I want a pre-registered recommendation on which method
spec, if any, is opened next.

**Why P1**: It releases or keeps blocked R8, R10 and R12.

**Acceptance criteria:**

1. The system SHALL apply the G1 rule exactly as pre-registered.
2. The system SHALL recommend M-F only if Spec B reports `GF1 = PASS`.
3. IF the evidence gives no clear signal THEN the system SHALL open no method and SHALL return the decision to the user.
4. The system SHALL cite the rows of R6 and the findings of R7 that decided the outcome.

**Required tests:** none.

**Evidence to produce:** a decision document.

**Risks:** reading the rule loosely to justify a preferred method. The rule is frozen in R5.

**Dependencies:** R6, R7; Spec B GF1 for M-F.

**Independent Test**: a reader applying the rule to R6/R7 reaches the same recommendation.

---

## Stop Criteria

- The spec ends at G1. It is not extended with more instances, more time or other seeds without a
  new pre-registration.
- R7 stops at the cap N per instance and at 5 instances.

## Edge Cases

- IF the core is not solved to optimality on an instance THEN its `Γ` SHALL be "unknown", not
  estimated.
- IF `LB* > OPT_core` THEN the lower bound of `Γ` is positive and SHALL be reported as such, not as
  a value.
- IF a recorded core optimum turns out feasible THEN it SHALL be reported (it certifies
  `OPT = OPT_core` on that instance) and the plateau analysis of that instance SHALL be reread.
- IF the primal test changes UB in only one seed THEN it SHALL count as not reproduced.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| DIAG-01 | P1: R5 | Design | Pending |
| DIAG-02 | P1: R5 | Design | Pending |
| DIAG-03 | P1: R5 | Design | Pending |
| DIAG-04 | P1: R5 | Design | Pending |
| DIAG-05 | P1: R6 | Design | Pending |
| DIAG-06 | P1: R6 | Design | Pending |
| DIAG-07 | P1: R6 | Design | Pending |
| DIAG-08 | P1: R6 | Design | Pending |
| DIAG-09 | P1: R6 | Design | Pending |
| DIAG-10 | P1: R7 | Design | Pending |
| DIAG-11 | P1: R7 | Design | Pending |
| DIAG-12 | P1: R7 | Design | Pending |
| DIAG-13 | P1: R7 | Design | Pending |
| DIAG-14 | P1: R7 | Design | Pending |
| DIAG-15 | P1: R7 | Design | Pending |
| DIAG-16 | P1: G1 | Design | Pending |
| DIAG-17 | P1: G1 | Design | Pending |
| DIAG-18 | P1: G1 | Design | Pending |
| DIAG-19 | P1: G1 | Design | Pending |

**Coverage:** 19 total, 0 mapped to tasks (`tasks.md` not created in this round), 19 unmapped.

---

## Success Criteria

- [ ] Every `Γ` reported with its class; no interval presented as a value.
- [ ] Primal test with one factor and 3 seeds.
- [ ] H-desc classified with counts; any repeatable structure written as a hypothesis.
- [ ] G1 issued by the pre-registered rule.

---

## Inconsistencies Found During Specification

| # | Inconsistency | Class |
|---|---|---|
| 1 | The plan's DAG places R7 after R4; R7 only needs the core, the oracle and certified instruments | plan stricter than needed |
| 2 | The plan lists TR among `Γ > 0` instruments; TR has `Γ = 0` (core = OPT) and serves here as a plateau instrument only | conflicting evidence (plan error) |
| 3 | The plateau evidence (E12) is pre-protocol; it motivates R7 but is not reused as a measurement | documentation note |

---

## Future conditional work — BLOCKED

- **M-A / R10, compatibility inequalities** (prefix `COMPAT-*`): released if G1 = compatibility.
  Mandatory flow: derivation → proof → validator → enumeration → Spec D certifiers → effect on `Γ`
  with SC as control → D/A development. At most 3 cycles.
- **M-F / R8 and R9** (prefixes `CG-*`): released only if G1 = compatibility **and** Spec B
  GF1 = PASS.
- **M-B / R12, matheuristic** (prefix `PRIMAL-*`): released only if G1 = primal.
- **R13, confirmation** (prefix `CONF-*`): released only when a method passes G2 (effect on ≥ 2 size
  levels and 3 seeds on the development partition).

Nothing in this spec authorizes them.
