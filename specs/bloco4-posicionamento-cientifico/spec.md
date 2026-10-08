# Block 4 — Scientific Positioning (MIN-STATION) Specification

Scope: T22 from `docs/technical/plans/historico/backlog-continuacao.md` — map the overlap with Das, Hanaka,
Melissinos and Ono, *Charging Station Placement for Anonymous Mobile Agents: A Parameterized
Complexity Perspective*, IJCAI-26, pp. 72–80, and rewrite the project's contribution claims on top
of that comparison.

Every statement in Current State was checked in this session against **primary sources**: the IJCAI
2026 PDF (all nine pages), the Das original PDF, the SBPO PDF, and the project's own versioned
documents and code. The internal assessment (`parecer`) was used only to decide where to look; each
of its claims reused here was re-verified against the paper itself, and one of them is corrected
below.

---

## Relationship with Blocks 1–3

### What Block 1 supplies as evidence (complete, committed)

| Deliverable | Evidence | Role in Block 4 |
|---|---|---|
| Oracle corrected for permanence in `S∩T` | `cuts.py`, commit `dc83ac9`; `verify_t1_oracle_sT.py`, 618 sets `C`, 0 divergences | Supports the erratum against the paper's `D` construction, and shows the project has a working corrected artifact |
| Independent validator by `(v, battery)` states | `experiments/cuts/independent_validator.py`, commit `658099a` | A second, non-flow feasibility mechanism; relevant when comparing against the paper's matching characterization |
| Terminal regression suite | `verify_t3_regressao_terminais.py`, commit `e0c36e7`; re-run clean this session | Keeps the `S∩T` claims reproducible |
| Equivalence proof of the base formulation | `validacao-formulacao-base.md` §5.5, commit `97b290d` | The evidence behind any claim about the ILP being a faithful model of Das's problem |

Block 4 does not reopen correctness. It only cites these artifacts as evidence.

### What Block 2 supplies as evidence (complete, in the working tree)

Deterministic model construction (`cortes_ordenados`), the budget decision (`WorkLimit` for method
comparison), the consolidated benchmark (`grupos_origem.csv`, `duplicata_de`), the instrumentation
schema (`schema-instrumentacao-mip.md`) and the paired-comparison protocol. **Block 4 must grade
the strength of every experimental claim by whether the result satisfied this protocol.** Results
from E0–E8, and from E9–E13, predate it; results from the Block 3 pilot and Phase E were produced
under it. That difference is a classification input, not a reason to discard older results.

### What Block 3 supplies, and what it leaves pending

Block 3 is executed. Verified outcomes this session:

| Family / line | Outcome | Effect on the contribution narrative |
|---|---|---|
| BP | **DISCARDED** at T20 — the "yes" side was not the predicted hard side | Removes BP as a positive experimental contribution; keeps it as a negative result |
| HB | **DISCARDED** at T20 — every method proves the optimum in under 1 s at the largest size | Same: negative result, plus the C6 measurement it enabled |
| SC | **PROMOTED**, Phase E executed at `k ∈ {8,9}` | The one structural family with a positive, protocol-compliant experimental result |
| TR | Validated only; did not enter the pilot | Generator exists; no experimental claim |
| T16 / CBI | Declared **not applicable**, A2 stays closed (E12) | Forbids any claim that CBI is a competitive method for Das |
| C6 (knapsack first-hop Hall) | Derived, validated for RHS `δ ≥ 2`, measured; **does not close the HB gap** | A validated inequality with a measured negative outcome |
| all-V disaggregation (T18) | Diagnostic only; LP gain does not justify `O(m·|A_r|)` | Forbids presenting it as a competitive formulation |

**Can be closed now, independently of anything else:** the whole literature comparison — problem
definitions, `G^r`, matching/Hall, Set Cover, Bin Packing, complexity, special classes, the absence
of an ILP in the literature, and the audit of the project's current claims.

**Still depends on Block 3 (and must be marked pending, not guessed):** only the final wording of
the experimental narrative around SC, and any statement about the relative value of C6 and of the
disaggregation. The outcomes are known; what is not yet written is how they read as contributions.

---

## Current State

Classified per the categories requested. Each line states how it was verified.

### Already in the literature — verified in the primary source this session

- **The problem is the same.** IJCAI p.73 defines CHARGING STATION PLACEMENT on an undirected `G`,
  with `S, T ⊆ V`, `|S| = |T| = k`, integer capacity `r`, minimum-cardinality `C ⊆ V`, feasibility
  by a bijection `f: S → T` with a `(C,r)-walk` for every pair, and the agents explicitly anonymous
  ("the final agent–terminal matching is not restricted", p.73). This is the project's problem, with
  `k` where the project writes `m`.
- **`G^r` is in the literature, as a proposition.** IJCAI p.74 defines `G^r` and p.75 **Proposition
  1** states that `(G,S,T,r,c)` is a yes-instance iff `(G^r,S,T,1,c)` is. The project's reach
  digraph is the same object. This transformation cannot be claimed as a project contribution.
- **Feasibility by matching is in the literature, as a theorem.** IJCAI p.75: the auxiliary digraph
  `D` on `S ∪ T ∪ C`, **Lemma 1** (a `(C,r)`-walk exists iff a directed `s–t` path exists in `D`),
  the bipartite graph `H`, **Lemma 2** (`C` is feasible iff `H` has a perfect matching) and
  **Theorem 1** (polynomial decision, returning the bijection and the walks), hence **Corollary 1**
  (NP membership) and **Corollary 2** (`n^{O(c)}`). The project's `is_valid_cut` and its independent
  validator implement this characterization.
- **`S∩T` is anticipated in the paper's `H`.** IJCAI p.75 explicitly creates two vertices `u_w` and
  `v_w` for `w ∈ S∩T`, "because we may have optimal solutions that do not match `s` with `t`, even
  if `s = t`". The authors were aware of the overlap case.
- **Set Cover is the source of the hardness, with the objective preserved.** IJCAI **Theorem 3**
  (p.76) reduces SET COVER to the problem on split and bipartite graphs with `r = 1`, building a
  clique `W = {w_F}` plus independent `s_u, t_u`, with `w_F s_u` iff `u ∈ F` and `w_F t_u` for all
  pairs; the text states "our reduction in Theorem 3 preserves the objective value exactly", giving
  **Corollary 3**: no `(1−ε) ln k` approximation unless P=NP.
