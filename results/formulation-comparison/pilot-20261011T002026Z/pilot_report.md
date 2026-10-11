# FC-05 — Relatório do piloto corrigido

**Gate preliminar:** `READY_FOR_EXTENDED`
**Decisão final:** depende de `verify_comparison_pilot.py` e da auditoria FC-04.

## Escopo e limitações

Amostra diagnóstica restrita às instâncias pré-selecionadas. COMP+K × F-CC+K é
o par primário. Baseline sem K é apenas ablação. Resultados `SOLVER_NUMERIC_OPTIMAL`
não são provas racionais. A decisão do gate não demonstra superioridade entre
formulações e não autoriza execução automática de 3.600 segundos.

## Denominadores e casos não medidos

- Instâncias selecionadas: 2
- Pares operacionais válidos: 2
- Instâncias não prontas: 0
- Instâncias censuradas/incompletas: 0

## Casos individuais

| Instância | Gate preliminar | Motivos |
|---|---|---|
| hb-q4-ndir2-p1-k1-L2.txt | READY_FOR_EXTENDED | — |
| bp-nao-q2-B2-s0.txt | READY_FOR_EXTENDED | — |

## Medições observadas por braço

| Instância | Braço | Status | LP numérico | Incumbente MIP numérica | UB física | Wall (s) | Work |
|---|---|---|---:|---:|---:|---:|---:|
| hb-q4-ndir2-p1-k1-L2.txt | lp_base | OPTIMAL | 0.3333333333333333 | — | — | 0.764988498063758 | 0.00019960000652625125 |
| hb-q4-ndir2-p1-k1-L2.txt | lp_comp | OPTIMAL | 1.0 | — | — | 1.0544307919917628 | 0.00020559046949305388 |
| hb-q4-ndir2-p1-k1-L2.txt | lp_fcc_k | OPTIMAL | 2.0 | — | — | 5.33225061907433 | 0.6762870672539164 |
| hb-q4-ndir2-p1-k1-L2.txt | comp_mip | OPTIMAL | — | 2.0 | 2 | 1.0518065380165353 | 0.0005729741333744554 |
| hb-q4-ndir2-p1-k1-L2.txt | fcc_k | OPTIMAL | — | 2.0 | 2 | 6.3887875829823315 | 2.3107140035831852 |
| bp-nao-q2-B2-s0.txt | lp_base | OPTIMAL | 3.0 | — | — | 0.9250976199982688 | 0.00012863789602040812 |
| bp-nao-q2-B2-s0.txt | lp_comp | OPTIMAL | 6.0 | — | — | 0.9766741060884669 | 0.00015080056382086175 |
| bp-nao-q2-B2-s0.txt | lp_fcc_k | OPTIMAL | 7.0 | — | — | 2.3340058519970626 | 0.1440766837716315 |
| bp-nao-q2-B2-s0.txt | comp_mip | OPTIMAL | — | 7.0 | 7 | 1.0503884290810674 | 0.00025227431224489805 |
| bp-nao-q2-B2-s0.txt | fcc_k | OPTIMAL | — | 7.0 | 7 | 3.868055089027621 | 2.683184425855764 |

## Motivos globais

- Nenhum identificado

## Conferência obrigatória

Execute `verify_comparison_pilot.py` sobre este diretório após o manifesto
ser finalizado. O verificador checa todos os SHA-256, recomputa o gate e
rejeita divergências. Uma rodada censurada permanece documentada.
