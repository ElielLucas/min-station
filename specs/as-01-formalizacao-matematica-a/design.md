# AS01 — Auditoria matemática da formulação A e errata T18 — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-01-formalizacao-matematica-a/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. Documento normativo proposto: `docs/technical/reference/formulacoes/astra-a-grupos-origens.md` (referência congelada, revisão matemática antes da implementação).
2. Para partição 𝓑 e origem indicadora a_Bv=1[v∈B]: c_Bv=|B|−1[v∈B] e κ_v=m−1 se v∈S∪T, senão m.
3. Variáveis: y_v∈{0,1}; f^B_uv≥0, g^B_v≥0, 0≤p_Bt≤1, 0≤h^B_v≤1 para v∈B∩T. Fora dos índices: p_Bv=h_Bv=0.
4. A1: Σ_u f^B_uv+h^B_v=p_Bv+g^B_v. A2: Σ_w f^B_vw+h^B_v=1[v∈B]+g^B_v. A3: Σ_B p_Bt=1 (t∈T).
5. A4: g^B_v≤c_Bv y_v. A5: Σ_B g^B_v≤κ_v y_v. A6: Σ_{v∈Z}y_v≥1 (Z∈K). A7: min Σ_v y_v.
6. A equivalência física exige também avaliação de permanência h, chegada final gratuita a destino, terminal intermediário que exige recarga e fluxos circulantes.
7. Cadeia candidata a provar: LP(U+K) ≤ LP(A(𝓑)+K) ≤ LP(A(unitária)+K)=LP(B+K) ≤ LP(F-CC+K) ≤ OPT.
8. Casos específicos: Sec59(L=7), Tri, SharedTerminal, estrela T18 (a,b,c,d), a-v-b com S∩T e estações instaladas nos terminais.
9. Separar revisão de teorema, testemunha racional Sec59 e resultados numéricos do Gurobi; não usar `OPTIMAL` como prova racional independente.

## Dependencies and Reuse

- **Pré-condição externa:** AS00 (controle de instâncias pequenas).
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

**Gate obrigatório:** resultado `PASS` de um verificador independente das provas. O exemplo Sec59 constitui uma testemunha de ganho, não demonstra desempenho geral. Não promover A por simples contagem de variáveis.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
