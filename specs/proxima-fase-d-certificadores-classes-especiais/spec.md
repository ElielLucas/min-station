# Next Phase D — Exact Certifiers for Special Graph Classes (MIN-STATION) Specification

Scope: task **R11 — S1, special graph classes** of `docs/technical/plans/plano-proxima-fase.md`.

**Final status:** `COMPLETE — CONFIRMED DIVERGENCE` (2026-10-07).

This spec implements the published exact polynomial algorithms for:

- paths — Das, `O(n)`;
- cycles — Das, `O(n²)`;
- spiders — Pereira & Ravelo, `O(|V|)` as stated in the article;

and evaluates them as **independent structural certifiers** for MIN-STATION.

The line has two purposes:

1. provide exact optima and explicit feasible station sets for special graph classes at sizes where exhaustive subset enumeration is no longer practical;
2. independently test the published algorithms against the project's already validated exact infrastructure.

This is a **support/certification line**, not a new optimization-method line.

Evidence vocabulary: **[Fato]**, **[Conferido]**, **[Evid.]**, **[Hipótese]**, **[Sugestão]**, as defined in the current research plan.

Nothing in this spec assumes that a published algorithm is incorrect. Ambiguities or possible proof gaps are treated as readings to be tested.

---

## Relationship with the other next-phase specs

| Spec / line | Relation |
|---|---|
| A — Foundation | **R1 completed.** The Pereira & Ravelo transcription is already available as `docs/technical/reference/pereira-ravelo-2026-aranhas.md`. |
| B — Formulations | **Completed through GF1.** F-CC is defined, implemented and computationally verified; `GF1 = PASS`. F-C3 remains `OPEN` because the trio networks are not defined precisely enough to implement. |
| C — Diagnosis | **Completed through G1.** Compatibility is the selected direction; R10 and R8/R9 were released under their respective gates. R11 remains an independent support line. |
| R8 / R9 — F-CC at scale | May use the certifiers produced here to validate exact results on paths, cycles and spiders. |
| R10 — Compatibility inequalities | Its mandatory validation flow includes the Spec D certifiers before moving to larger development instances. |
| Future exact work | May reuse the certified families and generated instances, but extending the algorithms beyond paths, cycles and spiders requires a new approved scope. |

R11 was originally allowed to start immediately after R1. The repository has advanced further: Specs B and C are now complete, so this execution SHALL consume their available results instead of treating them as future dependencies.

---

## Current State

**Audited:** 2026-10-07, after the official R11 run.

| Item | Status | Evidence |
|---|---|---|
| Das path algorithm (`O(n)`) | IMPLEMENTED + VERIFIED LITERAL | `experiments/structural/path_cycle.py::certificar_path`; 3 agreement / 12 suboptimal |
| Das cycle algorithm (`O(n²)`) | IMPLEMENTED + VERIFIED LITERAL | `experiments/structural/path_cycle.py::certificar_cycle`; 2 agreement / 9 suboptimal |
| Pereira & Ravelo spider readings | IMPLEMENTED + VERIFIED | `experiments/structural/spider.py`; `spider-A/B/U`; none is an exact universal certifier in the batch |
| Path/cycle/spider generators | DONE | deterministic structural generators + official catalog |
| Frozen R11 catalog | DONE | `experiments/structural/r11_catalog.py`; 44 official instances |
| Instance preparation / hash manifest | DONE | `experiments/structural/prepare_r11.py`; `instances/estrutural/r11-manifest.csv` |
| Local verification | PASS | `verify_r11.py` returned `ok: verify_r11` |
| Structural regressions | PASS | BP/HB/SC/TR verification scripts returned `ok` after the `S∩T` infrastructure change |
| Official runner | DONE | `experiments/structural/run_r11.py` produced 80 official rows |
| Raw R11 evidence | DONE | `results/structural/r11-certificadores.csv`; commit column `dd485dc` |
| Independent enumeration | CONSISTENT | `OPTIMAL` on all 69 micro rows; equals baseline/F-CC |
| Baseline ILP | CONSISTENT | `OPTIMAL` on 80/80 rows |
| F-CC binary cross-check | CONSISTENT | `OPTIMAL` on 80/80 rows; `reference_failure=0` |
| F-C3 | `OPEN` | trio networks remain undefined precisely enough for implementation |
| Divergence audit | DONE | `docs/technical/reference/auditoria-r11-divergencias.md` |
| Result report | DONE | `docs/technical/reference/resultados-r11-certificadores.md` |
| Final conclusion | `CONFIRMED DIVERGENCE` | `docs/technical/reference/conclusao-r11-certificadores.md` |
| Compatibility diagnosis / G1 | DONE — compatibility | R11 does not reopen G1 |

### Important correction to the original Spec D

`opt_por_enumeracao` has **no hard-coded `n ≤ 5` limit**.

It is exponential in `|V|`, so its practical use must be capped by protocol.

For reference, F3 pre-registered:

```text
n_opt_enum = 16
```

with larger instances using the baseline MIP solved to optimality.

R11 SHALL therefore define its own enumeration cap in its pre-registration instead of treating `n ≤ 5` as a property of the validator.

---

## Spider-proof readings to test

The following are **[Hipótese]** readings already identified in the research plan. They are test targets, not claims that the article is wrong.

### SP-R1 — Robots entering a radial

Lemma 1 reasons mainly about robots leaving a radial toward the center `c`.

A robot arriving from another radial toward a target inside that radial reaches `c` with a battery state that depends on the previous segment and on how the center is treated.

The implementation SHALL identify exactly how the published algorithm handles this direction.

### SP-R2 — Reachability from the center

The statement that from `c` every target is reachable requires examination when a target lies farther than `r` from `c` in a radial with no outgoing robot that would otherwise induce stations there.

Mandatory constructed case:

```text
s adjacent to c
t at distance 2r + 1 from c
t lies in another radial
that radial has no outgoing robot
```

### SP-R3 — Exchange argument

The exchange argument in Lemma 2 appears not to explicitly discuss:

