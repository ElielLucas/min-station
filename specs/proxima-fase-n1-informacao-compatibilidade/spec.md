# Next Phase N1 — Incremental Compatibility Information (MIN-STATION) Specification

**Status:** `ACTIVE` (created 2026-10-07, branch `novos_testes`, HEAD `0f16925`).
**Authority:** `docs/technical/plans/historico/Analise-consolidada-MIN-STATION-2026-10-07.md`
(analysis of `b3c7337`), §§8–21, in particular §17 N1. The older
`docs/technical/plans/execucao/plano-proxima-fase.md` is historical context only; where they differ,
the consolidated analysis prevails.

## Scope

N1 answers one question on small instances with certified OPT: **which information adds lower-bound
strength beyond the best current reference** — connected configurations (F-CC), the existing static
cuts, trio consistency (F-C3), or a more specific compatibility witness? It closes the open proofs of
F-CC, turns the recovered F-C3 source into one canonical definition, re-reads the existing R7 pool
correctly, runs one frozen small diagnostic, and ends with one decision that selects (or refuses) the
representation N2 will pursue. It also performs the documentation clean-up (T0) needed so that no
later reader misreads the current state.

N1 does **not** look for performance at scale. It produces no method, no column generation, no
benchmark-v1 run.

### Claim vocabulary (mandatory in every N1 artifact)

| Label | Meaning |
|---|---|
| `PROVEN` | Written proof in the repository, reviewed |
| `COMPUTATIONALLY VERIFIED` | A named test checks exactly the stated property on a named instance set |
| `SUPPORTED BY EXPERIMENT` | Measured on a pre-registered set; holds only for that set |
| `HYPOTHESIS` | Stated, not proven, not measured |
| `OPEN` | Not decided |
| `REFUTED` | Counterexample recorded |
| `NOT MEASURED` | Arm excluded (cap, missing certificate, out of scope). Never read as "no effect" |
| `UNRECOVERED` | Source cited by the analysis but not available; never used as evidence |

Provenance labels for formulation material: `SOURCE` (taken from the recovered original document),
`DERIVED` (follows from SOURCE or repo documents by a written argument), `NEW` (introduced in N1).

### Notation (anti-collision)

- **F-C3** always means the trio-consistency *formulation*.
- **C3-cut** means the old max-flow separation family of `experiments/cuts/cuts.py:254`
  (`check_C3_violations`). The bare token "C3" is forbidden in N1 artifacts.
- **K** is the exact list of static cuts produced by `harness.prepare_cuts(..., active_cuts={'C1','C2','C4'})`
  for an instance (C4 = C4-DM), stored with its hash. The same K is added to every arm that admits it.
- **COMP** = baseline U + C1 + C2 + C4-DM with continuous flow (official comparison method).
- **core IP** = integer covering problem in `y` with C1+C2+C4-DM. It is a lower bound; it is neither an
  LP nor an upper bound, and its optimal `y` is not automatically feasible.

---

## Relationship with Previous Specs

| Spec | Relation |
|---|---|
| Blocos 1–4 | Closed. N1 reuses the oracle (`viavel`), the battery validator, the gadgets and the IJCAI overlap boundaries. No reopening |
| A — Foundation | Closed operationally. Official baseline, partition and budget reused unchanged. T0 adds status notes (traceability still says `Pending`) |
| B — F-CC/F-C3 | F-CC side closed (F1–F3, **GF1 = PASS**, not reopened). F-C3 side (F1/F2/F3 for F-C3) is **absorbed** by N1 stories 2–3–5. P2/P3/P4/P7 repairs absorbed by story 1 |
| C — Gap/plateau | R5/R6/G1 closed; **G1 kept as operational gate only**. R7 collection closed; R7 second part (correct metrics, witnesses) **absorbed** by story 4 |
| D — Special-class certifiers | Closed with `CONFIRMED DIVERGENCE`. Its corpus may be used as small instances with certified OPT; the literal path/cycle/spider procedures are **never** an oracle in N1 |
| R8 / R10 (plan) | Merged into one question; the "F-CC + existing cuts" control is absorbed here; any method is N2 |
| N2 — Certified Compatibility Bound | `CONDITIONAL`; activated only by the N1 decision record (story 7) |
| N3 — Algorithmic utility | Not created; sketched inside N2 as `BLOCKED — DO NOT IMPLEMENT` |
| N4 — R11 theoretical opportunity | **Not created** (user decision 2026-10-07). Opening condition: one single target, final published versions of Das (DAM 381, 2026), IJCAI-26 and Pereira & Ravelo checked against the audited copies, novelty versus IJCAI Theorem 9 argued, and human review before any external communication. Until then R11 stays `CONFIRMED DIVERGENCE` |

---

## Current State (audited 2026-10-07, read-only, HEAD `0f16925`)

