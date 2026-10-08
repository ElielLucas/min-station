# G1 — portão de método (Spec C)

**Data:** 2026-10-06
**Regra:** `docs/technical/reference/experimentos/pre-registro-r5.md` §5, congelada antes da medição
**GF1:** PASS (`docs/technical/reference/decisoes/decisao-gf1.md`)
**Evidência:** `docs/technical/reference/experimentos/resultados-r6-gamma.md`, `resultados-r6-primal.md`, `resultados-r7-plato.md`

## Veredito

**G1 = compatibility (LB) dominates**

Recomenda **M-A** (desigualdades de compatibilidade, R10). Recomenda **também M-F** (geração de colunas / F-CC, R8–R9) porque GF1 = PASS.

**Não** recomenda M-B. Spec C não implementa nenhum método.

## Aplicação da regra

| Cláusula | Medido | Satisfeita? |
|---|---|---|
| `Γ > 0` exact em ≥ 2 famílias | 8 famílias: mapf, pace18, puc, pucn, b, lin, bp-nao, hb | sim |
| primal **não** atinge limiar UB em ≥ 2 famílias | 0 famílias atingem o limiar nas 3 sementes | sim |
| primal atinge limiar em ≥ 2 famílias | 0 | não |
| `Γ` exact zero em todas ou positivo em ≤ 1 família | 8 famílias com Γ > 0 | não |

- compatibility: as duas primeiras linhas → **sim**
- primal dominates: falha a terceira e a quarta
- both: falha a terceira
- no clear signal: não se aplica; compatibility já fecha

Leitura frouxa recusada: melhoria numa semente (pace18-t2-141 semente 43, ΔUB=1) não conta.

## Linhas que decidiram

Γ exact > 0 (amostra certificada, CSV `r6-gamma.csv`):

- mapf maze m10/m25: Γ = 2
- pace18 t2-001/061/081: Γ = 1
- puc-cc6-3p e puc-hc9u: Γ = 1
- pucn-cc3-5n / cc5-3n / cc6-2n: Γ = 3, 1, 2
- b-b15-regiao-f4: Γ = 1
- lin-lin03 / lin06-regiao: Γ = 2, 1
- BP-"não" B=10 e [3,1]: Γ = 1
- HB q=4 / q=5: Γ = 1, 2

Intervalos D/A **não** entram na regra. F fácil por seleção pode subestimar Γ de D/A; isso não enfraquece o sinal exact já obtido em oito famílias.

Primal: `resultados-r6-primal.md`. Nenhuma instância das 13 reproduz ΔUB ≥ 1 nas três sementes.

R7 (`resultados-r7-plato.md`): H-desc **CONFIRMED** nos C gravados (608 inviáveis, 0 não-H-desc). TR reproduz 8 ótimos / 2 viáveis. Hipótese escrita: suporte de `y` incompatível com configuração conexa em `H` que realize o emparelhamento S–T. Isso alinha M-A (e M-F) com o platô; **não** altera a regra G1, que não consulta R7 para o rótulo. R7 só informa a forma da desigualdade quando M-A abrir.

## Consequências

| Método | Estado depois de G1 |
|---|---|
| M-A / R10 `COMPAT-*` | **liberado** (ainda não executado) |
| M-F / R8–R9 `CG-*` | **liberado** (GF1 PASS; F-C3 continua OPEN) |
| M-B / R12 `PRIMAL-*` | **bloqueado** |
| R13 `CONF-*` | bloqueado até G2 |

Fluxo mandatório de M-A, se aberto: derivação → prova → validador → enumeração → certificadores da Spec D → efeito em Γ com SC como controlo → D/A desenvolvimento. No máximo 3 ciclos. Nada disto foi feito aqui.

---

**Nota de auditoria N1-T0 (2026-10-07).** O veredito **G1 é independente dos resultados R7**: seu gatilho usa R5/R6, não frequência ou cobertura dos cortes Z. Em R7, o contador histórico `max_elimina_um_Z` é frequência de retorno; `n_origens_sem_par` mede origens de grau zero, não déficit máximo. H-desc é caracterização de viabilidade, não identificação causal. As evidências R7 corrigidas informam N1, sem mudar G1.
