# AS28 — Tarefas

- [x] **T1 — Auditar a família histórica.** Identificar `check_C3_violations` e versão reversa, documentar a condição de validade, a diferença para F-C3 e histórico E9.
- [x] **T2 — Montar wrapper limitado.** Implementar seleção determinística, C3 de origem/destino, BFS topológica independente, deduplicação, estados conservadores.
- [x] **T3 — Microvalidar.** Testar caminhos diretos/indiretos, `S∩T`, reversão, limites, validade frente a instalações fisicamente viáveis geradas por enumeração.
- [x] **T4 — Pré-registrar e implementar LP.** Duas armas, seis grafos independentes, hash de código, prazos, censuras e analisador sem MIP.
- [x] **T5 — Verificar dry-run e suíte.** Confirmar 12 registros sem LP e os testes disponíveis no snapshot.
- [ ] **T6 — Commit sem mudanças concorrentes.** Pesquisador deve validar `git diff --check`, versionar código e plano, obter árvore limpa.
- [x] **T7 — Executar LP real.** Executada em `results/benchmark/as28-c3-lp-001`: 12 braços, classificação `NO_SIGNAL_BOUNDED_POLICY`; arquivar manifest/rows/analysis.
- [ ] **T8 — Decisão científica.** Relatório técnico pós-campanha produzido e recomenda STOP da política limitada; decisão humana/revisão independente pendente. AS26 não autorizada.

**Rastreabilidade T6:** manifesto registra commit `6f9e6e1e60e41876d916ca10fc82dd0aed43c275` e árvore rastreada limpa; confirmação final do histórico Git e arquivamento pelo pesquisador continuam necessários.
