# AS-08 — Registro de implementação pré-piloto (2026-10-12)

Este adendo não substitui `spec.md`, `design.md` ou `tasks.md` existentes, nem marca como concluída a revisão científica exigida pela spec.

| Item | Estado do código | Evidência / pendência |
|---|---|---|
| AS08-01 caminhos | IMPLEMENTADO T2a | Enumerator T2a e testes de caminho trivial e terminais internos |
| AS08-02 B1–B4 | IMPLEMENTADO T2a | Compilador e teste mutante sem B4 |
| AS08-03 equivalência | VERIFICADA NUMERICAMENTE EM PEQUENO | Parecer T1 existe; revisão independente ainda PENDENTE |
| AS08-04 pricing | IMPLEMENTADO / TESTADO LOCALMENTE | Dijkstra validado contra enumeração completa com duais racionais e valores negativos de pi/tau |
| AS08-05 LB global | IMPLEMENTADO / TESTADO LOCALMENTE | RMP+column/row generation, duais racionais e checagem de adulteração; Gurobi pendente |
| AS08-06 gate / piloto | IMPLEMENTADO, NÃO EXECUTADO NO BENCHMARK | Runner, plano, verificação, auditoria dual e relatório; executar no ambiente Gurobi |

A existência de código não constitui PASS final da AS-08; o gate depende dos testes reais, dos artefatos, da revisão matemática independente e da avaliação computacional.
