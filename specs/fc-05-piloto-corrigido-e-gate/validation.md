# FC-05 — Validação de implementação

**Situação:** IMPLEMENTADA PARA TESTE INTEGRADO; aceite final pendente de Gurobi, Ruff e auditoria de piloto real.

## Cobertura e rastreabilidade

| Critério | Entrega | Testes e evidência |
|---|---|---|
| PILOT-01 | `run_comparison.py` mantém execução LP/MIP com orçamento global por braço (FC-01); `verify_comparison_pilot.py` verifica estados, identidade e tempo | `test_pilot01_*` (modalidades, braços, teto, Work, Runtime, amostra) |
| PILOT-02 | Publicação de `pilot_gate.json` e `pilot_report.md` ANTES de `manifest.json`; hash dos arquivos no inventário FC-04; `out_dir` deve estar vazio | `test_pilot02_*` (SHA, alterações detectadas, sobrescrita rejeitada) |
| PILOT-03 | `NOT_READY` para mismatch de K, cap/timeout, incumbente inválido, modelo incompleto ou par inválido | `test_pilot03_*` e `test_pilot06_*` |
| PILOT-04 | Auditoria independente FC-04 exigida por `evaluate()`; recomputa `pilot_gate.json` com base em CSV/manifests | `test_pilot02_pilot04_full_sha_roundtrip_and_ready`, `test_pilot01_pilot04_*` |
| PILOT-05 | `solver_numeric_*` separados de `rational_verification` e `physical_feasible_ub`; sem inferir racional | `test_pilot05_*` |
| PILOT-06 | Todas as instâncias pré-registradas e braços previstos são contados, inclusive incompletos e censurados | `test_pilot02_selection_denominator_*`, `test_pilot03_cap_*`, `test_pilot06_*` |

## Testes executados neste ambiente (sem Gurobi)

- **29 testes FC-05:** PASS.
- **27 testes FC-04:** PASS.
- **25 testes FC-03:** PASS.
- **18 testes FC-02 pairing:** PASS.
- **10 testes FC-01:** PASS.
- **Total disponível sem Gurobi: 109 PASS.**
- `python -m py_compile` nos três scripts FC-05: PASS.
- `validate_spec.py --strict`: 0 erros, 0 avisos.
- `validate_tasks.py --strict`: 0 erros, 0 avisos.

**Não executados aqui:** suíte completa que depende de `gurobipy`, `ruff`, piloto FC-05 numérico, auditoria do output FC-05 real. O ambiente de geração não dispõe de Gurobi nem de Ruff. Não preencher status final como PASS antes desses passos.

## Comandos para aceite integrado (ambiente do usuário)

```bash
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/formulation-comparison -p 'test_*.py' -v
python -m ruff check experiments/formulation-comparison
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py \
  --tier pilot --modalities A,B --formulations comp_mip,fcc_k,baseline \
  --time-limit 120 --lp-time-limit 60 --plots
python experiments/formulation-comparison/verify_comparison_artifacts.py <RUN_REAL>
python experiments/formulation-comparison/verify_comparison_pilot.py <RUN_REAL>
```

Aceite somente com auditoria `PASS`, gate final `READY_FOR_EXTENDED`, 2/2 pares comparáveis e motivos vazios; caso contrário registrar abstenção e examinar instâncias/tempo/cortes sem alterar o protocolo silenciosamente.

## Evidência e interpretação

A implementação não modifica os dados N2 e não reinterpreta `N2 FAIL`. `READY_FOR_EXTENDED` não é um resultado de pesquisa que comprove superioridade, nem certificado racional. A confirmação de ambiente de produção deverá ser revisada por um validador distinto do autor deste patch, como exige o protocolo `/tlc-spec-driven`.
