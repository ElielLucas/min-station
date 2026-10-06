# Pré-registro F3 — LP de F-CC em instâncias pequenas

**Data:** 2026-10-06
**Spec:** `specs/proxima-fase-b-formulacoes-fcc-fc3/spec.md`
**Escrito antes de qualquer valor LP de F-CC ou F-C3.**

Este arquivo congela instâncias, caps, braços, fonte de OPT e a regra GF1.
Nenhuma medição de F-CC/F-C3 pode alterar estes números.

## Braços por instância

| Braço | Definição | Fonte de código |
|---|---|---|
| LP base | relaxação da formulação base, fluxo contínuo, sem cortes | `harness.measure_lp(..., [])` |
| LP base+C1+C2+C4 | idem com cortes estáticos C1, C2, C4-DM | `prepare_cuts` + `measure_lp` |
| núcleo IP | IP só em `y` com C1+C2+C4-DM | `medir.nucleo` |
| LP F-CC | relaxação da F-CC | `fcc.lp_fcc` |
| LP F-C3 | **não medido** | redes de trios `OPEN` (F1) |
| OPT | mínimo \(|C|\) viável | ver fonte abaixo |
| LP set-cover | só em SC-GF2, controle negativo | IP/LP de cobertura sobre o sistema GF2 |

`Γ = OPT − núcleo`, medido, nunca assumido.

## Forma da F-CC neste lote

A forma original `(W,I,J)` é usada nos testes de P1/P7 (`verify_fcc.py`), em instâncias com `n ≤ 9`.

F3 mede o LP da F-CC na **forma separada** `λ_W, α, β`, depois de F2 classificar P7 como `PROVEN` (prova em `docs/technical/reference/provas-fcc-fc3.md` §P7, cruzamento computacional no mesmo `verify_fcc.py`).

F-C3 completa (redes de 8 estados) **não entra**. GF1 usa só F-CC, default da spec B (confirmação de usuário pendente no texto da spec; default aplicado).

## Caps (congelados)

| Cap | Valor | Efeito se excedido |
|---|---|---|
| `n_max` | 21 | instância excluída, listada |
| `max_W` | 200000 | instância excluída; enumeração aborta; **não** se reporta LP com família `W` incompleta |
| `n_opt_enum` | 16 | OPT por `opt_por_enumeracao` se `n ≤ 16`; senão MIP da base até otimalidade (`T5`) |

`2^16 = 65536` subconjuntos. `n = 21` usaria `2^21` na enumeração de OPT; por isso o MIP da base.

## Conjunto de instâncias (fixo)

Gadgets de `experiments/cuts/synthetic.py` (parâmetros padrão, salvo onde indicado):

- Direct0, TermRelay, TermRelayForced, StayPut, StayPutIsolado, SharedTerminal, CaminhoABC
- Tri
- F1(`m=2`,`k=2`)
- F2(`k=1`,`L=3`)
- Sec59(`L=7`)

Estruturais do Apêndice B / spec B:

- HB `q=4, ndir=2, p=1, k=1` (`n=16`)
- HB `q=5, ndir=2, p=1, k=1` (`n=21`)
- BP-"não" `[3,1]`, `q=2`, `B=2` (`n=16`)
- TR `k=2, L=5, r=2, σ=None, m=2` (`n=18`)
- SC-GF2 `k=3` (`n=21`)

**Fora dos caps, listadas e não medidas em F-CC:**

- HB `q=6, ndir=1, p=1` (`n=28`), HB `q=8` (`n=38`), HB `q=6, p=2` (`n=25`)
- BP-"não" `[2,2,2]` `q=2` (`n=23`)
- TR `k=3, L=5` (`n=25`)
- SC-GF2 `k=4` (`n=45`)
- F1(`k=3`), F2(`k=2`) (`n=17`)
- família 20/15 vértices da F-C3: **não reconstruível** (definição ausente)
- aranhas da Spec D: **não disponíveis** neste repositório na data do pré-registro

Papel esperado (não decide `Γ`; só organização):

| Instância | Papel no desenho |
|---|---|
| gadgets Direct0…CaminhoABC | regressão `S∩T` / OPT 0 / estação em terminal |
| Tri, Sec59 | `Γ` a medir |
| F2(k=1) | controle de bound (`Γ` esperado 0) |
| HB q=4 e q=5 | instrumento `Γ > 0` (tipo HB) |
| BP-[3,1] | instrumento `Γ > 0` (tipo BP-não) |
| TR k=2 | controle de bound (`Γ` esperado 0) |
| SC-GF2 k=3 | controle negativo de cobertura |

## Fonte de OPT

- `n ≤ 16`: `independent_validator.opt_por_enumeracao`.
- `n > 16`: `medir.otimo_base` (MIP da formulação base até `OPTIMAL`). Equivalência com o validador: T5 em `validacao-formulacao-base.md`.
- Nunca OPT da F-CC nem da F-C3.

Campo `fonte_opt` no CSV: `enum` ou `mip_base`.

## LP de set-cover em SC-GF2

Para SC-GF2(k=3): LP `min 1^T y` s.t. cada elemento coberto, `y ≥ 0`. Valor esperado `n_elem / 2^{k-1} = 7/4 = 1,75`. Reportar ao lado do LP F-CC. Qualquer F-CC **estritamente acima** desse LP (e abaixo de OPT) em SC é tratado como erro suspeito, não como ganho.

## Solver e reprodutibilidade

- Gurobi, `Seed=42`, `Threads=1`, `OutputFlag=0`
- sem `TimeLimit` nos LPs deste lote (instâncias pequenas)
- `PYTHONHASHSEED=0` no runner

## Regra GF1 (congelada)

**PASS** se e somente se:

1. o LP da F-CC (ou da F-C3, se existisse) é **estritamente maior** que `max(LP base+C1+C2+C4, núcleo IP)` em pelo menos **2 tipos** de instância com `Γ > 0` **medido**; e
2. fecha pelo menos **50% de `Γ`** em pelo menos um desses tipos.

Tipo = família nomeada no CSV (`gadget`, `hb`, `bp-nao`, `tr`, `sc-gf2`, `f1`, `f2`, `tri`, `sec59`), não cada linha.

- Ganho em SC: investigar como erro **antes** de emitir GF1.
- **FAIL** caso contrário: geração de colunas permanece pausada; F-CC fica como caracterização exata com resultado de LP negativo.
- Não se afirma superioridade computacional (tempo, nós) a partir destes LPs.
- Não se acrescentam instâncias, prazos ou sementes para resgatar GF1.

Comparação numérica: diferença estrita se `lp_fcc - max(lp_cortes, nucleo) > 1e-6`.
Fração de `Γ` fechada: `(lp_fcc - max(lp_cortes, nucleo)) / Γ` quando `Γ > 1e-6`.
