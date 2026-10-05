# Next Phase D — Exact Certifiers for Special Graph Classes (MIN-STATION) Specification

Scope: task R11 (line S1) of `docs/technical/plans/plano-proxima-fase.md`. This spec implements the
published polynomial algorithms for paths and cycles (Das) and for spiders (Pereira & Ravelo, ETC
2026), and uses them for two purposes: (1) an independent source of exact optima at sizes where the
enumeration validator of Block 1 (`n ≤ 5`) cannot reach, to validate the baseline ILP and the
formulations of Spec B; (2) a verification of the algorithms themselves, whose proofs are partly
sketches.

Evidence vocabulary: **[Fato]**, **[Conferido]**, **[Evid.]**, **[Hipótese]**, **[Sugestão]** as in
the plan. Nothing in this spec asserts that a published algorithm is wrong; the points listed below
are readings to be tested.

---

## Relationship with the other next-phase specs

| Spec | Relation |
|---|---|
| A — Foundation | Depends on **R1** only (the Pereira & Ravelo file renamed to `pereira-ravelo-2026-aranhas.md`) |
| B — Formulations | Supplies small spiders with exact OPT as **optional** F3 instances; consumes Spec B's F-CC/F-C3 implementation, if available, for comparison. Neither blocks the other |
| C — Diagnosis | Not required |
| Future R8/R10 | Their validity checks at scale will use these certifiers |

---

## Current State (audited 2026-10-04, read-only)

| Item | Status | Evidence |
|---|---|---|
| Das path algorithm (`O(n)`) and cycle algorithm (`O(n²)`) | NOT STARTED | Source: `min-station-das.pdf`, Theorem 2 (Lemmas 2–4, Algorithm 1, pp. 6–11) and Theorem 3 (Lemma 5, Algorithm 2, pp. 11–13), as located in `overlap-ijcai2026-min-station.md` LC-5 |
| Pereira & Ravelo spider algorithm (`O(|V|)`) | NOT STARTED | Source: the `.md` transcription (renamed by Spec A R1), Lemma 1, Lemma 2, Theorem 1 |
| Generators of paths, cycles, spiders | NOT STARTED | No code found by `grep` |
| Independent validator | DONE | `experiments/cuts/independent_validator.py` (`viavel`, `opt_por_enumeracao`) |
| Baseline ILP | DONE | `baseline.py`; equivalence proved (T5) |
| F-CC / F-C3 implementations | NOT STARTED | Spec B |

**Readings of the spider proof to be tested [Hipótese]** (plan §5):
1. **Robots entering a radial.** Lemma 1 argues only about robots leaving a radial toward the center
   `c`; robots arriving from outside to targets inside a radial reach `c` with a charge that depends
   on the center step.
2. **"From `c` every target is reachable"** (Theorem 1) is not justified when a target lies more than
   `r` from `c` in a radial with no outgoing robots. Test case: `s` adjacent to `c`, `t` at distance
   `2r+1` from `c` in another empty radial.
3. **The exchange argument of Lemma 2** ignores stations inside the target's radial and pairs
   internal to one radial.
4. **`S∩T` and permanence** do not appear in the proofs.
5. **Boundary `r' = 0`**: the text assumes `0 < r'`.

---

## Problem Statement

New formulations (Spec B) and future inequalities (R10) need validation against optima that are
certified independently of any ILP. The only independent validator of the project enumerates subsets
and is limited to `n ≤ 5`. The literature provides exact polynomial algorithms for paths and cycles
(Das) and spiders (Pereira & Ravelo), which would give certified optima at much larger `n` — but the
spider algorithm's proof is a sketch, does not discuss `S∩T`, and has at least five points where a
literal reading may fail. Implementing these algorithms and comparing them with the baseline ILP and
the independent validator both creates the certifier the program needs and tests the algorithms
themselves.

## Goals

- [ ] The three algorithms are implemented as literally as their sources allow, with every reading
      ambiguity recorded rather than silently resolved.
- [ ] A pre-registered batch, including the five readings above and `S∩T`/permanence, is compared
      across algorithm, baseline ILP, independent validator and (when available) F-CC/F-C3.
