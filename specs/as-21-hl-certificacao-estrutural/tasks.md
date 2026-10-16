# AS21 — Tasks

## T1 — Contrato matemático e pré-registro
- [x] Formular e justificar o certificado `∀ |A|<k: inviável(F∪A) ⇒ Σ y_R≥k` com monotonicidade física.
- [x] Congelar seis fontes AS16, política LP, gate, caps e modo append-only em `as21-preregistro-hl-lp.json`.

## T2 — Certificação HL eficiente
- [x] Criar `hl_layered.py`, separador independente de H2, com teste das camadas estritamente inferiores ao RHS.
- [x] Abster-se para `UNKNOWN`, orçamento, cap, pattern incompleto; preservar hashes.
- [x] Reproduzir K4 com 11 chamadas e corte válido de cardinalidade 3.

## T3 — Seleção estrutural
- [x] Criar `hl_structural.py` para suportes K pequenos, uniões e projeções explícitas de K grandes.
- [x] Testar determinismo, identidade das projeções e validação independente pelo oráculo.

## T4 — Piloto LP comparável
- [x] Implementar `run_hl_lp_as21.py` com os braços U_K e U_K_HL em subprocessos, 90s totais por braço.
- [x] Implementar `analyze_hl_lp_as21.py` e comparação descritiva com AS20.
- [x] Validar seis arquivos em dry-run e integração com o compilador COMP+K sobre K4.
- [ ] Executar os seis casos em máquina com Gurobi e arquivar os JSON de saída.

## T5 — Resultado científico
- [ ] Registrar os ganhos/custos medidos e censuras da execução AS21 real.
- [ ] Submeter validade matemática e resultados a revisão independente.
- [ ] Decidir próximo gate sem habilitar MIP automaticamente.

**Estado:** implementação pronta; experimento real e decisão científica pendentes.