- **Bin Packing is the source of the `dts`/`dtc` hardness, with the bound `2n+m`.** IJCAI **Theorem
  4** (p.76) reduces UNARY BIN PACKING: `m` bin vertices `v_j` each with `B` destination leaves,
  item vertices `u_i` each with `e_i` origin leaves, and the edge `l^i_{e_i+j} v_j` connecting item
  `i` to bin `j`; the instance `(G,S,T,1,2n+m)` is a yes-instance iff the packing is, and "the
  construction forces any feasible `C` to include `{u_i} ∪ {v_j}`, and exactly one vertex from
  `{l^i_{e_i+1},…,l^i_{e_i+m}}` for each `i`".
- **Classical hardness beyond Das's original.** IJCAI **Theorem 2**: NP-hard for `r = 1` on planar
  bipartite with `Δ = 6`, for `r = 1` on bipartite with `Δ = 4`, and for `r = 3` on planar bipartite
  with `Δ = 3`, all by reductions from VERTEX COVER (proofs omitted for space). **Theorem 5**:
  W[1]-hard by `fvs + c`, with an ETH lower bound, from `(k,r)`-CENTER.
- **Positive algorithmic results.** FPT in `k` (**Theorem 6**, `k^{O(k)}`, via a "connecting forest"
  and WEIGHTED STEINER TREE — with the paper's own footnote that this forest may share vertices);
  FPT by modular-width (**Theorem 7**, `2^{mw}`); FPT by vertex cover (**Theorem 8**,
  `2^{2vc²+vc}`, which internally builds a SET COVER instance); polynomial on trees for the
  generalized EXT- version with pre-placed stations (**Theorem 9**); and a `k`-approximation
  (**Theorem 10**).
- **Das's original, for comparison.** `min-station-das.pdf` (journal preprint; preliminary version
  at CALDAM 2025) defines MIN-STATION identically, calls `v ∈ S ∪ T` a *terminal*, allows several
  robots to recharge at one station simultaneously, proves NP-hardness by reduction from 3,3-SAT for
  degree at most 6, and gives linear-time paths and quadratic-time cycles. It does **not** contain
  `G^r`, the matching characterization, or any ILP.

### Disproven novelty — things the project must stop treating as its own

- **The reach digraph / `G^r` equivalence.** Published as Proposition 1.
- **Feasibility checking by reachability plus bipartite matching.** Published as Lemmas 1–2 and
  Theorem 1. The project's `is_valid_cut` and independent validator are *implementations* of a
  published characterization, however much engineering they required.
- **The BP structural family as a construction.** The project's BP generator reproduces Theorem 4's
  gadget, down to the value `2n + q` (`2n + m` in the paper's notation). The project's own
  `familias-estruturais.md` already derives the bound and the assessment already attributes the
  `OPT = 2n+q` ⟺ partition equivalence to "artigo p.76" — but the family must never be described as
  a new reduction. It was discarded at T20 anyway.
- **The SC family as a construction.** SC-GF2 instantiates Theorem 3's split/bipartite reduction
  (`s_x–w_a` iff `a·x = 1`, `w_a–t_x` complete) with a classical GF(2) set system. The *instance
  family* is an instantiation; what is not in the paper is the experimental use.

### Candidate novelty — survives this session's comparison, still to be confirmed by the search

- **There is no ILP for this problem in the literature consulted.** The IJCAI paper contains no
  formulation, no solver, no experiments and no benchmark, and its bibliography contains no ILP work
  on CHARGING STATION PLACEMENT. Das's original contains none either. The gap the SBPO abstract
  claims ("has not yet been addressed through Integer Linear Programming") is **not closed by the
  IJCAI paper**. This must still be checked against the wider literature (see Required Literature
  Checks) before being asserted.
- **The exact `y`-space covering reformulation.** The project's `direcoes-pli-min-station.md`
  Theorem 6 `[Provado]` states `C` is feasible iff `C ∩ Z ≠ ∅` for every `Z ∈ 𝒵`, i.e. MIN-STATION
  *is* a set covering over an implicit exponential family, with Theorem 7 (each `y(Z) ≥ 1` is a
  Chvátal–Gomory rank-1 cut) and Corollary 7.1 (`LP_cov ≥ z_LP`). This is the **converse direction**
  of IJCAI Theorem 3: the paper reduces *from* Set Cover to prove hardness; the project reformulates
  the problem *into* a covering model to obtain bounds. They are not the same result, and conflating
  them would be an error in either direction. The project's own text already notes the inequality is
  "o análogo exato da *cut-set inequality* `Σ y ≥ ⌈D/C⌉`" of capacitated network design, which is
  the honest qualifier to keep.
- **Two errata in the published paper, both reproduced.**
  1. **The literal construction of `D` admits a station-free relay.** Arcs leave `u ∈ S ∪ C` and
     enter `v ∈ N_r(u) ∩ (T ∪ C)`. An intermediate vertex of a directed path therefore needs an
     in-arc (so `v ∈ T ∪ C`) and an out-arc (so `v ∈ S ∪ C`); with `v ∉ C` this forces exactly
     `v ∈ S∩T`. On the project's `SharedTerminal` gadget (star, centre `v`, leaves `p1..p4`,
     `r = 1`, `S = {v,p1,p2}`, `T = {v,p3,p4}`), `D` has the path `p1 → v → p3` with `C = ∅`, while
     the true optimum is `1`. **I re-derived this mechanism from the paper's text this session; the
     assessment's §2.2 claim is correct**, and the diagnosis is sharper than the assessment states:
     the failure is confined to `S∩T \ C`, not to `S∩T` in general. It is a specification gap in one
     construction; it does not touch Lemma 2's characterization nor any theorem.
  2. **Theorem 10's proof sketch inverts an inequality.** The text reads "the length of any
     `(C*,r)`-walk between `s*` and `f(s*)` is at most `dist(s*,f(s*))`"; a walk's length is at
     least the distance. The conclusion survives, and the assessment records a substitute argument.
- **The benchmark and the experimental diagnosis.** No benchmark for this problem exists in either
  paper or in their bibliographies. Strength of this claim depends on the search below.

### Project-specific implementation (not novelty by itself)

The aggregate-flow compact ILP, the cut families as code, the integer core as a solver-backed bound,
the CBI machinery, the harness, the generators and the manifest. Each may support a T3/T4/T5
contribution, never a T1 one on its own.

### Obsolete or incomplete claims found in the project's documents

- **`RESEARCH.md` does not cite the IJCAI paper.** Its §7 "Fontes principais" lists only Das, the
  SBPO article and the current base formulation. Verified: zero occurrences of "IJCAI".
