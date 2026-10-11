# AS09 — Contingência: formulação C de estados de bateria — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-09-formulacao-c-cumulativa/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. Estados (v,q) com q∈[0,r]; fluxo por arestas originais F^q_uv, recarga z^q_v (q≥1), absorção e^q_t; só y binário.
2. Conservação por estado conforme parecer, incluindo injeção da origem em q=0, retorno de recarga a q=0 e absorção de destino em qualquer q; demanda final Σ_q e^q_t=1.
3. Equação normativa candidata C1 (exigir revisão de índices): para todo vértice v e estado q=0,...,r, `Σ_{u:{u,v}∈E} F^{q−1}_{uv} + 1[q=0](a_v + Σ_{ℓ=1}^r z^ℓ_v) = Σ_{w:{v,w}∈E} F^q_{vw} + 1[q≥1]z^q_v + e^q_v`; termos de fluxo para q−1<0 ou q≥r são zero, `e^q_v=0` fora de T. Exigir C2: `Σ_{q=0}^r e^q_t=1` para t∈T.
4. Ativação obrigatória Σ_{q=1}^r z^q_v≤κ_v y_v; incorporar K idêntico a U_K; não confundir com ativação histórica z^q≤m y isolada.
5. Testar estrela, permanência, trânsito por destino, r=1 e comparações LP contra U; reportar quando pré-processamento de K materializa H/A_r apesar da formulação C.

## Dependencies and Reuse

- **Pré-condição externa:** AS01; AS03 tamanho de A_r; gate justificado.
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

C é reserva para custo de representação em alcance denso. A relação LP com U deve ser comprovada; não confundir possíveis ganhos por tamanho com força de relaxação.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
