# MAPF benchmarks (MovingAI)

- URL: https://movingai.com/benchmarks/mapf.html (arquivos em https://movingai.com/benchmarks/mapf/)
- Referência: R. Stern et al., "Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks", SoCS 2019.
- Licença: Open Data Commons Attribution License (ODC-By), conforme a página do benchmark.
- Download: 2026-09-26.

| Arquivo | SHA-256 |
|---|---|
| mapf-map.zip | 9da2e4c5ce03aa4e063b3a283ce874590b36cc4f31a297fe7ecb00d105abf288 |
| mapf-scen-random.zip | 20b7838f7a51f13e90a63ee138e9435fb4e41b0381becbc7313b7d3a7d859276 |
| mapf-scen-even.zip | 249896aaf15ef2d9beb378f954f0b7ca17189c6dec1b76a78965bbdbe714ad75 |

`maps/`, `scen-random/` e `scen-even/` são a extração desses zips, sem alteração.
Os comprimentos ótimos gravados nos `.scen` são octis (8-vizinhança); o benchmark-v1 usa
4-vizinhança (passos de Das) e não usa esses comprimentos.
