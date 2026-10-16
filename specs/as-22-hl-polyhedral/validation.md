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

## Validação posterior à campanha real (evidência externa)

- [x] O pesquisador executou `run_hl_lp_as22.py` com Gurobi: 6 casos e 12 registros, conforme JSON versionado.
- [x] Os arquivos `results/benchmark/as22-hl-lp-001/{manifest,rows,analysis}.json` foram examinados; gate `INVESTIGATE`.
- [x] Quatro pares ótimos apresentaram zero cortes e zero ganho LP; dois permanecem censurados.
- [x] Revisão externa Astra: 16 suportes de cardinalidade 8, 11 projeções de pares K, 5 projeções K grandes, 16 consultas físicas para padrão vazio viável, 4.080 inferências por monotonicidade. A linha local não foi promovida.

**Limitação documental:** `source_commit` no manifesto pode preceder código AS22 efetivamente executado; é preciso estabelecer proveniência integral antes de publicar como reprodução estrita.

**Não concluído:** autorização MIP (não concedida); generalização para HL global (não demonstrada).

Os ensaios sintéticos não são evidência de ganho sobre COMP+K em instâncias reais.
