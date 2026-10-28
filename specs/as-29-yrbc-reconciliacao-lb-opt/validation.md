# AS29 — Relatório do Verifier independente

**Verifier:** agente independente (autor ≠ verificador), sem participação na Rev. 0, Rev. 1 ou Rev. 2.
**Objeto:** `reconcile_as29.py`, `export_as29_installations.py`, `test_reconcile_as29.py`, `results/benchmark/as29-physical-ub-001/`, CSVs e relatórios `as29-*`, `spec/design/tasks.md` (árvore não commitada, branch `novos_testes`).

**Verdict:** PASS
**Result:** PASS — iteração 3 (2026-10-18). É PASS da **verificação da implementação e dos dados contra a spec**. O G0 é candidato (`G0_CANDIDATE_PASS`); a aprovação do gate continua sendo do pesquisador, e este relatório não a concede.

## Cronologia

### Rev. 0 (autor da implementação)
O autor registrou "IMPLEMENTED / TESTS_PASS" (11 testes, 260 linhas de proveniência) e `G0_BLOCKED_EVIDENCE` (8/31 UBs físicas *reportadas*, sem reexecutar o oráculo). Não era um relatório independente.

### Iteração 1 do Verifier — FAIL
Números do envelope reproduzidos (36/36 casos, 67/67 instalações aceitas). FAIL por lacunas de contrato:
1. limites do `manifest.csv` não exibidos lado a lado (P1.3);
2. caso sem UB virava `OPEN_SOLVER_UB_ONLY` e o gate dava PASS_RESTRICTED;
3. critério G0 Rev. 1 omitia LP e data/commit;
4. `plan.json` do AS06 sem conferência;
5. sondas vivas (LP de C/C_K, `censored`);
6. problemas de processo (premissas autoconfirmadas, checkbox do Verifier antecipado, redação sobre partição reservada trocada, alegações sem artefato);
7. `cuts_sha256` com semântica misturada.
Parecer: a "Rev. 1 do G0" era afrouxamento post hoc; AS30 dependia do G0 só formalmente.

### Iteração 2 do Verifier — PASS
As 7 lacunas foram resolvidas (manifesto lado a lado e flag `DOCUMENTED_BOUND_OUTSIDE_ENVELOPE`, estado `INCOMPLETE`, conferência do plano AS06, `source_versioned_in`/`cuts_scope`, gate de volta ao contrato vigente, emenda A1 separada e não adotada). Sensor: 17 de 24 mutantes mortos. Ressalvas não bloqueantes: ramo UB da flag sem teste, `cuts_scope` e `source_versioned_in` sem teste, "12/12 mutantes" do autor sem artefato, rótulo "datas" ambíguo, data de regeneração do manifesto não confirmada. Estado do gate na época: `G0_BLOCKED_EVIDENCE` (8/31).

### Iteração 3 do Verifier (este relatório)
Os dados mudaram: o pesquisador autorizou obter as instalações em vez de adotar a emenda A1. O autor rodou 46 solves (23 casos × {U, U_K}) e a Rev. 2 passou a lê-los como `AS29_POSTERIOR_EXPORT`.

## 1. Recompute independente (sem importar o auditor)

