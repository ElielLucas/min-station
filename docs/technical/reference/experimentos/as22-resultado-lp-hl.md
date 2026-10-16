# AS22 — HL poliédrica: evidência inicial e campanha real

**Status:** implementação/suíte de testes concluídas. **Campanha Gurobi pendente** no ambiente de pesquisa. **Nenhum ganho LP real pode ser atribuído à AS22 neste momento.**

## Motivação científica

A AS21 executou os seis casos do desenvolvimento e registrou gate `INVESTIGATE`: quatro pares ótimos, nenhum corte de cardinalidade; dois casos censurados. Suportes foram selecionados/certificados, mas a metodologia limitava `α_v = 1` e não cobria facetas gerais de `conv(Φ_R)`. Isso motiva uma triagem de coeficientes não uniformes, sem revisar resultados anteriores.

## Evidências sintéticas certificadas

**Testemunha não uniforme:** rede alternativa com caminhos `s-a-t` ou `s-b-c-t`, autonomia 1 e suporte `{a,b,c}`. A projeção viável é `a ∨ (b ∧ c)`. O ponto `(0.1,0.5,0.5)` soma 1.1 e não viola cardinalidade ≥1, mas viola a desigualdade racional válida `1/2 y_a + 1/2 y_c ≥ 1/2` por 0.2. O oráculo físico confirma todos os padrões (diretos ou por monotonicidade).

**K4:** sobre a implementação existente COMP+K, a triagem certifica HL e reproduz limite LP `2 → 3` no exemplo de quatro relés. Não é evidência de ganho real de benchmarks nem prova de superioridade global a K.

Arquivo de evidência: `results/benchmark/as22-hl-poly-micro-001.json` (gerado localmente, append-only).

## Campanha pendente

Executar no projeto com Gurobi:

```bash
poetry run python experiments/cuts/run_hl_lp_as22.py \
  --output-dir results/benchmark/as22-hl-lp-001
```

Depois registrar os 12 braços em `results/benchmark/as22-hl-lp-001/{manifest,rows,analysis}.json`, comparando limites LP, tempo parede total, tempo de certificação, padrões inferidos/consultados, tipos de suporte, cortes e razões de censura. O gate permanece **PENDENTE**, não `GO` ou `STOP`.

**Decisão:** continuar somente investigação LP de HL geral, sem habilitar MIP e sem inferir redundância universal de HL contra K.
