# Block 3 — Research and Structural Instances (MIN-STATION) Specification

Scope: T12–T21 from `docs/technical/plans/historico/backlog-continuacao.md`, with scientific basis in
`docs/technical/reference/documentacao-projeto/MIN-STATION-parecer-macro-consolidado.md` §11 (structural families,
pilot matrix, promotion criteria) and §9 Stage 3.

Every statement in Current State was checked in this session by reading the code and the current
documents, and by running the existing verification scripts where relevant. The assessment
(`parecer`) is dated `e9d1ccb` and predates T1–T11; it is treated as the scientific source, not as
a description of the repository state.

---

## Relationship with Blocks 1 and 2

Blocks 1 and 2 are **complete and committed or staged** (verified below). Block 3 consumes their
infrastructure and must not rebuild it.

### What Block 1 delivers to Block 3 (verified present)

| Deliverable | Where | How Block 3 uses it |
|---|---|---|
| Oracle with permanence arc for `S∩T` | `experiments/cuts/cuts.py` (`integer_oracle`, `_build_flow_net_aggregate`), commit `dc83ac9` | Any family measured with CBI or fractional separation; the structural families use `S∩T = ∅`, so the defect is not exercised, but the fix removes the caveat |
| Independent validator | `experiments/cuts/independent_validator.py` (`viavel(S,T,V,adj,r,C)`, `opt_por_enumeracao(S,T,V,adj,r)`, `avisar_se_desconexo`), commit `658099a` | **The enumeration backbone of T12–T17**: OPT by brute force on small cases, feasibility of each `C`, and the disconnection guard for generated instances |
| Terminal regression suite | `experiments/cuts/verify_t3_regressao_terminais.py`, commit `e0c36e7` | Regression safety net; new gadgets added by Block 3 must not break it |
| Equivalence proof of the base formulation | `validacao-formulacao-base.md` §5.5, commit `97b290d` | Licenses using the base model as ground truth for OPT on structural instances, including `S∩T ≠ ∅` if a family ever needs it |

The independent validator refuses non-unit edge weights (`_grafo_unitario`). All Block 3 families
are unit-weight by construction, so this is a fit, not a limitation — but it does mean a weighted
family could not be validated this way.

### What Block 2 delivers to Block 3 (verified present)

| Deliverable | Where | How Block 3 uses it |
|---|---|---|
| Deterministic model construction | `cortes_ordenados` in `cuts.py`, used by `harness.py`, `bc_yspace.py`, `yspace.py`; `verify_t6_determinismo.py` | Precondition for every pilot measurement |
| Budget decision | `decisao-orcamento-worklimit.md`: **`WorkLimit` for method comparison**, `TimeLimit` for wall-clock batches; no runner migrated yet | **Changes the pilot budget** from the assessment's "TL 600 s" — see Pilot Pre-registration |
| Benchmark consolidation | `instances/grupos_origem.csv`, manifest columns `duplicata_de` and `particoes_do_grupo`, `verify_t8_consolidacao.py` | The grouping rule Phase E must follow; note the partition itself was **not** reassigned (the 11 leaks are marked, not fixed) |
| Instrumentation | `measure_mip(..., coletar_incumbente=True)`, `schema-instrumentacao-mip.md` | The metric schema the pilot persists |
| Paired-comparison protocol | `protocolo-comparacao-pareada.md`, cited from `CLAUDE.md` | The checklist T19 and T21 must satisfy; it explicitly allows a pilot to explore configuration without closing a method verdict |

### Block 2 gaps that constrain Block 3

1. **No runner uses `WorkLimit` yet.** The decision was made but not wired into `harness.py`,
   `bc_yspace.py` or any `run_e*.py`. T19 is the first experiment that must comply, so the
   migration cost lands here.
2. **The development/evaluation partition was not reassigned.** T8 marked the 11 leaking origin
   graphs and the duplicates but left the partition as is. Block 3 therefore cannot inherit a
   clean partition from the real benchmark; the structural families define their own split
   (see T21).
3. **`build_manifest.py` scans only two directories** (`instances/*.txt` with a `LEGADO` entry,
   and `instances/benchmark-v1/**`). Structural instances need a third scan branch and a
   `classe` value that does not exist yet.

---

## Current State

Classified as proven, already implemented, partially implemented, hypothesis, contradicted,
obsolete, or still to verify. Each line states how it was checked.

### Already implemented (verified in this session)

- **Block 1 and Block 2 deliverables listed above.** Block 1 is committed (`dc83ac9`, `658099a`,
  `e0c36e7`, `97b290d`); Block 2 is in the working tree, not yet committed (`git status` shows
  modified `cuts.py`, `harness.py`, `bc_yspace.py`, `yspace.py`, `manifest.csv`,
  `build_manifest.py`, plus new `verify_t6/t7/t9`, `verify_t8_consolidacao.py`,
  `grupos_origem.csv`, and three new reference documents).
- **Existing synthetic gadgets:** `experiments/cuts/synthetic.py` defines `make_F1`, `make_F2`,
  `make_Tri`, `make_Sec59`, `make_Direct0`, `make_TermRelay`, `make_StayPut`,
  `make_SharedTerminal`, `make_StayPutIsolado`, `make_CaminhoABC`, `make_TermRelayForced`. The
  last two are new, added by Block 1 (T3). All are fixed-size correctness or cut-validation
  gadgets; `F1`, `F2` and `Sec59` take size parameters but were built to exercise specific cut
  families, not to serve as a benchmark.
