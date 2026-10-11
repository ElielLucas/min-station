# AS11 — Campanha final condicionada de até 3.600 s — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-11-campanha-avaliacao-congelada/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. `as_final_campaign.py`: ler `pre_register.json` congelado, executar somente braços promovidos e controles U/U_K com mesmas seeds; F-CC restrita a controles pequenos fora da seleção principal.
2. Armazenar manifest, input hash, commit, configuração do solver, Gurobi versão, wall de preparação e solver, Work/nós/memória, UB validado e LB numérico.
3. Análise de survival/runtime-to-target apropriada a timeouts, taxas de construção/conclusão, ganhos por família e regressões extremas.
4. Censura não vira zero, infinito artificial ou exclusão silenciosa. Se nenhum ramo tiver ganho, gerar registro legítimo de campanha não realizada.

## Dependencies and Reuse

- **Pré-condição externa:** AS06=GO, ou ramo condicional com gate aprovado; AS00 protocolo congelado.
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

Se nenhum candidato passar, **não executar** campanha longa. `CAMPAIGN_NOT_AUTHORIZED` é um resultado legítimo de planejamento, não ausência de pesquisa.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