| # | Item | State | Evidence |
|---|---|---|---|
| 1 | F-CC implemented | DONE | `experiments/alternative-formulations/fcc.py`: forms `qij` and `separada`, `enumerar_conexos`, cap `max_W=200000` |
| 2 | `fcc.py` matches the F-CC definition | PARTIAL | `qij` matches `formulacoes/formulacao-fcc-configuracoes-conectadas.md`. `separada` lacks SOURCE constraint CA5 (`λ_W ≤ Σ_s α_sW`), so it admits empty mass; LP value equality with `qij` was checked numerically (P7 cross-check). CSV column `n_W` mixes raw and filtered counts (`run_f3.py:176-178,210`) |
| 3 | `verify_fcc.py` | DONE (limited) | Enumerator check; P1 per installation `C ⊆ V` versus `viavel` in form `qij` only; P7 = LP value `qij` vs `separada`; 6 instances with `n ≤ 5` (the F3 pre-registration says `n ≤ 9`) |
| 4 | F3 reproducible | NEEDS VERIFICATION | `run_f3.py` and command in `decisoes/decisao-gf1.md:48-51`; not re-run |
| 5 | GF1 | DONE — `PASS` | `decisao-gf1.md:9`. `:37` says "Não há ganho em SC" although F-CC on SC-GF2-k3 was excluded by `max_W` → must read `NOT MEASURED` |
| 6 | P2, P7 | OPEN | `formulacoes/provas-fcc-fc3.md:87-96` (P2 adds direct arrival to an `m·y_v` transit bound informally; ignores inflow into `t ∈ J_q \ W_q`); `:195-205` (P7: vertex `I=J=∅` not excluded; claims marginals reproduced) |
| 7 | P3, P4 | OPEN (label unsupported) | Labelled `COMPUTATIONALLY VERIFIED` while their text says no computation tested it; P3 contains an unresolved inline question (`:115-117`) |
| 8 | F-C3 source | PARTIAL | Original 01/10/2026 document recovered: `formulacoes/formulacao-fc3-componentes-trios.md`, SHA-256 `fd5e9a0054ef6d10ba9f791f2cc77df55389c8cf72bcac3ccf56376558ef49f4` (verified 2026-10-07; untracked). Consolidated 05/10 version (SHA `b68e9b6b…`) is `UNRECOVERED` |
| 9 | `d_ss=0` | OPEN | `formulacoes/formulacao-fc3-consistencia-trios.md:59-60` |
| 10 | F-C3 implementation | OPEN | None; `lp_fc3 = OPEN` in `f3-fcc.csv` and `r11-certificadores.csv` |
| 11 | F-C3 results | NOT MEASURED | No CSV |
| 12 | F-CC + existing cuts | NOT MEASURED | `fcc.py` has no cut hook |
| 13 | R7 pool | OPEN | Re-read only in the analysis; CSV, summary and report unchanged |
| 14 | Cut × installation incidence | OPEN | `run_r7_plato.py:118-166` counts how often a `Z` was returned |
| 15 | `n_origens_sem_par` | OPEN | `run_r7_plato.py:74,153` counts degree-zero origins |
| 16 | Hall witnesses in R7 | OPEN | Only in `cuts.py:203` (C4-DM) and `:566` (C6), reusable |
| 17–19 | Pricing, F-CC dual, column generation | OPEN | No code, no document |
| 20 | R9 | BLOCKED | Depends on a useful certified R8/N2 |
| 21 | R12 | BLOCKED | Spec C `:308` |
| 22 | Later experiment satisfying N1/N2 | none | — |
| 23 | Specs A–D current | NO | A `:264-289` all `Pending`; B `:33-34` "NOT STARTED"; C `:69` vs `:303-306`; D `:35-36` R11 certifiers as future validators |
| 24 | Commits after `b3c7337` | `0f16925` only moves docs and adds the analysis | No decision changed; 7 of 14 paths in `CLAUDE.md`, 2 in `RESEARCH.md`, 1 in `docs/context-ai`, about 59 distinct old paths in 58 files are broken |

**Structural fact derived from the existing F3 CSV (not a new result):** among the measured rows with
`Γ > 0`, F-CC already reaches OPT on HB-q4, HB-q5 and BP-não-[3,1]-q2, so on them
`Δ_trio ≤ 0` necessarily. Sec59(L=7) is the only existing `Γ > 0` case with residual after F-CC
(4.5 vs 7). TR and F1 have `m = 2`, so F-C3 equals its compressed core there. Consequently story 6
(new micro-instances) is expected to be triggered for the F-C3 question; the trigger itself is frozen
below and evaluated on measured values.

**Reusable infrastructure:** `experiments/cuts/independent_validator.py` (`viavel` `:126`,
`opt_por_enumeracao` `:140`), `experiments/cuts/verify_t2_validador_independente.py`,
`baseline.py`, `experiments/cuts/harness.py` (`prepare_cuts` `:76`, `measure_lp` `:141`),
`experiments/cuts/cuts.py` (`generate_C4_DM`, `generate_C6`, `integer_oracle` `:765`,
`_max_matching`, `_alternating_reach`), `experiments/alternative-formulations/{fcc.py,run_f3.py,verify_fcc.py}`,
`experiments/cuts/synthetic.py` (gadgets), `experiments/structural/{hb,bp,tr,sc}.py`,
`experiments/structural/r11_catalog.py`, `results/benchmark/r7-plato.csv`.

---

## Problem Statement

GF1 showed that F-CC's LP beats `max(LP COMP, core IP)` on three small `Γ > 0` types, but its
enumeration already exceeds 200 000 connected sets at 21 vertices, and SharedTerminal shows that
COMP's LP can beat F-CC's: neither dominates. F-C3, the only proposed strengthening, now has its
original source back in the repository but no canonical definition, no implementation and no
measurement; two F-CC proofs (P2, P7) have gaps and two labels (P3, P4) are unsupported. R7 collected
a useful plateau pool but its summary measured the frequency of a returned `Z` instead of the
installations it cuts, and its H-desc test is the feasibility characterization itself. Before any
scalable method (N2) is chosen, the project must know which piece of compatibility information is
incremental, where, and why.

## Scientific Question

> Which information really adds strength beyond the best current reference — connected
> configurations, the existing cover/Hall cuts, trio consistency, or a more specific compatibility
> witness — and which single representation of it deserves N2?

## Hypotheses

| ID | Hypothesis | Status |
|---|---|---|
| H1 | F-CC + K captures a substantial part of the gain needed above `B0` | `HYPOTHESIS` |
| H2 | Trio consistency adds value above F-CC + K only for specific patterns of marginals, possibly only where `z_core^IP = OPT` | `HYPOTHESIS` |
| H3 | Infeasible core optima do not all fail for the same reason; "several components in `H[C]`" is not a mechanism | `HYPOTHESIS` |

## Goals

- [ ] F-CC proofs P2, P7 repaired and P3, P4 either proven, computationally verified by an
      appropriate test, or downgraded.
- [ ] One canonical, versioned F-C3 definition in the repository with explicit provenance.
- [ ] F-C3 and F-CC + K implemented only after mathematical review, and validated per installation.
- [ ] R7 pool re-read with correctly named metrics and Hall witnesses, without a new large pool.
- [ ] One frozen small diagnostic comparing LP base, LP COMP, core IP, LP F-CC, LP F-CC + K, LP F-C3,
      LP F-C3 + K and certified OPT.
- [ ] One decision record selecting exactly one representation for N2, or none.
- [ ] Documentation of previous phases annotated (not rewritten) and all broken paths fixed.

## Out of Scope

