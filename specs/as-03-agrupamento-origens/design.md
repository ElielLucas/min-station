# AS03 — Políticas reprodutíveis de agrupamento e limites de tamanho — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-03-agrupamento-origens/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. `experiments/astra-study/as_grouping.py`: `partition_two(instance,policy,seed)`; `refine_four(instance,groups2,policy)`; canonicalizar blocos por rótulos estáveis de origem.
2. Separar políticas estruturais (vizinhanças no alcance, regiões/bolsões) de uma linha de controle balanceada; não escolher vencedora pelos dados de avaliação.
3. `as_size.py` prevê contagem do parecer: n+k(a+n+m)+h; estimativa é filtro de admissibilidade, não evidência de memória real.
4. Arquivar política, parâmetros, seed, hashes e motivo de abstenção em cada execução.

## Dependencies and Reuse

- **Pré-condição externa:** AS02=PASS; AS00 pré-registro.
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

Escolhas de agrupamento devem ser fundamentadas estruturalmente; políticas distintas podem produzir LPs sem ordem total. Não afirmar que todo `k=4` domina todo `k=2` sem relação de refinamento.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
