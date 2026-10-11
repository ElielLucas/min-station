# AS07 — Contingência: cortes por origem e matching compartilhado — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-07-cortes-origem-matching/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. Desenvolver antes um documento formal `docs/technical/reference/formulacoes/astra-cortes-origem.md`: porta de saída da origem, arcos A_r ilimitados, trânsito em v com capacidade y_v, absorção t com capacidade p_st, permanência p_ss.
2. Matching parcial: para cada s∈U, Σ_t p_st=1; para cada t, Σ_s∈U p_st≤1; subset declarado; quando U=S, igualdade por contagem.
3. Separação por máximo fluxo/corte mínimo em uma rede auxiliar por vez; reusar estruturas e parametrizar máximo de origens/rodadas/cortes.
4. Integração apenas após solução LP raiz; adicionar desigualdades válidas, reotimizar LP, depois MIP completo U_K; não usar master restrito como bound global.
5. Comparar U_K+cuts vs U_K e A aprovada nas mesmas condições, sem fazer F-CC explícita requisito.

## Dependencies and Reuse

- **Pré-condição externa:** AS01 auditado; AS05=STOP ou AS06=STOP/INVESTIGATE, após decisão escrita.
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

A proposta anterior permanece concorrente, **não** método simultâneo obrigatório. Redes de origem têm capacidade `y_v` separadamente, nunca capacidade consumida em conjunto por todos os robôs.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
