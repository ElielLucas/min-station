# AS12 — Síntese científica e encerramento reproduzível — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-12-sintese-decisao-cientifica/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. `docs/technical/reference/astra-sintese-cientifica.md`: perguntas, hipóteses, provas, conjunto de casos, protocolo, limites e decisões.
2. `as_synthesis.py` compila tabelas somente de linhas existentes e validamente classificadas; faltas explícitas.
3. Comparação separada: (1) LP/custo de construção, (2) MIP ponta a ponta/UB/gap, (3) robustez/OOM/timeout, (4) validade física e certificação racional, (5) origem/família.
4. Decisão final inclui resultados não-promovidos e motivo de não executar 3.600 s; não importar automaticamente sucesso/fracasso de antigos FC/N2 para A.

## Dependencies and Reuse

- **Pré-condição externa:** AS05 e AS06, quando habilitada; AS07–AS11 se executadas ou dispensadas por gate.
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

A síntese deve preservar o caráter prospectivo em relação aos novos métodos, mas reconhecer que as instâncias de avaliação já possuem resultados históricos conhecidos.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
