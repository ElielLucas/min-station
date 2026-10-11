# AS10 — Contingência: busca primal controlada no compacto — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-10-busca-primal-contingente/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. `as_primal.py` usa conjuntos de estações e movimentos locais sob orçamento; pode reutilizar `experiments/cuts/primal.py` sem reinterpretar scripts E13.
2. `as_primal_compare.py` compara U_K com e sem a mesma política de busca e opcionalmente A sob mesma condição inicial; resultados separados do estudo de LB.
3. Núcleo inteiro somente como controle de bound, nunca como prova de viabilidade física; verificar todo UB via `viavel`.

## Dependencies and Reuse

- **Pré-condição externa:** AS06 sem ganho dual; decisão científica registrada.
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

O ganho de UB é avaliado em experimento separado. Um lower bound calculado em subproblema restrito não é limite inferior global do MIN-STATION.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
