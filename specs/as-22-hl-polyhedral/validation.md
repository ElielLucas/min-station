# AS22 — Validation

## Validações locais

- [x] LP de separação construído apenas sobre padrões `VIABLE` certificados.
- [x] `β` recalculado com `Fraction` sobre o conjunto viável completo.
- [x] Certificados físicos e monotonicidade sem `UNKNOWN` aceito silenciosamente.
- [x] Testes de fontes, hashes, quotas, caps, determinismo e append-only.
- [x] Testemunha não uniforme: `a OR (b AND c)`, LP fracionário massa 1.1, corte `1/2 a + 1/2 c ≥ 1/2`, violação 0.2.
- [x] K4: aplicação no compilador COMP+K existente fortalece o limite LP 2 → 3.
- [x] `--dry-run` das seis instâncias de desenvolvimento: 12 registros; **não constitui campanha LP**.
- [x] Suíte de cortes do snapshot: **160 testes OK** no ambiente de preparação.

## Pendências obrigatórias

- [ ] Executar `run_hl_lp_as22.py` com Gurobi no ambiente do pesquisador.
- [ ] Publicar `results/benchmark/as22-hl-lp-001/{manifest,rows,analysis}.json` e preencher relatório experimental.
- [ ] Verificar ganho marginal real e custo físico de certificação, observando limites/censuras.
- [ ] Revisão científica independente antes de qualquer decisão de promoção ou experimento MIP.

Os ensaios sintéticos não são evidência de ganho sobre COMP+K em instâncias reais.