- stations already inside the target radial;
- origin/target pairs lying entirely in the same radial;
- interactions between internal and cross-radial movements.

These cases SHALL be represented explicitly.

### SP-R4 — `S ∩ T` and permanence

The MIN-STATION definition allows:

```text
S ∩ T ≠ ∅
```

and the project baseline explicitly supports permanence.

The spider proof does not explicitly discuss these cases.

They SHALL be tested separately rather than silently interpreted.

### SP-R5 — Boundary `r' = 0`

The article text uses assumptions involving:

```text
0 < r'
```

The behavior at:

```text
r' = 0
```

SHALL be identified and tested.

---

## Problem Statement

The project now has:

- a validated baseline formulation;
- an independent feasibility validator;
- subset enumeration for exact OPT at small sizes;
- an exact F-CC characterization;
- a diagnosis showing that compatibility is a relevant source of difficulty.

Future compatibility inequalities and F-CC-based exact methods need independent validation beyond arbitrary general-purpose MIP comparisons.

Paths, cycles and spiders provide an unusually useful setting because published polynomial algorithms claim exact solutions for these graph classes.

If implemented faithfully and independently of the ILP machinery, they can serve as structural certifiers.

However, a certifier can only be trusted after its implementation has itself been validated.

For paths and cycles, the implementation must reproduce Das's algorithms exactly.

For spiders, the source contains cases that require explicit reading decisions, especially around cross-radial movement, `S∩T`, permanence and boundary conditions.

R11 therefore proceeds in this order:

```text
source reading
    ↓
documented interpretation
    ↓
literal implementation
    ↓
local verification
    ↓
pre-registration
    ↓
frozen comparison batch
    ↓
raw evidence
    ↓
result report
    ↓
minimal divergence analysis, if necessary
    ↓
final conclusion
```

The comparison SHALL distinguish between:

1. validity of the station set returned by the specialized algorithm;
2. optimality of its objective value.

Matching only the objective value is insufficient.

---

## Goals

- [x] Implement exact certifier code for paths, cycles and spiders as literally as their sources permit and verify the implementations before the official batch.
- [x] Record every non-trivial interpretation required to turn the publications into executable algorithms. (`docs/technical/reference/leituras-r11-certificadores.md`, 2026-10-06)
- [x] Preserve each algorithm's explicit station set `C`, not only `|C|`.
- [x] Add deterministic generators for paths, cycles and spiders following the existing `experiments/structural/` pattern and materialize the official instances.
- [x] Add opt-in `S∩T` support for R11 while preserving the previous default in existing structural families; regressions BP/HB/SC/TR passed.
- [x] Freeze the complete R11 comparison batch, including SHA-256 hashes, before observing comparison results.
- [x] Compare the specialized algorithms with the baseline, independent enumeration where tractable, and F-CC under the frozen protocol.
- [x] Keep F-C3 explicitly `OPEN`; never implement an inferred trio network.
- [x] Reduce/audit each confirmed divergence mechanism to a reproducible minimal witness whenever practical.
- [x] Produce versioned raw evidence and human-readable research conclusions.

---

## Out of Scope

| Item | Reason |
|---|---|
| IJCAI-26 general tree algorithm | Not approved as part of R11; requires separate scope approval |
| FPT algorithms | Already-published theory; not the purpose of S1 |
| Modular-width algorithms | Outside R11 |
| Vertex-cover parameterized algorithms | Outside R11 |
| New formulation for MIN-STATION | R11 is a certification line |
| Column generation | R8 |
| Branch-and-price / price-and-branch | R9 |
| Compatibility inequalities | R10 |
| Matheuristic | R12 |
| Changing the baseline | Baseline remains the reference exact ILP |
| Implementing F-C3 by guessing its trio networks | Explicitly forbidden while F-C3 remains `OPEN` |
| Proving published algorithms correct from experiments | Finite experimental agreement is not a proof |
| Correcting a publication | This line documents evidence; mathematical corrections belong to a separate research decision |
| Publicly asserting a published error before internal verification and author communication | Research-governance requirement |
| Benchmarking runtime superiority of the special-class algorithms against the ILP | Runtime may be recorded as context, but performance superiority is not a goal of R11 |

---

## Assumptions & Decisions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Algorithm fidelity | Implement the published description literally | R11 must test the source algorithm, not an improved reconstruction | y |
| Ambiguous source text | Record the ambiguity before experimentation; implement every materially plausible reading when practical | Avoids silently selecting the reading that agrees with the baseline | y |
| Source silence | Return an explicit `unspecified` state when no defensible reading exists | Guessing would invalidate the verification | y |
| Station-set output | Every certifier returns both `C` and `|C|` | Feasibility and objective must be checked independently | y |
| `S∩T` | Required in the batch | It is valid in the original MIN-STATION problem and supported by the current baseline | y |
| Permanence | Required in the batch | Das explicitly permits it and the project treats it as an invariant | y |
| Enumeration | Used only under a cap frozen in pre-registration | `opt_por_enumeracao` is exponential but has no intrinsic `n` limit | y |
| Baseline OPT | Baseline MIP solved to `OPTIMAL` may certify OPT when enumeration is outside its cap | Baseline equivalence already established by T5 | y |
| F-CC | Used as an additional exact cross-check when explicit connected-set enumeration stays under the R11 `max_W` cap | F-CC is now implemented and verified exact for binary `y` | y |
| F-C3 | Reported as `OPEN/not available` | Trio networks remain undefined | y |
| Batch size | Frozen before comparison | Prevents adding/removing instances based on observed agreement | y |
| Counterexample handling | Minimize, enumerate whenever practical, reread source line-by-line, then communicate before public mention | Avoids confusing implementation errors with publication errors | y |
| Existing structural families | Their current semantics SHALL remain unchanged | R11 must not regress BP/HB/SC/TR infrastructure | y |

**Open questions:** none required to begin implementation.

Exact batch sizes, seeds, `r` values, enumeration cap and F-CC `max_W` cap SHALL be fixed by the R11 pre-registration before the official batch runs.

---