| Item | Reason |
|---|---|
| Column generation, pricing, any partial master | N2, conditional on this spec's decision |
| Branch-and-price / price-and-branch (R9) | Blocked until N2 passes |
| Broad F-C3 campaign or F-C3 at scale | Analysis §16/§18: conditional on incremental gain |
| Reopening CBI / A2 or generic BC-Y | Closed by E12 / E7–E8; no new mechanism |
| Re-tuning the old baseline Lagrangian | Its bound is capped by the baseline LP |
| Classical Benders as a stronger bound | Projects the baseline LP; does not strengthen it |
| Expanding BP / HB / TR without a new hypothesis | Phase P/E decisions |
| Running benchmark-v1 in full | No discriminating small result yet |
| New synthetics to obtain timeouts | Instances only answer a stated question (story 6) |
| Changing baseline U, COMP, the core or `fcc.py` as measured in F3 | New models are separate modules |
| Moving instances between development and evaluation | Partition by origin is frozen |
| Literal R11 procedures as oracle | `CONFIRMED DIVERGENCE` |
| Reporting any restricted master as a MIN-STATION LB | Certification rules belong to N2 and forbid it |
| N4 (R11 theory), primal line (R12), confirmation (R13) | Not opened in this phase |
| Reconstructing the consolidated F-C3 version of 05/10 | `UNRECOVERED`; user decision forbids reconstruction |
| A global connectivity cut | Valid solutions may use several components of `H[C]` |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| F-C3 source | `formulacoes/formulacao-fc3-componentes-trios.md` is `SOURCE` (SHA `fd5e9a00…49f4`); the 05/10 consolidated version is `UNRECOVERED` and never cited as evidence | User decision 2026-10-07 | y |
| Arguments the analysis attributes to the consolidated version (normalization fix, SC/GF(2) trio argument) | Re-derived in N1 and labelled `NEW`, or left `HYPOTHESIS` | Their source is unavailable | y |
| SOURCE dependencies `MIN-STATION-formulacao-por-componentes.md`, `…-fluxos-origem-destino.md` | `UNRECOVERED`; the chain step F-CC ⊆ F-OD ⊆ AG is not used; `base ≤ F-CC` rests on repaired P2 | F-OD is discarded (2026-10-03); the documents are absent | y |
| Spec granularity | One `spec.md`; tasks as a section, no `tasks.md` this round | Precedent of Specs A–D | y |
| Documentation clean-up | Full T0 inside N1: status notes plus every broken relative path | User decision 2026-10-07 | y |
| Paths that are commit-pinned permalinks (e.g. links to `b3c7337` in the analysis) | Not changed | They still resolve and fix the audited version | y |
| Static cut set K | Output of `prepare_cuts` with `{'C1','C2','C4'}`, hashed per instance; C6 and C5 excluded from K | Same cuts as COMP; C6/C5 only serve as "already known" comparators for a projected inequality | y |
| Caps inherited from F3 | `n_max = 21`, `max_W = 200000`, `n_opt_enum = 16` | Keeps comparability with GF1 | y |
| F-C3 size cap | Exclude an instance when `2·C(m,3)·(35K+8) > 5 000 000` network-arc variables (`K = |𝒲|` after filtering) | Fixed now from sizes only, before any F-C3 value; SOURCE §10.2 bound | y |
| Restricted-trio variants of F-C3 | Not allowed in this round | The analysis forbids an implicit third variant | y |
| Numerical tolerance | `1e-6` on every LP comparison; a difference within tolerance is "no gain" | Same as F3 | y |
| "Distinct structures" | Different construction families (`tipo` in F3 CSV or the generator of a new pair); variants of one graph count once | Analysis §19: unit = graph/construction | y |
| Projected-inequality attempts | At most 2 attempts, each with a written proof | Analysis Q4 (2–3); the lower bound chosen to avoid drift | y |
| Gate threshold for "recovers" in the tie-break | `≥ 50%` of the largest positive increment over `B0` measured on the same cases | Same threshold the analysis proposes for N2 | y |

**Open questions:** none — every pending decision is recorded above with its default.

## Decisions

| ID | Decision |
|---|---|
| D-N1-1 | N2 is created now as `CONDITIONAL`; N3 is only a blocked section inside N2; N4 is not created |
| D-N1-2 | Implementation of F-C3 is gated by a mathematical review record (gate MR-F3, story 2) |
| D-N1-3 | F3 is re-run before any new arm; a non-reproduced F3 value stops the diagnostic |
| D-N1-4 | Historical documents and pre-registrations are annotated with dated notes, never rewritten |
| D-N1-5 | No commit happens without explicit user approval |

---

## Mathematical Preconditions

1. P1 (exactness of F-CC) stays `PROVEN`; its per-installation cross-check exists (`verify_fcc.py`).
2. P2 and P7 must be repaired (story 1) **before** any statement that relies on `base ≤ F-CC` or on
   the separated form; until then they are treated as `OPEN`.
3. The canonical F-C3 definition (story 2) must pass MR-F3 before code is written.
4. Every inequality added to any arm must be valid for every installation `C` of MIN-STATION as
   defined by Das (with `S∩T`, permanence, terminals as stations and as relays).
5. `OPT` comes from `opt_por_enumeracao`, from a certified baseline MIP (exact by T5), from the
   independent DP certificate of BP, or from a proven analytical value — recorded per instance. Never
   from F-CC/F-C3 themselves and never from an R11 literal procedure.

---

## User Stories

### P1: Story 0 — Documentation clean-up (task N1-T0) ⭐ MVP

**User Story**: As a researcher reading the repository after the analysis, I want every outdated
status and every broken path corrected or annotated, so that nobody acts on a superseded state.

**Why P1**: Wrong pointers and stale statuses already contradict GF1, G1 and R11.

**Acceptance Criteria**:

1. The system SHALL add a dated post-analysis note, without deleting prior text, to each item of analysis §15: Spec A traceability, Spec B Current State, Spec C R8/R9 status, Spec D R11-as-validator lines, plan R1–R13 statuses, backlog "Geração de colunas", `direcoes` A2/D-5, overlap paths/cycles, README `alternative-formulations`, validation/context historical sections, hc9u UB 38 versus UB 41, and `-dirty` snapshots.
2. The system SHALL annotate `decisao-gf1.md` so that the SC-GF2-k3 F-CC arm reads `NOT MEASURED (excluded by max_W)` while the verdict `GF1 = PASS` stays unchanged.
3. The system SHALL annotate `resultados-r7-plato.md` and `decisao-g1.md` stating that `max_elimina_um_Z` is a return frequency, that `n_origens_sem_par` counts degree-zero origins, that H-desc is the feasibility characterization, and that G1 does not depend on R7.
4. The system SHALL replace every relative path broken by commit `0f16925` in `.md` and `.py` files with the current location and SHALL record each replacement in a path changelog.
5. IF a path is a commit-pinned permalink, a CSV cell, or a value inside a pre-registration THEN the system SHALL NOT change it.
6. The system SHALL record the provenance of the recovered SOURCE file (path, SHA-256, date 01/10/2026, recovery date) in a provenance register without modifying the SOURCE file content.
7. WHEN T0 is complete THEN the system SHALL show that no path listed in `CLAUDE.md`, `RESEARCH.md` or `docs/context-ai/` points to a missing file.

**Independent Test**: a script lists every relative path in `.md`/`.py` and reports zero missing
targets; `sha256sum` of the SOURCE file is unchanged.

---

### P1: Story 1 — Close the F-CC proofs (task N1-T1)

**User Story**: As a researcher who will compare F-CC with other bounds, I want its proofs complete
and its labels honest, so that the comparison rests on established facts.

