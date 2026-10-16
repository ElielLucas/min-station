# AS23 — Validation (fechamento pós-revisão Claude)

**Resultado técnico: PASS (`VALIDATED`)** para matemática, certificados racionais e critérios obrigatórios de testes. **Condição operacional antes de abrir a AS24 no checkout do pesquisador:** commitar os arquivos e regenerar o JSON com o `source_commit` do commit aplicado. Isso não altera o veredito matemático nem autoriza saltar a AS24 para MIP.

## Revisão independente

- **Verificador externo:** Claude Code, distinto do agente responsável pela implementação inicial, conforme relato fornecido pelo pesquisador em 16/10/2026.
- **Parecer informado:** `CHANGES_REQUIRED (leve)`; nenhuma objeção matemática. Não redundância reportada como verificada independentemente com Gurobi, certificado dual próprio e 473 mil casos adversariais; ótimo inteiro 2 por enumeração.
- **Limite de auditoria:** foi disponibilizado apenas o resumo do parecer, não seu relatório integral nem logs dos 473 mil casos. Esses números são **atribuídos ao revisor externo** e não são afirmados como verificações repetidas neste fechamento.
- **MAJOR resolvido:** o teste `test_reject_invalid_q_and_terminal_counterexamples` agora verifica `L=('d1',)` com `Q=('e1',)` em FC-R-T e a configuração física mínima com `y_e1=0`; detecta a ausência da exclusão de `S` (`noSexcl`).
- **MINOR endereçados verificavelmente:** fronteiras `d_L=2` por enumeração, JSON de disco rechecado, modelo adicional COMP+K+C8+FC-R, comparação em frações, terminologia científica e notas de proveniência. Os dez achados menores não foram apresentados na íntegra, portanto não se declara fechamento individual de todos.

## Matriz de aceite

| Requisito | Evidência reproduzível | Gate |
|---|---|---|
| FC-R/FC-R-T válidos, incluindo exclusões de Q, circulação e terminais coincidentes | `docs/technical/reference/tecnico/as23-prova-fcr.md`; `experiments/cuts/test_as23_fcr_witness.py:96-128` | PASS |
| Seleção ótima de Q com L fixa e demandas 1 e 2 nas duas direções | `experiments/cuts/test_as23_fcr_q_selection.py:55-64` | PASS |
| Grafo do testemunho, K, C6 e C8 gerados a partir do baseline | `experiments/cuts/verify_fcr_witness.py:77-113` | PASS |
| Certificados exatos de seis LPs sintéticos | `results/benchmark/as23-fcr-witness-001.json`; `experiments/cuts/test_as23_fcr_witness.py:129-155` | PASS |
| Não redundância frente a K e complementaridade mensurável com C6+C8 | Objetivos `1`, `7/5`, `11/10`, `7/5`, `47/30`, `17/10` e diferenças exatas em `experiments/cuts/verify_fcr_witness.py:387-434` | PASS |
| Ótimo inteiro físico igual a 2 | `experiments/cuts/verify_fcr_witness.py:294-307`; 24 configurações unitárias inviáveis, par `x11,x21` viável | PASS |
| Literatura e limites de novidade | `docs/technical/reference/tecnico/as23-prova-fcr.md` | PASS (escopo delimitado) |
| Revisão adversarial autor ≠ revisor | Relato de parecer do Claude Code informado pelo pesquisador | PASS no conteúdo obrigatório; anexar o parecer integral quando disponível |
| Commit final e proveniência no checkout local | `source_commit` e `source_sha256` do JSON regenerado **após commit** | PENDENTE NO CHECKOUT DO USUÁRIO |

## Reprodução e publicação

```bash
poetry run python experiments/cuts/verify_fcr_witness.py --output results/benchmark/as23-fcr-witness-001.json
poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q
python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-23-fcr-revisao-matematica/spec.md
python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-23-fcr-revisao-matematica/tasks.md
```

**Proveniência:** o arquivo de origem compartilhado inclui HEAD `56b8957485c673fb08460ef836257773fb67933f`, mas contém alterações não commitadas. O verificador registra esse HEAD com ressalva quando disponível; **não deve ser confundido com o futuro commit que incluirá as correções**. Após o commit local, gerar novamente o JSON (para registrar o SHA efetivo) e adicionar a atualização de evidência em um commit complementar.

**Decisão:** não há bloqueador matemático reportado; o MAJOR de teste foi corrigido e revalidado. AS23 está tecnicamente validada. AS24 pode ser iniciada após finalizar a proveniência do checkout local, mantendo os MINOR não individualizados como pendências documentais não bloqueantes.