- **A2 closure is recorded** in `direcoes-pli-min-station.md` §13 (entry "Resultado [E12] — A2
  encerrada para Das") and in `plano-pos-e8-adiado.md` ("Situação após E12"). Verified by `grep`.
  No code or document treats the CBI as an open general method for Das.

### Not implemented at all (verified by exhaustive search)

- **No BP generator.** `grep -rln "make_BP\|bin_packing"` over all `*.py` returns nothing.
- **No HB generator.** Same search for `make_HB`; nothing.
- **No SC generator.** Same search for `make_SC`, `SC_GF2`, `gf2`; nothing.
- **No TR generator.** Same search for `make_TR`, `corredor`, `interleaved`; nothing.
- **No C6 implementation.** `grep -rn "C6\|generate_C6\|mochila\|knapsack"` over `experiments/`
  returns nothing. C6 exists only as text in `direcoes-pli-min-station.md`.
- **No validator for inequalities with RHS `δ ≥ 2`.** `is_valid_cut(S, T, A_r, Z, ...)` takes a
  **set** `Z` and decides validity of `y(Z) ≥ 1` only — there is no coefficient vector and no
  right-hand side argument. `assert_valid_cuts` iterates sets. Confirmed by reading both
  signatures. The assessment's warning is accurate and still applies.
- **No disaggregated all-V formulation.** `experiments/alternative-formulations/` holds
  `modelo_estendido.py` (now `construir_modelo_estendido_vi`: `y` only on `VI`, destination
  without outflow — renamed by T11, explicitly *not* equivalent to the baseline) and
  `modelo_min_station_fluxo.py` (an older copy of the aggregate baseline: a single `f[u,v]` per
  arc, no robot index). Neither is a per-commodity disaggregation.
- **No `estrutural` class in the manifest.** Current `classe` values are exactly
  `principal` (75), `extensao_dirigida` (11), `extensao_ponderada` (3), `historico` (3).
- **The Appendix B scripts were never committed.** The assessment states they stayed in the
  session scratchpad, and no equivalent exists in the repository. The 13 verified mini-cases are
  therefore **results without reproducible code** — they must be re-derived by the generators.

### Proven (mathematics available and marked as proven in a versioned document)

- **Knapsack version of first-hop Hall**, `direcoes-pli-min-station.md` §5.4 item 2, marked
  `[Provado]`: `Σ_{v∈N⁺(S')} min(δ, |N⁻(v)∩S'|) y_v ≥ δ` for `S' ⊆ S∖T` with deficiency
  `δ = |S'| − |N⁺(S')∩T|`. Coefficient rounding is valid for 0/1 covering.
- **C4-DM a priori construction** (Dulmage–Mendelsohn), §5.4 item 4, marked `[Provado]`.
- **Integer separation of the `𝒵` family** (Theorem 6) and the disjoint-cut packing bound,
  §5.5, marked `[Provado]`.
- **SC-GF2 `OPT = k`** and **`LP + C1 = n/2^(k−1)`**, assessment §11.3, marked `[Demonstrado]`
  with a complete argument (a family `{F_a}` covers `U` iff the `a` span `GF(2)^k`; the uniform
  solution `y = 2^−(k−1)` is feasible).
- **BP lower bound `LB = 2n + q`**, assessment §11.3, marked `[Demonstrado]` (C1 forces `y_{u_i}`
  and `y_{v_j}`; the distance-2 band of C2 forces `Σ_j y_{c_{i,j}} ≥ 1` per item).
- **BP `OPT = 2n + q` iff an exact partition exists**, attributed to the IJCAI 2026 paper, p.76.
- **TR `OPT = ⌈D/r⌉ − 1`** and the count of `k^R` core optima with only `k` feasible (σ = ∞),
  assessment §11.3, marked `[Demonstrado]`.
- **C6 first-hop does not close the HB gap**, assessment §11.3, marked
  `[Demonstrado pela fórmula de §5.4]`: with `S' = A`, the shared direct destination `c` receives
  coefficient `min(δ, |N⁻(c)∩S'|) = δ`, so `y_c = 1` alone satisfies the inequality.

### Computationally verified only (small cases, no proof, and **no committed code**)

The 13 cases of assessment Appendix B: SC-GF2 (k = 3, 4), BP (4 cases: two "yes", two "no"),
TR (k = 2, 3 with L = 5), HB (5 configurations). They report OPT, `z_LP`, LP with C1+C2+C4, the
core value, and the count of core optima with how many are feasible. Reproducing them is part of
T12, T13, T15 and T17 — they are not evidence that any generator exists.

### Hypothesis (used by the assessment, not yet proven)

- **BP:** `OPT = 2n + q + σ*` where `σ*` is the minimum number of items split across bins; and
  `OPT ≤ 2n + 2q − 1` via next-fit with splitting.
- **HB:** `OPT ≥ min(⌈δ/p⌉, 3)` (the two upper bounds are proven by explicit solutions; the lower
  bound is not), and additivity across pockets.
- **HB side finding:** that the cap of 3 per pocket is general in undirected graphs with shared
  direct destinations. The assessment explicitly says there is not enough evidence to conclude it.
- **TR:** that the feasible fraction of core optima grows with steps (`σ ≤ r`); and that CBI
  iterations grow with the number of core optima.
- **BP/CBI:** that CBI iteration count grows with the number of core optima.

### Contradicted or resolved by results produced after the assessment

- **The assessment §11.7 conditionals were never resolved.** The text still reads "TR. Depende do
  CBI corrigido e de a linha A2 seguir viva" and "E12: se A2 for encerrada para Das, TR cai para
  opcional e SC fica só como controle do núcleo". The actual outcomes are known: E12 closed A2
  (H16) and E14 was 0/4 inconclusive (H15). Applying the assessment's own rules to the branches
  that occurred yields: **order BP → HB → SC → TR**, with **SC demoted to a core control** and
  **TR demoted to optional/low priority**; E14's inconclusive result "reinforces the need for a
  known OPT", which raises BP. This is the assessment's rule applied, not a new decision.
- **The pilot budget changed.** Assessment §11.4 prescribes "TL 600 s, ou `WorkLimit` equivalente
  se adotado". `WorkLimit` **was** adopted for method comparison (T7). The pilot must therefore be
  budgeted in work units, not seconds.
- **The §11.4 instrumentation prerequisite is satisfied.** The assessment says "`harness.measure_mip`
  atual não registra NodeCount nem os tempos de incumbente". `node_count` was already returned, and
  T9 added `coletar_incumbente`. The prerequisite is met.

### Still to verify (deferred to the task that needs it)

- Whether the assessment's HB parameterization `HB(q, ndir, p; k, L)` is internally consistent for
  all parameter combinations in the pilot (the Appendix B cases cover `ndir ∈ {1,2}`, `p ∈ {1,2}`,
  single pockets only — the pilot asks for `k ∈ {1,4,8}` pockets, whose additivity is a hypothesis).
- Whether the BP "no" instances of the pilot (`q = 8`, `n = 24`, `B = 60`, so `m = 480`) are
  tractable at all for the base model; Appendix B only reached `q = 2`, `m ≤ 6`.
- Whether SC-GF2 at `k = 7` (|V| = 381, `n² = 16129` W–T edges) builds in acceptable time.
- Whether a rigid twin for SC can preserve degrees while actually lowering symmetry, measured by
  `classes_wl` (the manifest already computes this column for real instances).

---

## Problem Statement

The project knows its instances are hard (31 of 70 benchmark-v1 instances are classed D/A) but not
**why**: without a known OPT, the UB−LB interval cannot be split between a weak bound and a bad
incumbent. E13 reached a primal-gap verdict at the threshold (7/13) without attributing the 10.5%–
44.4% residual, and E14 failed to certify OPT on all four instances with an absolute gap of 2 even
with four hours and a cutoff. Meanwhile the strongest method-level result of the campaign (E12,
A2 closed) was only interpretable because the design separated the integer core from the iteration
— an attribution the real benchmark cannot generally support. Block 3 builds four synthetic
families whose optimum is known or independently certified and whose difficulty comes from one
identified mechanism each, so that a measurement can be attributed to a cause instead of to the
instance. Nothing of this exists in code today: there is no BP, HB, SC or TR generator, no C6
implementation, no validator for inequalities with RHS `δ ≥ 2`, no disaggregated all-V formulation,
and no `estrutural` class in the manifest. The assessment's mini-case verifications were never
committed, so even the 13 numbers in its Appendix B are currently results without reproducible code.

## Research Questions / Hypotheses

Each family exists to answer one question. A family that cannot discriminate its question is
discarded, however slow it may be.

| Family | Research question | Mechanism isolated | Falsified if |
|---|---|---|---|
| **BP** | When the covering bound is exact by construction, does difficulty sit in finding the solution (UB) or in proving the bound (LB)? | Collective assignment: a numeric partition the core cannot see | Both twins solve in under the pilot budget at the largest size, or both are hard on the same side |
| **HB** | In a pocket with Hall deficiency `δ ≥ 2`, is the gap a first-hop multiplicity gap that the knapsack inequality would close, or does it need a second layer? | Collective Hall deficiency with shared destinations | C6 closes the gap, which would mean the §5.4 coefficient analysis is wrong |
| **SC** | When covering represents the problem exactly, does proof difficulty come from the relaxation gap or from symmetry? | Logarithmic integrality gap plus a large automorphism group | Gurobi proves `k = 7` quickly by closing the root with its own cuts or symmetry detection |
| **TR** | Do many core optima that are infeasible in the full problem degrade core-based methods while the compact model stays simple? | Recharge layers: band choices that are individually valid but mutually incompatible | `𝒵` cuts eliminate whole classes and iterations grow only linearly — a positive finding about `𝒵`, and the end of TR as a stressor |
| **all-V (T18)** | How much LP strength does per-commodity disaggregation buy, at what model-size cost? | Aggregation loss in the flow relaxation | — (diagnostic, not a family) |

The families are instruments. They do not replace the real benchmark, and a mechanism shown to
produce difficulty synthetically is not evidence that it explains difficulty in MAPF, Vienna or PUC
— that bridge is a separate comparison in Phase E.

## Goals

- [x] Four generators (BP, HB, SC, TR) exist, are deterministic, emit `sha256`, and record full
      provenance, with every instance faithful to Das's problem.
- [x] Every property used to interpret a pilot result is PROVEN or independently certified before
      the pilot runs; no family enters the pilot resting on a HYPOTHESIS that its verdict depends on.
- [x] C6 has a written derivation, documented validity conditions, and a validator that handles
      RHS `δ ≥ 2`, before any performance measurement of C6.
- [x] Small cases of every family are cross-checked against the base model and the Block 1
      independent validator, with no circular validation.
- [x] The pilot (Phase P) is pre-registered — parameters, seeds, methods, budget, metrics and
      success criteria frozen before the first run — and executed under the Block 2 protocol.
- [x] Every family receives exactly one decision: `PROMOTE`, `DISCARD`, or
      `REVISE THEORY/GENERATOR`, by criteria fixed before the results were seen.
- [x] Phase E runs only on promoted families, with new generation seeds never used in development.
- [x] A2 is not reopened as a general method for Das; T16 and T17 exist only if a new structural
      hypothesis makes the core/iteration separation scientifically useful again.

## Out of Scope

| Item | Reason |
|---|---|
| T22 — positioning against the IJCAI 2026 paper, bibliography, contribution table | Block 4 |
| Rewriting the article | Block 4 |
| Correctness of the oracle, independent validator, terminal regressions, equivalence proof | Block 1, complete |
| Determinism, budget decision, benchmark consolidation, instrumentation, paired protocol, documentation fixes | Block 2, complete |
| A new CBI campaign on PUC/PUCN | E12 closed A2 for Das; T16 is not a repetition of E12 |
| Reopening Lagrangian relaxation, classic Benders, generic BC-Y, C5, generic symmetry breaking, column generation | Paused lines; reopening requires specific new evidence |
| Expanding the real benchmark (new MAPF/Vienna/PUC instances) | "Adding instances without a hypothesis" is a paused line |
| Promoting the all-V disaggregation to a production method | T18 is diagnostic only; expansion requires separate evidence |
| Using directed or weighted extensions as evidence about Das | Allowed only in an experiment explicitly labelled as an extension |
| Growing `n` until the solver is slow | Difficulty of scale is not the mechanism under study |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Meaning of "C6" in T14 | The **knapsack version of first-hop Hall from §5.4 item 2** (`Σ min(δ,·) y_v ≥ δ`), which is marked `[Provado]` — **not** the §5.6 family also called C6, which is marked `[Esboço]` | `plano-pos-e8-adiado.md` states "E11 redefinido: C4 na versão mochila (provada em §5.4) com δ ≥ 2; o C6 do §5.6 é só esboço e não entra", and the assessment's HB analysis uses the §5.4 coefficient formula. The name collision is recorded as an inconsistency | n |
| Where structural instances live | A new directory `instances/estrutural/<familia>/`, with `classe = estrutural` in the manifest and a third scan branch in `build_manifest.py` | Keeps them out of `classe = principal`, which `CLAUDE.md` defines as the Das recipe; the manifest's `classe` column is a free string, so no schema change is needed | n |
| Pilot budget unit | `WorkLimit`, calibrated so that the budget matches roughly 600 s of single-thread work on the pilot machine, with the calibration procedure recorded | T7 decided `WorkLimit` for method comparison; the assessment's "600 s" predates that decision. The calibration must be written down because work units are hardware-dependent | n |
| Pilot size if TR is not implemented | Run the pre-registered 33-cell matrix minus TR's 6 cells = 27, and record the reduction and its reason **before** any run | The assessment's matrix is pre-registered and must not change silently; dropping TR is driven by A2's closure (a result that predates the pilot), not by pilot outcomes | n |
| Granularity of this spec | Each task carries objective, evidence, files, acceptance criteria, tests, risks and dependencies inside `spec.md`; no separate `design.md`/`tasks.md` | Same pattern as Blocks 1 and 2, and the user asked for the spec only | n |
| Independent certificate for BP "no" instances | A dedicated exact bin-packing decision procedure (DP over subset sums, or a standalone IP) written for this purpose, never the MIN-STATION model | The assessment demands non-circular certification; using MIN-STATION to decide the bin-packing question it was built from would be circular | n |
| Independent certificate for the SC rigid twin | A standalone set-cover IP over the same set system | Same non-circularity rule; SC-GF2 itself has a proven `OPT = k` and needs no solver certificate | n |

**Open questions:** none — all resolved or recorded above.

---

## Mathematical Preconditions for Structural Families

Gate rule: **a family does not enter the pilot while a property its verdict depends on is still
HYPOTHESIS or TO BE CHECKED.** Properties that are merely descriptive may remain hypotheses.

| # | Family | Property | Status | Verdict depends on it? | What closes it |
|---|---|---|---|---|---|
| 1 | BP | `LB = 2n + q` (core and LP+C1+C2 equal this) | PROVEN (assessment §11.3) | Yes | — |
| 2 | BP | `OPT = 2n + q` ⟺ exact partition exists | PROVEN (IJCAI 2026 p.76; to be re-derived in repo) | Yes | Re-derivation written in the repo (T12) |
| 3 | BP | `OPT = 2n + q + σ*` (σ* = minimum splits) | HYPOTHESIS | No — the twins only need "yes ⇒ `2n+q`" and "no ⇒ `> 2n+q`" | Optional proof |
| 4 | BP | `OPT ≤ 2n + 2q − 1` | HYPOTHESIS | No | Optional proof |
| 5 | BP | Appendix B values (4 cases) | COMPUTATIONALLY VERIFIED, **code not in repo** | Yes, as a generator regression | Regenerate in code (T12) |
| 6 | HB | `OPT = min(⌈δ/p⌉, 3)` upper bounds (two explicit solutions) | PROVEN | Yes | — |
| 7 | HB | `OPT ≥ min(⌈δ/p⌉, 3)` lower bound | HYPOTHESIS | **Yes** — the gap claim "core = 1 vs OPT = 3" needs it | Written proof, or enumeration certificate per pilot instance (T13) |
| 8 | HB | Additivity across `k` pockets | HYPOTHESIS | **Yes** — the pilot uses `k ∈ {1,4,8}` | Proof, or per-instance certificate for the `k` used (T13) |
| 9 | HB | C6 first-hop does not close the gap (coefficient `= δ` on the shared destination) | PROVEN by the §5.4 formula | Yes | — |
| 10 | HB | The cap of 3 per pocket is general in undirected graphs | HYPOTHESIS, explicitly flagged as insufficient evidence | No — it is a side finding, not a pilot verdict | Out of scope here |
| 11 | SC | `OPT = k` for SC-GF2 | PROVEN | Yes | — |
| 12 | SC | `LP + C1 = n/2^(k−1)` | PROVEN | Yes | — |
| 13 | SC | Automorphism group contains `GL(k,2)`, transitive on `W` | PROVEN | Yes (symmetry arm) | — |
| 14 | SC | The rigid twin has materially lower symmetry at equal size/degrees | TO BE CHECKED | **Yes** — the whole point of the twin | `classes_wl` measurement on generated twins (T15) |
| 15 | SC | Twin `OPT` | TO BE CHECKED per instance | Yes | Independent set-cover IP (T15) |
| 16 | TR | `OPT = ⌈D/r⌉ − 1` | PROVEN | Yes | — |
| 17 | TR | `k^R` core optima, `k` feasible (σ = ∞) | PROVEN | Yes | — |
| 18 | TR | Feasible fraction grows with steps (σ ≤ r) | HYPOTHESIS | Yes for the steps arm | Exact count on small cases (T17) |
| 19 | TR | CBI iterations grow with the number of core optima | HYPOTHESIS — **this is the question, not a precondition** | No | Measured, not assumed |
| 20 | C6 | Validity of `Σ min(δ, |N⁻(v)∩S'|) y_v ≥ δ` | PROVEN (§5.4 item 2) | Yes | Re-derivation plus δ ≥ 2 validator (T14) |
| 21 | C6 | Separation beyond DM enumeration | SKETCH (§5.4 item 5 marks exactness open) | No — the pilot adds C6 statically | Out of scope here |

Properties 7, 8, 14, 15 and 18 are the gate items: HB cannot enter the pilot on 7 and 8 alone, and
SC's symmetry arm cannot be interpreted without 14.

---

## User Stories

### P1: T12 — Implement and validate the BP structural family ⭐ MVP

**User Story**: As a researcher who cannot tell whether a residual gap is primal or dual, I want a
family whose covering bound is exact by construction and whose optimum is known from a planted or
independently certified bin-packing answer, so that a measurement can be attributed to the UB side
or the LB side with the OPT in hand.

**Why P1**: It is the only family that directly attacks the question E13 and E14 left open, it
depends on neither C6 nor the CBI, and the assessment ranks it first — a ranking that E14's
inconclusive outcome reinforces by its own rule.

**Objective.** A deterministic generator producing comparable "yes"/"no" twins from a bin-packing
instance, with the partition answer certified outside MIN-STATION.

**Current problem.** No generator exists. The four Appendix B cases (`q = 2`, `m ≤ 6`) were
computed in a scratchpad that was never committed, so even they are not reproducible today.

**Expected behaviour.** `BP(items, q, B, seed)` builds: for each bin `j`, a vertex `v_j` with `B`
destination leaves; for each item `i`, a vertex `u_i` with `e_i` origin leaves and `q` connectors
`c_{i,j}` joined `u_i–c_{i,j}` and `c_{i,j}–v_j`; `r = 1`; `m = Σe_i = qB`. The graph is simple,
undirected, connected, unit-weight, `|S| = |T|`, `S∩T = ∅`, stations allowed on all of `V`.

**Files affected:** new `experiments/structural/bp.py` (or an equivalent module path chosen at
implementation time); a new independent bin-packing decision procedure (DP or standalone IP) in the
same package; `src/converters/build_manifest.py` (third scan branch and the `estrutural` class);
`instances/estrutural/bp/` for the emitted instances.

**Changes required.** Generator, certificate procedure, provenance emission, and a verification
script that reproduces the Appendix B cases from code.

**Acceptance criteria:**

1. WHEN the generator is called twice with the same `items`, `q`, `B` and seed, THEN the system SHALL
   emit byte-identical instance files and the same `sha256`.
2. The system SHALL record, per generated instance, family name, generator version, parameters,
   seed, `sha256`, `N`, `M`, `r`, `|S|`, `|T|`, `|S∩T|`, the known certificate, the certificate's
   origin, and the commit.
3. WHEN a "yes" instance is generated, THEN the system SHALL carry a constructive packing
   certificate produced by the planting procedure, independent of any MIN-STATION model.
4. WHEN a "no" instance is generated, THEN the system SHALL carry a proof of non-existence of the
   exact partition produced by a dedicated bin-packing decision procedure, and SHALL NOT use the
   MIN-STATION model as that certificate.
5. WHILE an instance is small enough for enumeration, the system SHALL confirm `OPT` by
   `independent_validator.opt_por_enumeracao` and by the base model, and the two SHALL agree.
6. The system SHALL reproduce, from committed code, the four BP rows of assessment Appendix B
   (core `= 2n+q` in all four; `OPT = 2n+q` on "yes"; `OPT = 2n+q+1` on "no"; zero feasible core
   optima on "no").

**Tests required:** `experiments/structural/verify_t12_bp.py` — determinism (same seed twice),
Appendix B reproduction, OPT agreement between enumeration and base model on the smallest cells,
connectivity via `avisar_se_desconexo`, and a fidelity check (`S∩T = ∅`, unit weights, `|S| = |T|`).

**Evidence to produce:** a versioned document with the construction, the re-derivation of
`LB = 2n+q` and of the `OPT = 2n+q` ⟺ partition equivalence, the generated instance table with
hashes, and the verification output.

**Risks:** the pilot's largest cell (`q = 8`, `n = 24`, `B = 60`) gives `m = 480` robots and a
large unary flow model; it may be intractable for the base model, which would make "OPT known"
useless there. Measure the smallest cell first and record the scaling before committing to `B = 60`.

**Dependencies:** Block 1 independent validator (enumeration); Block 2 determinism (before any
performance comparison). Recommended first among the families.

**Stop criteria:** if the `OPT = 2n+q` ⟺ partition equivalence cannot be re-derived in the repo,
stop and fix the theory before generating at scale.

**Out of scope:** tuning the bin-packing instances for solver difficulty; weighted variants.

**Independent Test**: generate one "yes" and one "no" twin at the smallest size and confirm the
enumerated OPT differs by exactly 1 while the core value is identical.

---

### P1: T13 — Implement and validate the HB structural family

**User Story**: As a researcher deciding whether to invest in C6, I want a family of Hall pockets
with controllable deficiency `δ` and relay multiplicity `p`, so that the predicted failure of the
first-hop knapsack inequality can be tested in a controlled setting before the inequality is built.

**Why P1**: It must come **before** T14. The assessment predicts, from the §5.4 coefficient
formula, that C6 will not close this gap; building C6 first and then looking for where it works
would invert the scientific order.

**Objective.** A generator `HB(q, ndir, p; k, L)` whose pockets have known core value and known
OPT, with C1 and C2 empty by construction in the predicted configurations.

**Current problem.** No generator exists. Five Appendix B configurations were computed in the
uncommitted scratchpad, all with a single pocket.

**Expected behaviour.** Origins `A` complete to shared direct destinations `C`; relays `X` each
adjacent to a disjoint block of `p` origins; `δ` distant destinations `D` adjacent to all relays
and to a balancer origin with its own destination; `r = 1`; `k` pockets linked by paths of `L ≥ 2`
non-terminal vertices, as in `make_F2`.

**Files affected:** new `experiments/structural/hb.py`; manifest wiring as in T12;
`instances/estrutural/hb/`.

**Changes required.** Generator plus the proof work for preconditions 7 and 8 of the Mathematical
Preconditions table, or per-instance enumeration certificates covering the pilot's `k` values.

**Acceptance criteria:**

1. The system SHALL generate instances in which `generate_C1` and `generate_C2` return no cuts in
   the configurations where the assessment predicts they are empty, and SHALL fail the verification
   if either returns a cut there.
2. WHEN a single-pocket instance is generated with the Appendix B parameters, THEN the system SHALL
   reproduce the recorded `OPT`, `z_LP`, LP with C1+C2+C4, and core value.
3. IF the lower bound `OPT ≥ min(⌈δ/p⌉, 3)` has neither a written proof nor a per-instance enumeration certificate, THEN the system SHALL
   block the family from entering the pilot.
4. IF additivity across `k` pockets has neither a written proof nor a certificate for the `k` values used, THEN the system SHALL
   block the multi-pocket cells from entering the pilot.
5. WHILE an instance is small enough for enumeration, the system SHALL confirm `OPT` with
   `independent_validator` and with the base model.
6. The system SHALL be deterministic and emit the same provenance fields required of BP.

**Tests required:** `experiments/structural/verify_t13_hb.py` — Appendix B reproduction for all
five configurations, the C1/C2 emptiness assertion, enumeration agreement, determinism, fidelity.

**Evidence to produce:** a document with the construction, the proof or certificates for
preconditions 7 and 8, the predicted-versus-measured table, and the explicit prediction for C6
(`LB ≈ 1` per pocket against `OPT = 3`) registered **before** T14 measures anything.

**Risks:** the assessment warns that this construction may admit unforeseen detours — the same risk
that defeated an earlier attempt recorded at `direcoes-pli-min-station.md` D:517-520. Enumeration
on small pockets is the guard; a detour that lowers OPT invalidates the gap claim.

**Dependencies:** T12 in the recommended order (not a hard dependency); Block 1 validator.
**Blocks:** T14, which uses HB as its control.

**Stop criteria:** if enumeration shows `OPT < min(⌈δ/p⌉, 3)` on a pocket, the theory is wrong —
fix it before the pilot, and do not reinterpret it as a computational phenomenon.

**Out of scope:** making HB hard in runtime; it is a bound instrument and is expected to be fast.

**Independent Test**: generate the `q = 6, ndir = 1, δ = 5, p = 1` pocket and confirm enumerated
`OPT = 3` with core `= 1`.

---

### P1: T14 — Derive, validate and implement E11/C6

**User Story**: As a researcher who was told C6 might close a multiplicity gap, I want the
inequality derived, its validity conditions documented, and a validator that handles RHS `δ ≥ 2`
built and passing on enumerated small cases, before any performance number is produced.

**Why P1**: It is a mathematical line in its own right, decoupled from the E14 trigger. E14's 0/4
outcome closed the old trigger but is not a licence to measure C6 either.

**Objective.** A correct, validated implementation of the knapsack first-hop Hall inequality, with
its predicted behaviour on HB confirmed or refuted.

**Current problem.** No implementation (`grep` for `C6`/`mochila`/`knapsack` over `experiments/`
returns nothing) and no validator for weighted inequalities: `is_valid_cut` takes a set `Z` and
tests `y(Z) ≥ 1` only, with no coefficients and no right-hand side.

**Expected behaviour.** Mandatory order: (1) derivation written in the repo; (2) validity
conditions documented; (3) a validator for `Σ a_v y_v ≥ δ`; (4) enumeration of small cases;
(5) implementation; (6) regressions; (7) only then measurement.

**Files affected:** `experiments/cuts/cuts.py` (new generator alongside `generate_C4_DM`, plus a
weighted-cut validator next to `is_valid_cut`); `experiments/cuts/harness.py` (`prepare_cuts`
must accept a weighted family without breaking `cortes_ordenados`, which today assumes sets);
`direcoes-pli-min-station.md` §5.4 (promote the derivation from an item to a numbered statement).

**Changes required.** The cut representation must grow from "frozenset `Z` meaning `y(Z) ≥ 1`" to a
form carrying coefficients and a right-hand side. This touches the ordering helper and the
validation path, which are Block 2 infrastructure — extend them, do not fork them.

**Acceptance criteria:**

1. The system SHALL contain a written derivation of `Σ_{v∈N⁺(S')} min(δ, |N⁻(v)∩S'|) y_v ≥ δ` with
   its validity conditions, versioned in `docs`, before any implementation is measured.
2. The system SHALL provide a validator that decides validity of a weighted inequality with RHS
   `δ ≥ 2`, and SHALL NOT rely on `is_valid_cut`, which only covers RHS 1 with unit coefficients.
3. WHEN the weighted validator is run on enumerated small instances, THEN it SHALL agree with the
   base model on whether the inequality cuts off any feasible solution.
4. IF the validator finds any feasible solution violating a generated C6 inequality, THEN the system SHALL
   treat the inequality as invalid and halt before measurement.
5. WHEN C6 is applied to the HB family, THEN the system SHALL compare the measured LB against the
   prediction registered in T13 (`≈ 1` per pocket against `OPT = 3`) and SHALL record agreement or
   disagreement explicitly.
6. IF C6 closes the HB gap, THEN the system SHALL treat the §5.4 coefficient analysis as refuted
   and SHALL redo it before drawing any conclusion about E11.
7. The system SHALL NOT run any performance benchmark of C6 before criteria 1 to 4 are satisfied.

**Tests required:** a weighted-cut validation regression over the enumerated small cases of HB and
of at least one family where C6 should be vacuous (BP or SC as a negative control), plus a
regression that the existing unit-coefficient path is unchanged.

**Evidence to produce:** derivation, validity conditions, considered counterexamples, the validator,
the regression output, and only afterwards any experimental result.

**Risks:** extending the cut representation touches `cortes_ordenados` and `add_cuts_to_model`,
both of which currently assume sets. A careless change here silently breaks Block 2's determinism
guarantee; the T6 verification script must be re-run after the change.

**Dependencies:** T13 (HB as control). Explicitly **not** dependent on the E14 trigger.

**Stop criteria:** if the derivation cannot be completed, C6 does not get implemented, and the
finding is recorded — a negative result that closes the line.

**Out of scope:** exact separation of C6 (open complexity, §5.4 item 5); the §5.6 sketch family.

**Independent Test**: on an HB pocket with `δ = 5, p = 1`, confirm that adding C6 leaves the LB at
roughly 1 per pocket, matching the registered prediction.

---

### P2: T15 — Implement and validate the SC structural family

**User Story**: As a researcher who cannot separate "the relaxation is weak" from "the model is
symmetric", I want a set-cover family with a proven optimum and a proven gap plus a rigid twin of
the same size and degrees without the symmetry group, so that the two causes can be told apart.

**Why P2**: After E12 closed A2, the assessment's own rule demotes SC from "positive control of the
core and the CBI" to a **core control only** — still useful, no longer a CBI instrument.

**Objective.** Generators for SC-GF2(k) and for a rigid twin of equal size and degree profile,
with symmetry measured rather than assumed.

**Current problem.** No generator; only two Appendix B rows (k = 3, 4) from uncommitted code.

**Expected behaviour.** `U = GF(2)^k∖{0}`, `n = 2^k−1`; sets `F_a = {x : a·x = 1}`; vertices `w_a`,
`s_x`, `t_x`; edges `s_x–w_a` iff `a·x = 1`, and `w_a–t_x` complete; `r = 1`, `m = n`, `|V| = 3n`.

**Files affected:** new `experiments/structural/sc.py`; a standalone set-cover IP for twin
certification; manifest wiring; `instances/estrutural/sc/`.

**Acceptance criteria:**

1. WHEN SC-GF2(k) is generated, THEN the system SHALL verify automatically that `OPT = k` and that
   `LP + C1 = n/2^(k−1)`, and SHALL fail generation if either disagrees.
2. The system SHALL generate a rigid twin preserving `n`, set size and element degree, and SHALL
   record its symmetry with `classes_wl` or an equivalent measure.
3. IF the rigid twin's measured symmetry is not materially lower than SC-GF2's at the same `k`, THEN the system SHALL
   report the twin as failed and SHALL NOT use it to separate symmetry from gap.
4. The system SHALL certify the twin's `OPT` with a standalone set-cover IP, and SHALL NOT use the
   MIN-STATION model as that certificate.
5. WHILE an instance is small enough, the system SHALL confirm `OPT` by enumeration with the Block 1
   validator and by the base model.
6. The system SHALL be deterministic and emit the provenance fields required of BP.

**Tests required:** `verify_t15_sc.py` — formula checks at `k ∈ {3,4}` against Appendix B, twin
symmetry measurement, twin OPT agreement with the independent IP, determinism, fidelity.

**Evidence to produce:** construction, the two proofs restated, the generated table with `classes_wl`
for both arms, and the twin certification.

**Risks:** `W–T` is complete, so `|A_r|` grows as `n²`; at `k = 7` (`n = 127`) the reach digraph is
already large, and at `k = 8` likely impractical. Measure build time at `k = 5` before committing
to `k = 7`.

**Dependencies:** Block 1 validator; Block 2 determinism before comparison.

**Stop criteria:** if Gurobi proves `k = 7` within the pilot budget with the root closed by its own
cuts, SC is too easy and is kept only as a sanity family.

**Out of scope:** using SC as a CBI control in the sense the assessment originally intended.

**Independent Test**: generate SC-GF2(4) and confirm `OPT = 4` and `LP+C1 = 15/8 = 1.875`.

---

### P3: T16 — Discriminant test of the core and the CBI (conditional)

**User Story**: As a researcher who must not credit the CBI for a gain that came entirely from the
integer core, I want the core, the oracle and the iteration measured separately — but only if a new
structural family raises a question that E12 did not already answer.

**Why P3**: **A2 is closed for Das (E12).** This task is not a repetition of that experiment and
does not reopen it. It exists only as a conditional instrument for new families.

**Objective.** Decide, explicitly, whether a scientifically new question about the core/iteration
split exists after the families are built; if yes, run the separation; if no, close the task.

**Current problem.** None in code — E12 already implemented the three-arm design
(`run_e12.py`, `tabela_e12.py`) and its verdict is recorded in `direcoes-pli-min-station.md` §13 and
`plano-pos-e8-adiado.md`. Nothing in the repository treats T16 as a rerun of E12.

**Expected behaviour.** A written applicability decision, then — only if applicable — COMP, the
isolated integer core, and the full CBI under equal total budget.

**Acceptance criteria:**

1. The system SHALL record an explicit applicability decision citing the specific new hypothesis a
   family raises about the iteration, before any run.
2. IF no new hypothesis about the CBI iteration exists after the families are built, THEN the system SHALL
   mark T16 `NOT APPLICABLE / CLOSED` and SHALL NOT run a battery merely because the task is in the
   backlog.
3. WHILE T16 runs, the system SHALL budget the CBI by total cost — master plus oracle plus any
   external primal construction — and SHALL NOT compare master solver time against COMP total time.
4. The system SHALL record LB, UB, gap, root bound, `NodeCount`, time to first incumbent, time to
   best incumbent, time to proof, CBI iterations, cuts per iteration, accumulated cuts, master time
   and oracle time.
5. The system SHALL attribute any observed gain to the specific component responsible, and SHALL
   NOT report "the CBI won" when the isolated core produced the same bound.

**Tests required:** none beyond the pilot harness; the verification is that the applicability
decision is written before any execution.

**Evidence to produce:** the applicability decision, and — only if applicable — the three-arm
comparison under the paired protocol.

**Risks:** the main risk is social, not technical: running the battery because it is on the list.
Criterion 2 exists to prevent that.

**Dependencies:** Block 1 (T1), Block 2 (T9, T10). Conditional on the families' outcomes.

**Stop criteria:** closing the task is a valid and expected outcome.

**Out of scope:** any re-run on PUC/PUCN; any reopening of A2.

**Independent Test**: the decision document names the family, the hypothesis and the arms, or
states that none exists.

---

### P3: T17 — Implement and validate the TR structural family (conditional)

**User Story**: As a researcher asking whether many infeasible core optima degrade core-based
methods, I want interleaved corridors with a proven optimum and a known count of core optima, so
that iteration growth can be measured against a known combinatorial quantity.

**Why P3**: The assessment's own conditional resolves against TR: A2 was closed, so TR loses the
method it was built to discriminate. It survives as an optional stress test of the isolated core.

**Objective.** A generator `TR(k, L, r, σ)` with proven OPT and counted core optima, used only if
T16 finds a live question.

**Current problem.** No generator; two Appendix B rows from uncommitted code.

**Expected behaviour.** `m` origins adjacent to corridor entrances `e_j`; corridor `j` is the path
`e_j – c_{j,1} … c_{j,L} – x_j`; `x_j` adjacent to all destinations; steps `c_{j,ℓ}–c_{j+1,ℓ}`
every `σ` positions; distance `D = L+3`.

**Files affected:** new `experiments/structural/tr.py`; manifest wiring; `instances/estrutural/tr/`.

**Acceptance criteria:**

1. WHEN an instance is generated, THEN the system SHALL verify `OPT = ⌈D/r⌉ − 1` against the base
   model on the small cells.
2. WHILE a case is small enough, the system SHALL count the core optima exactly and SHALL measure
   how many of them are feasible in the full problem, reproducing the Appendix B values (8 optima
   with 2 feasible at `k = 2`; 27 with 3 at `k = 3`).
3. The system SHALL generate both step variants (`σ = ∞` and `σ ≤ r`) from the same parameters.
4. IF T16 concludes that no live question about the CBI iteration exists, THEN the system SHALL
   stop TR at validation and SHALL NOT advance it to the benchmark.
5. IF CBI iterations grow only linearly in `R`, THEN the system SHALL record that as a positive
   finding about the `𝒵` family and SHALL discard TR as a stressor, without enlarging sizes to
   force difficulty.
6. The system SHALL be deterministic and emit the provenance fields required of BP.

**Tests required:** `verify_t17_tr.py` — OPT formula check, exact core-optima counting on small
cases, step-variant generation, determinism, fidelity.

**Evidence to produce:** construction, the restated proofs, the counting table, and the
applicability decision inherited from T16.

**Risks:** the family is trivial for the compact model by construction, so a null result here says
nothing about COMP; that is by design and must be stated when reporting.

**Dependencies:** T16's applicability decision.

**Stop criteria:** criteria 4 and 5 both end the line; neither is a failure.

**Out of scope:** the TR-F1 variant (restricting origin groups to disjoint corridor bundles), which
the assessment itself leaves as an unwritten hypothesis.

**Independent Test**: generate `TR(k=3, L=5, r=2, σ=∞)` and confirm `OPT = 3` with 27 core optima,
3 of them feasible.

---

### P2: T18 — Evaluate all-V disaggregation as an LP diagnostic

**User Story**: As a researcher wondering how much the aggregated flow costs in relaxation
strength, I want a per-commodity disaggregated formulation implemented faithfully and compared on
small instances only, so that the aggregation loss is measured instead of assumed.

**Why P2**: Independent of the families and of the CBI; it can run in parallel. It is a diagnostic,
never a production candidate at this stage.

**Objective.** Measure `z_LP` of the disaggregated model against COMP on a small controlled set,
with model size and build time recorded.

**Current problem.** No disaggregated formulation exists.
`experiments/alternative-formulations/modelo_estendido.py` is VI-only (`y` restricted to `VI`,
destination without outflow — renamed `construir_modelo_estendido_vi` by T11 precisely because it
is **not** equivalent to the baseline), and `modelo_min_station_fluxo.py` is an older copy of the
aggregate baseline with a single `f[u,v]` per arc.

**Expected behaviour.** A formulation with flow variables indexed by robot (or by origin–
destination commodity) over the reach digraph, faithful to Das: stations on all of `V`, unit
objective, `|S| = |T|`, autonomy in steps. Cost is `O(m·|A_r|)` variables, which is exactly why it
stays on small instances.

**Files affected:** new module under `experiments/alternative-formulations/`; a comparison script;
no change to `baseline.py`.

**Acceptance criteria:**

1. The system SHALL state the complete mathematical formulation, its relation to Das's problem and
   to COMP, and the variable and constraint counts, before measurement.
2. WHEN the disaggregated model is solved on a small instance, THEN the system SHALL report
   `z_LP` of COMP, `z_LP` of the disaggregated model, model size, build time and relaxation time
   side by side.
3. The system SHALL restrict the comparison to instances small enough that both models build and
   solve, and SHALL record the size at which the disaggregation becomes impractical.
4. The system SHALL NOT conclude that the disaggregated formulation is computationally better from
   root LP strength alone.
5. IF the LP improvement is not large enough to justify the `O(m·|A_r|)` cost, THEN the system SHALL
   record the diagnostic and SHALL NOT plan an expansion.
6. WHEN both models are solved to optimality on the same small instance, THEN their `OPT` values SHALL
   agree, as a fidelity check of the new formulation.

**Tests required:** an equality-of-OPT regression between the disaggregated model, the base model
and `independent_validator.opt_por_enumeracao` on the smallest gadgets.

**Evidence to produce:** formulation document, the comparison table, and the explicit decision on
whether any expansion is justified.

**Risks:** a faithful disaggregation is easy to get subtly wrong (per-robot balance at terminals,
`S∩T` handling); criterion 6 is the guard, and the Block 1 proof gives the semantics to match.

**Dependencies:** none hard. Can run in parallel with T12–T15.

**Stop criteria:** criterion 5 ends the line without expansion.

**Out of scope:** replacing COMP; column generation on top of the disaggregation (a paused line).

**Independent Test**: on `make_Tri`, confirm the disaggregated `OPT = 2` and compare its `z_LP`
against COMP's 1.0.

---

### P2: T19 — Run the pilot of the structural families (Phase P)

**User Story**: As a researcher who must not choose parameters after seeing which method won, I
want the pilot frozen in writing before the first run, executed under the Block 2 protocol with the
Block 2 metrics.

**Why P2**: It depends on the families existing and on their preconditions being closed.

**Objective.** Execute the pre-registered matrix (see Pilot Pre-registration) and persist every
metric needed by T20's criteria.

**Current problem.** No family exists yet, so the pilot cannot run. Additionally, no runner uses
`WorkLimit`, which the budget decision requires for method comparison.

**Acceptance criteria:**

1. The system SHALL freeze generator parameters, sizes, generation seeds, solver seeds, methods,
   cut families, budget, metrics and per-family success criteria in a versioned document before the
   first run.
2. IF any cell's family has an open gate property from the Mathematical Preconditions table, THEN the system SHALL
   exclude that cell and record the exclusion before running.
3. WHEN methods are compared within a cell, THEN the system SHALL give every arm the same budget in
   the unit chosen by the budget decision, with the same threads and the same absence of MIP start.
4. The system SHALL persist, per run, the metrics of `schema-instrumentacao-mip.md` including
   `NodeCount` and the incumbent times, plus CBI iteration and cut counts where the CBI arm runs.
5. The system SHALL record, per instance, the generator version, parameters, seed, `sha256`, the
   certificate and its origin, and the commit.
6. IF the matrix differs from the assessment's 33 cells, THEN the system SHALL record the old
   value, the new value, the justification, and the fact that the change was decided before any
   pilot result was observed.
7. The system SHALL NOT run the CBI arm unless T16 declared it applicable, and SHALL NOT run the C6
   arm unless T14's validation is complete.

**Tests required:** a dry-run that builds every planned instance and confirms hashes and
preconditions without solving, before the measured run.

**Evidence to produce:** the frozen Phase P manifest, the CSVs with the full metric schema, the
commits, and the input to T20.

**Risks:** the budget migration to `WorkLimit` is untested in the runners; calibrate and record the
mapping between work units and the intended effort before the measured run.

**Dependencies:** T9, T10 (Block 2, done), T12, T13, T15, and conditionally T14, T16, T17.

**Stop criteria:** an unmet gate property removes a cell, not the whole pilot.

**Out of scope:** adjusting any frozen parameter in response to results; that requires a new,
explicitly identified round.

**Independent Test**: the frozen manifest is readable and sufficient to regenerate every pilot
instance from scratch.

---

### P2: T20 — Apply promotion or discard criteria

**User Story**: As a researcher who wants to avoid an open-ended search for ever-larger instances,
I want each family judged by criteria fixed before the results, with exactly one decision recorded.

**Why P2**: It is the gate that keeps Phase E small and honest.

**Objective.** Convert pilot results into one decision per family, by the pre-registered rules.

**Acceptance criteria:**

1. The system SHALL apply the general rule: a family advances only if its predicted properties
   reproduce on all pilot instances, the phenomenon appears in at least 2 of the 3 size levels, the
   relevant result is stable across seeds where the verdict needs it, and the family discriminates
   at least two methods, bounds or cut families according to its original hypothesis.
2. The system SHALL record exactly one of `PROMOTE`, `DISCARD` or `REVISE THEORY/GENERATOR` per
   family, and SHALL NOT record "inconclusive" when the failing property can be identified.
3. The system SHALL apply the family-specific criteria: BP's twins must show opposite hard sides;
   SC's growth must follow the predicted gap with the rigid twin separating symmetry; HB's C6 gain
   must match the prediction, and HB may be kept as a bound instrument even if it is fast; TR must
   show iteration growth and a step effect.
4. IF a pilot result contradicts a property classified as PROVEN, THEN the system SHALL investigate
   an implementation or proof error first, and SHALL NOT interpret it as a computational phenomenon.
5. The system SHALL NOT modify any criterion after the results were observed.

**Tests required:** none; the verification is that the decisions cite the pre-registered criteria
verbatim.

**Evidence to produce:** the decision record, one entry per family, each citing the measurements
that triggered it.

**Risks:** the temptation to keep a family that is merely slow. Criterion 1's "discriminates at
least two methods" is the defence.

**Dependencies:** T19.

**Stop criteria:** `DISCARD` is a result, documented, not a failure to hide.

**Out of scope:** growing sizes to rescue a family.

**Independent Test**: each family's decision can be re-derived from the CSVs by a reader applying
the frozen criteria.

---

### P3: T21 — Run Phase E on promoted families

**User Story**: As a researcher reporting a structural result, I want the evaluation phase run on
new seeds with the generators frozen, so that no parameter or seed used during development can
inflate the final numbers.

**Why P3**: It runs only on what survives T20 and may apply to no family at all.

**Objective.** Expand only promoted families, with a strict development/evaluation separation.

**Current problem.** The real benchmark's partition was marked but not reassigned by T8, so Phase E
cannot inherit a clean split — the structural families must carry their own.

**Acceptance criteria:**

1. The system SHALL include only families marked `PROMOTE` by T20.
2. The system SHALL add two size levels above the pilot, use 5 generation seeds and 3 solver seeds.
3. WHEN evaluation instances are generated, THEN the system SHALL use generation seeds never used
   in development.
4. The system SHALL keep every variant of the same constructor and base parameters on the same side
   of the development/evaluation split, including both members of any twin pair.
5. The system SHALL freeze the generator, its version, parameters, cut families, methods, budget,
   metrics and analysis criteria before the first evaluation run, and any later change SHALL create
   a new, explicitly identified round.
6. The system SHALL record provenance per result following the Block 2 rules (instance hash, cut
   version, configuration, seed, solver, budget, certificate origin, commit).

**Tests required:** a check that the evaluation seed set is disjoint from the development seed set,
and that no twin pair is split across the partition.

**Evidence to produce:** a separate evaluation manifest, the frozen generators, raw results and a
final report.

**Risks:** splitting a twin across development and evaluation would destroy the comparison the twin
exists for; criterion 4 is explicit because the real benchmark already made this mistake with 11
origin graphs.

**Dependencies:** T20, plus the Block 2 consolidation rules.

**Stop criteria:** if no family is promoted, Phase E does not run, and that is the result.

**Out of scope:** adding families that were not in the pilot.

**Independent Test**: the evaluation manifest's seed set intersected with the development seed set
is empty.

---

## Pilot Pre-registration

The assessment's §11.4 matrix is reproduced verbatim as the starting point. It is pre-registered:
it does not change silently.

| Family | Cells | Instances |
|---|---|---|
| BP | `q ∈ {4,6,8}` (`n = 3q`, `B = 60`) × {yes, no} × 2 generation seeds | 12 |
| SC | `k ∈ {5,6,7}` × {GF2, rigid s0, rigid s1} | 9 |
| HB | pockets `k ∈ {1,4,8}` × `(q, ndir, p) ∈ {(6,1,1), (6,1,6)}` | 6 |
| TR | `(k,R) ∈ {(2,4),(3,4),(3,6)}` × `σ ∈ {∞, r}` | 6 |
| **Total** | | **33** |

**Methods** (assessment §11.4), with applicability updated by results that predate the pilot:

| Method | Applies to | Condition |
|---|---|---|
| M1 COMP (base U + C1+C2+C4) | all families | none |
| M2 BASE-C without cuts | all families | relaxation reference |
| M3 integer core | all families | the core is the bound mechanism under study |
| M4 CBI | only where T16 declares a live hypothesis | **A2 is closed for Das**; M4 is no longer a default arm |
| M5 COMP + C6 | HB, with BP and SC as controls | only after T14's derivation and validator are complete |

**Changes to the assessment's matrix, decided before any pilot result:**

1. **Budget unit.** The assessment says "TL 600 s, ou `WorkLimit` equivalente se adotado". T7
   adopted `WorkLimit` for method comparison, so the pilot budget is a `WorkLimit` calibrated to
   roughly the intended effort, with the calibration recorded. `TimeLimit` remains only as a wall
   guard for the batch.
2. **M4 becomes conditional.** The assessment wrote M4 as a default arm with the caveat "só roda
   depois da regressão da §9, Etapa 1" — that regression is done, but E12 then closed A2. M4 now
   requires a live hypothesis from T16.
3. **TR's 6 cells become conditional** on T17's applicability, which inherits T16's decision. If TR
   does not run, the pilot is **27 cells**, and the reduction is recorded with this justification.
4. **Instrumentation prerequisite is satisfied.** The assessment listed the missing `NodeCount` and
   incumbent times as a blocker; T9 closed it.

Conditions carried over unchanged: 4 threads, two slices, no MIP start, 1 solver seed in the pilot
and 3 seeds where a verdict turns on 1–2 units; metrics as listed in §11.4, which are a subset of
`schema-instrumentacao-mip.md`.

**Worst case** as estimated by the assessment: 33 instances × 4 methods × 600 s ≈ 22 h of CPU,
≈ 11 h in two slices; most small instances should finish before the limit.

---

## Promotion / Discard Rules

Pre-registered, from assessment §11.6. These are fixed before the pilot and are not revised
afterwards.

**General rule.** A family advances to Phase E only if all three hold:

1. every predicted property reproduces on every pilot instance — otherwise it is a generator or
   theory error and work stops until the cause is found;
2. the predicted phenomenon appears in at least 2 of the 3 size levels and repeats across 3 solver
   seeds where the verdict needs them;
3. the family discriminates at least two methods or two cut families.

**General discard.** Every method proves optimality quickly at the largest pilot size with no bound
difference; or time grows only with size, with no difference in root gap or nodes — that is scale
difficulty, not structural difficulty.

| Family | Keep if | Discard if |
|---|---|---|
| BP | the yes/no twins show opposite hard sides (UB on "yes", LB on "no"), or CBI iterations explode on "no" | both solve quickly at `q = 8` |
| SC | nodes and proof time grow with `k` while `UB = k` is found early, or the rigid twin differs clearly | `k = 7` is proved quickly with the root closed by the solver's own cuts |
| HB | the C6 LB matches the prediction (`≈ 1` per pocket) and some second-layer family closes the gap; kept as a bound instrument even when fast | C6 closes the gap — which forces the coefficient analysis to be redone before any conclusion |
| TR | CBI iterations grow super-linearly in `R` with COMP stable, and the step effect appears | iterations grow linearly — record as a finding about `𝒵` and discard TR as a stressor |

**Anti-HARKing rule.** No criterion in this section may be modified after results are observed. A
result that contradicts a PROVEN property triggers an implementation or proof investigation first.

---

## Edge Cases

- IF a family's theoretical property fails before the pilot, THEN the system SHALL stop and fix the
  theory or the generator, and SHALL NOT enter the pilot with the property downgraded.
- IF a generator emits a disconnected instance, THEN the system SHALL detect it with
  `independent_validator.avisar_se_desconexo` and SHALL reject the instance, since Das's problem
  assumes a connected graph.
- IF a yes/no twin pair stops being structurally comparable (different `N`, `M`, degree profile),
  THEN the system SHALL reject the pair, because the comparison depends on the twins differing in
  one property only.
- IF an external certificate contradicts the MIN-STATION result on the same instance, THEN the
  system SHALL treat it as a defect to be located, and SHALL NOT pick whichever answer is more
  convenient.
- IF C6 is valid but never violated on the HB instances where a violation was predicted, THEN the
  system SHALL record it as a refutation of the prediction, distinct from the inequality being wrong.
- IF C6 is found invalid for some `δ ≥ 2`, THEN the system SHALL halt the line and SHALL NOT
  measure it.
- IF the SC rigid twin still carries most of the symmetry, THEN the system SHALL report the twin as
  failed rather than interpreting its results as a symmetry separation.
- IF the all-V disaggregation is strong in LP but too large even on the small set, THEN the system
  SHALL record the size wall as the diagnostic result.
- IF a family becomes easy for every method, or hard for every method without discriminating any
  hypothesis, THEN the system SHALL discard it under the general rule.
- IF a mechanism appears in only one seed, THEN the system SHALL treat it as not reproduced.
- IF the generated instance and the manifest disagree (hash, `m`, `r`, `|S∩T|`), THEN the system
  SHALL fail the verification and SHALL NOT publish results from that instance.
- IF a pilot result contradicts a property classified as PROVEN, THEN the system SHALL investigate
  implementation and proof before interpreting it as a computational phenomenon.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| RES-01 | P1: T12 | Design | Pending |
| RES-02 | P1: T12 | Design | Pending |
| RES-03 | P1: T12 | Design | Pending |
| RES-04 | P1: T12 | Design | Pending |
| RES-05 | P1: T12 | Design | Pending |
| RES-06 | P1: T12 | Design | Pending |
| RES-07 | P1: T13 | Design | Pending |
| RES-08 | P1: T13 | Design | Pending |
| RES-09 | P1: T13 | Design | Pending |
| RES-10 | P1: T13 | Design | Pending |
| RES-11 | P1: T13 | Design | Pending |
| RES-12 | P1: T13 | Design | Pending |
| RES-13 | P1: T14 | Design | Pending |
| RES-14 | P1: T14 | Design | Pending |
| RES-15 | P1: T14 | Design | Pending |
| RES-16 | P1: T14 | Design | Pending |
| RES-17 | P1: T14 | Design | Pending |
| RES-18 | P1: T14 | Design | Pending |
| RES-19 | P1: T14 | Design | Pending |
| RES-20 | P2: T15 | Design | Pending |
| RES-21 | P2: T15 | Design | Pending |
| RES-22 | P2: T15 | Design | Pending |
| RES-23 | P2: T15 | Design | Pending |
| RES-24 | P2: T15 | Design | Pending |
| RES-25 | P2: T15 | Design | Pending |
| RES-26 | P3: T16 | Design | Pending |
| RES-27 | P3: T16 | Design | Pending |
| RES-28 | P3: T16 | Design | Pending |
| RES-29 | P3: T16 | Design | Pending |
| RES-30 | P3: T16 | Design | Pending |
| RES-31 | P3: T17 | Design | Pending |
| RES-32 | P3: T17 | Design | Pending |
| RES-33 | P3: T17 | Design | Pending |
| RES-34 | P3: T17 | Design | Pending |
| RES-35 | P3: T17 | Design | Pending |
| RES-36 | P3: T17 | Design | Pending |
| RES-37 | P2: T18 | Design | Pending |
| RES-38 | P2: T18 | Design | Pending |
| RES-39 | P2: T18 | Design | Pending |
| RES-40 | P2: T18 | Design | Pending |
| RES-41 | P2: T18 | Design | Pending |
| RES-42 | P2: T18 | Design | Pending |
| RES-43 | P2: T19 | Design | Pending |
| RES-44 | P2: T19 | Design | Pending |
| RES-45 | P2: T19 | Design | Pending |
| RES-46 | P2: T19 | Design | Pending |
| RES-47 | P2: T19 | Design | Pending |
| RES-48 | P2: T19 | Design | Pending |
| RES-49 | P2: T19 | Design | Pending |
| RES-50 | P2: T20 | Design | Pending |
| RES-51 | P2: T20 | Design | Pending |
| RES-52 | P2: T20 | Design | Pending |
| RES-53 | P2: T20 | Design | Pending |
| RES-54 | P2: T20 | Design | Pending |
| RES-55 | P3: T21 | Design | Pending |
| RES-56 | P3: T21 | Design | Pending |
| RES-57 | P3: T21 | Design | Pending |
| RES-58 | P3: T21 | Design | Pending |
| RES-59 | P3: T21 | Design | Pending |
| RES-60 | P3: T21 | Design | Pending |

**Coverage:** 60 total, 0 mapped to tasks (`tasks.md` not created in this round, by explicit user
request), 60 unmapped.

---

## Dependencies and Execution Order

Mandatory dependencies (mathematical or infrastructural):

```text
Block 1 (T1, T2) ──→ enumeration and feasibility checking for T12, T13, T15, T17, T18
Block 2 (T6)     ──→ any performance measurement: T19, T21
Block 2 (T9,T10) ──→ T19, T21 (metrics and paired protocol)
Block 2 (T7)     ──→ T19 budget unit
T13              ──→ T14   (HB is the control; the prediction is registered before C6 exists)
T19              ──→ T20 ──→ T21
T16 decision     ──→ T17 benchmark advance; T16/T17 arms inside T19
T14 validation   ──→ M5 (C6 arm) inside T19
```

Recommended order only (no mathematical dependency): T12 before T13; T15 after T14 in the
assessment's ordering, though the SC generator does not wait for T14.

Parallelizable: T18 with T12–T15; the SC generator with T13/T14.

Conditional tasks: T16 (may close as not applicable), T17 (inherits T16), T21 (runs only on
promoted families).

---

## Global Success Criteria

- [ ] Every implemented family has an explicit scientific hypothesis recorded before its generator.
- [ ] Every property needed to interpret a result is PROVEN or independently certified before the
      pilot; no gate property remains HYPOTHESIS.
- [ ] Generators are deterministic: same parameters and seed produce byte-identical instances and
      the same `sha256`.
- [ ] Structural instances are faithful to Das: simple, undirected, connected, unit weights,
      integer `r` in steps, `|S| = |T|`, stations on all of `V`, objective `min |C|`, and
      `S∩T = ∅` unless a deliberate, justified exception is recorded.
- [ ] Families derived from another problem carry a certificate produced outside MIN-STATION.
- [ ] Small cases are validated by the Block 1 independent validator and the base model, never by
      two implementations of the same construction.
- [ ] C6 is not measured before it is formally derived and validated for RHS `δ ≥ 2`.
- [ ] A2 is not reopened as a general method for Das.
- [ ] T16 and T17 exist only if a concrete new scientific question justifies them.
- [ ] The all-V disaggregation stays diagnostic until evidence justifies expansion.
- [ ] Phase P is pre-registered and Phase E uses new seeds.
- [ ] Each family receives exactly one decision, by criteria fixed beforehand.
- [ ] Negative results are documented and may close lines.

---

## Inconsistencies Found Between the Backlog, the Assessment, the Code, the Earlier Specs and the Current State

1. **"C6" names two different things.** `direcoes-pli-min-station.md` §5.4 item 2 defines the
   knapsack first-hop Hall inequality and marks it `[Provado]`; §5.6 defines a *different* family
   also called "C6" and marks it `[Esboço]`. The backlog's T14, the assessment's HB analysis and
   `plano-pos-e8-adiado.md` all mean the §5.4 one. Any implementation that follows the §5.6
   heading would build the wrong, unproven inequality. Recorded as an Assumption above.
2. **The assessment's §11.7 conditionals were never resolved.** The text still conditions TR on
   "a linha A2 seguir viva" and states what happens "se A2 for encerrada", although E12 closed A2
   and E14 came back 0/4. Applying the assessment's own rules yields BP → HB → SC (demoted to a
   core control) → TR (optional). The assessment file was edited after E12 only to add a pointer
   to the backlog.
