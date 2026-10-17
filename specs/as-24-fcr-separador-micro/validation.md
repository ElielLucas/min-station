# AS24 — Validation (fechamento com achados menores)

**Data:** 16/10/2026.  
**Spec:** `specs/as-24-fcr-separador-micro/spec.md`.  
**Result:** **PASS** — `VALIDATED_WITH_MINOR_FINDINGS`.  
**Revisão independente:** Claude, `APPROVED_WITH_MINOR_FINDINGS`, conforme veredito transmitido pelo pesquisador e documentado em `docs/technical/reference/experimentos/as24-revisao-independente-claude.md`. O parecer completo e os detalhes dos achados menores não foram fornecidos: essa limitação de rastreabilidade é declarada, não preenchida com fatos presumidos.

## Task Completion

| Tarefa | Status | Evidência |
|---|---|---|
| T1 — Representação FC-R | PASS | `experiments/cuts/fcr_rows.py:97`, `experiments/cuts/test_as24_fcr.py:91` |
| T2 — Separar Q para L fixa | PASS | `experiments/cuts/fcr_separator.py:51`, `experiments/cuts/test_as24_fcr.py:66` |
| T3 — Regiões unitárias e maiores | PASS | `experiments/cuts/fcr_regions.py:26`, `experiments/cuts/test_as24_fcr.py:106` |
| T4 — Testes independentes e adversariais | PASS | `experiments/cuts/test_as24_fcr.py:214`, `experiments/cuts/test_as24_fcr.py:120` |
| T5 — Microvalidação e relatório | PASS | `experiments/cuts/run_fcr_micro_as24.py:28`, `docs/technical/reference/experimentos/as24-validacao-separador-fcr.md:1` |

## Critérios de aceite ancorados na spec

| Requisito | Resultado esperado | Evidência e assertiva | Estado |
|---|---|---|---|
| FCR24-01 | Q ótimo para origem e L fixa | `experiments/cuts/test_as24_fcr.py:66` compara com enumeração exaustiva | PASS |
| FCR24-02 | Q ótimo para destino e L fixa | `experiments/cuts/test_as24_fcr.py:66` cobre as duas orientações | PASS |
| FCR24-03 | Todos os singletons elegíveis examinados | `experiments/cuts/test_as24_fcr.py:106`, `fcr_separator.py:143` | PASS |
| FCR24-04 | Abstenção em Q/L inválidos ou tolerância | `experiments/cuts/test_as24_fcr.py:91`, `fcr_separator.py:122` | PASS |
| FCR24-05 | Coeficientes e certificado algébrico registrados | `experiments/cuts/fcr_rows.py:97`, `fcr_separator.py:132` | PASS |
| FCR24-06 | Assinatura e deduplicação | `experiments/cuts/test_as24_fcr.py:145`, `fcr_separator.py:124` | PASS |
| FCR24-07 | Regiões maiores selecionadas com teto | `experiments/cuts/fcr_regions.py:26`, `test_as24_fcr.py:106` | PASS |
| FCR24-08 | Cobertura parcial e orçamento sem falso negativo global | `experiments/cuts/test_as24_fcr.py:120`, `fcr_separator.py:145` | PASS |

## Verificações executadas

- **Suíte geral:** `python -m unittest discover -s experiments/cuts -p 'test_*.py' -q` — **186/186 PASS** na reexecução deste fechamento; o pesquisador também relatou 186/186 com Poetry.
- **Microvalidação do pesquisador:** `MICRO_VALIDATION_COMPLETED`, seis casos, 72 verificações unitárias, quatro cortes para COMP+K com singletons. O JSON íntegro `results/benchmark/as24-fcr-micro-001.json` contém a ablação com regiões maiores; este fechamento documental **não** o reescreveu.
- **Conferência de integridade:** os cinco hashes dos arquivos AS24 contidos no JSON correspondem aos bytes no ZIP de origem; a evidência AS23 referenciada também corresponde ao hash.
- **TLC estrutural:** `validate_spec.py`, `validate_tasks.py` e `validate_state.py` executados para fechar esta revisão documental; resultados no pacote de entrega.
- **Sensor de mutação:** nenhum novo mutante foi aplicado neste fechamento somente documental. Testes comportamentais e revisão do Claude sustentam o gate; **não** atribuir ao revisor contagem de mutações não fornecida.

## Achados menores, proveniência e limites

1. `MINOR-AS24-OPEN-01` — o relatório completo do Claude não está disponível; a lista de achados menores permanece **aberta e não bloqueante**, sem inventar escopo ou correção.
2. `TRACE-AS24-COMMIT` — `source_commit` no JSON de microexecução representa o HEAD detectado antes do commit final, com `source_has_tracked_modifications=true`. Finalizar commit e regenerar evidências no checkout do pesquisador; não afirmar que o pacote criou um commit remoto ou local.
3. A separação de Q é exata apenas para L fixa. A varredura de regiões maiores é heurística, não global; a microexecução não mediu reotimização LP.

## Decisão de continuidade

**Overall:** PASS com achados menores registrados. **Gate científico AS24:** `VALIDATED_WITH_MINOR_FINDINGS`.  
**AS25:** autorizado desenvolver runner/analisador e congelar protocolo experimental. **Não executar campanha real antes do pré-registro e da conferência de proveniência.**  
**AS26:** bloqueada até evidência LP favorável e aprovação científica explícita.

**Referência do parecer independente:** `docs/technical/reference/experimentos/as24-revisao-independente-claude.md:1`.
