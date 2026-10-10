# N2-T5 — custos e curvas prospectivos

Medições produzidas pelo executor congelado em N2-T1. **N2 PASS/FAIL não é decidido aqui.**

## Proveniência e protocolo

- Freeze N2-T1 SHA-256: `b036e9d0fe8f446dfcaca2716df85054c73dbb8702484aacce3c807e6574de71`
- Replay corrigido N2-T4 CSV SHA-256: `62032d439ce86b62673b50e1cb3936e56fcea8cfef59c5a2376baf4b077c4153`
- F-CC+K root-only, Gurobi Threads=4, Seed=42, PYTHONHASHSEED=0.
- Work cap=164 por instância para *todos* os solves; wall cap=1800 s.
- Ref. nível 1: B0 e full LP históricos. Nível 2: COMP LP + core IP recomputados.
- Baselines de solver/histórico são referências, NÃO prova E5 de B0 físico.
- Certified físico somente com reauditoria E5. RMP/ObjBoundC são diagnósticos.
- Curva de LB certificado reaudita evidências da E4 contra o K real antes de publicar.
- Visualização: `n2-t5-lb-versus-work.svg` (somente pontos certificados).
- Memória é máximo RSS do processo até a medição; não é pico isolado por solve.

## Medições

| Caso | B0 referência | LB físico (exato) | Estado | Work total | Wall s | Pontos curva |
|---|---:|---:|---|---:|---:|---:|
| `HB-q4-ndir2-p1` | 1/1 | 1/2 | CERTIFIED_PHYSICAL_LB | 0.4179629278850957 | 4.4018341089831665 | 18 |
| `BP-nao-[3,1]-q2` | 6/1 | 1/1 | CERTIFIED_PHYSICAL_LB | 0.08305808597572574 | 1.2487644229549915 | 11 |
| `HB-q6-ndir2-p1` | 11500000000000001/10000000000000000 | 2/3 | CERTIFIED_PHYSICAL_LB | 1.364441288142522 | 5.787274754955433 | 28 |
| `BP-nao-[2,2,2]-q2` | 8/1 | 18/13 | CERTIFIED_PHYSICAL_LB | 0.6705444579647916 | 7.001144642010331 | 25 |

## Contabilidade

Work = COMP LP + core IP + master + pricing (unidades Work Gurobi).
Wall fases mutuamente exclusivas = montagem + alcance + K + COMP + core + CG + pós-validação + outros. O runtime do master/pricing e a validação E5 são subpartes da fase CG; não somar duas vezes.
Ausência/erro de Work ou perda de prazo invalida a publicação de um LB novo.

## Limites científicos

- Nível 2 não possui LP completo histórico: não imputar.
- A medição B0 nível 2 é numérica. Sem auditoria independente, não chamá-la de LB físico certificado.
- N2 N2-box usa multiplicadores racionais zero na E4; limites podem ser fracos.
- Pontos LB × Work pertencem ao momento anterior à auditoria final e só entram quando suas provas passam na reauditoria racional E5.
- Experimentos não alteram split benchmark-v1, freezes, nem introduzem branch-and-price.
- Gate N2-T6 aplicará as condições de ganho ≥50%, repetição por família/nível, custo e validade.

## Histórico de curva

82 pontos em `n2-t5-lb-versus-work.csv`.