- **`docs/project-overview.md` does not cite it.** Zero occurrences.
- **`docs/technical/reference/tecnico/source-map.md` does not cite it** — and this is the document
  `CLAUDE.md` designates for "Comparar documentos/artigos". It describes exactly three sources:
  Das's original, the SBPO article, and the all-vertices formulation PDF. Zero occurrences of
  "IJCAI".
- By contrast, **30 technical documents already cite the paper**, including the assessment, the
  Block 3 evidence documents and most `resultados-e*-pli.md`. The gap is confined to the three
  top-level positioning documents.
- **The SBPO abstract carries the project's strongest public novelty claim**: "O problema é recente,
  NP-difícil em grafos gerais e ainda não tratado por meio de Programação Linear Inteira (PLI)" /
  "has not yet been addressed through Integer Linear Programming (ILP)". Two qualifications are
  needed and neither is currently written anywhere: (a) the SBPO formulation restricts stations to
  `V∖(S∪T)`, so it models a **variant**, not Das's problem — the all-V baseline came later; (b) the
  claim's scope is bounded by the literature search that was done for it, which is not recorded.
- **No "first"/"unprecedented" overclaim was found in the Markdown documents.** A grep for
  novelty words returned only chronological statements internal to the project (for example "a
  primeira formulação de PLI do projeto" in `docs/technical/README.md`). The exposure is the
  *absence* of the IJCAI frame, not an inflated adjective.

### Unclear / needs a literature check

- Whether any work outside these two papers has formulated this problem (or a close variant) as an
  ILP, which is what the SBPO claim depends on.
- Publication order and priority between the SBPO article (LVIII SBPO) and IJCAI-26, both 2026.
- Whether the `(C,r)`-walk covering reformulation, or an equivalent hitting-set view over min-cut
  sets, already appears in the capacitated network design or shortest-path-hitting-set literature
  that the paper cites ([Agarwal et al., 2016] SHORTEST-PATH HITTING SET is the nearest candidate).

---

## Problem Statement

The project's scientific positioning predates the IJCAI 2026 paper, and the paper closes several
things the project has been treating as open ground. `G^r` is a published proposition, feasibility
by reachability-plus-matching is a published theorem, and the two structural families the project
built in Block 3 (BP and SC) instantiate the paper's own reductions. At the same time the three
documents that carry the project's scientific frame — `RESEARCH.md`, `docs/project-overview.md` and
`docs/technical/reference/tecnico/source-map.md` — do not cite the paper at all, while thirty technical
documents already do; and the project's one public novelty claim, in the SBPO abstract, asserts that
the problem "has not yet been addressed through Integer Linear Programming" without a recorded
literature search and without noting that the SBPO formulation models a restricted variant. Without
a systematic comparison, the project risks two symmetric failures: presenting known results as its
own, and discarding genuine contributions (the covering reformulation, the corrected artifacts, the
benchmark, the negative results) merely because they are built out of known components.

## Scientific Positioning Questions

The task exists to answer these, in this order. Each maps to a user story below.

1. **Is the problem literally the same?** Compare the definitions of Das's original, the IJCAI
   paper, the project's base formulation, the SBPO variant, and the weighted and directed extensions
   — attribute by attribute, without mixing variants.
2. **What theory is already published?** `G^r`, matching and Hall, Set Cover, Bin Packing, classical
   and parameterized complexity, approximation, special classes.
3. **What remains on the ILP side?** Separate the formulation, the `S∩T`/permanence semantics, the
   equivalence proof, and the computational evaluation — and judge each on its own.
4. **Which claims survive?** Classify every candidate contribution and audit every claim the project
   currently makes.
5. **What has to change in the documents?** Bibliography and the specific sentences that must be
   rewritten.
6. **What must wait?** The experimental narrative that depends on Block 3's consolidated results.

## Literature Scope

**Primary, mandatory, already in the repository:**
- `docs/technical/reference/novo_artigo_das_2026.pdf` — IJCAI-26, pp. 72–80. Read in full.
- `docs/technical/reference/min-station-das.pdf` — Das's original (journal preprint; preliminary
  version CALDAM 2025).
- `docs/technical/reference/artigo-sbpo.pdf` — the project's own prior publication.

**Secondary, read only the parts that a specific claim depends on**, from the IJCAI bibliography:
[Das, 2025] (CALDAM version), [Agarwal et al., 2016] SHORTEST-PATH HITTING SET, [Storandt and Funke,
2013], [Kundu and Saha, 2018; 2021; 2023], [Kumar et al., 2025], [Jansen et al., 2013] (unary bin
packing parameterized by bins), [Katsikarelis et al., 2019] (`(k,r)`-center).

**Directed search, bounded by the claims the project intends to keep** — not a systematic review.
The search is specified in Required Literature Checks and stops when those claims are resolved.

## Goals

- [ ] The IJCAI 2026 paper is a first-class source in the project's bibliography and in the three
      positioning documents that currently omit it.
- [ ] A single overlap matrix covers every theme listed in Overlap Matrix Requirements, each row
      carrying a relation type and a citation or a repository artifact.
- [ ] Every contribution the project currently claims, or intends to claim, carries a category
      (T1–T5) and a status (`KEEP`, `QUALIFY`, `REMOVE`, `EXPERIMENTAL ONLY`, `ENGINEERING ONLY`,
      `PENDING BLOCK 3`, `UNRESOLVED`).
- [ ] No idea already in the IJCAI paper appears anywhere as a project novelty, and no genuine
      contribution is dropped merely because it is assembled from known components.
- [ ] The SBPO ILP-gap claim is either confirmed with a recorded search, or qualified in writing.
- [ ] Negative results are recorded as experimental contributions, not omitted.
- [ ] Claims that depend on Block 3 are marked pending rather than filled in by assumption.

## Out of Scope

