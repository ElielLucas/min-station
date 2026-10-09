# N1-T5 — Diagnóstico congelado

**Status:** `COMPUTATIONALLY VERIFIED` para braços medidos; demais `NOT MEASURED`. 
**Base:** spec N1, seção Experimental Pre-registration. Não é decisão N1-T7.

**Freeze SHA-256:** `8135c5a043d4a03e2d7ea673287cdf86d3f7171b7b18394a600038f9da2f20e7`
**Reprodução F3:** `8987c387a04dbf808dbcecf35e4b17a6d828f001c78504e311026ae26a9c2c60`
**Casos registrados:** 18 (16 F3 + 2 SOURCE).

## Matriz de inclusão e ablação

| Braço | Informação acrescida |
|---|---|
| LP base | Fluxo U sem K |
| LP COMP | Fluxo U + K |
| core IP | Cobertura inteira em y + K; limitante inferior, NÃO solução |
| LP F-CC | Configurações conexas sem K |
| LP F-CC+K | Configurações conexas + mesmo K congelado |
| LP F-C3 | Consistência de trios sem K |
| LP F-C3+K | Consistência de trios + mesmo K congelado |
| OPT | Oracle independente (enum/MIP base) |

## Comparação por instância

| Instância | Tipo | B0 | OPT | LP FCC | LP FCC+K | LP FC3 | LP FC3+K | ΔFCC | ΔFCC+K | Δtrio |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Direct0 | gadget | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TermRelay | gadget | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| TermRelayForced | gadget | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| StayPut | gadget | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| StayPutIsolado | gadget | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| SharedTerminal | gadget | 1 | 1 | 0.5 | 1 | 0.5 | 1 | -0.5 | 0 | 0 |
| CaminhoABC | gadget | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Tri | tri | 2 | 2 | 1.5 | 1.5 | 2 | 2 | -0.5 | -0.5 | 0.5 |
| F1(m=2,k=2) | f1 | 9 | 9 | 9 | 9 | 9 | 9 | 0 | 0 | 0 |
| F2(k=1,L=3) | f2 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| Sec59(L=7) | sec59 | 3.66667 | 7 | 4.5 | 5 | 4.5 | 5 | 0.833333 | 1.33333 | 0 |
| HB-q4-ndir2-p1 | hb | 1 | 2 | 2 | 2 | NOT MEASURED | NOT MEASURED | 1 | 1 | NOT MEASURED |
| HB-q5-ndir2-p1 | hb | 1.08333 | 3 | 3 | 3 | NOT MEASURED | NOT MEASURED | 1.91667 | 1.91667 | NOT MEASURED |
| BP-nao-[3,1]-q2 | bp-nao | 6 | 7 | 7 | 7 | 7 | 7 | 1 | 1 | 0 |
| TR-k2-L5-r2 | tr | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 0 | 0 |
| SC-GF2-k3 | sc-gf2 | 3 | 3 | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| SOURCE-g2 | source | 4 | 4 | 3 | 3 | NOT MEASURED | NOT MEASURED | -1 | -1 | NOT MEASURED |
| SOURCE-C5 | source | 3 | 3 | 2.5 | 2.5 | 2.5 | 2.5 | -0.5 | -0.5 | 0 |

## Controle de mecanismo e caps

- Casos com Γ>0 e residual F-CC+K: 1; famílias: ['sec59'].
- Regra N1-T6: **ativar somente se menos de duas famílias distintas** acima.
- Gatilho calculado: ATIVADO.
- Registros de testemunha: 4;
  os vetores y* e status do modelo fixado estão em `results/alternative-formulations/n1-t5-testemunhas.json`.
- Diferenças negativas (ex. SharedTerminal) preservadas sem truncamento.
- Status NOT MEASURED e seus limites devem ser lidos no CSV, nunca como ganho zero.
- Não inferir melhora de tempo de CPU a partir de valores LP.

## Testemunhas de complementaridade

- **SharedTerminal**: ponto ótimo y* da F-CC com objetivo 0.5, corte K violado Z=['v'] (Σy*=0.5 < 1); vetor completo em JSON.
- **Tri**: F-CC+K=1.5 (< F-C3+K=2); vetor ótimo y* do F-CC+K não admite extensão F-C3+K (status INFEASIBLE). Prova computacional local em JSON.
- **Sec59(L=7)**: ponto ótimo y* da F-CC com objetivo 4.5, corte K violado Z=['t1', 'w1'] (Σy*=0.5 < 1); vetor completo em JSON.
- **Sec59(L=7)**: LP COMP=3.666667 (< LP F-CC+K=5), e o vetor ótimo y* do COMP torna F-CC+K inviável quando fixado. Vetor completo, hash K e status em JSON. Testemunha computacional apenas no caso nomeado.

## Limitações

- Ganho é suportado apenas no conjunto pré-registrado; não é prova global.
- SOURCE-g2/C5 são controles antigos, não pares sintéticos de N1-T6.
- Este relatório não aplica o gate promocional N1-T7.