| Item | Resultado |
|---|---|
| 46 JSONs + 46 sidecars | 46/46 sidecars conferem o SHA-256 do arquivo. 23 casos × 2 braços, sem duplicata nem ausente |
| Identidade | `instance_sha256` = SHA do manifesto nos 46. Nome do arquivo = `case_name--arm_id` nos 46. Todos os 23 casos são `desenvolvimento` (nenhum `avaliacao`, nenhum legado) |
| Configuração gravada | Nos 46: seed 42, 4 threads, `work_limit` 164, guarda 1800 s, Gurobi 12.0.3; commit `72c241d-dirty` nos 46 |
| Oráculo | Reexecutei `independent_validator.viavel`, com parser próprio e grafo não dirigido: **46/46 aceitas**; `len(installed)` = `physical_validated_ub` = `round(mip_numeric_incumbent)` |
| Reprodução da linha de base | **46/46** reproduzem a linha de seed 42 do braço correspondente (`base`→U, `comp`→U_K): `mip_obj` idêntico e `mip_bound` dentro de 0,01. Status: 27 ótimos e 19 `WORK_LIMIT` |
| LB do envelope, UB numérica, UB física, estado | 36/36 iguais ao CSV, agora incluindo a fonte nova |
| 31/31 casos de desenvolvimento com UB física | Confirmado: 18 `OPT_NUMERIC_PHYSICAL` + 13 `OPEN_PHYSICAL_UB`; 0 `INCOMPLETE`/`INCONSISTENT` |
| Proveniência | 192 + 36 + 32 + 32 + 46 = **338** = linhas do CSV. Oráculo: 113 aceitas (67 + 46), 0 rejeitadas |
| Regeneração | CSVs regenerados em diretório temporário: **idênticos byte a byte** aos versionados |
| Fontes primárias | `git diff HEAD --stat -- results instances` vazio; a única novidade é `results/benchmark/as29-physical-ub-001/` (untracked). `linha_base.csv` e as demais fontes seguem idênticas ao HEAD |
| 5 casos com UB física maior do que o menor objetivo numérico | `puc-cc12-2u` 198 vs 193, `puc-cc10-2u` 58 vs 57, `puc-cc11-2u` 104 vs 101, `puc-w23c23-seed` 158 vs 156, `puc-w3c571` 1079 vs 1064. A menor UB numérica é de outra seed e não tem instalação. Está documentado (E-29-12 cobre 4 casos; **w3c571 já era conhecido da E-29-02**). O status vira `OPEN_PHYSICAL_UB` e a UB numérica menor continua visível em `ub_numeric_envelope`: conservador |
| Caso com S∩T | `puc-w23c23-intercalado-f2-rho` agora tem instalação validada para 128 (LB = UB), e o oráculo foi exercitado em S∩T pela primeira vez. Fecha a lacuna R-S∩T das iterações anteriores |

## 2. Crítica do script de exportação (`export_as29_installations.py`)

| Pergunta | Achado |
|---|---|
| Reproduz a configuração da Spec A? | **Sim.** O braço U usa `_make_mip(...,'int',[])`, e U_K usa `prepare_cuts(...,{'C1','C2','C4'})` com f contínuo, igual a `run_linha_base.py:129-150`. Seed, threads, `TimeLimit`=guarda e `WorkLimit` conferem (`export:58-64`). `r` vem de `r_usado` do manifesto (`export:52`), igual à linha de base. Diferença: a linha de base liga um callback só de leitura (`coletar_incumbente=True`) e o export não. A reprodução exata dos 46 `mip_obj` mostra que isso não alterou a busca nesta execução, mas não é garantia geral |
| Instalação vem de `y.X>0.5`? | Sim (`export:77`), ordenada e validada no oráculo (`export:80`). Os JSONs gravam `invalid_incumbents=0` nos 46 |
| Instalação vinculada à instância errada? | Não: carga via `row['caminho']` do manifesto, SHA da instância gravado do arquivo lido (`export:113`), e o auditor ainda compara com o manifesto (`INSTANCE_SHA_MISMATCH`). Conferi nome, caso e SHA nos 46 |
| Sidecar e SHA conferidos? | O export grava o sidecar com o SHA do JSON (`export:117-119`). O auditor o confere antes de ler (`reconcile_as29.py:157-160`; teste de adulteração morre se removido, P1) |
| Contaminação entre shards? | Não encontrada. Cada (caso, braço) tem um nome de arquivo único, a partição é por índice módulo N e a escrita é por `.tmp` + rename. Cada caso tem exatamente 2 arquivos, e os identificadores internos batem com o nome |
| Usa `avaliacao`? | Não. `targets()` filtra `particao == 'desenvolvimento'` (`export:38`), e todos os 46 casos são de desenvolvimento |
| Reprodutibilidade de `targets()` | **Fraqueza menor.** `targets()` lê o CSV derivado `as29-envelope-casos.csv` (`export:35-36`), que o auditor sobrescreve. Depois da Rev. 2, rodar o script de novo devolve 0 alvos. Para auditoria, a seleção deveria vir da lista fixa de 23 nomes, ou da própria pasta de resultados |

## 3. Revisão adversarial

