# AS20 — Tasks

## T1 — Pré-registro e proveniência
- [x] Criar `as20-preregistro-hl-lp.json` com seis instâncias, hashes, braços, solver, orçamento e gate.
- [x] Validar plano de origem AS16 e identidade independente dos seis grafos.
- [x] Garantir ausência de dados de avaliação e modo dry-run.

## T2 — Seleção determinística de suportes HL
- [x] Implementar propostas baseadas em K pequenos e uniões limitadas de K, privilegiando incompatibilidades coletivas.
- [x] Não truncar suportes acima de 10; registrar casos sem candidatos.
- [x] Testar testemunha K4 e independência da ordem de entrada.

## T3 — LP pareado e certificação física
- [x] Implementar braços `U_K` e `U_K_HL` com `compile_u` e Gurobi.
- [x] Reutilizar `separate_hl` e oráculo físico AS14; cortar somente com enumeração completa.
- [x] Medir tempo total, preparação K, solves, suporte, certificação, cortes e hashes.
- [x] Aplicar deadline absoluto por subprocesso e proibir sobrescrita.
- [x] Executar seis casos LP no Gurobi do pesquisador (12 braços; `INVESTIGATE`).

## T4 — Análise e auditoria
- [x] Implementar `analyze_hl_lp` conservador para ótima/censura/gain/cost.
- [x] Testar casos negativos, orçamento parcial, duplicidade, alterações de proveniência e dry-run.
- [x] Rodar dry-run com arquivos reais e verificar saída estrutural.
- [x] Consolidar `manifest.json`, `rows.json`, `analysis.json` da execução real.

## T5 — Decisão científica
- [x] Redigir relatório numérico com efeitos e custos LP reais.
- [ ] Revisão científica independente da validade e resultados.
- [x] Registrar continuidade limitada pela AS21 sem promover HL a MIP.

**Etapa concluída experimentalmente:** 12 braços registrados; gate `INVESTIGATE`; nenhuma promoção MIP, revisão humana independente pendente.
