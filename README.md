# MIN-STATION — Programação Linear Inteira

Pesquisa em PLI e métodos exatos para o MIN-STATION de Das (alocação mínima
de estações de recarga para robôs não rotulados com autonomia limitada).

Antes de qualquer trabalho, leia `docs/project-overview.md` e `RESEARCH.md`.
Instruções para assistentes de IA estão em `CLAUDE.md`.

## Fontes de verdade

| Pergunta | Fonte |
|---|---|
| Definição do problema | `docs/technical/reference/min-station-das.pdf`, resumido em `docs/context-ai/min-station-domain.md` |
| Formulação matemática do baseline | `docs/context-ai/base-formulation.md` (balanço unificado, variante U) |
| Implementação do baseline | `baseline.py` (`construir_modelo_baseline`) e `ms_utils.py` (leitura e dígrafo de alcance) |
| Plano experimental vigente | `docs/technical/plans/` (o mais recente) e `docs/technical/reference/direcoes-pli-min-station.md` §13–14 |
| Pontos em aberto | `docs/technical/governance/open-questions.md` |

Documentos históricos, que **não** descrevem o baseline atual:
`docs/technical/reference/formulacao-base-all-vertices.pdf` (balanços separados,
anterior à variante U), `docs/technical/reference/artigo-sbpo.pdf` (estações só
em vértices intermediários) e os scripts em `experiments/alternative-formulations/`,
`experiments/benders/`, `experiments/lagrangean/`, `experiments/cumulative/` e
`experiments/preprocessing/`.

## Métrica das instâncias

Das mede a autonomia em passos num grafo não dirigido. O pipeline usa a
distância de caminho mínimo com os pesos do arquivo e não simetriza arcos.
Por isso:

- `hc9u` (pesos unitários, não dirigido) é o problema de Das;
- `hc10p`–`hc12p` e `bip42p` têm pesos, mas `A_r = E` (uma aresta por carga),
  o que as torna idênticas ao problema de Das com r=1;
- `cc10-2p` e `cc12-2p` são uma extensão ponderada;
- instâncias TNTP (Chicago, Barcelona, Philadelphia, Anaheim) são uma extensão
  ponderada e dirigida.

Detalhes em `open-questions.md` (Q2 e Q7).

## Gerar instâncias

```bash
# TNTP (arcos dirigidos, comprimentos convertidos para km inteiros)
python src/converters/gen_min_station_tntp_to_minstation.py \
    --repositorio raw-data/TransportationNetworks --caso Philadelphia \
    --saida instances/Philadelphia.txt --n-nos 800 --m-st 6 --percentil-r 0.5 --reindexar

# SteinLib (arestas não dirigidas com os pesos originais)
python src/converters/steinlib_to_minstation.py raw-data/steinlib/hc9u.stp instances/hc9u.txt
```

## Experimentos atuais

Código em `experiments/cuts/`; resultados em `results/cuts/`; relatórios em
`docs/technical/reference/resultados-*.md`.