| Pergunta | Achado |
|---|---|
| Falso G0 PASS? | Não encontrado. A condição do critério original (31/31 com UB física revalidada, sem `INCONSISTENT`/`INCOMPLETE`/`INTEGRITY_BLOCKED`) é verdadeira nos dados, conforme o recompute da §1, e não por afrouxamento |
| A mudança de gate é legítima? | Sim. `gate()` (`reconcile_as29.py:219-228`) não mudou de lógica desde a iteração 2: o veredito vem de `len(eligible)==len(dev)`. O que mudou foi o dado. A emenda A1 está registrada como não adotada e `amendment_candidate` ficou vazio. Mutante P5 (limiar frouxo) morto |
| UB física de outra instância ou braço? | Não. A UB física de cada caso é o mínimo, entre registros com SHA igual ao do manifesto, daqueles cujo oráculo aceitou a instalação. Para os 23 casos, a única fonte é a exportação (46 registros), e conferi que o mínimo calculado por mim bate com o CSV |
| A fonte nova bagunça o LB ou o OPT? | Não. O LB do envelope (36/36) não mudou com os bounds `WORK_LIMIT` de U/U_K (válidos como bound duais). A regra de OPT exige LB = UB física revalidada, e os 18 `OPT_NUMERIC_PHYSICAL` a cumprem; casos com LB < UB física ficam `OPEN_PHYSICAL_UB` |
| Mistura de versões? | A fonte posterior é rotulada `AS29_POSTERIOR_EXPORT`, com commit `-dirty` e `notes` próprios. Fica explícito que a UB física pode diferir da incumbente histórica |
| Partição reservada? | Não aberta. O auditor só lê JSONs da pasta nova (todos de desenvolvimento) e filtra o AS09 antes de abrir. O `git status` também não mostra mudança em `results/` além da pasta nova |
| Item novo no repositório | `min-station-relatorio-instancias/` (LaTeX/figuras) apareceu untracked. Não é do escopo da AS29, não foi lido por mim e não afeta nenhum artefato verificado |

## 4. Verificação ancorada na spec (iteração 3)

| Critério | Evidência (arquivo:linha) | Estado |
|---|---|---|
| P1.1 proveniência | `reconcile_as29.py:31,101-111,157-166`; limitações em `as29-envelope-lb-opt.md` (§6-§7) | ATENDIDO (limitação declarada: versão do Gurobi da Spec A; commit `-dirty`; LP 8/31) |
| P1.2 núcleo ≠ UB física | `reconcile_as29.py:29-30,99,166`; `test_reconcile_as29.py:50-61` | ATENDIDO |
| P1.3 divergências lado a lado | colunas `manifest_*`, flag em `reconcile_as29.py:94,183,204`; `as29-erratas-e-incompatibilidades.md:72-76` | ATENDIDO |
| P2.1 CC9 | `as29-erratas-e-incompatibilidades.md:6-12`; `test_reconcile_as29.py` (testes CC9) | ATENDIDO |
| P2.2 régua futura | `as29-envelope-lb-opt.md` §7 | ATENDIDO (documental) |
| P2.3 K pré-correção | `as29-erratas-e-incompatibilidades.md:29-33` | ATENDIDO (documental) |
| Edge: dados incompletos | `reconcile_as29.py:181,186,215`; teste `test_case_without_any_ub_is_incomplete_and_blocks` | ATENDIDO |
| Edge: S∩T | oráculo + instalação do caso `puc-w23c23-intercalado-f2-rho` revalidada (§1) | ATENDIDO agora |
| Edge: censura | `reconcile_as29.py:99,111`; teste de censura | ATENDIDO |
| Edge: fonte divergente | §1 da iteração 2 | ATENDIDO |
| SC: G0 PASS, critério original | `spec.md:106`; saída `gate=G0_CANDIDATE_PASS`; recompute da §1 | ATENDIDO como candidato; **aprovação cabe ao pesquisador** (plano §6) |
| SC: sem alterar histórico; sem reservados | `git diff HEAD --stat -- results instances` vazio; `spec.md:109` | ATENDIDO |

## 5. Sensor de discriminação (partes novas, em cópias)

Cópias em `scratchpad/verifier/mut2/` com `ROOT` apontando para a raiz. `git stash` não foi usado, e o `git status --porcelain` final é idêntico ao inicial.

| Mutante | Resultado |
|---|---|
| P1 remove a conferência do sidecar da fonte nova | MORTO (`test_posterior_export_sidecar_tamper_rejected`) |
| P2 descarta `work_limit` da fonte nova | MORTO (`test_posterior_export_reproduces_historical_seed42_rows`) |
| P3 lê só o braço U da fonte nova | MORTO (3 testes) |
| P4 desliga a exclusão por SHA divergente | MORTO (`test_evidence_from_other_instance_is_rejected`) |
| P5 gate aceita 8 casos sem UB física (limiar frouxo) | MORTO (`test_gate_rules`) |
| P9 gate considera também o legado | MORTO (2 testes) |
| **P6** aceita a instalação da fonte nova mesmo com o oráculo rejeitando | **VIVO** |
| P7 ignora o campo `schema` da fonte nova | VIVO (equivalente nos dados: os 46 têm o schema correto) |
| P8 promove a incumbente numérica da fonte nova a UB física | VIVO (equivalente nos dados: todas têm instalação válida) |

