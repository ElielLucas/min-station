# AS05 — Piloto LP de A e gate de promoção — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-05-piloto-lp-gate/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. `as_lp_pilot.py` usa universo AS00, construtor A e comparador AS04, sem alterar dados N1/N2/FC.
2. Campos: LP resolvido, best dual bound admissível, gap LP sobre U_K, tempo de leitura/build/solve, memória de pico, nvars/nconstr/nnz, família de grafo, status.
3. Apresentar núcleo IP como fonte alternativa de LB; se o núcleo supera A LP, discriminar a origem desse ganho.
4. Congelar um relatório `lp_gate.json` e digest dos artefatos; STOP interrompe avanço para campanha MIP, salvo nova hipótese documentada.

## Dependencies and Reuse

- **Pré-condição externa:** AS00,AS01,AS02,AS03,AS04=PASS.
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

O piloto LP é discriminante: ganho apenas em Sec59 não autoriza campanha MIP. Uma LP interrompida sem bound apropriado não recebe o rótulo de `z_LP` ótimo.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
