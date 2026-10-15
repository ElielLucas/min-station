# AS17 — Registro de bloqueio por pré-condição

**Status:** `NOT_AUTHORIZED` / não executada.

A spec exige `AS16 GO explícito`. Na AS16, o analisador devolveu `INVESTIGATE` devido a censuras, e a decisão de priorização humana foi `STOP` para a linha H2. Assim **não há condição de entrada** para AS17. Não foram implementados `h2_root_mip.py`/`run_h2_mip.py` nem realizados experimentos MIP H2.

**Evidências:** `docs/technical/reference/experimentos/as16-resultado-lp-h2.md`; `results/benchmark/as16-lp-h2-001/analysis.json`; `specs/as-18-hl-condicional-e-sintese/as18-gate-evidence.json` (campo `as17_mip_gate`).

**Condição para reabrir:** novo protocolo e GO explícito de fase LP com evidência justificada, revisão de pré-registro e orçamento; não alterar retrospectivamente o gate AS16. AS17-01 a AS17-08 permanecem **não verificados**, não são marcados como testes bem-sucedidos.