**Why P1**: P2 underlies `base ≤ F-CC`; P7 underlies the separated form used by `lp_fcc`.

**Acceptance Criteria**:

1. The system SHALL rewrite the proof of P2 choosing, per configuration, a bijection and simple paths in `H`, separating the free final arrival from transit, bounding transit through a destination `v` by `(m−1)·Σ_{q: v∈W_q} λ_q`, treating `v ∈ J_q` and `v ∉ J_q` separately, covering inflow into `t ∈ J_q \ W_q`, origins symmetrically, and `S∩T`.
2. IF the P2 argument only yields an inequality weaker than `in(v) ≤ b_v + (m − b_v)·y_v` THEN the system SHALL keep P2 `OPEN` and SHALL NOT label it `PROVEN`.
3. The system SHALL rewrite the proof of P7 stating explicitly that discarding the mass of `I = J = ∅` leaves `α`, `β`, `d` unchanged, decreases `λ`, loosens only the linking rows, and preserves the projection onto `y`, and SHALL relate it to SOURCE constraint CA5.
4. The system SHALL NOT claim that all marginals of `λ` are reproduced unless that is proven.
5. The system SHALL give P3 and P4 each exactly one of: a written proof labelled `PROVEN`; an implication test labelled `COMPUTATIONALLY VERIFIED` that, for every cut of the family on a named instance set, minimizes the cut's left side over the F-CC LP polytope and checks it is at least the right side; or the label `HYPOTHESIS`.
6. The system SHALL resolve the inline question of P3 (whether `s ∈ N^+(s)` at distance 0) in the text.
7. IF a repair produces a counterexample THEN the system SHALL label the proposition `REFUTED`, record the instance, and SHALL stop story 5 until the impact on GF1 is written down.

**Independent Test**: each P2/P3/P4/P7 label points to a proof section or to a test name and its
instance list; comparing objective values alone is never cited as evidence of polytope inclusion.

---

### P1: Story 2 — Canonical F-C3 definition from the recovered source (task N1-T2)

**User Story**: As a researcher about to implement F-C3, I want one versioned definition whose every
part has known provenance, so that what I implement is F-C3 and not a reading of a summary.

**Why P1**: The current repository text is incomplete (O1–O5 open) and wrong on `d_ss`.

**Acceptance Criteria**:

1. The system SHALL produce an audit table comparing SOURCE §§2–12 with `formulacao-fc3-consistencia-trios.md`, classifying each element as `SOURCE`, `DERIVED` or `NEW` with section references.
2. The system SHALL write a single canonical F-C3 definition document carrying a version number, the SOURCE SHA-256 and the list of `UNRECOVERED` dependencies, and SHALL turn the previous summary into a historical pointer to it.
3. The system SHALL resolve each open point O1–O5 by citing the SOURCE §5 element that fixes it: stages `j = 1..K` over a fixed enumeration of `𝒲`, states `(j,B)`, non-use and use arcs with `R ⊆ (U\B) ∩ S_{W_j}` (resp. `T_{W_j}`) including `R = ∅`, final arcs to `ω`, linking equalities C32–C34, one network per trio of each side.
4. The system SHALL state that `d_G(s,s) = 0` and that the permanence variable `d_ss` is free in `[0,1]` (value 1 allowed), removing the text "`d_ss = 0`".
5. The system SHALL include CA5 (`λ_W ≤ Σ_{s∈S_W} α_sW`) in the compressed core F-CA and SHALL document that `fcc.py` form `separada` omits it and why its measured LP values are unaffected.
6. The system SHALL name the formulation F-C3 and the old max-flow family C3-cut, with a sentence stating that they are unrelated.
7. The system SHALL remove F-OD from the dominance chain used by N1, keeping it only as historical mention.
8. The system SHALL relabel P8 and P11 after review: SOURCE analytical results (exactness, F-CA compression, dominance over F-CC, family `g` with LP `2g`, five-cycle with LP `5/2 < 3`) become `PROVEN` only when the review accepts the written argument, otherwise `HYPOTHESIS`.
9. The system SHALL record gate MR-F3 as a dated review entry listing each accepted or rejected argument; WHILE MR-F3 is not recorded as accepted the system SHALL NOT start story 3 for F-C3.

**Independent Test**: a reader can build F-C3 for a 6-vertex instance with `m = 3` from the
canonical document alone, and every row of the audit table cites a SOURCE section or is `NEW`.

---

### P1: Story 3 — Implement and validate F-C3 and F-CC + K (task N1-T3)

**User Story**: As a researcher measuring LP strength, I want the new arms proven to model
MIN-STATION exactly on small cases, so that LP differences are not implementation artefacts.

**Why P1**: Equal OPT values do not prove equivalence.

**Acceptance Criteria**:

1. The system SHALL implement F-C3 and F-CC + K as new modules that leave `baseline.py`, COMP, the core solver and `fcc.py` unchanged.
2. WHEN MR-F3 is accepted THEN the system SHALL compare, for every installation `C ⊆ V` of each validation instance, feasibility of binary-`y` F-C3 fixed at `χ_C` with `viavel(S,T,V,adj,r,C)`, reporting disagreements in both directions.
3. The validation set SHALL contain optimal and non-optimal installations and instances with `S∩T ≠ ∅`, permanence pairs, a terminal used as a relay, `m ≥ 3`, and a valid solution with several components in `H[C]`.
4. The system SHALL run the same per-installation comparison for binary-`y` F-CC + K.
5. IF any disagreement appears THEN the system SHALL stop, record the instance and installation, and SHALL NOT compute any LP value of that arm until it is resolved.
6. The system SHALL check on every instance that `z_LP(F-C3) ≥ z_LP(F-CC) − 1e-6` and `z_LP(F-C3+K) ≥ z_LP(F-CC+K) − 1e-6`, treating a violation as a bug or a refutation to resolve before continuing.
7. WHERE an instance of SOURCE §8 (`g = 2`, 20 vertices) or §9 (five-cycle, 15 vertices) fits the caps the system SHALL compare the measured LP with the SOURCE value (4, resp. 5/2) and SHALL record any divergence without adjusting the model or the claim.

**Independent Test**: `verify_*` scripts exit 0 and print, per instance, the number of installations
compared and the number of disagreements in each direction.

---

### P1: Story 4 — Re-read the R7 pool with correct metrics (task N1-T4)

**User Story**: As a researcher looking for a compatibility witness, I want the existing plateau pool
measured with correctly named quantities and Hall witnesses, so that the next inequality targets a
real mechanism.

**Why P1**: The current summary confuses return frequency with cut coverage and degree zero with Hall
deficiency.

**Acceptance Criteria**:

1. The system SHALL compute, for each distinct `Z` of each R7 pool, `z_freq_retorno` (times the oracle returned `Z`) and `z_n_instalacoes_cortadas` (recorded installations `C` of that pool with `C ∩ Z = ∅`), as two separate columns.
2. The system SHALL use only `results/benchmark/r7-plato.csv` and the instance files; it SHALL NOT collect a new large pool.
3. The system SHALL compute per infeasible `C`: `n_origens_grau_zero`, `n_origens_nao_emparelhadas` (origins unmatched by a maximum matching of `B_C`), `hall_deficit`, and one Hall-deficient origin set as witness.
4. The system SHALL classify each selected infeasible `C` into exactly one of: no individual reach, Hall deficiency without degree zero, collective incompatibility, distribution among components, inconsistency among configurations, or another category defined with a written criterion.
5. IF the only explanation found for a `C` is "several components in `H[C]`" THEN the system SHALL classify it as unexplained and SHALL NOT derive a global connectivity cut from it.
6. The system SHALL leave `run_r7_plato.py`, `r7-plato.csv` and `r7-plato-resumo.csv` unchanged and SHALL write the corrected metrics to new files with an audit note.
7. The system SHALL report that the metrics refer only to the recorded pools (three of them truncated at 200) and not to the whole plateau or to all cuts.

**Independent Test**: on PUC cc9-2p the maximum `z_n_instalacoes_cortadas` equals 27 and the maximum
`z_freq_retorno` equals 21 (values recomputed by the analysis from the CSV).

---

### P1: Story 5 — Frozen small diagnostic (task N1-T5)

**User Story**: As the owner of the program, I want the eight arms compared on the same small certified
instances under a pre-registration, so that the source of any gain is attributable.

**Why P1**: It is the evidence the N1 gate uses.

**Acceptance Criteria**:

1. The system SHALL write the pre-registration (instances, arms, K definition and hashes, caps, OPT sources, metrics, gate rule) before computing any value of F-CC + K, F-C3 or F-C3 + K.
2. The system SHALL re-run `run_f3.py` first and SHALL compare it with `f3-fcc.csv`; IF any value differs beyond `1e-6` THEN the system SHALL stop and investigate.
3. The system SHALL report per instance: LP base, LP COMP, core IP, LP F-CC, LP F-CC + K, LP F-C3, LP F-C3 + K, OPT, OPT source, `Γ`, `B0`, `Δ_FCC`, `Δ_FCC+K`, `Δ_trio`, `Δ_trio_raw`, residual fractions, `K` hash and sizes.
4. The system SHALL add to every arm that admits it exactly the same K.
5. WHEN an instance exceeds a cap THEN the system SHALL record the arm as `NOT MEASURED` with the cap exceeded and SHALL NOT read it as absence of gain.
6. The system SHALL report negative `Δ_FCC` values as measured, without truncation.
7. The system SHALL label every conclusion with the claim vocabulary of this spec.

**Independent Test**: the CSV is regenerable from the pre-registration with `PYTHONHASHSEED=0`.

---

### P2: Story 6 — Conditional micro-instances (task N1-T6)

**User Story**: As a researcher testing trio consistency, I want a bounded set of counterfactual
micro-instances only if existing cases cannot discriminate F-C3, so that new synthetics answer one
question and nothing else.

**Why P2**: Needed only if the trigger fires.

**Acceptance Criteria**:

1. WHEN the measured existing set has fewer than two distinct structures with `Γ > 0` and `z_{F-CC+K} < OPT − 1e-6` THEN the system SHALL allow story 6; otherwise it SHALL NOT generate instances.
2. The system SHALL freeze, before generating any instance, the generator rule, the obstruction it varies, the paired control, the certificate method and the list of pairs.
3. The system SHALL generate at most 12 pairs, each pair sharing `n`, `m` and `r` and differing only in the stated obstruction.
4. The system SHALL start with `n ≤ 10`, SHALL certify OPT by `opt_por_enumeracao`, and SHALL NOT perform an exhaustive search over all graphs.
5. The system SHALL check each instance for terminal shortcuts (stations on origins/destinations or between gadgets) that remove the intended obstruction, and SHALL document the result.
6. IF a pair loses its obstruction or its certificate THEN the system SHALL record it as excluded and SHALL NOT replace it after seeing any measurement.

**Independent Test**: the frozen rule regenerates exactly the recorded pairs.

---

### P1: Story 7 — N1 gate decision (task N1-T7)

**User Story**: As the owner of the program, I want one pre-registered decision naming the single
representation N2 may pursue, so that N2 does not start from preference.

**Why P1**: It activates or keeps blocked N2.

**Acceptance Criteria**:

1. The system SHALL apply the gate rule of this spec exactly as frozen and SHALL output exactly one of `PROMOTE FCC + EXISTING CUTS`, `PROMOTE FCC + C3`, `PROMOTE PROJECTED COMPATIBILITY INEQUALITY`, `NO INCREMENTAL TARGET FOUND`, citing the deciding rows.
2. WHEN more than one promotion category qualifies THEN the system SHALL apply the frozen tie-break and SHALL name exactly one representation for N2.
3. IF the decision is `NO INCREMENTAL TARGET FOUND` THEN the system SHALL keep N2 blocked, keep F-CC + K as reference, keep F-C3 as a theoretical result, and SHALL NOT propose a new family or formulation in the same round.
4. The system SHALL NOT state that any arm is computationally better on the basis of LP values.

**Independent Test**: a reader applying the gate rule to the CSV reaches the same decision.

---

## Tasks

| Task | Story | Depends on | Output |
|---|---|---|---|
| N1-T0 | 0 | — | Notes, path fixes, path changelog, provenance register |
| N1-T1 | 1 | N1-T0 | Revised `provas-fcc-fc3.md` sections P2, P3, P4, P7 (and test if chosen) |
| N1-T2 | 2 | N1-T0 | Canonical F-C3 document, audit table, MR-F3 record |
| N1-T3 | 3 | N1-T1, N1-T2 (MR-F3 accepted) | New modules, verify scripts |
| N1-T4 | 4 | N1-T0 | Corrected R7 metrics, witnesses, classification, audit note |
| N1-T5 | 5 | N1-T3, N1-T4 | Pre-registration, CSV, report |
| N1-T6 | 6 | N1-T5 (trigger) | Frozen rule, pairs, certificates, measurements |
| N1-T7 | 7 | N1-T5, N1-T6 if triggered | Decision record |

N1-T1, N1-T2 and N1-T4 may run in parallel after N1-T0.

---

## Validation Strategy

- Correctness before strength: per-installation equivalence against `viavel` for every new binary
  model (story 3) before any LP value is read.
