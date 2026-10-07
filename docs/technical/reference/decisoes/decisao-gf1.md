# GF1 — portão da linha F-CC / F-C3

**Data:** 2026-10-06
**Regra:** `experiments/alternative-formulations/pre-registro-f3.md` (congelada antes da medição)
**Evidência:** `results/alternative-formulations/f3-fcc.csv` e `docs/technical/reference/resultados-f3-fcc.md`

## Veredito

**GF1 = PASS**

A F-C3 não participou (redes de trios `OPEN`). A regra aplica-se à F-CC.

## Aplicação da regra

PASS se e só se (1) o LP da F-CC é estritamente maior que
`max(LP base+C1+C2+C4, núcleo IP)` em pelo menos **dois tipos** com `Γ > 0`
medido, e (2) fecha pelo menos **50% de Γ** em pelo menos um desses tipos.

Diferença estrita: `> 1e-6`. Fracção: `(lp_fcc - max)/Γ`.

### Tipos com Γ > 0

| Tipo | Linha do CSV | max(cortes, núcleo) | LP F-CC | Γ | fecha Γ? |
|---|---|---:|---:|---:|---|
| hb | HB-q4-ndir2-p1 | 1 | 2 | 1 | 100% ≥ 50% |
| hb | HB-q5-ndir2-p1 | 1,083… | 3 | 2 | 95,8% ≥ 50% |
| bp-nao | BP-nao-[3,1]-q2 | 6 | 7 | 1 | 100% ≥ 50% |
| sec59 | Sec59(L=7) | 3,667… | 4,5 | 5 | 16,7% < 50% |

Tipos distintos com ganho estrito: **hb**, **bp-nao**, **sec59** (três ≥ dois).
Condição (2): satisfeita em hb e em bp-nao.

Tri, F2, TR, gadgets: `Γ = 0` (controlos de bound). Não entram no numerador de tipos.

### SC

SC-GF2-k3: F-CC excluída por `max_W`. LP set-cover = 1,75, igual ao LP+C1+C2+C4. Não há ganho em SC. Nada a investigar antes do veredito.

## Consequências (spec B)

- Geração de colunas da F-CC (R8) **deixa de estar bloqueada por GF1**. Continua condicionada a formalizar o pricing em `H=G^r` e um limite dual válido (Farley ou Lagrangeano). Essa spec **não** implementa R8.
- F-CC fica registada como caracterização exata (P1) **e** como relaxação que fortalece o bound em HB, BP-"não" (neste caso) e parcialmente Sec59.
- Não se afirma que a F-CC seja mais rápida, nem que vença o COMP a trabalho igual.
- F-C3 permanece `OPEN`. Nada neste veredito autoriza adivinhar as redes de trios.

## Reprodução

```text
PYTHONHASHSEED=0 poetry run python experiments/alternative-formulations/verify_fcc.py
PYTHONHASHSEED=0 poetry run python experiments/alternative-formulations/run_f3.py
```

O CSV deve coincidir com a tabela de `resultados-f3-fcc.md`. Aplicar a regra acima ao CSV reproduz `PASS`.
