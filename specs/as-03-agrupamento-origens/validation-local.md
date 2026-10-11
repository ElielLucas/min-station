# AS03 — Evidências de validação local (não é homologação independente)

**Data:** 2026-10-11  
**Escopo:** pacote em cópia isolada, com `as02_model_a.py` do pacote AS-02 e com o validador de specs disponibilizado no ZIP do MIN-STATION.

## Testes executados

- `PYTHONHASHSEED=0 python3 -m unittest discover -s experiments/alternative-formulations -p 'test_as03*.py' -v` — **27/27 PASS**.
- `PYTHONPATH=. python3 experiments/alternative-formulations/run_as03_smoke.py` — `AS03_SMOKE_PASS`, sem resolver LP/MIP.
- `python3 -m compileall -q ...` — PASS, sintaxe Python.
- `validate_spec.py specs/as-03-agrupamento-origens/spec.md --strict` — 0 erro, 0 aviso.
- `validate_tasks.py specs/as-03-agrupamento-origens/tasks.md --strict` — 0 erro, 0 aviso.

## Rastreabilidade

| Requisito | Testes locais relevantes | Resultado |
|---|---|---|
| AS03-01 | reordenação V/S/T/A_r, hash entre processos com `PYTHONHASHSEED` distintos, cobertura de S | PASS local |
| AS03-02 | A4 aninhada, hash do pai, autorização, m baixo, instância diferente, adulteração de hash | PASS local |
| AS03-03 | fórmula de contagem exata com interseção S∩T, contagem `compile_a` em A2/A4, K | PASS local |
| AS03-04 | caps de tamanho, memória proxy, reserva de orçamento; casos retidos, medições nulas, não autorização | PASS local |
| AS03-05 | ausência de campos de objetivo, estabilidade sob nome de caso, registro de policy/seed/hash | PASS local |

## Sensores de discriminação

- `test_sensor_size_mutation_rejected_by_count_comparison` rejeita um contador intencionalmente incorreto (`nvars-1`).
- `test_as03_02_rejects_tampered_parent_hash` rejeita um vínculo A2 adulterado antes do refinamento.
- `test_as03_02_nonnested_candidate_detected` recusa uma partição cruzada não aninhada.

## Pendências bloqueantes para PASS

1. Ruff **não pôde ser executado no ambiente desta entrega** (não instalado aqui). Executar no Poetry do usuário.
2. Testes no checkout original e `git diff --check` pendentes.
3. `AS01` revisão matemática independente e `AS02` revisão/homologação pendentes no contexto observado.
4. Revisor independente (autor ≠ verificador) ainda precisa produzir `validation.md` com PASS/FAIL por requisito, caminhos e evidências.
5. Commits locais atômicos T1/T2/T3, sem push, ainda não foram criados no repositório.
6. Nenhuma campanha de avaliação, tuning ou teste de desempenho em instância difícil foi realizada. A4 segue `NOT_AUTHORIZED` sem AS05.

**Conclusão:** protótipo e testes locais prontos para integração, **AS03 não homologada**.