- Strength checks with hard invariants: `F-C3 ≥ F-CC`, `F-C3+K ≥ F-CC+K`, every LP `≤ OPT + 1e-6`.
- Attribution by ablation: identical K in F-CC + K and F-C3 + K; `Δ_trio` uses those two arms only.
- Analytical predictions of SOURCE are regressions, not targets.
- R7 metrics are recomputed from data, and the published counter values are reproduced as a check.

## Experimental Pre-registration

Frozen by this spec; N1-T5 may only add the per-instance K hashes, sizes and OPT sources before
measuring.

**Instances (existing):** Direct0, TermRelay, TermRelayForced, StayPut, StayPutIsolado,
SharedTerminal, CaminhoABC, Tri, F1(m=2,k=2), F2(k=1,L=3), Sec59(L=7), HB-q4-ndir2-p1,
HB-q5-ndir2-p1, BP-não-[3,1]-q2, TR-k2-L5-r2, SC-GF2-k3 (the 16 F3 rows); SOURCE §8 instance `g = 2`
and SOURCE §9 five-cycle instance, built exactly as specified in SOURCE (counted as existing analytical
controls, not as story-6 instances); small R11 instances with enumerated OPT only as additional
controls if they have `m ≥ 3`.

**Arms:** LP base; LP COMP; core IP; LP F-CC; LP F-CC + K; LP F-C3; LP F-C3 + K; OPT.

**Caps:** `n_max = 21`, `max_W = 200000`, `n_opt_enum = 16`, F-C3 size cap `2·C(m,3)·(35K+8) ≤ 5 000 000`.

**Metrics:**

- `B0 = max(z_COMP^LP, z_core^IP)`
- `Δ_FCC = z_FCC − B0`
- `Δ_FCC+K = z_{F-CC+K} − B0`
- `Δ_trio = z_{F-C3+K} − z_{F-CC+K}`
- `Δ_trio_raw = z_{F-C3} − z_{F-CC}`
- `ρ(arm) = (z_arm − B0)/(OPT − B0)` when `OPT > B0 + 1e-6`, else undefined
- the historical GF1 fraction `(z_FCC − max)/Γ` is reported separately under that name

No metric is truncated at zero.

**Gate rule (frozen):** see "Gate / Promotion Criteria".

## Required Tests

| Test | Checks |
|---|---|
| `verify_fcc.py` (existing) | Enumerator, P1 per installation, P7 value |
| P3/P4 implication test (if chosen) | Every C1/C2 cut implied by the F-CC LP polytope on named instances |
| F-C3 per-installation equivalence | Binary F-C3 vs `viavel`, all `C ⊆ V`, both directions |
| F-CC + K per-installation equivalence | Binary F-CC + K vs `viavel`, all `C ⊆ V` |
| LP invariants | `F-C3 ≥ F-CC`, `F-C3+K ≥ F-CC+K`, `≤ OPT` |
| SOURCE regressions | `g = 2`: LP 4; five-cycle: LP 5/2 (if within caps) |
| F3 reproduction | Re-run equals `f3-fcc.csv` |
| R7 reproduction | Recomputed `z_freq_retorno` maxima equal published `max_elimina_um_Z`; cc9 cut coverage 27 |
| Path check | Zero missing relative targets |
| Projected inequality validity (if attempted) | Exhaustive over all `C ⊆ V` on instances with `n ≤ 12` plus written proof |

## Evidence to Produce

- Path changelog, provenance register, dated notes (T0).
- Revised proofs P2/P3/P4/P7 with labels (T1).
- Canonical F-C3 document, SOURCE audit table, MR-F3 record (T2).
- New model modules and verification outputs (T3).
- Corrected R7 metrics CSV, witnesses, classification table, audit note (T4).
- N1 pre-registration, diagnostic CSV, report with inclusion/ablation matrix and at least one complete
  mechanism witness (T5).
- Story-6 frozen rule and pairs, if triggered (T6).
- N1 decision record (T7).

## Dependencies

Baseline U, COMP, core solver, `viavel`, F-CC code, existing instances and the recovered SOURCE.
No dependency on R11 corrections, on column generation or on benchmark-v1 runs.

---

## Gate / Promotion Criteria

N1 **passes** only if all hold:

1. Definitions and validity are unambiguous (stories 1–3 complete, no unresolved disagreement).
2. At least one specific mathematical mechanism is supported by a proof or a complete witness **and**
   by a measurable incremental gain.
3. The gain occurs in at least **two cases of distinct structures**.
4. To promote F-C3, the gain must not occur only on instances where `z_core^IP = OPT`.

Categories (thresholds use tolerance `1e-6`):

| Decision | Condition |
|---|---|
| `PROMOTE PROJECTED COMPATIBILITY INEQUALITY` | An inequality family, proven valid for every installation and exhaustively checked on small instances, raises LP COMP or LP F-CC + K in ≥ 2 distinct structures, and a point satisfying C1, C2, C4-DM, C5 and C6 is shown that violates it |
| `PROMOTE FCC + C3` | MR-F3 accepted, story 3 passed, `Δ_trio > 0` in ≥ 2 distinct structures, at least one of them with `z_core^IP < OPT` and `z_{F-CC+K} < OPT` |
| `PROMOTE FCC + EXISTING CUTS` | `Δ_FCC+K > 0` in ≥ 2 distinct structures with `Γ > 0`, with the complementarity mechanism documented (a cut of K violated by an optimal F-CC LP point, or the converse) |
| `NO INCREMENTAL TARGET FOUND` | None of the above |

**Tie-break (frozen):** when several categories qualify, choose the cheapest representation in the
order projected inequality, F-CC + K, F-C3, provided it recovers at least 50% of the largest positive
increment over `B0` measured on the same cases; otherwise the next one. The decision names exactly
one representation for N2: projected inequality → N2 path A; F-CC + K → N2 path B; F-C3 → N2 path B
with the trio variant.

## Stop Criteria

- Stop after the frozen round; never add instances, seeds or time after seeing results.
- If F-C3 adds no relevant gain: keep it as a theoretical result, keep F-CC + K as reference.
- If a candidate inequality only reproduces C4/C5/C6 or removes isolated installations: end that
  attempt; at most two attempts.
- If no mechanism is identified: decision `NO INCREMENTAL TARGET FOUND`; no new family or
  formulation is invented to continue.
- If story 1 refutes a proposition used by GF1: stop the diagnostic and record the impact first.

## Risks

| Risk | Mitigation |
|---|---|
| Attributing a C4 gain to trios | Identical K in both ablation arms |
| Equal OPT read as equivalence | Per-installation test in both directions |
| H-desc read as causal | Story 4 classification with witnesses |
| Exclusion read as negative | `NOT MEASURED` label, mandatory |
| Rescue by new instances | Story 6 frozen rule and cap of 12 pairs |
| Only Sec59 discriminates F-C3 among existing cases | Expected; story 6 trigger is pre-registered |
| F-C3 too large | Size cap fixed before measurement |
| Filling SOURCE gaps by intuition | `NEW` label and MR-F3 review |
| Rewriting history in T0 | Dated notes only; pre-registrations untouched |
| Changing the baseline | New modules only |