| Item | Reason |
|---|---|
| Writing the paper, the dissertation, or any section of them | T22 produces the positioning evidence, not the final text |
| Creating a new formulation, cut, or structural family | Blocks 1–3 are closed; inventing work to fill a novelty gap is explicitly forbidden |
| Changing C6, rerunning the pilot or Phase E, reopening CBI | Block 3 is executed; its verdicts stand |
| Re-running E0–E14 | Their evidence strength is classified, not regenerated |
| Reopening correctness (Block 1) or the experimental protocol (Block 2) | Complete; cited as evidence |
| A systematic literature review | The search is bounded by the claims being defended |
| Performance work of any kind | Not a positioning activity |
| Inventing a new scientific contribution to compensate for a lost one | Explicitly forbidden; the finding is the output |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Where the overlap matrix lives | `docs/technical/reference/documentacao-projeto/overlap-ijcai2026-min-station.md`, a new reference document | Matches the naming of every other evidence document produced by Blocks 1–3 | n |
| Whether `source-map.md` gains a fourth source or a rewrite | Add the IJCAI paper as a fourth numbered source with its own "Papel na pesquisa" and "Limite da fonte", in the existing style | The file's structure already supports it; a rewrite would churn text that is still correct | n |
| How to treat the SBPO article | As a prior publication of the project that models a **variant** (stations in `V∖(S∪T)`), whose abstract claim must be qualified rather than silently dropped | It is the group's own published record; the honest move is a written qualification, not a retraction that no reader can see | n |
| Priority between SBPO (LVIII SBPO) and IJCAI-26 | Treat as **UNRESOLVED** until the two publication dates are established from the official records | Both are 2026; guessing either way would be an unsupported priority claim | n |
| Status of the two errata found in the published paper | Record them as verified observations about the literature, with the reproducing artifact cited; do not inflate them into a headline contribution | Both are real and reproduced, but one is a specification gap in a proof construction and the other a typo-level inversion whose conclusion survives | n |
| Granularity of this spec | Six user stories inside one `spec.md`, no separate `design.md`/`tasks.md` | Same pattern as Blocks 1–3, and the user asked for the spec only | n |
| What counts as "the literature says X" | A page-level citation to a primary source read in full, never the internal assessment alone | The assessment is a pointer; this session already found one of its claims needed sharpening (the `S∩T` mechanism) | n |

**Open questions:** none — all resolved or recorded above.

---

## Mathematical and Bibliographic Preconditions

Gate rule: a claim does not enter the final contribution table while the evidence it rests on is
`UNRESOLVED`. It is recorded as `UNRESOLVED`, never as novelty.

| # | Claim it supports | Status after this session | What closes it |
|---|---|---|---|
| 1 | `G^r` is prior art | **VERIFIED** — IJCAI Proposition 1, p.75 | — |
| 2 | Matching feasibility is prior art | **VERIFIED** — Lemmas 1–2, Theorem 1, p.75 | — |
| 3 | BP reproduces a published gadget | **VERIFIED** — Theorem 4, p.76, bound `2n+m` | — |
| 4 | SC instantiates a published reduction | **VERIFIED** — Theorem 3, p.76 | — |
| 5 | The paper contains no ILP and no experiments | **VERIFIED** by full read of all nine pages | — |
| 6 | No ILP for this problem exists anywhere | **UNRESOLVED** — only two papers checked | Directed search (LC-1) |
| 7 | The `D` construction admits a station-free relay in `S∩T \ C` | **VERIFIED** — mechanism re-derived this session; reproduced by the `SharedTerminal` gadget | — |
| 8 | Theorem 10's sketch inverts an inequality | **VERIFIED** by reading p.78 | — |
| 9 | The `y`-space covering reformulation is not prior art | **UNRESOLVED** — it is the converse of Theorem 3, and the project itself calls it an analogue of capacitated-network-design cut-set inequalities | Directed search (LC-2) |
| 10 | No public benchmark exists for this problem | **UNRESOLVED** — absent from both papers, not searched beyond them | Directed search (LC-3) |
| 11 | Priority between SBPO and IJCAI-26 | **UNRESOLVED** | Publication dates (LC-4) |

---

## User Stories

### P1: T22.1 — Compare the problem definitions, attribute by attribute ⭐ MVP

**User Story**: As a researcher about to claim anything, I want a formal attribute-by-attribute
comparison of Das's original, the IJCAI paper, the project's base formulation, the SBPO variant and
the weighted/directed extensions, so that no novelty argument is built on a variant mismatch.

**Why P1**: Every later comparison is void if the problems differ. It also protects against the
opposite error — dismissing a project result because it was measured on an extension.

**Objective.** One table, one row per attribute, one column per source, with the differences named.

**Current problem.** The project already separates `classe = principal` from the weighted and
directed extensions in `manifest.csv` and in `CLAUDE.md`, and `source-map.md` separates Das from
SBPO — but no document puts the IJCAI definition beside them.

**Expected behaviour.** Attributes covered at minimum: graph type, directedness, weights, autonomy
semantics, where stations may be placed, objective, number of agents, anonymity, `S`, `T`, `S∩T`,
permanence, concurrent recharging at one station, and whether the final matching is constrained.

**Files affected:** the new overlap document; `source-map.md` for the source descriptions.

**Acceptance criteria:**

1. The system SHALL produce one row per attribute and one column per source, covering Das's original, IJCAI 2026, the project base formulation, the SBPO variant, and the weighted and directed extensions.
2. WHEN two sources agree on an attribute, THEN the system SHALL cite the page or the file where each states it, rather than asserting agreement.
3. The system SHALL record explicitly that the IJCAI paper studies the anonymous version with an unconstrained final matching, and that this matches the project's problem.
4. The system SHALL record that the SBPO formulation restricts stations to `V∖(S∪T)` and therefore models a variant, not Das's problem.
5. IF any attribute differs between the project's base formulation and Das's original, THEN the system SHALL mark that difference and state which published results stop applying.
6. The system SHALL NOT mix results measured on the weighted or directed extensions into any statement about Das's problem.

**Tests required:** none — a document review. The check is that every cell carries a citation.

**Evidence to produce:** the definitions table inside the overlap document.

**Risks:** terminology drift — the paper writes `k` for the number of agents where the project writes
`m`, and `c` for the station budget. A silent mismatch would corrupt every later comparison.

**Dependencies:** none. Blocks every other story.

**Out of scope:** judging novelty; this story only establishes that the objects are comparable.

**Independent Test**: a reader can tell, from the table alone, whether a given published theorem
applies to the project's baseline.

---

### P1: T22.2 — Map the published theory against the project's constructs

**User Story**: As a researcher deciding what to claim, I want each theoretical construct the
project uses mapped onto the published result it corresponds to, so that implementations of known
theorems are never presented as theory.

**Why P1**: This is where most of the overlap sits, and this session already found four items that
are prior art.

**Objective.** The overlap matrix rows for `G^r`, matching, Hall, Set Cover, Bin Packing,
NP-hardness, approximation, FPT, vertex cover, modular-width, trees, paths and cycles.

**Current problem.** The assessment §6 holds a partial version of this table, with page citations,
but it predates Blocks 1–3, leaves the positioning explicitly "Em aberto", and at least one of its
entries needed sharpening this session.

