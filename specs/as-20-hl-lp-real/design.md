# AS20 — Design experimental e infraestrutura

## Arquitetura

```text
Plano AS20 --hash AS16--> valida seis fontes AS16 (manifesto, SHA, split)
                         |
                [em dois processos distintos]
          U_K                            U_K_HL
   load + K + compile_u             load + K + compile_u
        solve LP                         solve LP y*
                                            |
                       select_hl_supports(K pequenos + pares K)
                                            |
                      separate_hl (AS19, MatchingOracle AS14)
                     ↙ cert. completa           ↘ UNKNOWN/cap
            cortes α=1, β exato                ABSTAIN
                      |                          |
               adiciona HL                      sem cortes
                      |                          |
                  reotimiza LP ──────────────────┘
                         |
             manifest.json + rows.json + analysis.json
                         |
               ganho marginal + tempo total + censuras
```

## Contratos

- `hl_supports.select_hl_supports(V, y*, k_supports=K, ...) -> (tuple[R], diagnostics)`: não certifica, não assume HL válido, suporta K grande via diagnóstico de exclusão, não trunca suportes.
- `hl_local.separate_hl(physical, y*, supports, options)`: usa `MatchingOracle` certificado, classifica todos padrões binários, recalcula RHS racional; um único `UNKNOWN` interrompe emissão daquele suporte.
- `run_hl_lp.py`: reutiliza solver e compilador AS16 sem alterar modelos congelados; todo braço é um subprocesso com deadline absoluto. `U_K_HL` paga **dois solves** (pré e pós-separação) e todo custo do oráculo.
- `analyze_hl_lp.py`: nunca usa limites LP censurados como se fossem ótimos; diferenças e tempos de parede são emparelhados pelo nome e `raw_graph_id`.

## Limitações explicitamente registradas

A seleção é proposicional e limitada. A ausência de suporte elegível em uma instância não descarta HL. Um suporte até dez vértices tem no máximo 1024 padrões para certificar. A política usa `α=1`, não separa o casco geral `Q_R` e não oferece provas de facetness. A campanha não incorpora H2 nem abre uma corrida MIP, preservando a independência matemática pretendida para HL.

**Segurança:** entrada inválida, hash divergente, saída existente, erro de solver ou timeout geram erro/status conservador, nunca aceitação de corte sem certificado.