## Definitions

### Special graph classes

**Path:** a connected graph in which exactly two vertices have degree 1 and all remaining vertices have degree 2, except the one-vertex trivial case if explicitly generated.

**Cycle:** a connected 2-regular graph.

**Spider:** a tree with exactly one vertex `c` of degree at least 3.

The connected components of:

```text
G - c
```

are the spider's **radials**.

A leaf directly adjacent to `c` corresponds to a radial containing one vertex.

### Station set

The specialized algorithm SHALL return:

```text
C ⊆ V
```

plus its objective:

```text
|C|
```

### Feasibility agreement

For a returned station set `C`:

```text
algorithm_feasible = independent_validator.viavel(...)
```

when the independent validator is applicable.

For larger cases, the runner MAY additionally validate a fixed `C` through another exact equivalent formulation, but this SHALL be recorded separately.

### Objective agreement

```text
algorithm_obj = certified_OPT
```

within exact integer comparison.

### Agreement

An algorithm variant agrees on an instance iff:

```text
algorithm_status == "ok"
AND
algorithm_feasible == true
AND
algorithm_obj == certified_OPT
```

### Divergence

A divergence exists when at least one of the following occurs:

```text
returned C is infeasible
algorithm_obj > certified_OPT
algorithm_obj < certified_OPT
```

The last case necessarily indicates that the returned solution, the reference, or the interpretation is inconsistent and SHALL be investigated before classification.

### Unspecified

`unspecified` means:

> the source does not provide enough information to define a faithful executable behavior for that case without adding an unproven interpretation.

It is not counted as agreement or divergence.

---

## Required Repository Organization

R11 SHALL follow the organization already established by the structural and experimental lines.

```text
experiments/
└── structural/
    ├── io_instancia.py
    ├── path_cycle.py
    ├── spider.py
    ├── r11_catalog.py
    ├── prepare_r11.py
    ├── verify_r11.py
    └── run_r11.py

instances/
└── estrutural/
    ├── path/
    ├── cycle/
    ├── spider/
    └── r11-manifest.csv

results/
└── structural/
    └── r11-certificadores.csv

docs/
└── technical/
    └── reference/
        ├── leituras-r11-certificadores.md
        ├── pre-registro-r11-certificadores.md
        ├── resultados-r11-certificadores.md
        └── conclusao-r11-certificadores.md

specs/
└── proxima-fase-d-certificadores-classes-especiais/
    └── spec.md
```

Existing files SHALL be reused instead of duplicated.

In particular:

- `experiments/structural/io_instancia.py`;
- `experiments/cuts/independent_validator.py`;
- baseline infrastructure;
- `experiments/alternative-formulations/fcc.py`.

---

# User Stories

## P1: R11a.1 — Record source interpretations ⭐ MVP

**User Story:** As a researcher implementing published exact algorithms, I want every mathematical reading needed for execution recorded before relying on the implementation.

**Why P1:** A code implementation is not an independent test of a publication if ambiguities are silently resolved in favor of expected results.

### Acceptance criteria

1. The system SHALL create:

```text
docs/technical/reference/leituras-r11-certificadores.md
```

2. The document SHALL identify the exact source sections used for:
   - Das path algorithm;
   - Das cycle algorithm;
   - Pereira & Ravelo spider algorithm.

3. The document SHALL map executable steps to the corresponding theorem, lemma or algorithm statement whenever available.

4. The document SHALL contain explicit entries for:

```text
SP-R1
SP-R2
SP-R3
SP-R4
SP-R5
```

5. WHEN two materially different readings are defensible THEN both SHALL receive stable identifiers.

6. WHEN no faithful reading can be extracted THEN that case SHALL be marked `OPEN/UNSPECIFIED`.

7. The document SHALL explicitly distinguish:
   - source statement;
   - project interpretation;
   - implementation consequence;
   - test that exercises the interpretation.

8. No algorithmic ambiguity SHALL exist only inside Python comments.

### Evidence to produce

```text
docs/technical/reference/leituras-r11-certificadores.md
```

### Dependencies

- `min-station-das.pdf`;
- `pereira-ravelo-2026-aranhas.md`;
- project invariants from `docs/project-overview.md`.

### Independent Test

A reader who has the publications and this document can explain why every implemented branch exists.

---

## P1: R11a.2 — Add deterministic generators for paths, cycles and spiders

**User Story:** As a researcher building reproducible structural experiments, I want the three graph classes generated using the same deterministic infrastructure as the existing structural families.

### Acceptance criteria

1. The system SHALL implement deterministic path and cycle generation in:

```text
experiments/structural/path_cycle.py
```

2. The system SHALL implement deterministic spider generation in:

```text
experiments/structural/spider.py
```

3. Every generated instance SHALL provide:

```text
S
T
V
arestas
adj
r
metadata
```

4. Every persisted instance SHALL use:

```text
experiments/structural/io_instancia.py
```

5. Every persisted instance SHALL contain deterministic metadata and a reproducible `sha256`.

6. Instance output SHALL be stored only under:

```text
instances/estrutural/path/
instances/estrutural/cycle/
instances/estrutural/spider/
```

7. Generators SHALL support intentionally constructed:
   - `S∩T`;
   - permanence;
   - same-radial origin/target pairs;
   - cross-radial pairs;
   - center in `S`;
   - center in `T`;
   - center in `S∩T`.

8. The generator SHALL NOT assume:

```text
S ∩ T = ∅
```

9. Existing BP/HB/SC/TR generators SHALL remain behaviorally unchanged.

### Required infrastructure adjustment

The current:

```python
conferir_fidelidade(...)
```

rejects `S∩T`.

R11 SHALL modify this API in a backward-compatible way, for example:

```python
conferir_fidelidade(
    S,
    T,
    V,
    arestas,
    r,
    permitir_intersecao=False,
)
```

The default SHALL preserve the semantics expected by existing structural generators.

R11 generators SHALL explicitly opt into:

```python
permitir_intersecao=True
```

when needed.

### Required tests

Existing structural verification scripts SHALL continue to pass after this change.

