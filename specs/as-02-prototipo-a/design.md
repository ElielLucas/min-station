# AS02 — Protótipo da formulação A e validação exaustiva — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-02-prototipo-a/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. Propor `experiments/astra-study/as_model_a.py` com `build_A(instance, groups, K, relax)` e metadados de contagem de variáveis, linhas e não zeros.
2. Reusar `ms_utils.py`, `experiments/cuts/harness.py::prepare_cuts` e `experiments/cuts/independent_validator.py`; não tocar em `fcc.py`/`baseline.py` para implementar A.
3. Testes `test_as_model_a.py`: partição aleatória válida, única, refinada, cruzamentos S∩T, instâncias Sec59 e SharedTerminal; comparar viabilidade de y fixado por enumeração física.
4. Separar solução incumbente MIP, bound numérico e eventual prova racional; registrar a origem de cada evidência.

## Dependencies and Reuse

- **Pré-condição externa:** AS01=PASS.
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

**Gate obrigatório:** correspondência exaustiva com o validador físico em todos os pequenos casos. Implementações inválidas não devem ser corrigidas com exceções ad hoc para uma única instância.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