## Edge Cases

- WHEN `s ∈ S∩T` THEN every arm SHALL allow `d_ss` up to 1 and the networks SHALL treat the origin and destination roles separately.
- WHEN a terminal is used as a relay station THEN the per-installation test SHALL include it.
- WHEN a valid installation has several components in `H[C]` THEN every model SHALL accept it.
- WHEN a pair is direct THEN it SHALL be served by `d` and its trio member SHALL leave the network through the final arc.
- IF a configuration has `I = J = ∅` THEN CA5 SHALL exclude it from F-CA/F-C3 and the P7 proof SHALL treat it explicitly.
- WHEN a selected `W` serves no member of a trio THEN the use arc with `R = ∅` SHALL carry it, distinct from the non-use arc.
- WHEN a configuration does not serve a member of a trio THEN that member SHALL remain in the state set `U \ B`.
- IF F-C3 raises the LP only where `z_core^IP = OPT` THEN the system SHALL record it as polyhedral strength only, not as promotion evidence.
- IF F-C3 does not raise the LP on a `Γ > 0` case THEN the system SHALL record that case as negative evidence.
- WHEN `m < 3` THEN F-C3 SHALL equal F-CA and `Δ_trio_raw` SHALL be reported as 0 by construction.
- WHEN an origin has degree zero in `B_C` THEN story 4 SHALL classify it as no individual reach.
- WHEN no origin has degree zero but Hall fails THEN story 4 SHALL report the deficient set.
- WHEN `B_C` has several maximum matchings THEN the reported unmatched count SHALL be the deficiency, independent of the matching chosen.
- WHEN several `Z` exist for one installation THEN `z_n_instalacoes_cortadas` SHALL count the installation under each `Z` it violates.
- WHEN a `Z` cuts installations for which it was never returned THEN they SHALL be counted.
- WHEN TR (`Γ = 0`) has infeasible core optima THEN story 4 SHALL report them without reading them as a bound loss.

---

## Requirement Traceability

| Requirement ID | Story | Plan origin | Current evidence | Status | Task | Test / verification | Artifact |
|---|---|---|---|---|---|---|---|
| COMPAT-INFO-01 | 0 | §15 | Stale texts listed in Current State | Pending | N1-T0 | Review checklist | Dated notes |
| COMPAT-INFO-02 | 0 | §7, §15 GF1 | `decisao-gf1.md:37` | Pending | N1-T0 | Review | GF1 note |
| COMPAT-INFO-03 | 0 | §10, §15 R7/G1 | `resultados-r7-plato.md:29,45,51` | Pending | N1-T0 | Review | R7/G1 notes |
| COMPAT-INFO-04 | 0 | user decision T0 | ~59 broken paths | Pending | N1-T0 | Path check | Path changelog |
| COMPAT-INFO-05 | 0 | §15 | Permalinks, CSVs, pre-registrations | Pending | N1-T0 | Diff review | — |
| COMPAT-INFO-06 | 0 | §9 | SOURCE untracked, SHA verified | Pending | N1-T0 | `sha256sum` | Provenance register |
| COMPAT-INFO-07 | 0 | §15 | `CLAUDE.md` 7/14 broken | Pending | N1-T0 | Path check | — |
| COMPAT-INFO-08 | 1 | §8 P2 | `provas-fcc-fc3.md:87-96` | Pending | N1-T1 | Proof review | P2 section |
| COMPAT-INFO-09 | 1 | §8 P2 | idem | Pending | N1-T1 | Proof review | P2 label |
| COMPAT-INFO-10 | 1 | §8 P7 | `provas-fcc-fc3.md:195-205` | Pending | N1-T1 | Proof review | P7 section |
| COMPAT-INFO-11 | 1 | §8 P7 | idem | Pending | N1-T1 | Proof review | P7 section |
| COMPAT-INFO-12 | 1 | §15 P3/P4 | `provas-fcc-fc3.md:105-142` | Pending | N1-T1 | Proof or implication test | P3/P4 sections |
| COMPAT-INFO-13 | 1 | §15 P3 | `:115-117` | Pending | N1-T1 | Review | P3 section |
| COMPAT-INFO-14 | 1 | §19 | — | Pending | N1-T1 | Review | Refutation record if any |
| COMPAT-INFO-15 | 2 | §9 | SOURCE vs repo summary | Pending | N1-T2 | Review | Audit table |
| COMPAT-INFO-16 | 2 | §9, user decision | Two divergent texts | Pending | N1-T2 | Review | Canonical F-C3 doc |
| COMPAT-INFO-17 | 2 | §9, Spec B O1–O5 | `formulacao-fc3:62-82` | Pending | N1-T2 | Review | Canonical doc §networks |
| COMPAT-INFO-18 | 2 | §9 `d_ss` | `formulacao-fc3:59-60` | Pending | N1-T2 | Review | Canonical doc |
| COMPAT-INFO-19 | 2 | §8 P7, §9 | `fcc.py` `separada` lacks CA5 | Pending | N1-T2 | Review | Canonical doc |
| COMPAT-INFO-20 | 2 | §17 N1 item 1 | `cuts.py:254` | Pending | N1-T2 | Review | Canonical doc |
| COMPAT-INFO-21 | 2 | §9 | SOURCE cites F-OD | Pending | N1-T2 | Review | Canonical doc |
| COMPAT-INFO-22 | 2 | §9 | P8/P11 `HYPOTHESIS` | Pending | N1-T2 | Review | Relabelled table |
| COMPAT-INFO-23 | 2 | user decision | — | Pending | N1-T2 | Review record exists | MR-F3 record |
| COMPAT-INFO-24 | 3 | §19 | No new module | Pending | N1-T3 | Diff of protected files | New modules |
| COMPAT-INFO-25 | 3 | §17 N1, §19 | `verify_fcc.py` covers F-CC `qij` only | Pending | N1-T3 | F-C3 equivalence test | Verify output |
| COMPAT-INFO-26 | 3 | §13 edge cases | — | Pending | N1-T3 | Instance list review | Validation set |
| COMPAT-INFO-27 | 3 | §8 | F-CC + K not measured | Pending | N1-T3 | F-CC + K equivalence test | Verify output |
| COMPAT-INFO-28 | 3 | §19 | — | Pending | N1-T3 | Stop rule | Disagreement log |
| COMPAT-INFO-29 | 3 | §9 | — | Pending | N1-T3 | LP invariants | CSV checks |
| COMPAT-INFO-30 | 3 | §9 | SOURCE §§8–9 analytical | Pending | N1-T3 | SOURCE regressions | Comparison table |
| COMPAT-INFO-31 | 4 | §10 | `run_r7_plato.py:118-166` | Pending | N1-T4 | R7 reproduction | Corrected metrics CSV |
| COMPAT-INFO-32 | 4 | §17 N1 item 2 | 610-row pool | Pending | N1-T4 | Script inputs review | — |
| COMPAT-INFO-33 | 4 | §10 | `run_r7_plato.py:74,153` | Pending | N1-T4 | Hand check on BP pool | Witness table |
| COMPAT-INFO-34 | 4 | §10, §13 Q4 | H-desc tautological | Pending | N1-T4 | Review | Classification table |
| COMPAT-INFO-35 | 4 | §10, §12 item 5 | — | Pending | N1-T4 | Review | Classification table |
| COMPAT-INFO-36 | 4 | §10 | Original files | Pending | N1-T4 | `git diff` empty on originals | Audit note |
| COMPAT-INFO-37 | 4 | §10 | Pools truncated at 200 | Pending | N1-T4 | Review | Audit note |
| COMPAT-INFO-38 | 5 | §17 N1 item 3 | — | Pending | N1-T5 | Timestamp order | Pre-registration |
| COMPAT-INFO-39 | 5 | §19 | F3 not re-run | Pending | N1-T5 | F3 reproduction | Reproduction log |
| COMPAT-INFO-40 | 5 | §17 N1 | — | Pending | N1-T5 | CSV schema check | Diagnostic CSV |
| COMPAT-INFO-41 | 5 | §19 | — | Pending | N1-T5 | K hash equality across arms | Diagnostic CSV |
| COMPAT-INFO-42 | 5 | §7, §19 | SC excluded in F3 | Pending | N1-T5 | Review | Diagnostic CSV |
| COMPAT-INFO-43 | 5 | §8 | SharedTerminal `Δ_FCC = −0.5` | Pending | N1-T5 | Review | Report |
| COMPAT-INFO-44 | 5 | user §12 | — | Pending | N1-T5 | Review | Report |
| COMPAT-INFO-45 | 6 | §13, §17 N1 item 4 | — | Pending | N1-T6 | Trigger evaluation | Trigger record |
| COMPAT-INFO-46 | 6 | §17 N1 item 4 | — | Pending | N1-T6 | Timestamp order | Frozen rule |
| COMPAT-INFO-47 | 6 | §17 N1 item 4 | — | Pending | N1-T6 | Count ≤ 12 | Pair list |
| COMPAT-INFO-48 | 6 | §17 N1 item 4 | — | Pending | N1-T6 | Certificates | Certificates |
| COMPAT-INFO-49 | 6 | §12 item 6 | HB terminal hub | Pending | N1-T6 | Review | Shortcut check |
| COMPAT-INFO-50 | 6 | §17 N1 | — | Pending | N1-T6 | Review | Exclusion log |
| COMPAT-INFO-51 | 7 | §17 N1 | — | Pending | N1-T7 | Reader re-derivation | Decision record |
| COMPAT-INFO-52 | 7 | §17 N1/N2 | — | Pending | N1-T7 | Review | Decision record |
| COMPAT-INFO-53 | 7 | §17 N1 negative branch | — | Pending | N1-T7 | Review | Decision record |
| COMPAT-INFO-54 | 7 | §7 | — | Pending | N1-T7 | Review | Decision record |