**Expected behaviour.** Every row states the published result with a page citation, the project
artifact, a relation type from the fixed vocabulary, and a sustainability verdict.

**Files affected:** the overlap document; `direcoes-pli-min-station.md` for the cut-by-cut rows.

**Acceptance criteria:**

1. The system SHALL map `G^r` to IJCAI Proposition 1 and SHALL classify the project's reach digraph as `SAME`, not as a contribution.
2. The system SHALL map the project's feasibility checking — `is_valid_cut`, the integer oracle and the independent validator — to IJCAI Lemmas 1–2 and Theorem 1, and SHALL classify them as `IMPLEMENTATION` of a published characterization.
3. WHEN the project's Theorem 6 (`y`-space covering reformulation) is compared with IJCAI Theorem 3, THEN the system SHALL state that they run in opposite directions — the paper reduces *from* Set Cover for hardness, the project reformulates *into* a covering model for bounds — and SHALL NOT present either as the other.
4. The system SHALL produce a per-family cut table with columns for mathematical origin, prior literature and novelty, covering C1, C2, C3, C4, C5, C6 and any other family used in an experiment.
5. WHERE a cut family is derived in the project's own documents as a special case of its Theorem 6, the system SHALL record that derivation rather than claiming an independent inequality.
6. The system SHALL record the IJCAI results on special classes and parameters — trees, paths, cycles, FPT in `k`, modular-width, vertex cover, `dts`, `dtc`, `fvs`, and the `k`-approximation — and SHALL state for each whether the project explored it, paused it, or never touched it.
7. The system SHALL record the two errata found in the paper, each with the page, the mechanism and the reproducing artifact, and SHALL state explicitly that neither refutes the paper's theorems.

**Tests required:** none beyond citation checking. The `SharedTerminal` erratum is already covered by
the Block 1 regression suite, which was re-run clean this session.

**Evidence to produce:** the theory rows of the overlap matrix and the cut table.

**Risks:** over-reading the errata. Both are real, but one is a gap in a construction used inside a
proof and the other a typo-level inversion; inflating them would be its own overclaim.

**Dependencies:** T22.1.

**Out of scope:** fixing anything in the project's cuts; this is classification only.

**Independent Test**: every row cites either a page of a primary source or a repository artifact.

---

### P1: T22.3 — Analyse the ILP contribution on four separate axes

**User Story**: As a researcher who cannot assume "the paper has no ILP" means "our ILP is a strong
contribution", I want the formulation, the `S∩T` semantics, the equivalence proof and the
computational evaluation judged separately, so the claim matches what each one actually earns.

**Why P1**: This is the project's central candidate contribution and the one most exposed to
overclaiming.

**Objective.** Four independent verdicts, not one bundled claim.

**Current problem.** Verified this session: neither paper contains an ILP, a solver or experiments,
and no ILP for this problem appears in either bibliography. That makes the gap real so far, but the
project has never recorded how hard the formulation is to derive, nor whether its computational
usefulness is demonstrated rather than asserted.

**Expected behaviour.**
- *Formulation.* Is the aggregate flow over the reach digraph more than a routine translation of a
  standard flow model onto `G^r`? Judge naturalness, proximity to textbook flow, and derivation
  difficulty, and say so plainly.
- *Semantics.* Does the `S∩T` and permanence treatment add anything beyond making the project's own
  model correct? Note that Das's original already allows terminals in both sets, and that the
  paper's `H` already splits `u_w`/`v_w` — so the semantics are required by the problem, not
  invented by the project. The erratum against `D` is the part that is genuinely about the
  literature.
- *Proof.* Does `validacao-formulacao-base.md` §5.5 contain content beyond routine verification?
- *Computation.* What do the solver results actually demonstrate, graded by Block 2 compliance?

**Files affected:** the overlap document; the contribution table.

**Acceptance criteria:**

1. The system SHALL issue a separate verdict for the formulation, the `S∩T` semantics, the equivalence proof and the computational evaluation, and SHALL NOT merge them into a single claim.
2. The system SHALL record that neither primary source contains an ILP, a solver or experiments, citing the full read rather than the abstract.
3. IF the directed search finds any prior ILP for this problem or a close variant, THEN the system SHALL downgrade the formulation claim accordingly and record the source.
4. The system SHALL assess the formulation's derivation difficulty and its proximity to a standard flow model honestly, and SHALL NOT infer strength from the absence of a competing ILP alone.
5. WHEN the `S∩T` treatment is classified, THEN the system SHALL distinguish the part that only fixes the project's own model from the erratum against the paper's `D` construction.
6. The system SHALL grade each computational claim by whether its experiment satisfied the Block 2 paired-comparison protocol, and SHALL label pre-protocol results as weaker evidence rather than discarding them.
7. The system SHALL classify the all-V disaggregation as a diagnostic with a measured negative outcome, consistent with T18, and SHALL NOT present it as a competitive formulation.

**Tests required:** none; the computational grading reads existing CSVs and reports.

**Evidence to produce:** the ILP section of the overlap document, with the four verdicts.

**Risks:** the tempting inference "no ILP in the literature, therefore our ILP is a strong
contribution". Criterion 4 exists to block exactly that.

**Dependencies:** T22.1, T22.2, and LC-1 from Required Literature Checks.

**Out of scope:** changing the formulation or the proof.

**Independent Test**: each of the four verdicts can be read, and disagreed with, on its own.

---

### P2: T22.4 — Classify every contribution and audit every current claim

**User Story**: As a researcher preparing to write, I want each candidate contribution categorised
and each sentence the project currently asserts audited against evidence, so that what gets written
is exactly what can be defended.

**Why P2**: It consumes the output of the three P1 stories.

**Objective.** Two tables: candidate contributions with a category and a status, and current claims
with a recommended rewrite.

**Current problem.** No contribution table exists. The claims are scattered, and the only strong
public one — the SBPO ILP gap — has no recorded search behind it.

**Expected behaviour.** Candidates A–I from the backlog brief are all assessed, including the ones
this session expects to come out negative.

**Acceptance criteria:**