### Evidence to produce

- generator code;
- generated instances;
- deterministic hashes;
- regression checks for existing structural families.

### Dependencies

R11a.1.

---

## P1: R11a.3 — Implement the exact special-class certifiers

**User Story:** As a researcher needing exact independent structural solutions, I want the published path, cycle and spider algorithms implemented faithfully.

### Acceptance criteria

1. The system SHALL implement Das's path algorithm according to the published algorithm and supporting lemmas.

2. The system SHALL implement Das's cycle algorithm according to the published algorithm and supporting lemma.

3. The system SHALL implement the Pereira & Ravelo spider algorithm according to its published description.

4. Every non-trivial algorithm step SHALL reference its source or a stable reading ID from:

```text
leituras-r11-certificadores.md
```

5. Each certifier result SHALL contain at least:

```text
status
C
obj
variant
notes
```

6. `obj` SHALL equal:

```text
len(C)
```

whenever `status == "ok"`.

7. Multiple plausible spider readings SHALL be implemented as separate variants.

8. No variant SHALL silently repair another variant after observing disagreement with the baseline.

9. Cases unsupported by a faithful reading SHALL return:

```text
status = "unspecified"
```

instead of guessing.

10. `S∩T` and permanence SHALL be treated explicitly.

11. The case:

```text
r >= diameter(G)
```

SHALL be present in verification and in the official batch. The certifier SHALL
**not** special-case it to force `C = ∅`: PATH-ALG1 / DAS-A2 must remain
literal even if their published counter logic returns a nonempty set while the
MIN-STATION reference optimum is 0. Such a difference is classified by the
normal R11 agreement/divergence rules.

12. The certifiers SHALL NOT call:
   - `baseline.py`;
   - Gurobi;
   - F-CC;
   - `opt_por_enumeracao`;

to construct their own answer.

Those references may only be used by verification or comparison code.

### Evidence to produce

Implementation in the structural experiment module(s).

### Risks

The principal risk is transforming an incomplete proof sketch into a stronger algorithm than the publication actually states.

This is forbidden.

### Dependencies

R11a.1 and R11a.2.

### Independent Test

Each certifier can be called directly on a small compatible instance and returns an explicit station set without invoking any project optimization model.

---

## P1: R11a.4 — Verify implementation locally before the official batch

**User Story:** As a researcher, I want implementation errors separated from experimental divergences before the pre-registered comparison begins.

### Acceptance criteria

1. The system SHALL create:

```text
experiments/structural/verify_r11.py
```

2. The verification SHALL include hand-checkable path cases.

3. The verification SHALL include hand-checkable cycle cases.

4. The verification SHALL include hand-checkable spider cases.

5. The verification SHALL exercise all implemented spider variants.

6. The verification SHALL check:

```text
obj == len(C)
```

for every successful result.

7. Every successful returned `C` SHALL be checked through:

```text
independent_validator.viavel
```

on the local verification instances.

8. The verification SHALL include:
   - OPT 0;
   - one-station cases;
   - `S∩T`;
   - permanence;
   - center in `S∩T`;
   - a one-vertex radial;
   - same-radial movement;
   - cross-radial movement;
   - SP-R2;
   - SP-R5.

9. The script SHALL fail loudly on an unexpected disagreement.

10. Expected `unspecified` cases SHALL be asserted explicitly rather than treated as test failures.

### Evidence to produce

```text
experiments/structural/verify_r11.py
```

and a reproducible successful execution.

### Dependencies

R11a.3.

### Independent Test

Running the verification script from a clean checkout reproduces the assertions without consulting the official R11 result CSV.

---

# P1: R11b — Pre-registered comparison batch

**User Story:** As a researcher validating structural certifiers, I want the comparison sample and interpretation rule fixed before seeing the official results.

**Why P1:** The batch must not expand or shrink in response to whether a published algorithm agrees.

---

## R11b.1 — Write the pre-registration

### Acceptance criteria

1. Before running the official comparison, the system SHALL create:

```text
docs/technical/reference/pre-registro-r11-certificadores.md
```

2. The pre-registration SHALL freeze:
   - instance families;
   - generator parameters;
   - deterministic seeds;
   - sizes;
   - `r` values;
   - number of radials for spiders;
   - `S/T` construction policies;
   - spider variants;
   - enumeration cap;
   - F-CC `max_W` cap;
   - baseline solver settings;
   - exact-reference priority;
   - treatment of time/cap failures;
   - comparison tolerance, if any;
   - required output columns;
   - stop rule.

3. The official batch SHALL contain two explicit strata:

### Micro stratum

Instances small enough for subset enumeration under the frozen cap.

Where practical, these SHALL have:

```text
specialized algorithm
baseline
independent enumeration
F-CC exact cross-check
```

### Medium stratum

Instances deliberately beyond the subset-enumeration cap.

These SHALL compare at minimum:

```text
specialized algorithm
baseline solved to optimality
```

and additionally F-CC where `max_W` permits.

4. The pre-registration SHALL include:
   - random/deterministic paths;
   - random/deterministic cycles;
   - random/deterministic spiders;
   - hand-built SP-R1–SP-R5 cases.

5. `S∩T` SHALL NOT be represented by a single token edge case only.

The batch SHALL include multiple structurally different intersection/permanence cases.

6. Exact sizes SHALL be chosen before official comparison results are produced.

7. No new size, seed, variant or instance SHALL be inserted into the official batch after comparison begins.

Any exploratory follow-up requires a new labeled pre-registration.

### Evidence to produce

```text
docs/technical/reference/pre-registro-r11-certificadores.md
```

### Dependencies

R11a.4.

---

## R11b.2 — Version the five spider-proof cases

### Acceptance criteria

The project SHALL persist explicit instances for the five proof readings.

Stable IDs SHOULD follow:

```text
spider-reading-01
spider-reading-02
spider-reading-03
spider-reading-04
spider-reading-05
```

or an equally stable documented naming convention.

Each case SHALL be stored under:

```text
instances/estrutural/spider/
```

