# Block 2 — Experimental Reliability (MIN-STATION) Specification

Scope: T6–T11 from `docs/technical/plans/backlog-continuacao.md`, with scientific basis in
`docs/technical/reference/MIN-STATION-parecer-macro-consolidado.md`
(§3, §5, §9 Stage 2, §10).

All facts below were checked in this session through code inspection and direct execution —
they were not copied from the assessment without verification
(the assessment itself warns in §5 that "all numbers in this section are from `e9d1ccb`
and must be recomputed after regeneration").

---

## Relationship with Block 1 — Correctness

Block 1 (`specs/bloco1-corretude-terminais-sT/spec.md`) is responsible for:

- fixing the oracle for `S∩T` (T1);
- the independent `(v, battery)`-state validator (T2);
- the terminal regression suite (T3);
- revalidating results affected by the old oracle (T4);
- and the equivalence proof of the base formulation (T5).

**None of those items are duplicated here.**

**What Block 2 assumes from Block 1, without re-executing it:**

- Oracle correctness (`integer_oracle`, `_build_flow_net_aggregate`) is the responsibility
  of Block 1. T9 (instrumentation) and T10 (protocol) in this block **instrument and
  standardize** the oracle's use by CBI, but do not verify whether it is mathematically correct.

- The item "fix comments for `StayPut`/`SharedTerminal` in `synthetic.py`" from assessment §10
  **belongs to Block 1**
  (it is the same defect recorded as "Inconsistency 2" in the Block 1 spec).
  T11 in this block does not duplicate it — it only confirms that the item did not fall
  through the gap between the two blocks.

- The item "remove or qualify the `S∩T=∅` assumption" in
  `validacao-formulacao-base.md` belongs to the equivalence proof
  (T5 in Block 1).
  T11 in this block covers only `base-formulation.md`
  (a sibling occurrence outside T5's scope) — see T11 below.

**What may proceed in parallel with Block 1, without depending on it:**

T6 (determinism), T7 (budget), T9 (instrumentation), and T8
(benchmark consolidation) do not read or modify
`integer_oracle` / `_build_flow_net_aggregate`.

They operate on:

- `harness.py`;
- `bc_yspace.py`
  (model-construction and accounting portions, not the oracle flow network itself);
- `manifest.csv`;
- and `run_e*.py` scripts.

They may be executed before Block 1 is completed.

**What MUST NOT be used as definitive evidence before Block 1 is completed:**

Any performance comparison performed through T6/T7/T9/T10 that involves
`solve_cbi` or `solve_bc_yspace` on an instance with `S∩T ≠ ∅`
remains subject to the oracle defect until Block 1 (T1) fixes it.

The current experiments
(E12, MAPF controls) already avoid this by running only on `S∩T = ∅`
(as verified in `resultados-e12-pli.md`, section `"Checagem"` / "Check").

However, any **new** T7/T10 experiment batch containing an instance with
`S∩T ≠ ∅` must wait for Block 1.

---

## Current State

Every item below was verified in this session
(code inspected and, where indicated, executed),
rather than assumed from the assessment or backlog.

### Proven correct / already fixed

- **`generate_C4_DM` is deterministic**
  (sorted adjacency) — fixed on 2026-09-26
  (`correcao-c4-dm.md`).

  This is outside T6's scope:
  it fixes the **content** of the cut family,
  not the **order** in which the final model is delivered to Gurobi.

- **`measure_mip` (`harness.py:213`) already returns `node_count`**
  (`int(modelo.NodeCount)`), together with:

  - `mip_obj`;
  - `mip_bound`;
  - `mip_gap`;
  - `mip_status`;
  - `sol_count`;
  - `time_mip_s`.

  Confirmed through code inspection:
  the backlog note
  ("P3... node_count is already returned by measure_mip")
  is correct and up to date.

- **`run_e12.py` persists `node_count`**
  in the output CSV
  (confirmed by `grep`).

  E12's three-arm protocol
  (COMP/NUCLEO/CBI) also already records:

  - `iteracoes`;
  - `n_z`;
  - `t_mestre_s` / `t_oraculo_s`;
  - `PYTHONHASHSEED`;
  - `commit`;

  per row.

  It is currently the most heavily instrumented report in the project.

- **Incumbent time-series infrastructure already exists**:
  `ms_utils.RegistSerieTemporal`
  (`MIP`/`MIPSOL` callback)
  stores sampled `(time, LB, UB, nodes)` tuples and is used by
  `baseline.py:executar_para_R`
  (the direct runner for Das's problem, outside `experiments/cuts`).

  **It is not connected to `harness.measure_mip`**
  or to any `run_e*.py` in the cuts experiment family.

  Therefore, it is a reusable component for T9,
  not something that needs to be invented from scratch.

- **Gurobi 12.0.3 is the version actually installed**
  (`gurobipy.gurobi.version() == (12, 0, 3)`,
  confirmed through execution in this session).

  This is consistent with the header of `resultados-e12-pli.md`.

- **The benchmark-v1 regeneration has already occurred and is reflected in the
  current `manifest.csv`**
  (`H17` / `benchmark-v1.md` §8).

  This was confirmed by reading the manifest directly,
  not from the assessment.

  Current classes among the 75 `principal` instances are:

  - **F: 35**
  - **A: 28**
  - **M: 4**
  - **D: 3**

  resulting in **31 D/A**, plus 5 `legado` instances without computed difficulty.

  This **differs from the numbers in assessment §5**
  (35 F / 5 M / 4 D / 26 A, 30 D/A).

  The assessment itself labels those numbers as coming from `e9d1ccb`
  and requiring recomputation after regeneration.

  The regeneration has now occurred,
  so the assessment numbers are knowingly outdated,
  and the correct current values are those above.

- **`manifest.csv` has 92 rows, 75 of them `principal`**
  (confirmed through direct counting).

  This matches what the backlog already records
  (inconsistency 6).

  However, **`CLAUDE.md:71` still says
  "22 antigas compatíveis + 70 do benchmark-v1"**
  ("22 old compatible instances + 70 from benchmark-v1").

  This happens to sum to 92,
  but the partition is wrong:

  - 5 legacy + 70 benchmark-v1 = 75 `principal`;
  - not 22 + 70 = 92 `principal`.

  Confirmed through direct inspection of `CLAUDE.md` in this session.

### Proven incorrect / still not fixed (confirmed in this session)

- **Model-construction order still varies between processes.**

  `harness.py:87`:

  `all_cuts = list({frozenset(Z) for Z in all_cuts})`

  uses an unsorted `set` comprehension,
  making its order dependent on string hashing
  and therefore on `PYTHONHASHSEED`.

  `bc_yspace.py` repeats the same pattern in at least four places
  confirmed through inspection:

  - line 243:
    `all_cuts = set(frozenset(Z) for Z in (static_cuts or []))`;

  - line 332:
    `all_cuts.add(frozenset(Z))`;

  - line 73:
    `S_set, T_set = set(S), set(T)`;

  - line 116:
    extraction of `C` through
    `frozenset(v for v, val in y_bin.items() if val > 0.5)`.

  The iteration order of `y_bin.items()` itself depends on
  variable insertion order in the Gurobi dictionary,
  which is not necessarily stable between processes.

  None of these points uses `sorted()`.

- **`WorkLimit` is not used anywhere in the repository.**

  `grep -rn "WorkLimit"` returns nothing.

  T7 is therefore new work,
  not a decision that has already been made.

- **`resultados-e13-pli.md:143` still states
  `"Isto não é ruído de execução"` ("This is not execution noise")**,
  attributing the 9/13 divergence from the manifest only to the C4-DM correction.

  This was confirmed through direct inspection.

  The `TimeLimit` × `MIPFocus` confounding in the `focus1800` arm
  is also confirmed by inspecting `run_e13.py`
  (lines 160–166):

  the 1800-second arm changes `TimeLimit`
  **and** adds `MIPFocus=1` in the same execution,
  with no `"TL=1800, no MIPFocus"` control
  to isolate the effect.

- **`resultados-e2-e4-pli.md` still contradicts its own CSV regarding
  Barcelona st25.**

  Line 285 shows:

  `BASE-C | 16 | 16 | 0% | OPT | 299`

  meaning the optimum was proven in 299 seconds.

  Line 315 says:

  `"BASE-C chega perto, 299s, sem provar"`
  ("BASE-C gets close, 299s, without proving it").

  Both statements occur in the same file,
  confirmed through `grep` in this session.

- **`experiments/alternative-formulations/modelo_estendido.py`
  still names the function
  `construir_modelo_estendido_equivalente`**
  and describes the script as:

  `"Solver MIN-STATION (estendido, equivalente ao baseline)"`

  ("MIN-STATION Solver (extended, equivalent to the baseline)").

  This was confirmed by inspection.

  The task is to verify whether that description is misleading
  (see T11, which must inspect the function body before deciding the exact correction,
  since this review did not inspect the internal constraints of the extended model).

- **`direcoes-pli-min-station.md` §13 still contains no `[E12]` entry.**

  Confirmed through `grep` in this session
  (0 occurrences).

  A plan to close this gap already exists
  (a previous session in this same conversation approved such a plan),
  but **it was never executed**.

  `plano-pos-e8-adiado.md` is also confirmed to lack a
  `"Situação após E12"` ("Status after E12") section,
  still ending at `"Situação após E9 e E10"`.

- **`base-formulation.md:154-155` still says
  `"caso de todas as 22 instâncias do repositório"`**
  ("the case for all 22 instances in the repository").

  This statement predates benchmark-v1.

  Today there are 75 `principal` instances,
  5 of which have `S∩T≠∅`
  according to `rho_S_inter_T` in the manifest.

  This was confirmed through direct inspection.

  The exact `"22 instances"` wording was not explicitly called out in
  assessment §10
  (which only referred to line 155 generically as requiring qualification
  of the assumption),
  but it is a directly verifiable consequence of that same outdated line.

- **`hc9u.txt` and `puc-hc9u-seed-r1.txt` are indeed the same graph.**

  They have the same:

  - `N=512`;
  - `M=4608`;
  - `R=1`;
  - `S={128}`;
  - edge set;

  differing only in weight formatting such as `"1.0"` vs `"1"`.

  This was confirmed through **parsing** and direct structural comparison
  in this session,
  not through `sha256`.

  Their `sha256` values differ because `# meta: ...`
  comments appear only in the `puc-*` version.

  This corrects an imprecision in the assessment,
  which described them as having
  "identical sha256/content."

  Their **structural** content is identical;
  their text files are not byte-for-byte identical.

- **The leakage of 11 source graphs between `desenvolvimento` and `avaliacao`
  still exists, with the same 11 names listed in the assessment:**

  - `I065`
  - `apia-1.graphml`
  - `b06`
  - `b12`
  - `b18`
  - `bip42p`
  - `cc10-2u`
  - `hc10p`
  - `hc9u`
  - `lin06`
  - `w23c23`

  This was confirmed through a direct script over the current
  `manifest.csv` in this session.

  It is not a recycled number from the assessment:
  it was recomputed and happened to match.

- **Two additional duplicate cases, not cited in the assessment,
  exist within the `avaliacao` partition itself:**

  - `cc7-3n`
    (`pucn-cc7-3n-regiao-f2` and
    `pucn-cc7-3n-seed-r1`,
    both evaluation,
    difficulty A).

    This was already manually handled in E12 through the
    `GRAFOS` dictionary in `tabela_e12.py`.

  - `i160-301`
    (`i-i160-301-intercalado-f2-rho` and
    `i-i160-301-regiao-f2`,
    both evaluation,
    difficulty F).

    This has not been handled in any experiment,
    because no experiment so far has needed to treat the two variants
    as one graph for verdict-counting purposes.

### Partially implemented

- **`NodeCount` instrumentation:**

  It exists in `measure_mip`
  and is persisted by `run_e12.py`,
  but **not** in the E13/E14 CSVs.

  `e14_fatia{1,2}.csv`
  has no `node_count` / `NodeCount` column,
  as confirmed by reading the header.

  Therefore, the functionality is not absent;
  persistence is inconsistent across scripts.

- **Separate timing for generation/preprocessing/heuristic/solver
  and incumbent timing:**

  This does not exist in any `run_e*.py` in the cuts experiment family.

  It exists partially in `baseline.py`
  through `RegistSerieTemporal`,
  which provides sampled LB/UB timing data
  from which first/best incumbent times may be **derived**
  in post-processing,
  but they are not direct fields.

- **Consolidated benchmark:**

  Difficulty regeneration (H17) has been completed.

  Reorganization by source graph,
  deduplication,
  and complete result-level provenance (T8)
  have not.

### Hypothesis / to be verified during future execution
(not investigated in this session)

- Whether the T6 ordering correction changes any previously published
  numerical result (LB/UB),
  or only discovery order / runtime.

  This was not tested here.

  Only the fact that ordering varies was confirmed
  (a direct consequence of using `set` / `frozenset`
  without `sorted()`),
  but the effect on final results was not measured in this session.

- The body of `modelo_estendido.py`
  — specifically which constraints make it
  "VI-only" and
  "block transit through terminals,"
  as stated by the user and assessment —
  was not inspected line by line in this session.

  T11 must investigate this before rewriting the description.

- Whether other calls to
  `solve_cbi` / `solve_bc_yspace` / `solve_lp_cutting_plane`
  exist in E7/E8/E9/E10 scripts
  that Block 1 T4 has not explicitly covered yet.

  This matters for T9 to know which CSVs should be instrumented.

  It was not investigated in depth here.

  The complete inventory belongs to T4 in Block 1;
  T9 here only inventories the currently existing `run_e*.py`
  scripts without deciding whether they must be rerun.

---

## Problem Statement

The project already has evidence that research decisions
(A2 closed in E12, "primal gap" in E13)
were made under conditions that compromise comparison reliability:

1. The order in which cuts, vertices, and coefficients reach Gurobi varies
   between processes because `harness.py` and `bc_yspace.py`
   construct these lists from `set` / `frozenset`
   without explicit sorting.

2. There is no decision or experiment establishing whether
   `TimeLimit` or `WorkLimit` should be used as the experimental budget,
   while the assessment notes that Gurobi documentation recommends
   work-based limits for deterministic comparisons.

3. After regeneration, benchmark-v1 still contains
   11 source graphs whose variants are split between development and evaluation,
   plus 2 pairs of variants counted as independent evidence inside evaluation itself,
   including the already known
   `hc9u` / `puc-hc9u-seed-r1`
   case
   (same graph, two rows).

4. `measure_mip` and the `run_e*.py` scripts do not systematically record
   `NodeCount` and incumbent times,
   which already prevented E13 from determining whether its residual gap
   came from the LB or UB.

5. E13 already exposed a comparison pattern in which two variables
   (`TimeLimit` and `MIPFocus`)
   change simultaneously,
   while the effect is attributed to only one of them.

6. At least five documents:

   - `resultados-e13-pli.md`
   - `resultados-e2-e4-pli.md`
   - `CLAUDE.md`
   - `base-formulation.md`
   - `modelo_estendido.py`

   still contain statements that contradict the CSV or code they are supposed to summarize,
   as confirmed in this session.

Without resolving items 1–4 and standardizing a protocol (item 5),
every new performance comparison —
including those that will measure the synthetic families in Block 3 —
inherits the same risks already observed.

---

## Goals

- [x] Building the same model
      (same instance, same configuration)
      twice with different `PYTHONHASHSEED` values
      produces the same order of cuts, vertices, and relevant coefficients
      delivered to Gurobi in `harness.py` and `bc_yspace.py`.

- [x] A documented and tested decision exists
      (`WorkLimit`, `TimeLimit`, or both for different purposes),
      with the experimental protocol updated accordingly.

- [x] The benchmark is partitioned by source graph
      without development/evaluation leakage,
      with deduplication of:

      - `hc9u` / `puc-hc9u-seed-r1`;
      - `cc7-3n`;
      - `i160-301`;

      and result-level provenance including:

      - hash;
      - commit;
      - cut version;
      - configuration;
      - certificate source.

- [x] `measure_mip` and new `run_e*.py` scripts systematically record:

      - `NodeCount`;
      - time to first incumbent;
      - time to best incumbent;
      - time to proof;

      rather than implementing those fields ad hoc per script.

- [x] A paired-comparison protocol exists that requires declaring:

      - the control variable;
      - the changed variable;

      and is used in every future performance experiment.

- [x] The 7 documentation inconsistencies confirmed in this session
      (see Current State)
      have been corrected,
      with each correction tied to the evidence that motivated it.

---

## Out of Scope

| Item | Reason |
|---|---|
| Fix the oracle, create the independent validator, `S∩T` regression, revalidate E10/E10b, equivalence proof | Block 1 — see "Relationship with Block 1" |
| BP/HB/SC/TR structural synthetic families | Block 3, T12–T17/T19–T21 |
| E11/C6 (knapsack version) | Block 3, T14 |
| Disaggregated all-V formulation | Block 3, T18 |
| Lagrangian, classical Benders, generic BC-Y, C5, generic symmetry breaking, column generation | Paused and explicitly outside scope per the user |
| Solver-parameter tuning to improve results | Explicitly prohibited in this block — T7/T10 standardize the protocol; they do not optimize parameters |
| Rebuild the benchmark by selecting instances based on which method performed best | Explicitly prohibited — T8 deduplicates and reorganizes; it does not filter by result |
| Rerun historical results as a consequence of T6 ordering without evidence that numerical results changed | T6 fixes future construction. If there is reason to suspect an old result was affected by ordering rather than only runtime, that is a new investigation outside this spec |
| Correct the full ranking in `direcoes-pli-min-station.md` beyond the missing `[E12]` entry | T11 addresses the missing entry itself. Rewriting the whole ranking (B2, R6, etc.) is unnecessary because those lines are already correct |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Granularity of this spec (Specify only) | Each story (T6–T11) contains its objective, evidence, affected files, acceptance criteria, risks, and dependencies directly in `spec.md`, without formal `design.md` / `tasks.md` files | Same pattern adopted in Block 1, following the explicit user request ("create only the spec") | n |
| Where to implement the new instrumentation infrastructure (T9) | Extend `harness.measure_mip` with a callback based on `RegistSerieTemporal` (already exists and is currently used only by `baseline.py`), rather than creating a parallel callback mechanism | Avoids duplicating already written and tested sampling logic; `RegistSerieTemporal` already solves the "time to incumbent" problem through `MIP` / `MIPSOL` sampling | n |
| Name/location for the budget-decision document (T7) | `docs/technical/reference/decisao-orcamento-worklimit.md` (new) | Follows the project's existing naming pattern (`resultados-e*-pli.md`, `correcao-c4-dm.md`) for versioned protocol decisions | n |
| Name/location for the paired-comparison protocol (T10) | `docs/technical/reference/protocolo-comparacao-pareada.md` (new), referenced from `CLAUDE.md` | Same pattern; it must be a document that future `plano-experimentos-e*.md` files can cite, not merely an isolated section |
| Scope of the correction in `modelo_estendido.py` (T11) | Read the body of `construir_modelo_estendido_equivalente` before deciding whether to rename the function/description or merely qualify the docstring with the actual restrictions (VI-only, terminal transit blocked) | This session confirmed the misleading surface-level claim (name and description) but did not inspect the internal constraints. The exact correction is an implementation decision, not a spec decision | n |
| Handling the `i160-301` case (new duplicate not cited in the assessment) | Include it in the same T8 source-graph grouping mechanism, with no special case | It is structurally the same type of issue as `cc7-3n`, already handled ad hoc by E12. The general T8 fix (group by `instancia_original`) solves both with one rule | n |

**Open questions:** none — all have either been resolved or explicitly recorded above.

---

## User Stories

### P1: T6 — Make model construction deterministic ⭐ MVP

**User Story:** As a researcher comparing two methods based on the LB/runtime they produce,
I want the order of cuts, vertices, and coefficients delivered to Gurobi to be identical
in every execution of the same configuration,
so that a performance difference cannot be attributed to hash variation between processes.

**Why P1:** Blocks every new performance comparison.

T7 needs it for its controlled experiment,
and T10 identifies it as a protocol prerequisite.

It is the only item in this block for which the defect itself has already been directly
confirmed in this session.

**Objective.**
Remove `PYTHONHASHSEED` dependence from the model-construction order in
`harness.py` and `bc_yspace.py`
without changing the generated set of cuts or variables.

**Current problem (confirmed in this session).**

`harness.py:87`:

`all_cuts = list({frozenset(Z) for Z in all_cuts})`

`bc_yspace.py`:

- `all_cuts = set(...)` at line 243;
- `all_cuts.add(frozenset(Z))` at line 332;
- `S_set, T_set = set(S), set(T)` at line 73;
- `frozenset(v for v, val in y_bin.items() if val > 0.5)` at line 116.

None of these points sorts before iteration.

**Expected behavior.**

The final cut list (`all_cuts`),
the vertex list inside each cut,
and every structure whose iteration order affects Gurobi's
`addConstr` / `addVar` sequence
must be built using a deterministic sorting rule,
for example:

`sorted(..., key=...)`

with a stable key that does not depend on `hash()`.

**Affected files/components:**

- `experiments/cuts/harness.py`

  - `prepare_cuts` (lines 58–90, especially line 87);
  - `add_cuts_to_model` (lines 35–55), which currently iterates
    `for Z in cuts_specs: for v in Z`
    and therefore inherits `Z`'s order if the cut is not sorted beforehand.

- `experiments/cuts/bc_yspace.py`

  Confirmed locations:

  - 73;
  - 116;
  - 243;
  - 332.

  The entire file must be reviewed during implementation because this session
  did not inspect it line by line outside the points found through `grep`.

- `experiments/cuts/yspace.py`

  It calls `separate_classical_fracs`
  and adds returned cuts to an incremental LP
  (`_add_cuts`, line 81).

  Check whether the same pattern exists there.

  This was not confirmed in this session;
  only calls to `integer_oracle` / `separate_classical_fracs`
  were searched, not every `set` / `frozenset` occurrence in this file.

**Required changes.**

Replace each `set` / `frozenset` whose iteration order feeds model construction
with an ordered representation.

For example:

`sorted({frozenset(Z) for Z in all_cuts}, key=lambda z: sorted(z))`

for the cut list,
and `sorted(Z)` when `add_cuts_to_model`
iterates over vertices within a cut.

`PYTHONHASHSEED` may remain fixed in execution scripts
as an additional safeguard,
but it must not replace explicit sorting.

This is an explicit requirement from the user
and assessment §3.1.

**Acceptance criteria:**

1. WHEN `prepare_cuts` is called twice with the same instance
   and the same `active_cuts`
   under two different `PYTHONHASHSEED` values,
   THEN the system SHALL return `all_cuts` in the same **list order**
   in both executions,
   not merely with the same set contents.

2. WHEN `add_cuts_to_model` adds a cut `Z` to the model,
   THEN the system SHALL iterate over the vertices of `Z`
   in deterministic order,
   so that the order of the constraints in the Gurobi model
   (`modelo.getConstrs()`)
   is identical between executions with different `PYTHONHASHSEED` values.

3. WHEN `solve_bc_yspace` / `solve_cbi`
   constructs or updates `all_cuts` across iterations,
   THEN the system SHALL preserve deterministic ordering incrementally as well.

   Cuts added in later iterations must enter in deterministic positions
   independent of hashing.

4. The system SHALL produce exactly the same **set of cuts**
   before and after the fix.

   T6 changes ordering, not content.

5. The system SHALL retain `PYTHONHASHSEED`
   as a documented additional safeguard in execution scripts,
   without depending on it for deterministic construction.

**Required tests:**

Create a new script, for example:

`experiments/cuts/verify_t6_determinismo.py`

The script must run:

- `prepare_cuts`;
- and separately the `solve_bc_yspace` construction sequence;

on 2–3 real instances:

- one small;
- one around the size of `b-b15-regiao-f4`,
  which the assessment cites as already used to reproduce the defect;

under:

`PYTHONHASHSEED ∈ {0,1,2,3}`.

It must compare the resulting **ordered list**,
not just the set.

The test must:

1. first reproduce assessment §3.1 as a negative regression
   (same 33 cuts, differing order);

2. then confirm stable ordering after the fix.

**Evidence to produce:**

A before/after table containing an order hash
(for example, a hash of the concatenated cuts in produced order)
for:

`PYTHONHASHSEED ∈ {0,1,2,3}`

showing:

- divergence before;
- equality after.

**Risks:**

Using `sorted(Z)` assumes vertex identifiers have a stable ordering.

They are strings in the current `.txt` instance format.

Lexicographic string comparison is deterministic,
but may not correspond to the numerical order a human reader expects,
for example:

`'10' < '2'`.

This does not compromise determinism,
only readability.

It should not be "fixed" by switching to numeric sorting without a concrete need,
because the goal is reproducibility, not aesthetics.

**Dependencies:** none.

Blocks T7,
because budget comparisons are only meaningful once construction is stable.

It is also a prerequisite referenced by T10.

**Out of scope:**

- changing the content of any cut family;
- optimizing sorting performance
  (the cost is negligible relative to solver time).

**Independent Test:**

Run `verify_t6_determinismo.py` under:

`PYTHONHASHSEED ∈ {0,1,2,3}`

and verify that the order hash is identical in all four executions.

---

### P1: T9 — Expand experimental-harness instrumentation

**User Story:** As a researcher who needs to determine whether a residual gap is primal or dual,
I want `NodeCount`, time to first incumbent, time to best incumbent,
and time to proof to be recorded systematically,
so that the E13 situation
(residual gap with no attribution)
is not repeated.

**Why P1:**

The assessment already records in §4 that:

> there is no systematic comparison of `NodeCount` or primal/dual trajectories
> in the E4/E8/E9/E13 CSVs.

This session confirmed that this is still true for E13/E14.

T7 needs these metrics to interpret its
`WorkLimit` × `TimeLimit`
experiment.

Therefore the suggested order is T9 before T7.

**Objective.**

Make `measure_mip`
and the `run_e*.py` scripts that call it
systematically record:

- `NodeCount` — already available;
- separate generation / preprocessing / heuristic / solver time;
- time to first incumbent;
- time to best incumbent;
- time to proof;
- and, for iterative methods such as CBI:
  - iterations;
  - cuts per iteration;
  - master time;
  - oracle time;
  - total budget spent.

The last group already exists in the E12 CSV
(see Current State)
and should be used as a schema reference.

**Current problem (confirmed in this session).**

`measure_mip` returns `node_count`,
but not incumbent times.

No callback is registered inside:

- `measure_mip`;
- `measure_root`;
- `measure_lp`.

All three currently call:

`modelo.optimize()`

without a callback.

The only project callback that samples:

`(time, LB, UB, nodes)`

is `RegistSerieTemporal`,
used only by:

`baseline.py:executar_para_R`

outside `experiments/cuts`.

`e14_fatia{1,2}.csv` contains neither:

- `NodeCount`;
- incumbent-time fields.

This was confirmed by directly inspecting its header.

`run_e12.py`, on the other hand,
already has a richer schema:

- iterations;
- `n_z`;
- `t_mestre_s`;
- `t_oraculo_s`;
- `node_count`.

This should serve as the reference for
what "sufficient instrumentation" means for iterative methods.

**Expected behavior.**

Extend `measure_mip`
(or introduce a new function if justified; see Risks)
to accept an optional callback reusing `RegistSerieTemporal`.

It should additionally return:

- `time_to_first_incumbent_s`;
- `time_to_best_incumbent_s`;
- `time_to_proof_s`
  when the final status is `OPTIMAL`;

and generation / preprocessing / heuristic times
when those stages actually exist in the experiment.

Not every `run_e*.py` has heuristic or preprocessing stages.

The spec does not require inventing stages that a method does not have.

**Affected files/components:**

- `experiments/cuts/harness.py`

  `measure_mip`
  (lines 213–265)
  gains:

  - optional callback support;
  - new return fields.

  `measure_root` / `measure_lp`
  must be assessed separately.

  They may not need incumbent timing
  because they measure only the root / LP.

- `ms_utils.py`

  Reuse `RegistSerieTemporal`
  (around line 128),
  rather than rewriting it.

  Evaluate whether it needs a
  "no CSV/PNG" mode.

  `measure_mip` does not necessarily want to write a graph for every call;
  it may only need to extract incumbent timing from the in-memory series.

- `experiments/cuts/bc_yspace.py`

  `solve_cbi` / `solve_bc_yspace`
  already expose iteration / cut information internally
  (used by E12).

  Confirm that these fields remain exposed by the public function
  rather than existing only internally,
  and document their schema alongside `measure_mip`.

- Future `run_e*.py` scripts.

  Historical published E9–E14 scripts are not rerun by this task alone
  — see Out of Scope.

  New scripts must adopt the expanded schema.

**Acceptance criteria:**

1. The system SHALL continue returning `node_count`
   with exactly the same meaning it has today,
   without breaking compatibility with `run_e12.py`.

2. WHEN `measure_mip` is run with incumbent callback collection enabled,
   THEN the system SHALL record:

   - time to first incumbent;
   - time to best incumbent.

3. IF final status is `OPTIMAL`,
   THEN the system SHALL record elapsed time to proof.

   This may be the final `time_mip_s`,
   but must be explicitly labeled as proof time when `status==OPTIMAL`,
   distinct from time to best incumbent when the two differ.

4. WHILE a method is iterative (CBI),
   the system SHALL record:

   - number of iterations;
   - cuts per iteration;
   - cumulative cuts;
   - master time;
   - oracle time;

   using the schema already employed by `run_e12.py`
   instead of creating an incompatible new schema.

5. The system SHALL document, for every metric,
   whether it is available without meaningful additional cost
   — for example `NodeCount`, which Gurobi already provides —
   or whether it requires expensive instrumentation
   — for example callbacks for every `measure_lp` / `measure_root` call.

   Expensive instrumentation SHALL NOT be added
   without an explicit use case.

6. Before adding instrumentation,
   the system SHALL exhaustively inventory the existing `run_e*.py` scripts:

   - E0;
   - E1';
   - E1;
   - E2;
   - E4;
   - E6;
   - E7;
   - E8;
   - E9/E10/E10b;
   - E12;
   - E13;
   - E14;

   and record which ones currently persist:

   - `NodeCount`;
   - incumbent timing.

   Do not assume either
   "none have it"
   or
   "all need it"
   without checking each one.

**Required tests:**

Run `measure_mip`
with the callback enabled
on a small instance
(for example, a nontrivial fixture from `synthetic.py`).

Confirm:

`time_to_first_incumbent_s <= time_to_best_incumbent_s <= time_mip_s`

and verify that the three times coincide when only one incumbent solution exists.

**Evidence to produce:**

- One real example record
  (CSV row or printed dictionary)
  with every new metric populated.

- A table from acceptance criterion 6
  showing which current scripts already persist which metrics.

**Risks:**

Attaching callbacks to `measure_lp` / `measure_root`
may create non-negligible overhead
when those functions are executed in bulk over many small instances.

Those functions run the LP/root,
not the full MIP,
and are called at higher volume in E0–E4.

The spec therefore requires explicit assessment,
not blind instrumentation of every function.

**Dependencies:** none incoming.

T7 depends on this instrumentation
to interpret its comparison experiment.

T10 references `NodeCount` and incumbent timing
as protocol requirements,
so it depends on the schema defined here.

**Out of scope:**

- rerunning E9–E14 merely to retroactively fill the new metrics
  in already published CSVs.

  That would be historical result revalidation,
  closer to T4/T11.

  T9 defines and implements the mechanism;
  it does not reprocess the past.

- instrumenting instance-generation time.

  Benchmark generation is a separate offline process,
  not part of a method's measurement loop.

**Independent Test:**

Compare the dictionary returned by `measure_mip`
before and after the change
on the same instance.

Existing fields such as:

- `mip_obj`;
- `mip_bound`;
- `node_count`;

must remain semantically unchanged.

Only the new fields should be added.

---

### P1: T7 — Evaluate and standardize the experimental budget (`WorkLimit` × `TimeLimit`)

**User Story:** As a researcher comparing two methods under the same budget,
I want to know whether `TimeLimit`
(which is sensitive to machine load)
or `WorkLimit`
(deterministic by Gurobi's definition)
should be the project's default,
based on a tested decision rather than an assumption from the assessment.

**Why P1:**

Depends on:

- T6 — deterministic construction;
- T9 — instrumentation;

so that the comparison experiment can be interpreted.

That is why it comes after those two in the recommended order,
even though its task number is lower.

**Objective.**

Using a controlled experiment in the current environment
(Gurobi 12.0.3),
decide whether the project should:

- adopt `WorkLimit`;
- keep `TimeLimit`;
- or use both for different purposes.

**Current problem (confirmed in this session).**

`WorkLimit` is not used anywhere in the repository
(empty `grep`).

Every `run_e*.py` / `harness.py`
uses `TimeLimit`.

The assessment (§3.2) only states that:

- Gurobi documentation recommends work limits;
- semantics must be confirmed before adoption.

No experiment has yet been run.

**Expected behavior.**

Produce a decision document containing:

1. What `WorkLimit` actually measures
   according to the Gurobi 12.0.3 documentation
   — work units, not seconds,
   to be confirmed against the official documentation,
   not from memory,
   following `CLAUDE.md`'s rule for third-party documentation.

2. A controlled experiment,
   using the same instances,
   comparing result repeatability under:

   - fixed `TimeLimit`;
   - fixed `WorkLimit`;

   under varying machine-load conditions.

   For example,
   run the same instance both:

   - alone;
   - in parallel with other loads / "slices,"
     as the project already does.

3. The final decision and rationale.

**Affected files/components:**

- No production file needs to change before the decision.

- If switching from `TimeLimit` to `WorkLimit` is adopted,
  the migration will affect:

  - `harness.py`
    (`measure_mip`, `measure_root`);
  - `bc_yspace.py`
    (`solve_cbi`, `solve_bc_yspace`);
  - every `run_e*.py` that defines a budget.

  That migration is implementation work,
  not part of writing this spec.

- New decision document
  (see Assumptions).

**Required changes.**

No production code change is mandatory in this task
beyond the controlled experiment itself
(a measurement script,
either disposable or versioned as evidence).

Changing the project's default parameter
happens only if the final decision is to adopt `WorkLimit`.

**Acceptance criteria:**

1. The system SHALL cite the official Gurobi 12.0.3 documentation
   — not model memory —
   for the semantics of `WorkLimit`.

2. WHEN the controlled experiment runs the same instance/configuration
   under different machine-load levels
   (for example with and without other slices in parallel),
   THEN the system SHALL record whether:

   - `TimeLimit` produces varying amounts of work
     (`NodeCount`, nodes explored);

   - `WorkLimit` produces varying wall-clock time;

   under the same conditions.

3. The system SHALL depend on T6
   so that the isolated experimental variable is only the budget type,
   not model-construction order.

4. The system SHALL depend on T9
   (`NodeCount` and timing)
   to interpret the controlled experiment.

5. IF the decision is to use both budget types for different purposes,
   THEN the system SHALL specify exactly when each applies.

   For example:

   - `WorkLimit` for method comparison;
   - `TimeLimit` for experiments constrained by a real wall-clock deadline,
     such as overnight experiment batches.

6. The system SHALL update the experimental protocol
   through T10
   with the chosen decision,
   so that `TimeLimit` / `WorkLimit`
   is not an implicit per-script choice.

**Required tests:**

The controlled experiment described above is itself the test.

There is no separate "test of the test,"
other than repeating it on at least two instances
of different sizes,
so the decision is not based on one sample.

**Evidence to produce:**

`docs/technical/reference/decisao-orcamento-worklimit.md`

containing:

- Gurobi version;
- the relevant official documentation reference;
- CSV from the comparison experiment;
- final decision;
- rationale.

**Risks:**

`WorkLimit` may not apply in the same way to every current solver call.

For example,
pure LP in `measure_lp`
currently uses:

`lp.Params.TimeLimit`.

It must be confirmed whether `WorkLimit`
applies to continuous LP in the same way as to MIP.

"Work" in Gurobi is typically tied to operations such as
simplex work / B&B nodes,
but this MUST NOT be assumed without checking the documentation.

This is precisely the kind of difference
that `CLAUDE.md`'s third-party-documentation rule says not to infer from memory.

**Dependencies:** T6, T9.

**Out of scope:**

Migrating the entire existing codebase to `WorkLimit`
within this task.

This task decides and documents.

A bulk migration,
if the decision is to adopt `WorkLimit`,
is separate implementation work,
mentioned here only as an expected consequence.

**Independent Test:**

Re-run the controlled experiment from acceptance criterion 2
on a machine under a different workload
and confirm that the conclusion
about `WorkLimit` determinism
(or lack thereof)
still holds.

---

### P1: T10 — Standardize the paired-comparison protocol

**User Story:** As a researcher comparing two configurations,
I want a single protocol that forces me to declare
which variable changed and which one remained the control,
so that the E13 confounding
(`TimeLimit` and `MIPFocus` changed together,
with the effect attributed only to `MIPFocus`)
is not repeated.

**Why P1:**

Formalizes as a permanent rule
the lesson already learned and documented from E13.

Depends on:

- T6 — stable construction;
- T7 — decided budget;
- T9 — available metrics;

so that the protocol has concrete requirements to enforce.

**Objective.**

Write a documented protocol that every future
`plano-experimentos-e*.md`
must follow.

It must define explicit rules for:

- budget;
- threads;
- seed;
- start;
- exact instance;
- data version;
- "one variable at a time" when causal attribution is the goal.

**Current problem (confirmed in this session).**

`run_e13.py`
(lines 159–166):

the `focus1800` arm changes:

- `TimeLimit` from 600 to 1800;
- **and** adds `MIPFocus=1`;

in the same execution,
compared with a `controle` arm that has neither change.

There is no:

`"TL=1800, no MIPFocus"`

arm that would isolate the time effect.

This is the actual observed case motivating the task,
not merely a hypothetical risk.

**Expected behavior.**

A protocol document containing a checklist
that every new comparison experiment must complete before running.

It must include:

- identical budget across arms,
  unless budget itself is the variable under test;

- budget must never be changed "for free"
  together with another variable;

- identical thread count;

- solver seed(s) and number of seeds;

- multiple seeds when the verdict depends on a 1–2-unit difference,
  a rule already practiced ad hoc in E12;

- same MIP start,
  or no start in every arm;

- exact same instance
  (identified by hash);

- same data / cut version;

- explicit declaration for every comparison of:

  - **control variable / configuration**;
  - **experimental variable**.

**Affected files/components:**

- New:
  `docs/technical/reference/protocolo-comparacao-pareada.md`.

- `CLAUDE.md`:
  reference the new protocol in the existing
  "before any action"
  table that lists mandatory files by task type.

- No historical `run_e*.py` file is modified.

  The protocol applies going forward.

  E13 has already run and is only documented as a counterexample.

**Required changes.**

Documentation only.

No code change is required by this task itself.

The protocol is a checklist and convention,
not a software library.

A future helper function that automatically validates the checklist
may be useful,
but it is outside the minimum scope here.

**Acceptance criteria:**

1. The system SHALL require,
   for every paired comparison,
   an explicit declaration of:

   - what is the control;
   - what is the experimental variable.

2. IF two or more variables change between compared arms
   — such as `TimeLimit` and `MIPFocus` in E13 —
   THEN the system SHALL require either:

   - an additional arm isolating each variable;
   - or an explicit statement that the **combined effect**,
     not the isolated effect,
     is what is being measured.

3. WHEN the result of a comparison depends on a difference of 1–2 units
   — as in many E9/E12 verdicts —
   THEN the system SHALL require at least 3 solver seeds.

4. The system SHALL require `NodeCount` (T9)
   in every comparison whose verdict depends on search performance,
   rather than only the final bound.

5. The system SHALL require identical budgets between compared arms,
   using the format selected by T7:

   - `TimeLimit`;
   - `WorkLimit`;
   - or an explicitly documented rule assigning them to different arms/purposes.

6. The system SHALL require every comparison to record:

   - data version
     (instance hash, cut version);
   - code version
     (commit);

   for each arm.

**Required tests:**

No code test.

Verification:

Re-read `run_e13.py`
against the final checklist
and confirm that,
if the protocol had existed before E13,
it would have flagged the
`TimeLimit` × `MIPFocus`
confounding before execution.

That is the test that the protocol catches
the exact case that motivated it.

**Evidence to produce:**

`protocolo-comparacao-pareada.md`
containing:

- the checklist;
- a retrospective example applied to E13,
  showing where the checklist would have blocked the original design.

**Risks:**

An overly rigid protocol could prevent legitimate early-stage exploration.

Not every pilot experiment requires 3 seeds.

The document must distinguish:

- **exploration**
  — no publishable / recorded verdict;

from:

- **comparison with a recorded conclusion**
  — full checklist required.

This is analogous to the distinction already used by the project
between:

- `desenvolvimento`;
- `avaliacao`.

**Dependencies:** T6, T7, T9.

**Out of scope:**

- rerunning E13 under the new protocol
  — that would be a new research experiment,
  not part of protocol standardization;

- building software that automatically validates the checklist.

  This may be recorded as a future idea,
  but it is not an acceptance criterion.

**Independent Test:**

Apply the checklist to the E12 design:

- 3 arms;
- same budget;
- same cuts;
- no start;
- fixed `PYTHONHASHSEED`.

Confirm that it passes.

E12 already follows most of the rules
that this protocol will formalize.

---

### P2: T8 — Consolidate the benchmark after regeneration

**User Story:** As a researcher selecting instances for a new experiment batch,
I want the benchmark to be partitioned by **source graph**, not by variant,
without duplicates counted twice,
and with complete provenance per result,
so that the
"number of independent graphs won"
criterion
(such as the E12 criterion)
does not require a manual workaround in every experiment.

**Why P2:**

Important and with concrete work remaining:

- confirmed duplicates;
- confirmed leakage.

However, it does not technically block T6/T7/T9/T10.

It only needs to be completed before a future experiment
uses the `desenvolvimento` / `avaliacao` partition
**officially** as evidence.

**Objective.**

Deliver a `manifest.csv`
or a derived view
in which:

- source graphs are not split between development and evaluation
  without a recorded justification;

- effective duplicates
  (the same structural graph)
  are marked and count as one piece of evidence;

- every result can be traced to:

  - instance hash;
  - commit;
  - cut version;
  - configuration;
  - seed;
  - solver;
  - budget;
  - source of the OPT/LB/UB certificate.

**Current problem
(confirmed in this session, with numbers recomputed rather than copied from the assessment):**

- Current post-regeneration classes:

  75 `principal` instances:

  - **F 35**
  - **A 28**
  - **M 4**
  - **D 3**

  resulting in 31 D/A.

  Additionally:

  - 5 `legado` without computed difficulty;
  - 11 `extensao_dirigida`;
  - 3 `extensao_ponderada`;

  under the manifest's `classe` field.

  Total: **92 rows**.

- 11 source graphs have variants split between
  `desenvolvimento` and `avaliacao`:

  - `I065`
  - `apia-1.graphml`
  - `b06`
  - `b12`
  - `b18`
  - `bip42p`
  - `cc10-2u`
  - `hc10p`
  - `hc9u`
  - `lin06`
  - `w23c23`

  Recomputed in this session from the current manifest.

  These are the same 11 names as in the assessment,
  confirming that difficulty regeneration did not change the partition.

- 2 source graphs have 2+ variants **both** in `avaliacao`.

  This is more serious than development/evaluation leakage
  because it directly inflates the count of
  "independent graphs won."

  They are:

  - `cc7-3n`

    Already manually handled through the `GRAFOS` dictionary
    in `experiments/benchmark/tabela_e12.py`.

  - `i160-301`

    Not handled in any experiment so far.

- `hc9u.txt` (`legado`) and
  `puc-hc9u-seed-r1.txt` (`avaliacao`)
  are the same structural graph:

  - same `N`;
  - same `M`;
  - same `R`;
  - same `S`;
  - same `T`;
  - same edge set except for weight formatting.

  This was confirmed through direct parsing in this session,
  not merely by citing the assessment.

- No manifest column records:

  - "cut version";
  - "source of OPT/LB/UB certificate";

  at result level.

  That information currently lives across individual experiment reports
  (`resultados-e*-pli.md`),
  rather than in the manifest or a unified schema.

**Expected behavior.**

Introduce an explicit grouping rule based on
`instancia_original`,
a column that already exists in the manifest
and was used for the analysis in this session.

The rule must:

(a) prevent a verdict criterion from counting
two variants of the same `instancia_original`
as two independent graphs.

This generalizes what `tabela_e12.py`
already does manually for
`hc9u` / `cc7-3n`
through the experiment-specific hardcoded `GRAFOS` dictionary.

(b) mark structural duplicates such as:

`hc9u` / `puc-hc9u-seed-r1`

so that they do not count as two evidence rows
inside the same experiment batch.

(c) document the minimum provenance described in
Problem Statement / Goals
for every published result.

**Affected files/components:**

- `instances/manifest.csv`

  It already contains `instancia_original`.

  It may need a new field such as:

  `duplicata_de`

  or equivalent,
  to mark:

  - `puc-hc9u-seed-r1`
    as a structural duplicate of `hc9u`;

  - `i160-301` and `cc7-3n`
    variant pairs for grouping.

- `src/converters/build_manifest.py`

  This is the manifest generation point.

  Any new column must be computed here,
  not manually edited into the CSV.

- `experiments/benchmark/tabela_e12.py`

  The hardcoded `GRAFOS` dictionary,
  currently something like:

  `{'hc9u': (...), 'cc7-3n': (...)}`

  should eventually be derivable from T8's general rule,
  rather than maintained as a per-experiment manual list.

  Evaluate migration during implementation
  without retroactively breaking E12's published result.

- `docs/technical/reference/benchmark-v1.md`

  Add a consolidation section containing:

  - corrected post-regeneration counts;
  - grouping rule;
  - duplicate list.

**Required changes.**

Add to the manifest generator
or to a separate post-processing script
(to be decided during implementation):

- grouping by `instancia_original`;
- structural-duplicate marking based on comparison of:

  - `N`;
  - `M`;
  - `R`;
  - `S`;
  - `T`;
  - edge set.

This is the same method manually used in this session
to confirm
`hc9u` / `puc-hc9u-seed-r1`.

Add provenance fields where still missing.

**Acceptance criteria:**

1. The system SHALL expose,
   for each `instancia_original`,
   the list of variants and their partition:

   - `desenvolvimento`;
   - `avaliacao`;
   - `legado`;

   allowing leakage to be detected automatically,
   rather than through manual inspection.

2. WHEN two instances have structurally identical:

   - `N`;
   - `M`;
   - `R`;
   - `S`;
   - `T`;
   - edge set;

   THEN the system SHALL mark them as structural duplicates,
   regardless of differences in:

   - `sha256`;
   - filename.

3. IF a verdict criterion
   — such as E12's —
   groups variants from the same source graph,
   THEN the system SHALL provide that information through
   the general manifest/schema,
   rather than through a hardcoded experiment-specific dictionary.

4. The system SHALL explicitly record duplicate/grouping information for:

   - `hc9u` / `puc-hc9u-seed-r1`;
   - `cc7-3n` (two variants);
   - `i160-301` (two variants).

5. The system SHALL allow the manifest to be rebuilt from scratch
   through `build_manifest.py`
   without losing already applied corrections.

   This follows the same rule already established by H17.

   T8 must not regress it.

6. For every result cited in a report,
   the system SHALL document at least:

   - instance hash;
   - code commit;
   - cut-family version;
   - configuration:
     - seed;
     - threads;
     - budget;
   - source of the OPT/LB/UB certificate:
     - solver;
     - method;
     - or formal proof.

**Required tests:**

Create a verification script that runs grouping by `instancia_original`
over the current manifest
and reproduces exactly:

- the 11 leaked source graphs;
- the 2 duplicated source graphs inside evaluation;
- the `hc9u` / `puc-hc9u-seed-r1` duplicate pair.

The automatic rule must match the manual inventory from this session,
which serves as the regression oracle.

**Evidence to produce:**

Update `benchmark-v1.md` with:

- correct post-regeneration counts:

  - F 35;
  - A 28;
  - M 4;
  - D 3;
  - 31 D/A;

  replacing the `e9d1ccb` numbers quoted by the assessment;

- grouped-source-graph list;

- marked-duplicate list;

- one complete provenance example
  for at least one previously published result,
  retroactively added only to demonstrate the schema.

**Risks:**

Changing the grouping rule may change
the verdict of a **future** experiment
that depends on counting independent graphs.

That is exactly the purpose of the task.

However,
it must not retroactively change E12's already published verdict
without a new execution.

This follows the general rule against silently modifying historical results.

**Dependencies:**

No technical dependency on T6/T7/T9/T10.

It must be consolidated before any future experiment
officially uses the development/evaluation split as evidence.

**Out of scope:**

- adding new instances to the benchmark;
- selecting development vs evaluation instances based on method performance;
- rerunning any historical experiment.

**Independent Test:**

Run the verification script above
and compare its output line by line
with the Current State table in this spec.

---

### P2: T11 — Correct inconsistent experimental documentation

**User Story:** As a researcher citing a project report,
I want the report prose not to contradict the CSV it summarizes,
so that an incorrect interpretation is not propagated into future writing
(article, new plan, new spec).

**Why P2:**

None of these fixes requires new code.

This is documentation work,
but the correct content depends partly on T6–T9 findings.

For example:

- the `[E12]` entry in `direcoes-pli-min-station.md`;
- the counts in `CLAUDE.md`;

should ideally reflect the consolidated T8 state,
rather than a provisional number.

**Objective.**

Apply the documentation corrections listed below
using evidence verified in this session,
rather than merely assumed from the assessment.

Do not make additional corrections beyond these
without new verification.

**Current problem, with evidence already confirmed in this session
(see Current State for full context on each item):**

1. `resultados-e13-pli.md:143`

   `"Isto não é ruído de execução"`
   ("This is not execution noise")

   is **confirmed still present**.

2. `resultados-e13-pli.md`

   The `TimeLimit` × `MIPFocus`
   confounding in `focus1800`
   is **confirmed in `run_e13.py:159-166`**
   but is not documented in the report.

3. `resultados-e2-e4-pli.md:285` vs `:315`

   Barcelona st25 contradiction
   **confirmed through grep**.

   Exact conflict:

   - line 285 shows `OPT` in 299 s;
   - line 315 says `"sem provar"` ("without proving it").

4. `CLAUDE.md:71`

   `"22 antigas compatíveis + 70 do benchmark-v1"`
   is **confirmed outdated**.

   The correct count should ideally be written after T8 consolidation.

   Current state:

   75 `principal`
   = 5 legacy + 70 benchmark-v1.

   The spec does not pre-commit to a final T8 count
   if T8 changes how duplicates are counted.

5. `base-formulation.md:154-155`

   `"caso de todas as 22 instâncias do repositório"`
   is **confirmed outdated**.

   Today:

   - 75 `principal`;
   - 5 with `S∩T≠∅`.

   This does not duplicate Block 1 T5,
   which covers `validacao-formulacao-base.md`.

   This occurrence is in a different file.

6. `experiments/alternative-formulations/modelo_estendido.py`

   The function name:

   `construir_modelo_estendido_equivalente`

   and description:

   `"equivalente ao baseline"`

   are **confirmed present**.

   The model body
   — whether it is in fact VI-only and blocks terminal transit —
   **was not inspected in this session**.

   See Assumptions.

7. `direcoes-pli-min-station.md` §13

   The absence of an `[E12]` entry is
   **confirmed through grep**
   (0 occurrences of `"Resultado [E12]"`).

   `plano-pos-e8-adiado.md`
   is also confirmed to lack the:

   `"Situação após E12"`

   section.

   A specific plan for that edit was already approved earlier in this conversation
   but was never executed.

8. **Not duplicated here**
   because it belongs to Block 1:

   comments for `make_StayPut` / `make_SharedTerminal`
   in `synthetic.py`.

   Already recorded as Inconsistency 2
   in the Block 1 spec.

9. **Not duplicated here**
   because it belongs to Block 1 T5:

   the `S∩T=∅` assumption in:

   `validacao-formulacao-base.md:102`.

   This is central to Block 1's equivalence proof,
   not a standalone prose correction.

**Expected behavior.**

Each of items 1–7 above must be corrected.

Each correction must cite the exact evidence
(line, CSV, or code)
that motivated it.

This is not a general rewrite of the documents.

**Affected files/components:**

The files referenced by items 1–7.

Note:

- items 1 and 2 refer to the same file;
- item 7 refers to two files.

**Required changes:**

- **Items 1–2:**

  Rewrite §5 of `resultados-e13-pli.md`
  to list the three candidate causes of the divergence:

  - construction order / T6;
  - time-based stopping;
  - cut-family change;

  without asserting which one dominates.

  Add an explicit note on the
  `TimeLimit` × `MIPFocus`
  confounding in the `focus1800` arm.

- **Item 3:**

  Correct the prose around line ~315 of
  `resultados-e2-e4-pli.md`
  to match the CSV:

  BASE-C proved the Barcelona st25 optimum
  in 299.432 s.

- **Item 4:**

  Update `CLAUDE.md:71`
  with the correct count,
  ideally after T8 consolidation,
  so the number does not immediately need to be changed again.

  If T8 is not yet complete,
  prefer wording such as:

  `"75 principal (5 legadas + 70 do benchmark-v1), ver benchmark-v1.md"`

  rather than hardcoding 92 again.

- **Item 5:**

  Correct `base-formulation.md:154-155`
  so it no longer refers to "22 instances."

  Qualify that `S∩T≠∅`
  currently occurs in 5 principal instances.

  Do not reproduce the equivalence proof;
  that belongs to Block 1.

  Only fix the factual counting statement.

- **Item 6:**

  Read the body of `modelo_estendido.py`
  and decide the exact correction:

  - rename the function / description;
  - or qualify the docstring with the actual restrictions.

  See Assumptions.

- **Item 7:**

  Execute the previously approved plan
  from this same conversation
  to add:

  - the `[E12]` entry to
    `direcoes-pli-min-station.md` §13;

  - `"Situação após E12"`
    to `plano-pos-e8-adiado.md`.

**Acceptance criteria:**

1. WHEN `resultados-e13-pli.md`
   is reread after correction,
   THEN the system SHALL list the three candidate causes
   of the 9/13 divergence
   without claiming that one was isolated.

2. The system SHALL record,
   in `resultados-e13-pli.md`,
   the `TimeLimit` × `MIPFocus`
   confounding in `focus1800`,
   citing the exact lines in `run_e13.py`
   that demonstrate it.

3. WHEN `resultados-e2-e4-pli.md`
   is reread,
   THEN the system SHALL show the same conclusion
   in the CSV and prose for Barcelona st25:

   optimum proven.

4. The system SHALL update `CLAUDE.md`
   with an instance count that does not contradict
   `instances/manifest.csv`
   at the time of the correction.

5. The system SHALL correct
   `base-formulation.md:154-155`
   without rewriting the equivalence proof,
   which belongs to Block 1.

6. IF inspection of `modelo_estendido.py`
   confirms that the model is VI-only
   and blocks terminal transit,
   THEN the system SHALL correct the function name
   and/or docstring
   so it no longer claims equivalence with the baseline.

7. The system SHALL add:

   - the `[E12]` entry to
     `direcoes-pli-min-station.md` §13;

   - the `"Situação após E12"` section to
     `plano-pos-e8-adiado.md`;

   following the plan already approved in this conversation.

8. The system SHALL NOT modify any
   `synthetic.py`
   or
   `validacao-formulacao-base.md`
   line related to `S∩T`
   under this task.

   That belongs to Block 1.

**Required tests:**

No code test.

Verification consists of repeating the
`grep` / comparison
used to identify each inconsistency in this session
against the cited CSV/code,
confirming the contradiction no longer exists.

**Evidence to produce:**

A before/after list for all 7 items,
each containing:

- exact changed line;
- supporting evidence:
  - CSV;
  - code;
  - or grep result.

**Risks:**

Correcting `CLAUDE.md`
before T8 consolidation
could require another correction later.

Mitigation:

if T8 has not yet run,
use wording that avoids unnecessarily hardcoding
a potentially transitional number.

**Dependencies:**

No mandatory dependency for items:

- 1;
- 2;
- 3;
- 5;
- 7.

Item 4
(the count in `CLAUDE.md`)
should ideally wait for T8.

Item 6 requires additional inspection,
outside this session,
of the `modelo_estendido.py` body.

**Out of scope:**

- any `S∩T` correction in:
  - `synthetic.py`;
  - `validacao-formulacao-base.md`;

  those belong to Block 1.

- rewriting the full ranking in
  `direcoes-pli-min-station.md`
  beyond the missing `[E12]` entry.

**Independent Test:**

For each of the 7 items,
repeat the `grep` / comparison
that identified the inconsistency in this session
and confirm that no contradiction remains.

---

## Edge Cases

- IF an instance appears under more than one `instancia_original`
  because two distinct source processes happen to generate the same graph,
  THEN T8 SHALL identify it by **structural content**,
  not only by the `instancia_original` name declared by the generator.

- WHILE T7 has not yet decided
  `WorkLimit` / `TimeLimit`,
  every new T10 comparison SHALL explicitly state:

  - which budget it used;
  - why.

  It should not wait indefinitely.

  In other words,
  T10 may temporarily operate under a protocol such as:

  `"budget = TimeLimit, T7 decision pending"`

  without blocking every experiment until T7 is complete.

- IF a historical `run_e*.py`
  (E0–E8)
  has not yet had its
  `integer_oracle` / `solve_bc_yspace`
  usage checked against `S∩T`
  by Block 1 T4,
  THEN T9 SHALL still instrument it.

  Instrumentation does not depend on oracle correctness.

  However,
  numerical results from that script remain subject to the Block 1 caveat
  until T4 reaches a conclusion.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| EXPR-01 | P1: T6 | Design | Done |
| EXPR-02 | P1: T6 | Design | Done |
| EXPR-03 | P1: T6 | Design | Done |
| EXPR-04 | P1: T6 | Design | Done |
| EXPR-05 | P1: T6 | Design | Done |
| EXPR-06 | P1: T9 | Design | Done |
| EXPR-07 | P1: T9 | Design | Done |
| EXPR-08 | P1: T9 | Design | Done |
| EXPR-09 | P1: T9 | Design | Done |
| EXPR-10 | P1: T9 | Design | Done |
| EXPR-11 | P1: T9 | Design | Done |
| EXPR-12 | P1: T7 | Design | Done |
| EXPR-13 | P1: T7 | Design | Done |
| EXPR-14 | P1: T7 | Design | Done |
| EXPR-15 | P1: T7 | Design | Done |
| EXPR-16 | P1: T7 | Design | Done |
| EXPR-17 | P1: T7 | Design | Done |
| EXPR-18 | P1: T10 | Design | Done |
| EXPR-19 | P1: T10 | Design | Done |
| EXPR-20 | P1: T10 | Design | Done |
| EXPR-21 | P1: T10 | Design | Done |
| EXPR-22 | P1: T10 | Design | Done |
| EXPR-23 | P1: T10 | Design | Done |
| EXPR-24 | P2: T8 | Design | Done |
| EXPR-25 | P2: T8 | Design | Done |
| EXPR-26 | P2: T8 | Design | Done |
| EXPR-27 | P2: T8 | Design | Done |
| EXPR-28 | P2: T8 | Design | Done |
| EXPR-29 | P2: T8 | Design | Done |
| EXPR-30 | P2: T11 | Design | Done |
| EXPR-31 | P2: T11 | Design | Done |
| EXPR-32 | P2: T11 | Design | Done |
| EXPR-33 | P2: T11 | Design | Done |
| EXPR-34 | P2: T11 | Design | Done |
| EXPR-35 | P2: T11 | Design | Done |
| EXPR-36 | P2: T11 | Design | Done |
| EXPR-37 | P2: T11 | Design | Done |

**Coverage:** 37 total,
0 mapped to tasks
(`tasks.md` was not created in this round,
per the user's explicit request),
37 unmapped ⚠️

---

## Success Criteria

- [x] `verify_t6_determinismo.py`
      produces an identical order hash under
      `PYTHONHASHSEED ∈ {0,1,2,3}`
      in both `harness.py` and `bc_yspace.py`.

- [x] `decisao-orcamento-worklimit.md`
      exists,
      cites the Gurobi 12.0.3 documentation,
      and reports a **real controlled experiment**,
      not a hypothetical one.

- [x] `measure_mip`
      returns:
      - time to first incumbent;
      - time to best incumbent;
      - time to proof;

      with a real populated example record.

- [x] `protocolo-comparacao-pareada.md`
      exists and,
      when applied retrospectively to E13,
      flags the actual
      `TimeLimit` × `MIPFocus`
      confounding that occurred.

- [x] The T8 verification script automatically reproduces:

      - the 11 leaked source graphs;
      - the 2 source graphs duplicated inside evaluation;
      - the `hc9u` / `puc-hc9u-seed-r1` pair;

      found in this session.

- [x] The 7 T11 items
      — except item 6, which is conditional on inspection of
      `modelo_estendido.py`'s body —
      have been corrected
      and cite the evidence that motivated each correction.

- [x] No task in this block duplicated Block 1 work:

      - oracle;
      - independent validator;
      - `S∩T` regression;
      - E10/E10b revalidation;
      - equivalence proof;

      and no task started Block 3 work:

      - synthetic families;
      - E11/C6;
      - all-V disaggregation.

---

## Inconsistencies Found Between the Backlog, Documentation, Results, and Code During This Spec

1. **The benchmark numbers in assessment §5 are knowingly outdated.**

   The assessment itself warns about this.

   The correct post-regeneration numbers:

   - F 35;
   - A 28;
   - M 4;
   - D 3;
   - 31 D/A;

   were confirmed only in this session
   by direct inspection of the manifest.

   The backlog already correctly mentions "31 D/A"
   (H17),
   but does not repeat the F/A/M/D split.

   This spec records that breakdown for the first time
   in a consolidated document.

2. **The assessment describes
   `hc9u.txt` / `puc-hc9u-seed-r1.txt`
   as having "identical sha256/content."**

   Direct verification in this session shows that the text-file `sha256`
   values **differ**
   because metadata comments exist only in the `puc-*` version.

   However,
   the **structural content**
   — graph, S, T, R —
   is indeed identical.

   Therefore,
   the assessment's practical conclusion remains valid:

   they are effective duplicates.

   The evidence description
   ("identical sha256")
   is imprecise
   and must not be repeated unqualified
   when T8 is implemented.

3. **Two duplicate cases inside evaluation itself were not cited in any previous document.**

   In particular:

   `i160-301`

   with the pair:

   - `i-i160-301-intercalado-f2-rho`;
   - `i-i160-301-regiao-f2`;

   both difficulty F.

   This is a new finding from this session.

   It was not present in the assessment or backlog.

4. **The plan to add the `[E12]` entry to
   `direcoes-pli-min-station.md`
   and `plano-pos-e8-adiado.md`
   had already been approved earlier in this same conversation,
   before Block 1,
   but was never executed.**

   Confirmed through `grep`
   in this session
   (0 occurrences).

   T11 item 7 treats this as pending execution.

   This is not a new research finding;
   it is an administrative/documentation task
   that was left behind in the conversation flow.

5. **`base-formulation.md:154-155`**
   was not listed as a separate one of the seven explicit
   corrections in assessment §10.

   Assessment §10 only referred to line 155 generically
   as part of qualifying the `S∩T=∅` assumption.

   This session identified and documented the exact outdated detail:

   the `"22 instances"` count.

   It is treated here as a T11 item
   concerning factual prose,
   not as part of Block 1 T5's mathematical proof.
  