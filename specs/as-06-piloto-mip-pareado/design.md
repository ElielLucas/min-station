# AS06 — Piloto MIP 300/600 s com seeds e controles — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-06-piloto-mip-pareado/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. `as_mip_pilot.py`: agenda pareada com seeds e braços; nenhuma alteração no executor FC histórico.
2. Separar custo de preparação compartilhada e custo imputado a cada braço por regra congelada, incluindo preparo de A_r, K e inicialização; reportar tanto wall total global quanto custo atribuído.
3. `as_mip_gate.py`: versão e hashes das políticas; séries de LB/UB validados, gap relativo e absoluto, falhas de build/memory/timeout como dados de aplicabilidade.
4. Núcleo inteiro serve para atribuir origem do bound; não considerar instalação física sem validação.
5. Critérios de materialidade e não inferioridade são numéricos pré-registrados em AS00; gate requer duas famílias e explica riscos ocultados por médias.

## Dependencies and Reuse

- **Pré-condição externa:** AS05=GO; AS04=PASS.
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

Não usar apenas média de instâncias resolvidas; contabilizar regressões, timeouts, OOM e custo pré-solver. Candidatos precisam superar controles em pelo menos duas famílias de grafos independentes.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