- [ ] Every confirmed divergence is reduced to a minimal counterexample verified by enumeration and
      recorded.

## Out of Scope

| Item | Reason |
|---|---|
| The tree algorithm of IJCAI-26 (Theorem 9) | Not approved by the plan; needs a new approval |
| FPT, modular-width, vertex-cover algorithms | Out of scope by the plan (certifiers only, not a research line) |
| Correcting a published algorithm | This spec documents and reports; any correction is the authors' decision |
| Public statements about a counterexample | Communicated first to the authors (same research group) |
| Performance comparison of the ILP on special classes | Not a goal; may be recorded as context only |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Implementation fidelity | Literal implementation of the published description; each ambiguity gets a documented reading, and when two readings are plausible both are implemented and tested | Testing a guessed variant would not test the published algorithm | n |
| Batch composition | Random paths, cycles and spiders with `S∩T` and permanence, plus hand-built instances for readings 1–5, sizes chosen so that the baseline ILP proves optimality | Certification needs an independent OPT for every instance | n |
| OPT reference | Baseline ILP solved to optimality (T5 equivalence) for all instances; `opt_por_enumeracao` additionally where `n` allows | Two independent references where possible | n |
| Handling a counterexample | Minimal instance, verified by enumeration, documented, and communicated to the authors before any public mention | Plan §5 rule | y (plan) |
| Batch size | Fixed in the pre-registration before running | Avoids stopping when convenient | n |

**Open questions:** none — every pending decision is recorded above with its default.

---

## Definitions

- **Path, cycle**: as in Das (§2 of the preprint). **Spider**: a tree with exactly one vertex `c` of
  degree ≥ 3; the components of `G − c` are the radials.
- **Agreement**: the algorithm's value equals the certified OPT **and** the algorithm's station set is
  feasible according to `independent_validator.viavel` (or the baseline ILP with `y` fixed when `n` is
  too large for the validator).
- **Divergence**: any instance where either condition fails.

---

## User Stories

### P1: R11a — Implement the certifiers ⭐ MVP

**User Story**: As a researcher who needs optima certified independently of the ILP, I want the
published algorithms for paths, cycles and spiders implemented faithfully.

**Why P1**: The rest of the spec depends on it.

**Acceptance criteria:**

1. The system SHALL implement Das's path algorithm and cycle algorithm as described in the preprint, citing the lemma or algorithm line for each step.
2. The system SHALL implement the Pereira & Ravelo spider algorithm as described in the article, citing Lemma 1, Lemma 2 and Theorem 1 for each step.
3. WHEN the description admits more than one reading THEN the system SHALL document each reading and implement every plausible one as a separate variant.
4. The system SHALL return, for each instance, the station set and its size, not only the size.
5. The system SHALL handle `S∩T` and permanence explicitly, recording where the source is silent.

**Required tests:** hand-checked small cases from the sources' own examples, when available.

**Evidence to produce:** code with references to the sources, and a document listing every reading
decision.

**Risks:** filling gaps of a sketch by intuition. Criterion 3 forbids choosing a single reading
silently.

**Dependencies:** Spec A R1.

**Independent Test**: each variant runs on a path, a cycle and a spider of a few vertices and returns
a feasible station set.

---

### P1: R11b — Pre-registered comparison batch

**User Story**: As a researcher validating formulations at scale, I want each certifier compared
against independent references on a batch fixed in advance.

**Why P1**: It produces both the certified instances and the verification of the algorithms.

**Acceptance criteria:**

1. The system SHALL write the batch (generators, seeds, sizes, `r` values, the hand-built instances for readings 1–5, `S∩T` cases) before running any comparison.
2. The system SHALL compare every instance across: the specialized algorithm, the baseline ILP, the independent validator where `n` allows, and F-CC/F-C3 when Spec B provides an implementation.
3. The system SHALL report agreement or divergence per instance, per algorithm variant.
4. The system SHALL include the test case of reading 2 (`s` adjacent to `c`, `t` at distance `2r+1` from `c` in an empty radial).
5. The system SHALL record the generator seed and sha256 of every instance.

**Required tests:** the baseline ILP and the validator agree on every instance where both run (a
disagreement there is a regression of Block 1, not of the certifier).