1. The system SHALL assign every candidate contribution exactly one category among T1 theoretical, T2 algorithmic, T3 computational, T4 experimental and T5 engineering, and SHALL NOT present a T4 or T5 item as T1.
2. The system SHALL assign every candidate exactly one status among `KEEP`, `QUALIFY`, `REMOVE`, `EXPERIMENTAL ONLY`, `ENGINEERING ONLY`, `PENDING BLOCK 3` and `UNRESOLVED`.
3. The system SHALL assess candidates A through I explicitly, including the CBI line, which SHALL be presented as an investigated line with a negative verdict rather than as a competitive method.
4. WHEN a claim cannot be classified with the sources available, THEN the system SHALL mark it `UNRESOLVED` and SHALL NOT mark it as new.
5. The system SHALL audit the SBPO abstract claim, recording the file, the current sentence, the problem, the evidence and the recommended replacement.
6. The system SHALL record negative results — CBI not beating the core, the Lagrangian below the LP, BP and HB discarded, C6 not closing the HB gap, the disaggregation not justifying its cost — as experimental contributions with their protocol grade, and SHALL NOT omit them.
7. The system SHALL NOT remove a contribution solely because it is assembled from known components, and SHALL state, for each kept item, which part is the project's.
8. The system SHALL produce, for every claim it recommends changing, a tuple of file, current claim, problem, evidence and recommended claim.

**Tests required:** none; the audit is verified by its citations.

**Evidence to produce:** the contribution table and the claim-correction list.

**Risks:** an audit that quietly becomes a defence. The mitigation is that the status vocabulary
includes `REMOVE` and `UNRESOLVED`, and that the three P1 stories fix the facts before this one
starts.

**Dependencies:** T22.1, T22.2, T22.3.

**Out of scope:** editing the documents; this story only specifies the edits.

**Independent Test**: for any contribution in the table, a reader can trace its status to a cited
page or artifact.

---

### P2: T22.5 — Update the bibliography and specify the document changes

**User Story**: As a maintainer of the project's documentation, I want the IJCAI paper cited where
the scientific frame is set, and a precise list of the sentences to change, so that the positioning
is consistent across the repository rather than correct only in the technical reports.

**Why P2**: Mechanical, but it is where the gap is most visible today.

**Objective.** A complete bibliographic record, and a file-by-file change list.

**Current problem.** Verified: `RESEARCH.md`, `docs/project-overview.md` and `source-map.md` contain
zero occurrences of "IJCAI", while 30 technical documents cite it.

**Acceptance criteria:**

1. The system SHALL record the full reference for the IJCAI 2026 paper — authors, title, venue, pages — and for Das's original, including its CALDAM 2025 preliminary version.
2. The system SHALL add the IJCAI paper to `source-map.md` as a numbered source with its role and its limits, in the style of the existing entries.
3. The system SHALL list, per file, the current sentence, why it must change, and the evidence, for at least `RESEARCH.md`, `docs/project-overview.md`, `source-map.md`, `base-formulation.md` and `direcoes-pli-min-station.md`.
4. WHEN a document already cites the paper correctly, THEN the system SHALL leave it unchanged and SHALL record that it was checked.
5. The system SHALL NOT edit any scientific document during T22's analysis phase; the edits are a separate, later step driven by this list.
6. The system SHALL produce a scientific dependency map showing, for each claim, whether it rests on a proof, an experiment, the benchmark, Block 3 or the literature.

**Tests required:** a grep confirming that every file on the change list is covered, and that no file
outside the list was modified during the analysis phase.

**Evidence to produce:** the bibliography record, the change list and the dependency map.

**Risks:** touching the documents while analysing, which would make the audit unverifiable.
Criterion 5 forbids it.

**Dependencies:** T22.4.

**Out of scope:** applying the edits.

**Independent Test**: the change list is executable by someone who did not do the analysis.

---

### P3: T22.6 — Close the experimental narrative that depends on Block 3

**User Story**: As a researcher writing the contribution section, I want the experimental narrative
to be written only against consolidated Block 3 results, so that nothing is filled in by assumption.

**Why P3**: Block 3 is executed, but its results have to be read as contributions, which is a
different act from running them.

**Objective.** Convert the Block 3 verdicts into positioned claims, with the right strength.

**Current problem.** The Block 3 evidence documents state outcomes; no document states what those
outcomes are worth as contributions relative to the literature.

**Expected behaviour.** SC is the only promoted family and the only positive experimental claim;
BP, HB, TR, C6 and the disaggregation yield negative or diagnostic claims. The SC narrative must
also note the structural link worth making: the paper's hardness comes from Set Cover (Theorem 3,
objective-preserving, with a `ln k` inapproximability corollary), and the project's strongest bound
mechanism is the covering core — the theory and the measurement point at the same structure.

**Acceptance criteria:**

1. The system SHALL classify the SC family as an instantiation of IJCAI Theorem 3's reduction used as an experimental instrument, and SHALL NOT claim the construction as new.
2. The system SHALL classify the BP family as a reproduction of IJCAI Theorem 4's gadget, and SHALL record its T20 discard as a negative experimental result.
3. WHEN the covering core is positioned, THEN the system SHALL connect it to the paper's Set Cover hardness and inapproximability results, and SHALL state that the link is interpretive unless a proof is written.
4. The system SHALL present C6 as a derived and validated inequality whose measured effect on HB was negative, with the prediction-before-measurement record cited.
5. IF any statement about the structural families cannot be supported by a consolidated Block 3 artifact, THEN the system SHALL mark it `PENDING` rather than assert it.
6. The system SHALL grade each Block 3 experimental claim by its compliance with the Block 2 protocol, noting that the pilot and Phase E were run under it.

**Tests required:** none; the claims are read against existing CSVs and evidence documents.

**Evidence to produce:** the experimental section of the contribution table.

**Risks:** promoting the Set Cover link from interpretation to theorem without a proof.

**Dependencies:** T22.4, and the consolidated Block 3 artifacts.

**Out of scope:** running anything.

**Independent Test**: every experimental claim cites a CSV or an evidence document from Block 3.

---

## Required Literature Checks

Directed, bounded by the claims being defended. Each check has a stop condition.

| ID | Question | Why it is needed | Where to look | Stop condition |
|---|---|---|---|---|
| LC-1 | Has any work formulated this problem, or a close variant, as an ILP? | The SBPO claim and the project's main candidate contribution rest on it | Both primary papers (done: none); then the charging-station and station-placement works in the IJCAI bibliography — Kundu and Saha 2018/2021/2023, Storandt and Funke 2013, Agarwal et al. 2016, Kumar et al. 2025 — then a directed search on charging/recharge/station placement with ILP or MIP | Either a prior ILP is found, or the checked set is exhausted and recorded |
| LC-2 | Does the covering reformulation over min-cut sets already exist for this or an isomorphic problem? | The project's Theorem 6 is its strongest theoretical candidate | Capacitated network design cut-set inequalities; SHORTEST-PATH HITTING SET [Agarwal et al., 2016] | Either a matching formulation is found, or the nearest analogue is cited as a qualifier |
| LC-3 | Does a public benchmark exist for this problem? | Candidate F | Both papers (done: none); the works above | Recorded either way |
| LC-4 | What are the publication dates of LVIII SBPO and IJCAI-26? | Priority, where the two overlap | Official proceedings records | Dates recorded, or marked `UNRESOLVED` |
| LC-5 | Does Das's original contain `G^r`, matching, or anything the project attributes to the IJCAI paper? | Avoid attributing to 2026 what is already in 2025 | `min-station-das.pdf`, full read | Recorded per construct |

