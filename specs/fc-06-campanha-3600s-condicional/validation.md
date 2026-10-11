# FC-06 — Evidência de implementação (verificação pendente no Gurobi)

**Veredito:** `PENDING_REAL_GUROBI`, não `PASS` final.  
**FC-05:** piloto externo `READY_FOR_EXTENDED` confirmado na cópia do repositório enviada.  
**Campanha de 3.600 segundos:** **NÃO EXECUTADA**. Não houve compromisso automático de uso de recursos.

## Matriz de aceite

| AC | Evidência de código/teste | Resultado local |
|---|---|---|
| HOUR-01 — Gate bloqueia | `run_extended_comparison.py`: `_pilot_preflight`, `preflight_execute`, `execute`; `test_fc06_campaign_pure.py`: `test_hour01_*` | PASS, casos simulados + gate real FC05 |
| HOUR-02 — Pré-registro antes do solver | `run_extended_comparison.py`: `prepare`, `preflight_execute`; pré-registro SHA e plano imutável; `test_hour02_*` | PASS, sem Gurobi |
| HOUR-03 — 3.600 s wall por braço | `run_extended_comparison.py`: `execute` reaproveita `fc_core`/`fc_budget.run_bounded` via `ExperimentConfig`, 3.600 s; `test_hour03_*` | PASS estrutural; prova de execução real pendente |
| HOUR-04 — CAP/censura | `fc06_campaign.py`: `pair_screening`, `grouped_counts`; `test_hour04_*` e testes CAP no verificador | PASS, simulações; Gurobi pendente |
| HOUR-05 — Denominador e grupos | `fc06_reporting.py`: `summary`; `fc06_campaign.py`: `origin_from_manifest`, `make_plan`, `grouped_counts`; `test_hour05_*` | PASS, caso sintético |
| HOUR-06 — LP/MIP/prova distintos | `verify_extended_campaign.py`: `verify`; `fc06_reporting.py`: `write_report`; `test_hour06_*` | PASS, incluindo prova falsa rejeitada |

**Testes locais:** `test_fc06_campaign_pure.py`, testes anteriores FC04/FC05, compilação Python, validadores `validate_spec.py` e `validate_tasks.py` (ambos `--strict`) passaram. Não houve execução integrada com Gurobi nem Ruff no ambiente desta entrega.

**Verificador independente:** `verify_extended_campaign.py` recompõe os pares, identidades, períodos, grupos e campos de prova diretamente do CSV e pré-registro, sem chamar o módulo de agregação. Detecta alterações de hashes e relatório e usa o auditor FC04 para os bytes dos artefatos.

**Sensor de discriminação:** testes adversos alteram K, fonte, plano, wall, prova racional e omitem resultados; o verificador os rejeita. Teste ponta a ponta usa solver simulado; **não** substitui execução Gurobi real.

## Pendências para fechamento científico

1. Executar Ruff e a suíte completa com a licença Gurobi.
2. Fazer a sondagem MAIN de curta duração e auditar seus resultados.
3. Pré-registrar casos realmente elegíveis. Se `NOT_ELIGIBLE`, documentar abstenção, **não iniciar** 3.600 s.
4. Somente se elegível e cientificamente justificado, executar explicitamente a campanha longa e verificar `PASS` em `verify_extended_campaign.py`.
5. Registrar os resultados observados e atualizar este relatório sem confundir evidência numérica e certificação racional.
