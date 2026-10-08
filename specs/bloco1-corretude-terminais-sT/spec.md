# Block 1 — Correctness (MIN-STATION) Specification

Scope: T1–T5 from `docs/technical/plans/historico/backlog-continuacao.md`, with scientific basis in
`docs/technical/reference/documentacao-projeto/MIN-STATION-parecer-macro-consolidado.md` (§2, §9) and
`docs/technical/reference/validacao-e-correcoes/validacao-formulacao-base.md` (§5.4, Appendix A.9–A.10). No
tasks from Blocks 2–4 (experimental reliability, synthetic families/new formulations,
scientific positioning) are included in this spec.

---

## Current State

Established through code inspection and direct execution in this session (not from memory of the assessment).

This section distinguishes what is proven correct, proven incorrect, hypothesized, and still to be verified.

### Proven correct (execution confirmed in this session)

- **Base model (`construir_modelo_baseline`, `baseline.py`)** implements variant U (unified balance)
  and is treated as the ground truth throughout this spec: no task here modifies
  `baseline.py`.

- **`is_valid_cut` (`experiments/cuts/cuts.py:550`)** — cut validator based on bipartite
  reachability + matching, independent of the aggregate flow network. It treats
  `v ∈ S∩T` as "trivially reaches itself" (the comment cites Das's Lemma 5).
  Executed in this session through `experiments/cuts/verify_e5_validador.py`:
  **0 divergences in 88 tests** against the base model solved with Gurobi, over the
  5 existing fixtures (`Direct0`, `TermRelay`, `Tri`, `StayPut`, `SharedTerminal`),
  including the two with `S∩T ≠ ∅`.

- **`make_StayPut` and `make_SharedTerminal` (`synthetic.py`)** reproduce OPT=0 and OPT=1,
  respectively, through `is_valid_cut`. However, `make_StayPut` **does not** exercise
  staying in place itself: with `S=T={a,b}` and edge `a–b`, feasibility of `C=∅`
  is achieved through a **swap** (the robot at `a` moves to `b` and vice versa),
  not through literal staying in place — confirmed in this session (see next section).

### Proven incorrect (execution confirmed in this session)

- **`integer_oracle` (`cuts.py:642`) and `_build_flow_net_aggregate` (`cuts.py:355`,
  used by `separate_classical_fracs`) report infeasibility for isolated pure staying-in-place cases.**
  Minimal case:
  `S=T={v}`, `v` with no edges, `m=1`, `C=∅`.
  Expected: feasible, OPT=0 (Das's Lemma 5; no movement is required).
  Direct execution in this session:

  - `integer_oracle(S=['v'], T=['v'], N_plus={}, C=[])`
    → `(False, frozenset())`.

  - `separate_classical_fracs` on the same isolated pure-stay instance with
    `y_v=0` and `y_v=1`
    → both raise `InstanciaInviavel`
    ("instance infeasible even with y ≡ 1"), meaning the network declares the instance
    always infeasible, even with stations on every vertex in `V`.

  - The same defect appears with two independent isolated vertices
    (`S=T={v1,v2}`, `m=2`).

  - `make_StayPut` **does not** capture this defect because edge `a–b` allows a swap
    that masks the lack of a stay arc — confirmed by executing `integer_oracle`
    on that fixture (`feasible=True`, but because of the swap, not staying in place).

- **Root cause identified:** the aggregate network splits every vertex into
  `v_in`/`v_out` and connects the vertex as an origin to `v_out`
  (`σ→v_out`, cap. 1) and as a destination from `v_in`
  (`v_in→τ`, cap. 1), but only connects `v_in` to `v_out` through the
  station-gated transit arc (`cap = (m-1)·y_v` or `m·y_v`).
  For `v ∈ S∩T` with `y_v=0`, there is no path from `v_out` to `v_in`,
  therefore no path from `σ` to `τ` that uses only the unit corresponding to `v`
  itself — even though physically the robot does not need to move.

### Hypothesis (verified on small cases in this session, not a proof)

- **Candidate fix:** add an unconditional `v_out → v_in` arc of capacity 1,
  independent of `y_v`, for every `v ∈ S∩T`, in both functions
  (`_build_flow_net_aggregate` and `integer_oracle`).

  Tested in this session by exhaustive enumeration of **every** `C ⊆ V`
  (not only singleton/pair subsets) against the Gurobi base model, over the
  6 fixtures in `synthetic.py`
  (`Direct0`, `TermRelay`, `Tri`, `StayPut`, `SharedTerminal`, `TermRelayForced`)
  plus the two isolated pure-stay cases above:
  **618 tests, 0 divergences**.

  This is evidence from small cases, not a proof — see T1 for what remains:
  proof that the arc preserves the intended capacity semantics at all other
  vertices, and broader regression coverage through T2/T3.

- The same fix should apply to `_build_flow_net_aggregate`, since its construction
  is structurally identical to `integer_oracle` at this point
  (confirmed by code inspection; it did not receive a separate round of testing
  beyond the `separate_classical_fracs` case mentioned above).

### To be verified (outside the scope of this reading session)

- Whether `solve_cbi`/`solve_bc_yspace` (`bc_yspace.py`) produced, in any historical
  recorded execution, a spurious infeasibility decision due to this defect.
  This depends on which experiments ran on instances with `S∩T ≠ ∅` (T4).

- Whether the equivalence proof (`validacao-formulacao-base.md` §9) is complete
  for variant U as currently implemented, or only for the textual "(B)" version.
  Section A.10 of that document already lists 6 pending formal gaps (T5).

- Whether there are other calls to `integer_oracle` /
  `_build_flow_net_aggregate` in the repository beyond `bc_yspace.py`
  and `yspace.py`. A complete inventory is part of T4, not this reading.

---

## Problem Statement

The base formulation (`baseline.py`, variant U) has been treated as correctly adjusted
for `S∩T ≠ ∅` since the E5 round (Das's Lemma 5: a robot may remain at its own vertex
when that vertex is also a target of another robot).

However, two other components used by the project to reason about the same problem —
the aggregate-flow feasibility oracle (`integer_oracle`, used by
`solve_cbi`/`solve_bc_yspace`) and the classical fractional cut separator
(`separate_classical_fracs`, used by `solve_lp_cutting_plane` /
`solve_ip_yspace`) — do not represent this staying-in-place behavior and report
spurious infeasibility (or, worse, raise `InstanciaInviavel` even with `y ≡ 1`)
on pure-stay instances.

There is currently no second feasibility-verification mechanism structurally
independent from these two functions.

The only existing independent comparison, `is_valid_cut` vs. Gurobi, checks
cut validity rather than feasibility of an arbitrary `C`, and it does not expose
the discovered defect because `is_valid_cut` is already correct.

Without these two repairs and without permanent regression coverage:

(a) any method that calls the oracle on an instance with `S∩T ≠ ∅` — including CBI,
line A2 — risks an incorrect false-negative decision; and

(b) the formal equivalence proof (`validacao-formulacao-base.md` §5–9) remains
incomplete, with documented gaps (§A.10) that no previous task has closed.

---

## Goals

- [x] The feasibility oracle (`integer_oracle`) and fractional-separation network
      (`_build_flow_net_aggregate`) no longer produce false negatives on instances
      involving staying in place in `S∩T`, verified through exhaustive enumeration
      on the existing fixtures plus the new pure-stay cases.

- [x] A second feasibility-verification mechanism exists and is algorithmically
      independent (`(v, battery)` states + matching), used to validate the corrected
      oracle and to compute OPT by enumeration on small instances.

- [x] A permanent regression suite exists (following the `verify_*.py` pattern
      already used in the project), comparing the base model, oracle, fractional
      separation, cut validation, and independent validator on all known terminal
      cases, and fails automatically if any divergence occurs.

- [x] For every historical experiment that used the oracle
      (`solve_cbi` / `solve_bc_yspace` / `solve_lp_cutting_plane` /
      `solve_ip_yspace`), it is documented whether it ran on an instance with
      `S∩T ≠ ∅` and, if so, whether the result is still valid, must be rerun,
      or should be marked obsolete.

- [x] The equivalence proof for the base formulation explicitly covers `S∩T`,
      staying in place, and zero optimum, closing the 6 gaps already listed in
      `validacao-formulacao-base.md` §A.10.

---

## Out of Scope

Explicitly excluded from this spec. See `backlog-continuacao.md` for the corresponding task.

| Item | Reason |
|---|---|
| Deterministic model construction (`set`/`frozenset` in `harness.py`, `bc_yspace.py`) | Block 2, T6 — this is an experimental-reproducibility issue, not correctness |
| `WorkLimit` vs. `TimeLimit`, `NodeCount`/incumbent-time instrumentation | Block 2, T7/T9 |
| Benchmark consolidation (partition by source graph, provenance) | Block 2, T8 |
| Structural synthetic families BP/HB/SC/TR | Block 3, T12–T17/T19–T21 |
| Disaggregated all-V formulation | Block 3, T18 |
| Mapping against the IJCAI 2026 paper | Block 4, T22 |
| Solver parameter tuning (`MIPFocus`, `Cutoff`, `Symmetry`, etc.) | Explicitly requested by the user as out of scope |
| Removing support for `S∩T` or restricting stations to intermediate vertices | Prohibited by `CLAUDE.md` and by the rule not to reintroduce the old assumption |
| Modifying `baseline.py` / the base formulation to match the oracle | The base model is considered unaffected by the defect (see Current State); only modify it if T4 finds concrete contrary evidence |
| Rerunning E9, E13, E14 (without `-rho`, without `S∩T`) | Outside the scope of the defect — T4 only concerns experiments that actually called the oracle on `S∩T ≠ ∅` |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Where the formal proof (T5) is written | Complete the gaps directly in `validacao-formulacao-base.md` §5–9 and Appendix A (do not create a new document) | The document already contains the corrected formulation (§9) and the explicit list of missing pieces (§A.10); a separate document would duplicate context and risk divergence between two texts describing the same model | n |
| Regression-suite format (T3) | `verify_*.py` scripts following the existing pattern (`verify_e5_validador.py`, `verify_e8_oracle.py`), not `pytest` | There is no `pytest` setup or test framework configured in the repository (`pyproject.toml` does not list `pytest`); all existing project regressions follow this pattern | n |
| Scope of brute-force OPT enumeration (T2/T3) | Connected graphs with `n ≤ 5`, `r ∈ {1,2,3}`, `m ≤ 3`, including `S∩T ≠ ∅` | Protocol already defined in `validacao-formulacao-base.md`, section "Recommended verification (not executed)" — not a new choice introduced by this spec, but adoption of an existing project plan | n |
| Granularity of this spec (Specify only, without formal `design.md`/`tasks.md`) | Each user story (T1–T5) contains objective, affected files, required changes, risks, and dependencies directly inside `spec.md` | Explicit user request ("create only the spec... do not implement yet"); the requested technical detail is incorporated directly into each story instead of a separate `design.md` | n |
| Threshold for "affected result" in T4 | An experiment is a review candidate iff (a) it used `solve_cbi`, `solve_bc_yspace`, `solve_lp_cutting_plane`, or `solve_ip_yspace`, **and** (b) it ran on at least one instance with `S∩T ≠ ∅` in the manifest (`rho_S_inter_T` in `manifest.csv`) | Same criterion E12 already used to declare itself outside the risk set (it checked that `S∩T` was empty in its own CSV); this generalizes that rule to the other experiments | n |

**Open questions:** none — all have either been resolved or explicitly recorded above.

---

## User Stories

### P1: T1 — Fix the oracle to support staying in place in `S∩T` ⭐ MVP

**User Story**: As a researcher validating methods on instances with `S∩T ≠ ∅`, I want
`integer_oracle` and `_build_flow_net_aggregate` to report feasibility correctly
when a robot remains at its own vertex, so that no method depending on the oracle
(CBI, fractional separation) discards a feasible solution through a false negative.

**Why P1**: Blocks T3, T4, and any future use of the oracle on overlapping instances;
it is the only item with a defect already confirmed by execution (see Current State).

**Objective.** Make `integer_oracle` and `_build_flow_net_aggregate` agree with the base
model (`construir_modelo_baseline`) on every instance with `S∩T ≠ ∅`, without changing
behavior on `S∩T = ∅`.

**Current problem.** Neither function connects `v_out` to `v_in` for `v ∈ S∩T`
outside the transit arc gated by `y_v`. A robot already at its own target is forced
to "leave" through a real graph edge, or the network declares infeasibility.
Confirmed by execution: see Current State, "Proven incorrect".

**Expected behavior.** For `v ∈ S∩T`, there is a
`σ → v_out → v_in → τ` path of capacity 1, independent of `y_v`
(staying in place never requires a station — Das's Lemma 5, and `CE1'`/`Q1`
already establish that this case cannot be preprocessed by removing the vertex).
For `v ∉ S∩T`, no new arc is created.

**Affected files/components:**

- `experiments/cuts/cuts.py` —
  `_build_flow_net_aggregate` (around line 355) and
  `integer_oracle` (around line 642); both construct the network in a structurally
  identical way at this point and require the same new arc.

- Indirect consumers, with no direct modification expected but inheriting the fix:

  - `experiments/cuts/bc_yspace.py`
    (`solve_bc_yspace`, `solve_cbi` — call `integer_oracle` and
    `separate_classical_fracs`);

  - `experiments/cuts/yspace.py`
    (`solve_lp_cutting_plane`, `solve_ip_yspace` — call
    `separate_classical_fracs`).

**Required changes.** Candidate already tested on small cases (see Current State):
for every `v ∈ S∩T` identified during network construction, add

`arc(f'{v}_out', f'{v}_in', 1.0)`

unconditionally (outside the `if v in C_set` / outside the `y_v` factor),
in both functions.

Do not modify the existing `σ→v_out`, `v_in→τ`, or `v_in→v_out`
transit arcs.

**Acceptance criteria** (each line follows an EARS-style requirement):

1. WHEN `integer_oracle` receives `S=T={v}`, with `v` having no edges,
   `m=1`, and `C=∅`, THEN the system SHALL return `viavel=True`.

2. WHEN `separate_classical_fracs` receives the same isolated pure-stay instance
   with `y_v=0` or `y_v=1`, THEN the system SHALL return without raising
   `InstanciaInviavel`.

3. WHILE `v ∉ S∩T`, the system SHALL keep the flow graph identical to the
   pre-fix version, with no new arc incident to `v`.

4. The system SHALL agree with `construir_modelo_baseline`
   (solved with Gurobi, `y` fixed by `C`) for every `C ⊆ V` in each of the
   6 fixtures from `synthetic.py`
   (`Direct0`, `TermRelay`, `Tri`, `StayPut`, `SharedTerminal`,
   `TermRelayForced`).

5. IF an instance with `S∩T ≠ ∅` was already correctly classified before the fix
   (for example `SharedTerminal`, through swapping), THEN the system SHALL preserve
   that result without regression.

6. The system SHALL produce the same `Z` (combinatorial cut) as before the fix on
   every instance whose feasibility result did not change — the correction is local
   to staying in place, not to `Z` extraction.

**Required tests:** new
`experiments/cuts/verify_t1_oracle_sT.py`, following the pattern of
`verify_e8_oracle.py`:

- exhaustive enumeration of `C ⊆ V` on the 6 fixtures;
- plus 2 new pure-stay cases (one isolated vertex and two isolated vertices);
- compare `integer_oracle` and `separate_classical_fracs` against
  `construir_modelo_baseline` solved with Gurobi.

This is the same script used to generate the Current State evidence above,
promoted to a permanent regression.

**Evidence to produce:** before/after table
(defect reproduced → corrected), divergence count by fixture, fix diff,
and test-script output.

**Risks:** capacity 1 on the new arc could, in principle, interact with `Z`
extraction (`_extract_Z`) if a vertex in `S∩T` appears on the source side of the
minimum cut through a path using the new arc.

This was not observed in the 618 tests run in this session, but the T1 suite
must cover it explicitly before the task is considered complete.

**Dependencies:** no incoming dependency. Blocks T2 partially
(the `C` enumeration uses the same type of small instance), T3, and T4.

**Out of scope:** modifying `baseline.py`; changing `Z` extraction beyond what is
strictly required to accommodate the new arc; any `r > 1` instance in this item
(the regression cases use `r=1`, which is sufficient to expose and fix the defect —
`r>1` is covered by the broader T3 suite).

**Independent Test:** run `verify_t1_oracle_sT.py` in isolation and obtain
0 divergences.

---

### P1: T2 — Implement an independent feasibility validator

**User Story**: As a researcher who must trust the corrected oracle, I want a second
feasibility-verification mechanism that does not reuse the flow construction from
`integer_oracle`, so that future errors in the oracle (or in the T1 correction)
can be detected by a structurally different reference mechanism.

**Why P1**: This is the only truly independent validation mechanism planned for
`S∩T`. Without it, T1 is only checked against the PLI base model (Gurobi), which is
another formulation of the same underlying idea rather than a different mechanism.
`validacao-formulacao-base.md` already records this validator as
"recommended verification (not executed)."

**Objective.** Build a feasibility checker for a given `C ⊆ V`, based on explicit
`(vertex, battery)` states and bipartite matching between origins and destinations,
without constructing or calling the
`integer_oracle` / `_build_flow_net_aggregate` network.

**Current problem.** No such component exists in the repository.
A search through `experiments/cuts/*.py` finds no `(v, battery)` state structure.

The only independent comparison today
(`is_valid_cut` vs. Gurobi in `verify_e5_validador.py`)
checks cut validity through reachability in `A_r`, which uses the same abstraction
"one hop = one edge of `A_r`" as the oracle.

Therefore, it does not independently re-derive battery semantics from the original
graph and unit-length edges and cannot serve as a validation that `A_r` itself
is correct.

**Expected behavior.** Given `(G, S, T, r, C)`, the validator decides feasibility
by exploring `(v, remaining battery)` states from each origin.

Battery resets to `r` whenever the current vertex has a station
(i.e. `v ∈ C`).

The exploration produces the set of destinations reachable from each origin
without constructing `A_r` as a precomputed distance graph.

Global feasibility is then decided by maximum bipartite matching between
origins and reachable destinations.

**Affected files/components:**

- New module, for example
  `experiments/cuts/independent_validator.py`
  (final name to be decided during implementation; there is no existing naming
  convention to follow, except that it should not live in `cuts.py`, to avoid
  sharing implementation with the oracle).

- No existing file needs to be modified for this item in isolation.

**Required changes.** Implement:

1. State-space search over `(v, battery)` for each origin
   (BFS/DFS over the original graph `G`, not over `A_r`), with:

   - battery decremented by one per traversed edge;
   - battery reset to `r` when entering a vertex in `C`;
   - explicit treatment of the case where the origin itself is in `S∩T`
     (staying in place; battery is irrelevant for the zero-length stay).

2. For each origin, compute the set of destinations reachable with
   battery `≥ 0` in at least one state.

3. Compute maximum bipartite matching
   (Hopcroft–Karp or a simple max-flow implementation, but implemented separately
   from `cuts.py`) between origins and the reachable destination set of each origin.

   The instance is feasible iff the matching covers every origin.

4. Add brute-force enumeration of `C` to obtain OPT on small instances,
   reusing the feasibility check above for each candidate.

**Acceptance criteria:**

1. The system SHALL decide feasibility without calling
   `integer_oracle`, `_build_flow_net_aggregate`, or `_edmonds_karp`
   from `cuts.py`.

2. The system SHALL represent battery explicitly in the state, decrementing it
   on each traversed edge and resetting it to `r` when entering a vertex in `C`.

3. WHEN an origin `s` is also a destination (`s ∈ S∩T`), THEN the system SHALL
   consider `s` reachable from itself at zero cost, independently of whether
   `s ∈ C`.

4. WHEN the validator receives a `C` and an instance, THEN the system SHALL return
   the same feasibility verdict as `construir_modelo_baseline` solved with Gurobi
   for every connected graph with:

   - `n ≤ 5`;
   - `r ∈ {1,2,3}`;
   - `m ≤ 3`;
   - including `S∩T ≠ ∅`;

   following the protocol in
   `validacao-formulacao-base.md`, "Recommended verification".

5. WHEN OPT is requested for a small instance, THEN the system SHALL enumerate
   `C` by brute force and return the minimum feasible `|C|`, agreeing with the
   OPT obtained by `construir_modelo_baseline`.

6. The system SHALL agree with the corrected oracle (post-T1) on all 6 fixtures
   from `synthetic.py` plus the new cases from T1.

**Required tests:**
`experiments/cuts/verify_t2_validador_independente.py`

The script generates all connected graphs with `n ≤ 5`
(labeled graphs; deduplication by isomorphism is not required because redundancy
does not invalidate the test), for:

- `r ∈ {1,2,3}`;
- combinations of `S`,`T`;
- `m ≤ 3`;
- including `S∩T ≠ ∅`;

and compares:

independent validator × Gurobi × corrected oracle.

**Evidence to produce:**

- number of enumerated instances;
- 0 divergences;
- total execution time of the enumeration, to document whether the `n ≤ 5`
  protocol is practically tractable, since `validacao-formulacao-base.md`
  currently marks this verification as "not executed."

**Risks:** the combinatorial explosion of labeled connected graphs with `n=5`
may be large enough to require isomorphism reduction or sampling.

This should first be measured during implementation; record the actual number
of cases and runtime as part of the evidence.

**Dependencies:** no direct incoming dependency on T1 because the validator is
implemented independently, but acceptance criterion 6 can only close after
T1 is complete.

Blocks T3, which uses the validator as one of the five comparison mechanisms.

**Out of scope:** optimizing the validator for large instances
(it exists for correctness checking on small cases, not to replace the production
oracle); weighted graphs or directed graphs
(outside Das's original problem, see `CLAUDE.md`).

**Independent Test:** run the validator alone on `make_SharedTerminal()` and verify
`OPT=1`, and on the isolated pure-stay instance and verify `OPT=0`.

---

### P1: T3 — Create a terminal-correctness regression suite

**User Story**: As a researcher who will propose new cuts, formulations, or methods
involving `S∩T`, I want a permanent regression suite comparing every correctness
mechanism in the project on the same terminal cases, so that future regressions
are detected automatically rather than discovered manually, as happened with T1.

**Why P1**: This formally closes T1+T2. Without it, both fixes remain validated
only by ad-hoc scripts from this session rather than by a permanent repository
guarantee.

**Objective.** Consolidate the terminal cases already identified
(in this session and in the macro assessment) into a single regression script
that runs the five mechanisms:

- base model;
- oracle;
- fractional separation;
- `is_valid_cut`;
- independent validator;

over the same set of cases, and exits with a non-zero code if any pair diverges.

**Current problem.** The cases are scattered across the repository.

Fixtures exist in `synthetic.py`:

- `StayPut`;
- `SharedTerminal`;
- `TermRelay`;
- `TermRelayForced`;
- `Direct0`.

However, `make_StayPut` does not cover isolated pure staying in place
(see Current State), and no script runs all five mechanisms together.

`verify_e5_validador.py` only covers `is_valid_cut` vs. Gurobi.

**Expected behavior.** A single script, or a small cohesive set of
`verify_t3_*.py` scripts, that:

(a) defines the mandatory cases listed below;

(b) runs all five correctness mechanisms on each case;

(c) prints divergences with the case name and the pair of mechanisms involved;

(d) exits with a non-zero code if any divergence occurs.

**Affected files/components:**

- `experiments/cuts/synthetic.py`
  — add the missing isolated pure-stay fixture
  (suggested name: `make_StayPutIsolado`,
  with no edge, so that a swap cannot mask the defect as in `make_StayPut`).

- New:
  `experiments/cuts/verify_t3_regressao_terminais.py`
  or an equivalent cohesive set of scripts.

**Required changes.** No production-code modification beyond the new fixture
in `synthetic.py`.

The rest is a new test script importing:

- `baseline.py`;
- `cuts.py`
  (`is_valid_cut`, `integer_oracle` corrected by T1);
- the T2 validator;
- `synthetic.py`.

**Acceptance criteria:**

1. The system SHALL include at least the following cases:

   - pure staying in place with `S=T={v}` and no edge
     (`make_StayPutIsolado`, new);
   - partial overlap (`SharedTerminal`);
   - swap through a common edge (`StayPut`);
   - `TermRelay` / `TermRelayForced`
     (recharging at a terminal; robot only reaches its destination by passing through
     another terminal);
   - the `a–b–c` path case referenced in the assessment as a regression for
     incorrect cancellation of the intersection
     (to be confirmed against the assessment/code before implementation —
     see note below).

2. WHEN the suite runs on any listed case, THEN the system SHALL compare the five
   mechanisms:

   - base model;
   - oracle;
   - fractional separation;
   - `is_valid_cut`;
   - independent validator;

   and report each divergence with the case name and the two disagreeing mechanisms.

3. IF any pair of mechanisms diverges on any case, THEN the system SHALL terminate
   with a non-zero exit code.

4. The system SHALL run in finite and documented time
   (seconds to a few minutes, since all cases are intentionally small)
   without requiring anything beyond the Gurobi dependency already used by
   `construir_modelo_baseline`.

5. WHEN the suite passes, THEN the system SHALL record versioned evidence under
   `docs/technical/reference/`
   (final filename to be chosen during implementation), including:

   - 0 divergences;
   - list of cases;
   - date;
   - commit.

**Required tests:** the suite itself is the test.

There is no "test of the test" beyond running it before and after the T1 fix
to verify that it actually detects the original defect.

Negative regression:

- run the suite against the pre-T1 `integer_oracle`;
- confirm that it reproduces the failure.

**Evidence to produce:** short document or section in an existing document recording:

- final list of cases;
- suite result;
- confirmation that the suite reproduces the T1 defect when executed against
  the uncorrected version.

This proves that the suite would have caught the original bug.

**Risks:** the `a-b-c` path case cited in the user's brief was not found during this
session in `synthetic.py`, `validacao-formulacao-base.md`, or the
`verify_e5_*.py` files that were read.

See Inconsistencies below.

The task must begin by locating the exact reference
(probably in `MIN-STATION-parecer-macro-consolidado.md` or in some `verify_e*.py`
not yet read) before assuming a new fixture must be created from scratch.

**Dependencies:** depends on T1
(corrected oracle) and T2 (independent validator) so that all five mechanisms
are available.

**Out of scope:** performance or size-stress cases
(the suite is for correctness, not benchmarking);
weighted or directed graph cases.

**Independent Test:** run the suite twice:

- once against the pre-T1 `integer_oracle`
  (using git stash or checkout of the previous commit)
  and confirm that it fails on the isolated pure-stay case;

- once against the corrected code and confirm 0 divergences.

---

### P2: T4 — Revalidate experimental results affected by the old oracle

**User Story**: As a researcher deciding whether a historical result can still be
cited, I want to know which experiments called the defective oracle on instances
with `S∩T ≠ ∅`, so that an invalid conclusion is not carried forward unknowingly.

**Why P2**: Important, but does not block T1–T3.

It is an audit that only makes sense after T1 exists, because only then can we
determine what would have changed, and it does not prevent closing the core
correctness work itself.

**Objective.** For every experiment that has already called:

- `integer_oracle`;
- `separate_classical_fracs`;
- `solve_cbi`;
- `solve_bc_yspace`;
- `solve_lp_cutting_plane`;
- `solve_ip_yspace`;

determine whether it ran on an instance with `S∩T ≠ ∅`, and if so classify the
result.

**Current problem.** `resultados-e12-pli.md` already checked and documented that
`S∩T` was empty in its own CSV ("Check" note in the report).

No other experimental report
(E9, E10, E10b, E13, E14)
makes that check explicit.

The backlog already names likely candidates:

- E10/E10b (`-rho` instances);
- conditionally, the MAPF controls in E12.

**Expected behavior.** A table, per experiment, containing:

- oracle-related function called;
- instances executed;
- which instances have `S∩T ≠ ∅`
  (from `manifest.csv`, column `rho_S_inter_T` or equivalent);
- one of three decisions:
  - unaffected;
  - needs rerun;
  - result replaced.

**Affected files/components**
(read-only plus a new document; no production-code modification):

- `docs/technical/reference/experimentos/resultados-e9-e10-pli.md`
- `docs/technical/reference/experimentos/resultados-e13-pli.md`
- `docs/technical/reference/experimentos/resultados-e14-pli.md`
- `docs/technical/reference/experimentos/resultados-e12-pli.md`
  (already checked)

- `experiments/benchmark/run_e12.py`
- `experiments/benchmark/run_e14.py`
- E9/E10/E10b `run_e*.py` scripts

These scripts must be located before assuming that
`bc_yspace` / `yspace` were used.

Verification must be empirical:

grep/search for
`solve_cbi`,
`solve_bc_yspace`,
`solve_lp_cutting_plane`,
`solve_ip_yspace`
inside each `run_e*.py`.

- `instances/manifest.csv`
  — overlap column for `S∩T`, already used in E12.

**Required changes:** no production-code changes.

The output is an audit document and, where necessary, reruns of specific experiments
using the original parameters from their corresponding reports:

- same time limit;
- same seed;
- same cuts;
- corrected oracle.

**Acceptance criteria:**

1. The system SHALL list every `run_e*.py` or equivalent script that calls,
   directly or indirectly:

   - `integer_oracle`;
   - `separate_classical_fracs`;
   - `solve_cbi`;
   - `solve_bc_yspace`;
   - `solve_lp_cutting_plane`;
   - `solve_ip_yspace`.

2. WHEN a listed experiment ran on at least one instance with `S∩T ≠ ∅`
   (verified in `manifest.csv`),
   THEN the system SHALL mark it as a review candidate.

3. IF a review candidate produced a binary decision
   (for example, "A2 closed" or "primal gap")
   that depended on the oracle output for those instances,
   THEN the system SHALL rerun it with the corrected oracle and compare
   the before/after decision.

4. IF a candidate experiment did not affect the published verdict
   (for example because it was only a control, or because the affected instance
   was already outside the decision criterion),
   THEN the system SHALL document that justification instead of rerunning it.

5. The system SHALL produce a final report with three closed lists:

   - unaffected;
   - rerun;
   - replaced;

   with each item citing the original report and the relevant `S∩T` condition.

**Required tests:** no code-level tests.

The verification consists of:

- code search / grep;
- document inspection;
- where applicable, reruns compared with the original report.

**Evidence to produce:** new document, for example:

`docs/technical/reference/validacao-e-correcoes/revalidacao-oraculo-pos-t1.md`

containing the complete audit table and any rerun results.

**Risks:** the backlog note
("E12 already checked `S∩T` empty... E12 MAPF controls do not use `-rho`")
may cause the amount of required rerunning to be underestimated if other experiments
(E7, E8) also called `solve_bc_yspace` / `solve_cbi` on instances with
`S∩T ≠ ∅` without recording that check.

Therefore, acceptance criterion 1 requires a complete inventory before making
any assumption.

**Dependencies:** depends on T1, because otherwise there is no "corrected oracle"
to compare against.

**Out of scope:**

- rerunning experiments that do not call any of the listed functions
  (E13, E14, which use only `baseline.py` / COMP);

- changing the A2 verdict (E12) without new evidence.

A2 remains closed unless a rerun changes the result.

**Independent Test:** for every item marked "rerun", the new report must display
before/after LB/UB side by side.

---

### P2: T5 — Formalize the equivalence proof of the base formulation

**User Story**: As a researcher reviewing the base formulation, I want a complete
written proof — not only computational verification — that variant U represents
Das's MIN-STATION problem, including `S∩T`, so that this correspondence can be
cited without relying on case-by-case tests.

**Why P2**: Important for the rigor of the baseline, but does not block T1–T4.

It can be written in parallel, except for the part that references the auxiliary
network corrected by T1.

**Objective.** Close the 6 gaps already listed in
`validacao-formulacao-base.md` §A.10 and produce a complete proof that formulation
(B) / variant U (§9 of the same document) is equivalent to Das's MIN-STATION
for every `S∩T`, including:

- `S=T`;
- staying in place;
- transit through terminals;
- zero optimum.

**Current problem.** `validacao-formulacao-base.md` already contains:

- problem definition (§1);
- formulation (§2);
- constraint-by-constraint correspondence (§3–4);
- a proof for `S∩T=∅` (§5), under explicit assumption H1;
- an explicit statement of where that proof fails for `S∩T≠∅` (§5.4);
- the corrected formulation (§9), already implemented in `baseline.py`;
- an explicit list of 6 formal gaps (§A.10);
- a computational-verification protocol marked
  "recommended, not executed"
  (adopted in this spec as T2).

A proof for variant (B)/U with `S∩T≠∅` exists in prose
(§8, items "For v∈S∩T..."),
but not as a numbered lemma/proof in the same formal style as the rest of the document.

**Expected behavior.** Close the 6 gaps in §A.10:

1. Formal definition of the auxiliary network `N`:
   - `σ`;
   - `τ`;
   - capacity-1 arcs at the endpoints;
   - the same network corrected by T1;
   - described as a mathematical object, not only as code.

2. Cite the integer-flow decomposition theorem
   (Ahuja–Magnanti–Orlin, Thm. 3.5)
   and prove that each `σ–τ` path has weight 1.

3. Explicitly prove the bijection `π: S → T`
   from injectivity of the terminal arcs.

4. Formalize the battery invariant:
   - battery `r` when leaving `x_i ∈ C`;
   - `≥ r − d ≥ 0` until `x_{i+1}`.

5. Prove the cycle lemma in two cases:
   - cycles do not touch `y=0`;
   - subtracting a cycle preserves feasibility.

6. Perform balance/activation analysis by vertex class for variant (U):

   - `S∖T`;
   - `T∖S`;
   - `S∩T` with a stationary robot;
   - `S∩T` with a swap;
   - `V∖(S∪T)`.

   This must now include the role of the T1 stay arc in the
   MIN-STATION→PLI direction:

   a stationary robot corresponds exactly to the path

   `σ→v_out→v_in→τ`.

**Affected files/components:**

- `docs/technical/reference/validacao-e-correcoes/validacao-formulacao-base.md`

  - Section 5 (main proof) gains items 1–5 above as numbered subsections or lemmas.
  - Sections 8/9 gain item 6.
  - Appendix A.10 is marked closed item by item, with references to the new numbering.

- No code changes are expected.
  This task is mathematical documentation only.

**Required changes:** write the proof.

No model change is expected.

The model is already considered correct; only the proof is incomplete
(see Current State, where `baseline.py` is treated as unaffected).

**Acceptance criteria:**

1. The system SHALL version the complete proof in
   `validacao-formulacao-base.md`,
   not in a detached new document or code comments.

2. The system SHALL explicitly handle `S∩T ≠ ∅`, including:

   - `S=T`;
   - zero optimum;
   - an instance solved entirely by staying in place;
   - `C=∅`.

3. WHEN the proof references the auxiliary network,
   THEN the system SHALL use exactly the construction corrected by T1,
   including the stay arc,
   not the pre-defect version.

4. The system SHALL justify the use of continuous flow
   (`f` is a nonnegative real variable in `baseline.py`,
   even though the problem is combinatorial)
   by citing the integer-flow decomposition theorem,
   rather than relying only on computational analogy.

5. The system SHALL mark each of the 6 items in §A.10 as closed,
   citing the proof subsection that resolves it.

6. IF any of the 6 items cannot be closed with the available results,
   THEN the system SHALL explicitly record it as a remaining gap instead of
   omitting it.

**Required tests:** no code test.

Verification criterion:

every lemma must contain:

- statement;
- assumptions;
- complete proof;

with no "left as an exercise" or unsupported assertion,
following the general rule in `CLAUDE.md`.

**Evidence to produce:** the revised
`validacao-formulacao-base.md` itself,
with a short changelog at the top listing what was closed in this round.

**Risks:** the proof may reveal that the T1 correction
(the stay arc) is not the only possible way to encode the semantics.

If so, this is a legitimate finding from the proof, not a spec error.

It must be documented as such and should not retroactively change T1 without
new evidence.

**Dependencies:** item 6
(class-based analysis for variant U) and any reference to the corrected network
depend on T1 being complete.

Items 1–5 can be written in parallel with T1–T4.

**Out of scope:**

- proving strength properties of cuts C1–C8
  — that belongs to `direcoes-pli-min-station.md`, not to MIN-STATION↔PLI equivalence;

- extending the proof to weighted-distance `r` or directed graphs
  — outside Das's problem.

**Independent Test:** a reader following only the proof,
without executing code, must be able to verify equivalence for any instance with
`S∩T≠∅`, including the T1/T3 cases.

---

## Edge Cases

Boundary cases that the tasks above must explicitly cover in addition to the central fixtures:

- IF `S=T=V` entirely
  (every vertex is both origin and destination for some robot),
  THEN the corrected oracle and the independent validator SHALL agree on the
  feasibility of `C=∅`.

- IF a vertex in `S∩T` is isolated (degree zero),
  THEN the system SHALL treat it as trivially feasible through staying in place,
  never as an invalid disconnected component
  (see T1).

- IF `m=0` (no robots),
  THEN the system SHALL consider every `C`, including `∅`, feasible.

- WHEN the original graph `G` is disconnected,
  THEN the system SHALL follow Das's definition, which assumes connected `G`.

  This case is outside the correctness-fix scope, but the system should not
  silently accept such input as valid without warning.

  It remains to be checked whether
  `ler_instancia` / `ms_utils`
  already validates connectivity;
  this was not investigated in this spec.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| CORR-01 | P1: T1 | Design | Done |
| CORR-02 | P1: T1 | Design | Done |
| CORR-03 | P1: T1 | Design | Done |
| CORR-04 | P1: T1 | Design | Done |
| CORR-05 | P1: T1 | Design | Done |
| CORR-06 | P1: T1 | Design | Done |
| CORR-07 | P1: T2 | Design | Done |
| CORR-08 | P1: T2 | Design | Done |
| CORR-09 | P1: T2 | Design | Done |
| CORR-10 | P1: T2 | Design | Done |
| CORR-11 | P1: T2 | Design | Done |
| CORR-12 | P1: T2 | Design | Done |
| CORR-13 | P1: T3 | Design | Done |
| CORR-14 | P1: T3 | Design | Done |
| CORR-15 | P1: T3 | Design | Done |
| CORR-16 | P1: T3 | Design | Done |
| CORR-17 | P1: T3 | Design | Done |
| CORR-18 | P2: T4 | Design | Done |
| CORR-19 | P2: T4 | Design | Done |
| CORR-20 | P2: T4 | Design | Done |
| CORR-21 | P2: T4 | Design | Done |
| CORR-22 | P2: T4 | Design | Done |
| CORR-23 | P2: T5 | Design | Done |
| CORR-24 | P2: T5 | Design | Done |
| CORR-25 | P2: T5 | Design | Done |
| CORR-26 | P2: T5 | Design | Done |
| CORR-27 | P2: T5 | Design | Done |
| CORR-28 | P2: T5 | Design | Done |

**Coverage:** 28 total, implemented in T1–T5 (no separate `tasks.md`).
Status `Done` means the corresponding story was executed and its script or
document passed. T2 on `n = 5` is a documented sample, not the full labeled
enumeration; see `validacao-formulacao-base.md`, "Verificação recomendada".

---

## Success Criteria

- [x] `verify_t1_oracle_sT.py` runs with 0 divergences against the base model
      on the 6 fixtures from `synthetic.py` plus the 2 new pure-stay cases,
      testing every `C ⊆ V`.

- [x] The independent validator (T2) agrees with Gurobi and the corrected oracle
      on all connected graphs with
      `n≤4`, `r∈{1,2,3}`, `m≤3`,
      every `C ⊆ V` (7998 instances, 125922 sets, 0 divergences).
      For `n=5` the labeled universe has 728 graphs; full comparison against
      Gurobi extrapolates to about two hours. A sample of 60 instances
      (seed 42, 1920 sets `C`) had 0 divergences. Recorded in
      `validacao-formulacao-base.md`.

- [x] The T3 regression suite fails when executed against the pre-T1 oracle
      (proof that it detects the original bug) and passes with 0 divergences
      against the corrected code.

- [x] T4 produces a closed list — not an open-ended one — of experiments classified as:

      - unaffected;
      - rerun;
      - replaced;

      with no experiment left pending classification.

- [x] The 6 gaps in `validacao-formulacao-base.md` §A.10 are marked as closed
      or explicitly documented as remaining gaps in the revised text.

---

## Inconsistencies Found Between the Backlog, Documentation, and Code During This Spec

1. **The `a-b-c` path** cited in the user's brief as a regression case
   ("incorrect cancellation of the intersection") was not found during this session
   in:

   - `synthetic.py`;
   - `validacao-formulacao-base.md`;
   - the `verify_e5_*.py` files that were read.

   It may exist in an unread portion of the large consolidated assessment
   (`MIN-STATION-parecer-macro-consolidado.md`)
   or may refer to a counterexample that has not yet been implemented in code.

   T3 must locate the exact reference before creating a new fixture from scratch.

2. **`make_StayPut` is cited in the backlog and assessment as the
   "pure staying-in-place" fixture**, but execution in this session shows that it
   establishes feasibility through a swap over the common edge, not through isolated
   staying in place.

   The T1 defect only appears on a fixture that does not yet exist
   (`make_StayPutIsolado`, proposed in T3).

   This does not invalidate previous work
   (H02, the correction to the base-model balance),
   but it means that the existing regression suite
   (`verify_e5_validador.py`)
   could never have caught the T1 defect even while passing with 0 divergences.

3. **`direcoes-pli-min-station.md` §13 (A2 ranking)** still lacks the E12 verdict entry
   (inconsistency 9 from the backlog, not covered by any Block 1 task).

   It is mentioned here only because T4 touches the same experiments.

   Correcting that ranking remains T11 (Block 2), not part of this spec.