Os mutantes P7 e P8 só se diferenciariam com um JSON malformado; P6 é uma lacuna real de teste: nenhum teste rejeita uma instalação da fonte nova que o oráculo recusa. Os dados atuais não são afetados (46/46 aceitas por mim, de forma independente).

## 6. Ressalvas e lacunas restantes (nenhuma bloqueia)

1. **Teste de rejeição pelo oráculo para a fonte nova** inexistente (mutante P6 vivo). Código: `reconcile_as29.py:165` (o caminho comum com `solver_record`, que é bem testado para AS09, mas não com a fonte nova).
2. **`targets()` não reproduzível** (`export_as29_installations.py:35-36`): depende do CSV derivado. Recomendo fixar a lista dos 23 casos em arquivo ou constante.
3. **Callback**: o export não liga o callback de incumbente da linha de base (`harness.measure_mip`, `coletar_incumbente=True`). A reprodução 46/46 mostra que não alterou o resultado, mas a equivalência não é provada.
4. **Texto antigo**: `spec.md:36` ainda fala em "aprovar ou não a emenda A1", embora ela esteja não adotada e sem efeito. `ENVELOPE_VERSION = 'AS29-r1'` (`reconcile_as29.py:25`) e o docstring de `gate()` ainda mencionam a emenda A1. O comentário "datas presentes por fonte" refere-se a data de versionamento git, não à data de execução.
5. **Os 13 casos `OPEN_PHYSICAL_UB`** têm UB física da seed 42; em 5 deles há UB numérica menor sem instalação. Alegações de melhoria de UB nesses casos devem superar a menor entre as colunas física e numérica, conforme as colunas `*_documented_*` e `ub_numeric_envelope`. Não é defeito, é regra de uso.
6. **Pasta `min-station-relatorio-instancias/`** untracked, fora do escopo.

## 7. Parecer

- **`AS29_COMPLETE`:** sim, sem ressalvas de contrato. As 6 ressalvas acima são de qualidade de teste/documentação. O critério G0 original foi atendido sem emenda.
- **Motivo técnico para o pesquisador não aprovar o G0:** não encontrei nenhum. Os riscos que ele deve conhecer, e que o relatório já declara, são: (i) OPT é "numérico" (solver + oráculo, não certificado racional); (ii) a UB física vem de um solve posterior (seed 42, commit `-dirty`), que em 5 casos é maior do que o menor objetivo numérico histórico; (iii) a lacuna de teste P6.
- **AS30:** continua sem dependência substantiva da AS29 (provas R-dom/BF/BR e microinstâncias). A dependência é formal (`specs/as-30-yrbc-validacao-matematica/spec.md:3,5`). AS31 em diante passa a ter 31/31 UBs físicas de referência, mas a obrigação de superar `ub_documented_min` e `ub_numeric_envelope` deve ser escrita na spec da AS31.

## 8. Comandos e resultados

```bash
poetry run python -m unittest discover -s experiments/benchmark -p 'test_reconcile_as29.py' -q   # Ran 34 tests — OK
poetry run python experiments/benchmark/reconcile_as29.py --output-dir <scratchpad>/verifier/out3
#   provenance_rows 338; oracle_revalidated_records 113; oracle_rejected_records 0
#   development_by_status {OPT_NUMERIC_PHYSICAL:18, OPEN_PHYSICAL_UB:13}; gate G0_CANDIDATE_PASS; amendment_candidate ""
cmp (casos, proveniência) versionados × regenerados      # idênticos
<venv>/bin/python <scratchpad>/verifier/recompute3.py    # 46 sidecars/SHA/schema ok; 46/46 reproduções; 113 oráculo, 0 rejeições; 36/36 estados; 338 linhas
<venv>/bin/python <scratchpad>/verifier/mutate3.py       # 6 mortos, 3 vivos (2 equivalentes nos dados)
python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py  specs/as-29-yrbc-reconciliacao-lb-opt/spec.md  --strict   # 0 errors, 0 warnings
python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-29-yrbc-reconciliacao-lb-opt/tasks.md --strict   # 0 errors, 0 warnings
git diff --check                                         # exit 0
git diff HEAD --stat -- results instances                # vazio
git status --porcelain                                   # idêntico antes/depois
```

Nenhuma execução de Gurobi nesta verificação. Nenhum resultado `avaliacao` foi inspecionado. Nenhum arquivo além deste foi alterado.