LC-5 is partially done: the first four pages were read this session and contain the definition, the
3,3-SAT hardness and the path/cycle results, with no `G^r` and no matching. The remaining pages,
including the Lemma 5 that the project cites for permanence, still need a full read.

## Overlap Matrix Requirements

One document, one table, with the columns: theme, Das original, IJCAI 2026, project, relation type,
sustainable novelty, evidence.

**Rows required at minimum:** problem definition; `G^r`; matching; Hall; Set Cover; Bin Packing;
NP-hardness; approximation; FPT in `k`; vertex cover; modular-width; `dts`/`dtc`; `fvs`; trees;
paths; cycles; ILP formulation; flow formulation; `S∩T`; permanence; the covering core; C1; C2; C3;
C4; C5; C6; CBI; benchmark; structural families; experimental results.

**Relation vocabulary, fixed:** `SAME`, `DIRECT CONSEQUENCE`, `ADAPTATION`, `EXTENSION`,
`IMPLEMENTATION`, `EXPERIMENTAL VALIDATION`, `NEW FORMULATION`, `NEW INEQUALITY`, `NEGATIVE RESULT`,
`OPEN / UNCLEAR`. Binary "new / not new" is not permitted where the relation is subtler.

**Every row carries evidence**: a page of a primary source, or a repository artifact, or both.

## Contribution Classification

Categories T1 theoretical, T2 algorithmic, T3 computational, T4 experimental, T5 engineering, as
defined in the backlog brief. Statuses `KEEP`, `QUALIFY`, `REMOVE`, `EXPERIMENTAL ONLY`,
`ENGINEERING ONLY`, `PENDING BLOCK 3`, `UNRESOLVED`.

Candidates to assess, with this session's starting expectation — to be confirmed or overturned by
the task, never assumed:

| Candidate | Starting expectation | Why |
|---|---|---|
| A — compact all-V ILP | `KEEP` as T1 plus T3, conditional on LC-1, with the derivation difficulty stated honestly | No ILP in either primary source |
| B — `S∩T` and permanence | `QUALIFY` — mostly correctness of the project's own model; the erratum against `D` is the part aimed at the literature | Das's original already allows terminals in both sets; the paper's `H` already splits `u_w`/`v_w` |
| C — cut families | Row by row; C1 and C3 are the project's own special cases of its Theorem 6, C4's knapsack form is proven, C6 is validated with a negative measurement | The project's own documents already derive most of them |
| D — integer covering core | `KEEP` as T3 plus T4, with the reformulation itself under LC-2 | The strongest measured bound mechanism, and the SC Phase E result supports it |
| E — CBI | `EXPERIMENTAL ONLY`, negative | E12 closed A2; T16 confirmed it is not applicable |
| F — benchmark | `KEEP` as T4 plus T5, conditional on LC-3 | No benchmark in either paper |
| G — difficulty study | `KEEP` as T4, graded by protocol compliance | E9–E14 plus the Block 3 pilot |
| H — structural families | `EXPERIMENTAL ONLY`; BP and SC are instantiations of published reductions | Theorems 3 and 4 |
| I — negative results | `KEEP` as T4, provided the question and the protocol are stated | Several are protocol-compliant |

## Claim Audit

Every claim the project asserts today gets a row: file, current sentence, problem, evidence,
recommended claim, status. The audit starts from the items this session verified:

| File | Current claim | Problem | Recommended direction |
|---|---|---|---|
| `artigo-sbpo.pdf` (abstract) | "has not yet been addressed through Integer Linear Programming" | No recorded search; and the SBPO formulation models the `V∖(S∪T)` variant, not Das's problem | Qualify on both axes, after LC-1 |
| `RESEARCH.md` §7 | Lists Das, SBPO and the base formulation as the main sources | Omits the IJCAI paper, which is the closest prior work | Add the paper and its consequences for scope |
| `docs/project-overview.md` | No IJCAI mention | Same | Add |
| `source-map.md` | Three numbered sources | Same, and this is the file `CLAUDE.md` designates for comparing documents | Add as a fourth source |
| `direcoes-pli-min-station.md` | Cites the paper in places, states Theorem 6 as the project's | Needs the explicit note that Theorem 6 runs converse to IJCAI Theorem 3, and the cut-set analogue qualifier | Qualify |
| `base-formulation.md` | Describes the baseline without positioning it against the paper | The `S∩T` semantics are required by Das, not invented here | Qualify |

The audit is not limited to these rows; it must sweep the documents listed in T22.5.

## Evidence to Produce

1. **Overlap matrix** — `docs/technical/reference/documentacao-projeto/overlap-ijcai2026-min-station.md`, with the
   definitions table, the theory rows, the cut table and the ILP section.
2. **Contribution table** — candidate, category, prior literature, project evidence, final status.
3. **Claim-correction list** — file, current claim, problem, evidence, recommended claim.
4. **Bibliography** — full references for the IJCAI paper, Das's original and its CALDAM version,
   plus every source used in the comparison.
5. **Scientific dependency map** — per claim, whether it rests on a proof, an experiment, the
   benchmark, Block 3 or the literature.

## Dependencies

```text
T22.1 ──→ T22.2 ──→ T22.3 ──→ T22.4 ──→ T22.5
                                  └────→ T22.6 (also needs consolidated Block 3 artifacts)
LC-1 ──→ T22.3 (ILP verdict) and T22.4 (SBPO claim audit)
LC-2 ──→ T22.4 (covering reformulation status)
LC-3 ──→ T22.4 (benchmark status)
LC-4 ──→ T22.4 (priority, may stay UNRESOLVED)
LC-5 ──→ T22.2 (attribution between Das 2025 and IJCAI 2026)
Blocks 1 and 2 ──→ evidence and evidence grading throughout
```

T22.1 and the literature checks can start immediately. Nothing here waits on new experiments.

## Risks