**Evidence to produce:** pre-registration, CSV of results, report.

**Risks:** the ILP may be slow on long cycles with small `r`; sizes are bounded in the
pre-registration.

**Dependencies:** R11a.

**Independent Test**: the CSV can be regenerated from the pre-registration.

---

### P1: R11c — Divergence handling

**User Story**: As a member of the same research group as the authors, I want any confirmed
divergence documented precisely and communicated before any public mention.

**Why P1**: A published algorithm may need correction; this must be handled carefully.

**Acceptance criteria:**

1. WHEN a divergence is found THEN the system SHALL reduce it to a minimal instance and verify the true optimum by enumeration.
2. The system SHALL record the divergence with the instance, the algorithm variant, the reading used, the algorithm's output, the certified OPT and the infeasibility or suboptimality found.
3. IF the divergence depends on the reading THEN the system SHALL report which readings fail and which do not.
4. The system SHALL mark every confirmed divergence for communication to the authors before any public mention.
5. IF no divergence is found in the batch THEN the system SHALL record agreement and the batch coverage, and SHALL NOT claim the algorithm proven.

**Required tests:** enumeration of the minimal instance.

**Evidence to produce:** a divergence report (or an agreement report).

**Risks:** confusing an implementation bug with an error in the published algorithm; the minimal
instance must be checked against the source text line by line.

**Dependencies:** R11b.

**Independent Test**: each recorded divergence can be reproduced from its minimal instance alone.

---

## Stop Criteria

- The spec ends when the pre-registered batch is complete and R11c has produced its report.
- It is never extended with larger or more instances without a new pre-registration.

## Edge Cases

- IF a spider has a radial of length 0 (center adjacent to a leaf) THEN it SHALL be handled as a
  radial of one vertex.
- IF `S∩T` contains the center `c` THEN the case SHALL be included explicitly.
- IF `r` exceeds the diameter THEN OPT is 0 and every algorithm SHALL return the empty set.
- IF the source is silent on a case THEN the implementation SHALL raise an explicit "unspecified"
  outcome rather than guess.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| CERT-01 | P1: R11a | Design | Pending |
| CERT-02 | P1: R11a | Design | Pending |
| CERT-03 | P1: R11a | Design | Pending |
| CERT-04 | P1: R11a | Design | Pending |
| CERT-05 | P1: R11a | Design | Pending |
| CERT-06 | P1: R11b | Design | Pending |
| CERT-07 | P1: R11b | Design | Pending |
| CERT-08 | P1: R11b | Design | Pending |
| CERT-09 | P1: R11b | Design | Pending |
| CERT-10 | P1: R11b | Design | Pending |
| CERT-11 | P1: R11c | Design | Pending |
| CERT-12 | P1: R11c | Design | Pending |
| CERT-13 | P1: R11c | Design | Pending |
| CERT-14 | P1: R11c | Design | Pending |
| CERT-15 | P1: R11c | Design | Pending |

**Coverage:** 15 total, 0 mapped to tasks (`tasks.md` not created in this round), 15 unmapped.

---

## Success Criteria

- [ ] Three certifiers implemented with every reading decision documented.
- [ ] Pre-registered batch compared across all available references.
- [ ] Every divergence minimal, enumerated and marked for communication; or agreement recorded with
      coverage.

---

## Inconsistencies Found During Specification

| # | Inconsistency | Class |
|---|---|---|
| 1 | The Pereira & Ravelo file still has its original name with spaces | plan ahead of implementation (Spec A R1) |
| 2 | The `overlap` document's reference to Pereira & Ravelo (§1.2, ref. 4) was written from a web search, before the article was in the repository | documentation stale (to be checked in Spec A R1) |
| 3 | The definition in the article allows `S∩T`, but the proofs never treat it | mathematical claim unverified |

---

## Future conditional work — BLOCKED

The IJCAI-26 tree algorithm (Theorem 9) could extend the certifiers, but it requires new approval.
The certifiers produced here are inputs to the future specs R8 (column generation) and R10
(compatibility inequalities), which remain blocked by GF1 and G1. Nothing in this spec authorizes
them.