Each SHALL have:

- deterministic contents;
- metadata identifying the reading;
- `sha256`.

### Mandatory SP-R2 instance

At least one persisted case SHALL satisfy literally:

```text
d(s,c) = 1
d(c,t) = 2r + 1
s and t are in different radials
the radial containing t has no outgoing robot
```

unless the source interpretation itself makes the construction impossible, in which case the reason SHALL be documented before execution.

### Dependencies

R11b.1.

---

## R11b.3 — Define exact comparison references

The official comparison SHALL distinguish sources of evidence.

### Reference A — Independent enumeration

When the instance is under the frozen cap:

```text
experiments/cuts/independent_validator.py::opt_por_enumeracao
```

is the preferred independent OPT.

### Reference B — Baseline exact MIP

When enumeration is outside the cap:

```text
baseline / existing exact measurement infrastructure
```

may certify OPT only when the model terminates with an exact optimal status.

A time-limited incumbent SHALL NOT be labeled OPT.

### Reference C — F-CC

F-CC is already established as an exact characterization for binary `y`.

When its connected-set enumeration is within the pre-registered `max_W`, R11 SHALL use F-CC as an additional exact cross-check.

The current F-CC implementation exposes LP and fixed-`y` verification but no public helper dedicated to optimizing binary `y`.

R11 MAY add a minimal helper such as:

```python
opt_fcc(...)
```

provided that:

- it reuses the existing F-CC model definition;
- `y` is genuinely binary;
- it does not change the mathematical F-CC definition;
- existing F3 behavior remains unchanged;
- the helper is covered by tests.

F-CC SHALL NOT replace independent enumeration where enumeration is available.

### Reference D — F-C3

F-C3 remains:

```text
OPEN
```

Therefore every result table SHALL report it as unavailable/open rather than inventing an implementation.

---

## R11b.4 — Implement one official runner

### Acceptance criteria

1. The system SHALL create:

```text
experiments/structural/run_r11.py
```

2. This SHALL be the official producer of:

```text
results/structural/r11-certificadores.csv
```

3. The runner SHALL reproduce exactly the frozen pre-registration.

4. It SHALL NOT adaptively:
   - add instances;
   - change sizes;
   - change `r`;
   - change variants;
   - change solver limits;

because of observed results.

5. Each row SHALL represent one:

```text
(instance, algorithm_variant)
```

pair.

6. The runner SHALL validate the returned station set independently from the algorithm that generated it.

7. It SHALL compare objective values only after feasibility has been checked.

8. It SHALL record failure/cap states instead of dropping rows.

---

## R11b.5 — Raw-result schema

The CSV SHALL contain enough information to regenerate the research report.

At minimum:

```text
id
familia
variante
n
m
r
seed
sha256

alg_status
alg_obj
alg_C
alg_viavel

opt
fonte_opt

baseline_obj
baseline_status

enum_obj
enum_status

fcc_obj
fcc_status

fc3_status

acordo_obj
acordo_viabilidade
resultado

commit
```

Additional provenance MAY be included, such as:

```text
n_radiais
max_W
n_W
solver_seed
threads
runtime
notes
```

### Required status semantics

`resultado` SHALL distinguish at least:

```text
agreement
infeasible_solution
suboptimal
objective_below_reference
unspecified
reference_failure
implementation_error
```

No missing row SHALL be interpreted as agreement.

---

## R11b.6 — Cross-reference consistency checks

### Acceptance criteria

1. On every instance where baseline and enumeration both finish exactly:

```text
baseline_OPT == enumeration_OPT
```

SHALL hold.

2. IF they disagree THEN R11 interpretation SHALL stop for that instance.

The discrepancy SHALL first be treated as a regression or reference inconsistency, not as evidence against the specialized algorithm.

3. On every instance where exact binary F-CC finishes:

```text
F-CC_OPT == certified_OPT
```

SHALL hold.

4. IF F-CC disagrees with baseline/enumeration within its supported caps THEN the discrepancy SHALL be debugged before using that row to evaluate a specialized algorithm.

5. F-C3 SHALL never be substituted for an unavailable reference.

---

## R11b.7 — Special-case coverage

The frozen batch SHALL include explicit coverage of:

- `r >= diameter(G)`;
- `S∩T = ∅`;
- `S∩T ≠ ∅`;
- single permanence;
- multiple permanence candidates;
- center in `S`;
- center in `T`;
- center in `S∩T`;
- all cross-radial movement;
- all same-radial movement;
- mixed same-radial and cross-radial movement;
- target radial without outgoing robot;
- origins adjacent to the center;
- targets farther than `r` from the center;
- boundary case related to `r' = 0`;
- minimum spider with at least three radials;
- unequal radial lengths.

Not every combination must occur, but every listed phenomenon SHALL appear in at least one frozen instance.

---

## Evidence to produce for R11b

```text
docs/technical/reference/pre-registro-r11-certificadores.md
instances/estrutural/path/*
instances/estrutural/cycle/*
instances/estrutural/spider/*
instances/estrutural/r11-manifest.csv
results/structural/r11-certificadores.csv
```

### Risks

- F-CC connected-set enumeration can explode even on structurally simple graphs.
- Baseline proof to optimality may become expensive on larger cycle instances with small `r`.
- A large batch can turn a support line into a benchmark project.

The pre-registration caps SHALL prevent this.

### Dependencies

R11a.

### Independent Test

Deleting the CSV and running the documented R11 command sequence from the frozen pre-registration regenerates the same instance hashes and experimental rows, modulo explicitly recorded solver timing fields.

---

# P1: R11c — Interpret results and handle divergences

**User Story:** As a researcher, I want agreement and divergence classified conservatively so implementation bugs are not confused with mathematical counterexamples.

---

## R11c.1 — Produce the result report

### Acceptance criteria

The system SHALL create:

```text
docs/technical/reference/resultados-r11-certificadores.md
```

The report SHALL begin with reproducibility metadata:

```text
date
spec
pre-registration
raw CSV
commit
source documents
```

It SHALL contain separate sections for:

1. path results;
2. cycle results;
3. spider results;
4. `S∩T` and permanence;
5. SP-R1–SP-R5;
6. reference consistency;
7. unsupported/unspecified cases;
8. divergences, if any.

The report SHALL distinguish:

```text
number of instances
number of algorithm variants
number of agreement rows
number of divergence rows
number of unspecified rows
number of reference failures
```

It SHALL NOT hide unsuccessful rows.

---

## R11c.2 — Reduce confirmed divergences

WHEN a candidate divergence occurs:

1. verify that the instance file hash matches the pre-registration;
2. verify the reference result;
3. verify station-set feasibility independently;
4. reread the source step-by-step;
5. check whether the behavior depends on an interpretation variant;
6. only then classify it as a confirmed divergence candidate.

For every confirmed divergence, the system SHALL attempt to reduce:

```text
|V|
|S| = |T|
number of radials, if spider
radial lengths
r
```

while preserving the divergence and the relevant graph class.

The reduction SHALL NOT change a spider into a non-spider or a cycle into a path.

---

## R11c.3 — Verify minimal counterexamples independently

Whenever the reduced instance fits the frozen or a separately justified safe enumeration range, the true optimum SHALL be checked through:

```text
opt_por_enumeracao
```

The final counterexample record SHALL contain:

```text
instance id
sha256
graph class
reading / variant
S
T
r
returned C
returned objective
returned feasibility
certified OPT
OPT source
reason for divergence
source passage involved
```

If the instance cannot reasonably be enumerated, the report SHALL state why and SHALL use at least two exact cross-checks when available.

---

## R11c.4 — Distinguish reading-dependent divergences

IF:

```text
variant A diverges
variant B agrees
```

then the report SHALL NOT state simply that "the published algorithm fails".

It SHALL state that the result depends on the interpretation and identify exactly which reading produces which behavior.

---

## R11c.5 — Communication rule

Every confirmed divergence from a published algorithm SHALL be marked:

```text
COMMUNICATION REQUIRED BEFORE PUBLIC CLAIM
```

The repository report MAY document the internal technical evidence.

It SHALL NOT frame the result as a public correction or erratum within this spec.

---

## R11c.6 — Negative result rule

IF the complete pre-registered batch contains no confirmed divergence, the conclusion SHALL use language equivalent to:

> No divergence was found in the pre-registered R11 batch.

It SHALL NOT use language equivalent to:

> The algorithm was proven correct.

The report SHALL state the tested coverage.

---

## R11c.7 — Produce one stable conclusion document

The system SHALL create:

```text
docs/technical/reference/conclusao-r11-certificadores.md
```

Its primary conclusion SHALL be exactly one of:

```text
AGREEMENT ON PRE-REGISTERED BATCH
```

or:

```text
CONFIRMED DIVERGENCE
```

or, if execution cannot provide a valid conclusion:

```text
INCONCLUSIVE
```

### `INCONCLUSIVE` is allowed only when

- reference inconsistency could not be resolved;
- a mandatory source reading remains unimplementable;
- required exact comparisons cannot be completed under the frozen protocol.

An inconclusive result SHALL not be converted into agreement by dropping cases.

---

# Preparation status before execution

As of 2026-10-07, all non-experimental implementation artifacts required to
start R11 are written. **No R11 verification, structural regression, instance
materialization, enumeration, MIP, F-CC comparison, official CSV, result report
or conclusion has been executed/produced by this preparation.**

The remaining work begins with executable evidence: run local verification and
regressions, materialize/freeze the manifest hashes, then run the official batch.

---

# Execution Order

The source reading, pre-registration draft and non-experimental implementation preparation were completed before any official R11 result was observed. Because the pre-registration was intentionally drafted before code, the remaining order is now an **evidence-producing execution order**, not a replay of the historical preparation steps.

Completed preparation:

```text
source/spec reading
    → leituras-r11-certificadores.md
    → pre-registration draft (before implementation/results)
    → optional S∩T infrastructure
    → path/cycle/spider generators + certifiers
    → frozen deterministic catalog
    → verify_r11.py + prepare_r11.py + run_r11.py
    → opt_fcc helper
```

Remaining execution SHALL occur in this order:

```text
1. run verify_r11.py
       ↓
2. run the required BP/HB/SC/TR structural regressions
       ↓
3. fix implementation bugs only; do not repair mathematical divergences
       ↓
4. commit/version the preparation and require a clean working tree
       ↓
5. run prepare_r11.py to materialize the frozen catalog
       ↓
6. review/version the official instances and r11-manifest.csv with SHA-256
       ↓
7. confirm the pre-registration is fully frozen; no parameter/variant changes
       ↓
8. run run_r11.py once under the frozen protocol
       ↓
9. write r11-certificadores.csv
       ↓
10. check reference consistency
       ↓
11. classify agreement/divergence
       ↓
12. minimize confirmed divergences, if any
       ↓
13. write resultados-r11-certificadores.md
       ↓
14. write conclusao-r11-certificadores.md
       ↓
15. update traceability/statuses with the executed evidence
```

No official comparison run SHALL occur before the manifest hashes are frozen and steps 1–7 have completed.

---

# Stop Criteria

R11 stops when all of the following hold:

1. the three source-algorithm lines have executable implementations or explicitly documented `unspecified` cases;
2. the pre-registered batch has been fully processed;
3. every expected CSV row is present or has an explicit failure status;
4. reference inconsistencies have been resolved or marked `INCONCLUSIVE`;
5. every confirmed divergence has undergone the R11c verification flow;
6. `resultados-r11-certificadores.md` exists;
7. `conclusao-r11-certificadores.md` exists.

The line SHALL NOT be extended by:

- adding more seeds;
- increasing sizes;
- adding new graph families;
- changing caps;
- changing spider readings;

after the official results are observed.

Any such follow-up requires a new pre-registration or new approved task.

---

# Edge Cases

### `S∩T`

IF:

```text
S ∩ T ≠ ∅
```

THEN no implementation SHALL discard or duplicate those terminals merely to force disjoint sets.

