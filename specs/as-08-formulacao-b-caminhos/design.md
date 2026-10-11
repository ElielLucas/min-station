# AS08 — Contingência: formulação B por caminhos e pricing — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-08-formulacao-b-caminhos/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. Caminhos P_s em H; x_P≥0; B1 Σ_{P∈P_s}x_P=1; B2 Σ_{P:end=t}x_P=1; B3 Σ_{P∈P_s:v interno}x_P≤y_v (v≠s); B4 Σ_{P:v interno}x_P≤κ_v y_v; K e min Σy.
2. Custo reduzido: Σ_{v interno P}(γ_sv+μ_v)−π_s−τ_t. Busca em rede de nós divididos para custos internos não negativos.
3. Bound dual candidato do parecer: η_v=max(0,κ_v μ_v+Σ_{s≠v}γ_sv+Σ_{Z∋v}θ_Z−1); L=Σπ+Στ+Σθ−Ση; LB=max(0,L+Σ_s min(0,ℓ_s)). Provar e verificar sinal/orientação antes de uso.
4. No pequeno porte, enumeração de caminhos para comparar o pricing implícito com o master completo; em grande porte, orçamento + censura.
5. Não reabrir `N2 FAIL`, que usa outro pricing de configurações; reutilizar apenas infraestrutura quando contratos coincidirem.

## Dependencies and Reuse

- **Pré-condição externa:** AS01; AS05/AS06 evidenciam que A exige muitos grupos.
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

B é uma alternativa de **representação implícita da versão totalmente desagregada**, não uma família independente de força. Custo reduzido e certificação dual são hipóteses matemáticas a revisar.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
