# AS00 — Escopo, benchmark difícil e pré-registro — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-00-benchmark-e-pre-registro/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. Arquivo proposto `experiments/astra-study/as_protocol.py`: validação do manifesto, fingerprints, `family_id` e seleção sem dependência de F-CC.
2. Produzir `protocol.json` e `pre_register.md` em novo diretório versionado de resultados; marcar hipóteses e regras de exclusão antes dos resultados.
3. Incluir as instâncias grandes que estressam a nova abordagem, mesmo quando A ou F-CC não couberem na memória.
4. Tratamento de faltas: `NOT_MEASURED_INPUT`, `NOT_MEASURED_CAP`, `NOT_MEASURED_MEMORY`, `NOT_MEASURED_BUDGET`, `ERROR`, nunca imputar zero.

## Dependencies and Reuse

- **Pré-condição externa:** Pareceres Astra; manifesto benchmark-v1.
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

A ordem do estudo é: corrigir universo e pré-registro → provar A → validar protótipo → comparar controles → pilotos → ramificação condicionada → avaliação. A inexistência de nova evidência nunca autoriza alterar resultados históricos.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