### Permanence

IF an origin and destination are the same vertex, the corresponding robot MAY remain there without moving.

This SHALL be represented consistently with the MIN-STATION definition.

### Center in `S∩T`

A spider case with:

```text
c ∈ S ∩ T
```

SHALL appear explicitly in the batch.

### Large autonomy

IF:

```text
r >= diameter(G)
```

THEN the independent reference SHALL detect the recharge-free case correctly.
The specialized certifier remains literal; if PATH-ALG1/DAS-A2 returns a
nonempty `C`, R11 records the corresponding divergence instead of repairing it.

### One-vertex radial

A leaf adjacent to the spider center forms a radial of one vertex and SHALL NOT be interpreted as an empty radial.

### `r' = 0`

WHEN the spider algorithm reaches the boundary corresponding to `r' = 0`, behavior SHALL follow an explicitly documented source reading or return `unspecified`.

### Multiple optimal station sets

Agreement does not require:

```text
C_algorithm == C_reference
```

It requires:

```text
C_algorithm feasible
AND
|C_algorithm| == OPT
```

### F-CC cap exceeded

IF explicit connected-set enumeration exceeds `max_W` THEN:

```text
fcc_status = "cap_exceeded"
```

No incomplete F-CC value SHALL be reported.

### Baseline not optimal

IF baseline terminates without an exact optimum THEN its incumbent SHALL NOT be written into the OPT field.

### Enumeration skipped

IF `n` exceeds the pre-registered enumeration cap THEN:

```text
enum_status = "not_run_cap"
```

rather than failure.

### Source silence

IF a published algorithm does not determine a case faithfully THEN:

```text
alg_status = "unspecified"
```

It SHALL NOT be silently patched using baseline behavior.

---

# Regression Requirements

Before the official R11 run:

1. existing structural-family verification SHALL still pass;
2. independent-validator regression tests SHALL still pass;
3. baseline invariants SHALL remain unchanged;
4. F-CC verification SHALL still pass if `fcc.py` is modified;
5. no existing F3 CSV or report SHALL be regenerated or altered by R11;
6. R11 SHALL not modify historical experimental evidence.

---

# Result Interpretation Rules

## Path / cycle / spider agreement

A row is:

```text
agreement
```

only if:

```text
alg_status == ok
alg_viavel == true
alg_obj == OPT
```

## Same objective but infeasible `C`

This is:

```text
infeasible_solution
```

not agreement.

## Feasible but larger objective

This is:

```text
suboptimal
```

## Objective below certified optimum

This is:

```text
objective_below_reference
```

and SHALL trigger immediate consistency investigation.

## Unsupported reading

This is:

```text
unspecified
```

and is reported separately.

## Reference inconsistency

This is:

```text
reference_failure
```

and SHALL be resolved before drawing a conclusion about the specialized algorithm.

---

# Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| CERT-01 | R11a.1 | Source interpretation | Complete — source readings versioned |
| CERT-02 | R11a.1 | Source interpretation | Complete — executable source mapping recorded |
| CERT-03 | R11a.1 | Source interpretation | Complete — SP-R1…SP-R5 explicit |
| CERT-04 | R11a.2 | Structural infrastructure | Complete — infrastructure implemented; regressions BP/HB/SC/TR PASS |
| CERT-05 | R11a.2 | Structural infrastructure | Complete — generators + materialized official instances |
| CERT-06 | R11a.2 | `S∩T` compatibility | Complete — opt-in support; old families preserved |
| CERT-07 | R11a.3 | Path certifier | Complete — literal `path-alg1` implemented and audited |
| CERT-08 | R11a.3 | Cycle certifier | Complete — literal `cycle-alg2` implemented and audited |
| CERT-09 | R11a.3 | Spider certifier | Complete — `spider-A/B/U` implemented and audited |
| CERT-10 | R11a.3 | Explicit station-set output | Complete — `status,C,obj,variant,notes` recorded |
| CERT-11 | R11a.3 | Ambiguous/unspecified behavior | Complete — conservative `unspecified` used for source gaps |
| CERT-12 | R11a.4 | Local verification | Complete — `verify_r11.py` PASS before official batch |
| CERT-13 | R11b.1 | Pre-registration | Complete — frozen protocol + append-only execution record |
| CERT-14 | R11b.2 | Hand-built spider readings | Complete — SP-R1…SP-R5 materialized with SHA-256 |
| CERT-15 | R11b.3 | Exact references | Complete — enum/baseline policies executed consistently |
| CERT-16 | R11b.3 | F-CC cross-check | Complete — binary F-CC exact cross-check on 80/80 rows |
| CERT-17 | R11b.3 | F-C3 remains OPEN | Complete — `OPEN` in all official rows |
| CERT-18 | R11b.4 | Official runner | Complete — official runner executed |
| CERT-19 | R11b.5 | Raw CSV + provenance | Complete — 80-row CSV with hashes/provenance |
| CERT-20 | R11b.6 | Reference consistency | Complete — `reference_failure=0` |
| CERT-21 | R11b.7 | Special-case coverage | Complete — frozen catalog executed |
| CERT-22 | R11c.1 | Human-readable report | Complete — `resultados-r11-certificadores.md` |
| CERT-23 | R11c.2 | Divergence reduction | Complete — reduced/audited by mechanism; path n=2, cycle n=3; SP-R2 minimal under its construction |
| CERT-24 | R11c.3 | Independent counterexample verification | Complete — enum-based post-lot verifier + exact official references |
| CERT-25 | R11c.4 | Reading-dependent classification | Complete — spider conclusions explicitly variant-dependent |
| CERT-26 | R11c.5 | Communication rule | Complete — public-claim warning recorded |
| CERT-27 | R11c.6 | Conservative negative result | Complete / branch not applicable — batch contains divergences; no false correctness claim |
| CERT-28 | R11c.7 | Final conclusion | Complete — `CONFIRMED DIVERGENCE` |

**Coverage:** 28/28 requirements closed.

# Success Criteria

