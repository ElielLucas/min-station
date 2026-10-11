# AS05 — Piloto LP de A e gate de promoção — Design

**Status:** implementação estrutural preparada; campanha LP não executada  
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

## Implementação concreta

- Runtime: `experiments/formulation-comparison/as05_{protocol,gate,pilot}.py`.
- CLI: `experiments/formulation-comparison/run_as05_pilot.py`.
- Matrizes: seis instâncias AS00, U/U_K/A2_K com Gurobi via AS04; CORE_IP e FCC pequenos apenas controles condicionais, sem objetivos imputados.
- Comparabilidade: o AS04 passa a receber `grouping_seed` opcional; fixar 42 enquanto variam seeds do solver 42/43/44 impede confusão entre efeitos da partição e do solver.
- `GO` condicionado à materialidade prospectiva em ao menos dois grafos e duas fontes, com reprodução e custo; falta de evidência → `INVESTIGATE`.
- Apêndice prospectivo materialidade fica em `results/benchmark/as05-prospective-plan-v1.json` gerado por CLI **somente no repositório do usuário**; não é fornecido como resultado realizado.
- Resultados em diretório exclusivo append-only, hashes e evidências AS04 por caso.