- **Defending instead of auditing.** The whole task can silently become a search for reasons the
  project is still novel. The status vocabulary includes `REMOVE`; if nothing is ever removed, the
  audit should be suspected.
- **Over-reading the two errata.** Both are verified, but neither overturns a theorem.
- **Under-claiming.** The symmetric failure: discarding the covering reformulation, the benchmark or
  the negative results because they use known components. Criterion 7 of T22.4 guards this.
- **Terminology drift** between `k`/`m` and `c`/budget.
- **An unbounded search.** LC-1 through LC-5 have stop conditions for this reason.
- **Writing the documents during the analysis**, which would make the audit unverifiable.

## Edge Cases

- IF the paper uses different terminology for an idea the project also has, THEN the system SHALL
  match on the definition, never on the term.
- IF two results look identical but rest on different hypotheses, THEN the system SHALL record the
  hypothesis difference rather than merging the rows.
- IF the project has a computational implementation of a known theorem, THEN the system SHALL
  classify it as T3 or T5, never as T1.
- IF a formulation looks new but is a direct translation of a standard flow model onto `G^r`, THEN
  the system SHALL say so.
- IF a cut is an immediate consequence of Hall or of set covering, THEN the system SHALL classify it
  as `DIRECT CONSEQUENCE`.
- IF a structural family reproduces a gadget from a published reduction, THEN the system SHALL
  classify it as `ADAPTATION` or `IMPLEMENTATION`, whatever its experimental value.
- IF the benchmark is new while the techniques behind it are not, THEN the system SHALL keep it as a
  T4 or T5 contribution.
- IF the project's own prior publication claimed something the IJCAI paper later also published,
  THEN the system SHALL establish the dates before asserting priority, and SHALL mark the row
  `UNRESOLVED` while the dates are unknown.
- IF the same idea was developed independently but published later, THEN the system SHALL assign
  priority to the earlier publication and SHALL record the independence separately.
- IF a claim cannot be classified with the available sources, THEN the system SHALL mark it
  `UNRESOLVED`, never `NEW`.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| SCI-01 | P1: T22.1 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-02 | P1: T22.1 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-03 | P1: T22.1 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-04 | P1: T22.1 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-05 | P1: T22.1 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-06 | P1: T22.1 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-07 | P1: T22.2 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-08 | P1: T22.2 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-09 | P1: T22.2 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-10 | P1: T22.2 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-11 | P1: T22.2 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-12 | P1: T22.2 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-13 | P1: T22.2 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-14 | P1: T22.3 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-15 | P1: T22.3 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-16 | P1: T22.3 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-17 | P1: T22.3 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-18 | P1: T22.3 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-19 | P1: T22.3 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-20 | P1: T22.3 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-21 | P2: T22.4 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-22 | P2: T22.4 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-23 | P2: T22.4 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-24 | P2: T22.4 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-25 | P2: T22.4 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-26 | P2: T22.4 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-27 | P2: T22.4 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-28 | P2: T22.4 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-29 | P2: T22.5 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-30 | P2: T22.5 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-31 | P2: T22.5 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-32 | P2: T22.5 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-33 | P2: T22.5 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-34 | P2: T22.5 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-35 | P3: T22.6 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-36 | P3: T22.6 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-37 | P3: T22.6 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-38 | P3: T22.6 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-39 | P3: T22.6 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |
| SCI-40 | P3: T22.6 | Design | Done (`overlap-ijcai2026-min-station.md` §10) |

**Coverage:** 40 total, 40 delivered in `docs/technical/reference/documentacao-projeto/overlap-ijcai2026-min-station.md` (mapping per requirement in its §10); 0 mapped to `tasks.md` (not created in this round, by explicit user
request), 40 unmapped.

---

## Global Success Criteria

- [ ] The IJCAI 2026 paper is reviewed in full and cited in the bibliography and in the three
      positioning documents that omit it today.
- [ ] The overlap matrix covers every required row, each with a relation type and an evidence
      citation.
- [ ] No novelty claim stands without a reference or a repository artifact.
- [ ] Theoretical, algorithmic, computational, experimental and engineering contributions are
      distinguished, and no T4 or T5 item is presented as T1.
- [ ] Every current claim is audited, with a recommended rewrite where needed.
- [ ] Nothing already in the IJCAI paper appears as a project novelty — specifically not `G^r`, not
      matching-based feasibility, and not the BP and SC constructions.
- [ ] No genuine contribution is discarded merely because it is built from known components.
- [ ] Negative results are preserved as experimental contributions, with their protocol grade.
- [ ] Claims depending on Block 3 are marked pending, not assumed.
- [ ] Items that cannot be resolved with the available sources are marked `UNRESOLVED`, not `NEW`.

---

## Inconsistencies Found Between the Backlog, the Assessment, the Literature and the Code

1. **The assessment's §2.2 claim is correct but imprecise.** It says the literal `D` construction
   "falha" with `S∩T`. Re-deriving it from the paper this session shows the failure is confined to
   `S∩T \ C`: an intermediate vertex needs an in-arc (forcing `v ∈ T ∪ C`) and an out-arc (forcing
   `v ∈ S ∪ C`), so with `v ∉ C` it must lie in both `S` and `T`. The sharper statement should be
   what the overlap document carries.
2. **The three positioning documents omit the paper while thirty technical documents cite it.**
   `RESEARCH.md`, `docs/project-overview.md` and `source-map.md` have zero occurrences of "IJCAI".
   `source-map.md` is the file `CLAUDE.md` designates for comparing documents and articles.
3. **The SBPO claim has never been qualified anywhere in the repository**, on either axis — the
   missing literature search, or the fact that the SBPO formulation models the `V∖(S∪T)` variant
   rather than Das's problem.
4. **The backlog's T22 acceptance criteria are weaker than the brief.** They ask for the paper in
   the bibliography, a comparison table, and matching/`G^r`/Hall compared. They do not mention the
   Set Cover and Bin Packing overlaps, which this session found to be the two places where Block 3's
   families coincide with published reductions. The spec covers them; the backlog line should be
   updated when T22 is executed.
5. **`familias-estruturais.md` derives BP's `LB = 2n+q` as "o argumento do parecer"** while the
   assessment attributes the equivalence to the paper's p.76. The attribution chain should point at
   the paper directly, since the bound is the paper's `2n+m`.
6. **The assessment's §6 already lists "Pendência de posicionamento (Em aberto)"** with almost
   exactly T22's content. It predates Blocks 1–3 and was never closed; T22 supersedes it, and the
   assessment should point at the overlap document once it exists.