- [x] Source readings for Das and Pereira & Ravelo are versioned and sufficient to audit every executable branch.
- [x] Deterministic generators for paths, cycles and spiders are implemented under `experiments/structural/`.
- [x] Existing structural infrastructure passes regression after enabling optional `S∩T`.
- [x] Path, cycle and spider certifiers return explicit station sets/objectives without using the baseline to construct their answers.
- [x] Every official spider reading is explicit; unsupported mixed/ambiguous cases return `unspecified`.
- [x] `verify_r11.py` passed before the official batch.
- [x] The official batch was frozen before comparison results were observed.
- [x] Every official instance has deterministic provenance and `sha256`.
- [x] The official CSV is reproducible from the pre-registration/manifest.
- [x] Baseline and enumeration agree wherever both exact references were run.
- [x] Exact F-CC agrees with the certified OPT on all official rows.
- [x] F-C3 remains explicitly `OPEN`.
- [x] All successful algorithm outputs are independently checked for feasibility.
- [x] Confirmed divergence mechanisms are reduced and independently verified when practical.
- [x] The final report distinguishes agreement, divergence, unspecified behavior and reference failure.
- [x] The conclusion does not convert finite experimental evidence into an unsupported public erratum claim.

**Final criterion:** satisfied. R11 is closed with `CONFIRMED DIVERGENCE`.

# Inconsistencies Resolved by This Update

| # | Previous statement / state | Updated resolution | Class |
|---|---|---|---|
| 1 | Pereira & Ravelo file still needed to be renamed | Already renamed to `pereira-ravelo-2026-aranhas.md` by Spec A R1 | stale specification state |
| 2 | Spec D depended on future F-CC/F-C3 implementation | F-CC now exists and GF1 = PASS; F-C3 remains OPEN | project advanced after original audit |
| 3 | Independent validator described as limited to `n ≤ 5` | No hard-coded limit exists; enumeration is exponential and receives a pre-registered practical cap | incorrect limitation |
| 4 | R11 comparison treated F-CC as optional future work | F-CC is now a required cross-check where `max_W` permits | stale dependency |
| 5 | F-C3 could be compared "when available" without current status | F-C3 SHALL explicitly remain `OPEN/not available` until its trio networks are formally defined | ambiguity removed |
| 6 | Structural fidelity helper assumes `S∩T = ∅` | R11 requires backward-compatible optional intersection support | implementation mismatch with base problem |
| 7 | Original spec did not define the exact result-location pattern | R11 now fixes code, instance, result and report locations consistent with the repository structure | organization gap |
| 8 | Original spec did not separate station-set validity from objective agreement strongly enough | Both are now mandatory independent conditions for agreement | validation gap |
| 9 | Original spec had only a generic divergence/agreement report | R11 now requires raw CSV, result report and stable conclusion document | reproducibility gap |
| 10 | Spec D relationship text reflected the pre-B/pre-C state | A, B and C current outcomes are now consumed explicitly | stale project state |
| 11 | Earlier acceptance text could be read as forcing `C=∅` when `r≥diam(G)` | The certifier remains literal; `r≥diam` is a test condition and any nonempty result is classified normally | specification-vs-fidelity conflict |

---

# Relationship to Current Gates

## GF1

Current state:

```text
GF1 = PASS
```

Therefore F-CC is an active validated research direction.

This does not make F-C3 executable.

## G1

Current state selects the compatibility side.

Therefore:

```text
R10 / M-A = released
R8 / R9 / M-F = released subject to their own technical specifications
R12 / M-B = blocked
```

R11 remains a parallel support line.

Its execution does not require reopening either GF1 or G1.

---

# Final R11 Decision

```text
COMPLETE — CONFIRMED DIVERGENCE
```

The decision is grounded in `results/structural/r11-certificadores.csv`,
`resultados-r11-certificadores.md` and `auditoria-r11-divergencias.md`. The
path/cycle literal procedures are not valid exact certifiers for the current
MIN-STATION definition; the tested spider readings do not form a universal
exact certifier. Public claims of an erratum remain outside this spec.

---

# Future Conditional Work — NOT AUTHORIZED BY THIS SPEC

The following may consume R11 results but are not implemented here:

### R8 — F-CC column generation

May use path/cycle/spider certifiers to validate exact behavior on controlled special classes.

### R9 — Branch-and-price / price-and-branch

Only under the R8 progression rule.

### R10 — Compatibility inequalities

Its validation sequence SHALL use R11 special-class certifiers before moving to larger development instances, as required by the current research plan.

### General-tree certifier

The IJCAI-26 tree algorithm may be considered in a future approved extension.

It is not silently added to R11.

### New counterexample-driven research

A confirmed divergence may motivate:

- a correction analysis;
- a new theorem;
- a modified spider algorithm;
- communication with the publication authors.

None of those is automatically authorized by this spec.

---

# Final Deliverables

R11 is complete only when the repository contains the applicable versions of:

```text
docs/technical/reference/leituras-r11-certificadores.md

experiments/structural/path_cycle.py
experiments/structural/spider.py
experiments/structural/r11_catalog.py
experiments/structural/prepare_r11.py
experiments/structural/verify_r11.py
experiments/structural/run_r11.py

instances/estrutural/path/*
instances/estrutural/cycle/*
instances/estrutural/spider/*
instances/estrutural/r11-manifest.csv

docs/technical/reference/pre-registro-r11-certificadores.md

results/structural/r11-certificadores.csv

docs/technical/reference/resultados-r11-certificadores.md
docs/technical/reference/auditoria-r11-divergencias.md
docs/technical/reference/conclusao-r11-certificadores.md

experiments/structural/verify_r11_counterexamples.py
```

and this specification's requirement/status table has been updated to reflect the actual execution.

The expected organization is:

```text
source
  → reading
  → implementation
  → local verification
  → pre-registration
  → versioned instances
  → exact comparisons
  → raw CSV
  → interpreted results
  → divergence reduction, if needed
  → final conclusion
```

This is the complete scope of **Next Phase D — Exact Certifiers for Special Graph Classes**.