**Coverage:** 54 total, 54 mapped to tasks, 0 unmapped (`tasks.md` not created; tasks are listed in this spec).

---

## Success Criteria

- [ ] Zero broken relative paths; every §15 item annotated; no pre-registration text changed.
- [ ] P2, P7 `PROVEN` (or `REFUTED` with record); P3, P4 with a label backed by proof or test.
- [ ] Canonical F-C3 document with provenance; MR-F3 recorded.
- [ ] Zero disagreements with `viavel` for F-C3 and F-CC + K on the validation set.
- [ ] R7 corrected metrics reproduce the published counters and the cc9 coverage of 27.
- [ ] Diagnostic CSV regenerable; every excluded arm `NOT MEASURED`.
- [ ] One decision record with one of the four categories and, if positive, one representation.

---

## Inconsistencies Found

| # | Inconsistency | Class |
|---|---|---|
| 1 | `decisao-gf1.md:37` "Não há ganho em SC" while F-CC on SC-GF2-k3 was excluded | exclusion read as result |
| 2 | P3/P4 labelled `COMPUTATIONALLY VERIFIED` without a test | unsupported label |
| 3 | P2 sums a transit bound and a free arrival informally; ignores inflow into `t ∈ J_q \ W_q` | proof gap |
| 4 | P7 does not exclude `I = J = ∅` and claims reproduced marginals | proof gap |
| 5 | `formulacao-fc3:59-60` writes `d_ss = 0` | notation error (distance vs variable) |
| 6 | `fcc.py` form `separada` omits CA5 present in SOURCE | code vs source divergence (LP value unaffected per P7 check) |
| 7 | `verify_fcc.py` uses `n ≤ 5`; F3 pre-registration states `n ≤ 9` | documentation vs test |
| 8 | `f3-fcc.csv` column `n_W` mixes raw and filtered counts | data semantics |
| 9 | R7 `max_elimina_um_Z` is a return frequency; cc9 real coverage 27, not 21 | measurement error |
| 10 | R7 `n_origens_sem_par` counts degree-zero origins | naming error |
| 11 | R7 H-desc equals the feasibility characterization (`hdesc = not match_ok`) | causal over-reading |
| 12 | `resultados-r7-plato.md:51` says R10 blocked; G1 released it | stale status |
| 13 | Spec A traceability all `Pending`; Spec B "NOT STARTED"; Spec C BLOCKED vs released; Spec D R11 as validator | stale specs |
| 14 | Backlog `:454` and `direcoes` D-5 pause column generation generically | stale status |
| 15 | Overlap says paths/cycles never touched | superseded by R11 |
| 16 | README treats `alternative-formulations/` as historical; it holds active `fcc.py` | stale |
| 17 | hc9u UB 38 (historical) vs UB 41 (baseline run) | two references, both valid with source |
| 18 | `-dirty` commit hashes in 13 files | provenance debt |
| 19 | 7/14 `CLAUDE.md` paths and ~59 paths repo-wide broken by `0f16925` | broken references |
| 20 | SOURCE relies on two unrecovered studies and on discarded F-OD | provenance gap |
| 21 | The analysis cites a consolidated F-C3 (05/10) that is unrecovered | provenance gap |
