# AS21 — Pré-registro da triagem LP de HL (camadas inferiores)

**Política congelada antes de resultados AS21 com Gurobi.** Contrato executável no JSON vizinho `as21-preregistro-hl-lp.json`.

- Mesmos seis arquivos de desenvolvimento e hashes do AS16/AS20; dois braços `U_K` e `U_K_HL`.
- 90 segundos totais por braço; política Gurobi idêntica à AS16; saídas append-only.
- 14 vértices máximos por suporte; quatro suportes, 48 sementes K, 32 propostas por pares, 700 chamadas totais, 180 padrões por suporte, RHS máximo três; total 24 s de certificação, 10 s por suporte.
- Seleção estendida a projeções **heurísticas** de suportes K grandes; nenhuma desigualdade presumida válida a partir da projeção.
- Certificação `k=floor(sum(y*_R)+1e-7)+1`: exige inviabilidade física individual de cada padrão abaixo de k, não enumeração total do suporte.
- Ganho ≥1% em ≥2 grafos independentes e razão de tempo total ≤2 produz apenas **candidato a GO após revisão**, nunca autorização MIP automática.
- `UNKNOWN`, limite de tempo, ausência de suporte ou cap => indeterminado; não concluir dominância matemática de HL por K.
- A análise AS20 permanece preservada e pode ser comparada descritivamente, não usada para mudar os parâmetros desta AS21 após observação dos resultados.