3. **The pilot budget in §11.4 predates the budget decision.** It prescribes "TL 600 s"; T7
   adopted `WorkLimit` for method comparison. The pilot cannot follow both.
4. **Appendix B's numbers have no code behind them.** The assessment states the scripts stayed in
   a session scratchpad. Thirteen verified mini-cases are therefore results that no one in the
   repository can currently reproduce; T12, T13, T15 and T17 must regenerate them.
5. **The backlog's T13 criterion assumes C6 behaviour that T13 is supposed to predict.** It reads
   "O comportamento do coeficiente C6 em destinos compartilhados é validado" as an HB acceptance
   criterion, but C6 does not exist until T14. This spec resolves it by having T13 *register the
   prediction* and T14 test it.
6. **Block 2 is complete in the working tree but uncommitted.** `cuts.py`, `harness.py`,
   `bc_yspace.py`, `yspace.py`, `manifest.csv`, `build_manifest.py` and six new files are
   unstaged. Block 3 depends on all of them; a lost working tree would silently remove its
   foundations.
7. **T8 marked the partition leaks without fixing them.** The backlog records "A partição não foi
   reatribuída; os 11 vazamentos ficaram marcados." Phase E therefore cannot inherit a clean
   development/evaluation split from the real benchmark and must define its own.
8. **`build_manifest.py` cannot see structural instances.** It scans `instances/*.txt` (requiring a
   `LEGADO` entry, otherwise printing "sem proveniência registrada" and skipping) and
   `instances/benchmark-v1/**`. Structural families need a third branch; without it, generated
   instances would be silently absent from the manifest.
9. **The backlog's dependency block still lists `T12 → T13 → T14` as a chain.** T12 before T13 is a
   recommended order, not a mathematical dependency; only T13 → T14 is binding (HB is C6's
   control). This spec states the distinction explicitly, as requested.
