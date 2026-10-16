# AS21 — Relatório de implementação e campanha real

**Status:** implementação validada; **campanha AS21 Gurobi executada pelo pesquisador**, evidências em `results/benchmark/as21-hl-lp-001/`. Gate automático `INVESTIGATE`. Nenhum ganho marginal de HL foi observado nos quatro pares ótimos; os dois restantes foram censurados.

## Contexto AS20 (observado, não resultado AS21)

O arquivo arquivado `results/benchmark/as20-hl-lp-001/analysis.json` registra 12 braços e gate `INVESTIGATE`, zero cortes; quatro pares ótimos sem ganho marginal e dois pares censurados. A enumeração integral teve interrupções e ausências de suportes elegíveis. Não permite concluir que HL seja redundante.

## Verificação sintética AS21

Na construção K4 de quatro relés, o LP COMP+K é 2. O certificado AS21 para `y(W)≥3` examina todos os subconjuntos inferiores a três relés, isto é `1+4+6=11` padrões físicos inviáveis. Após adicionar a desigualdade ao COMP+K, o LP passa a 3. AS19 usava 16 padrões para a mesma testemunha. A melhoria é de **contagem de padrões no exemplo sintético**, sem extrapolação para tempo ou ganho em benchmark real.

## Campanha real AS21 — evidências arquivadas

A execução Gurobi produziu 12 registros: quatro pares ótimos (`PUC CC9`, `PUC BIP42`, `PUCN CC3`, `MAPF Room`), nenhum corte HL, nenhum ganho LP; nesses casos o oráculo retornou padrões viáveis com cardinalidade inferior à necessária para os RHS testados. `Vienna I056` e `PUC W3C571` tiveram pelo menos um braço censurado. Isso não testa as desigualdades de coeficientes gerais.

**Gate científico AS21:** `INVESTIGATE`, conforme `results/benchmark/as21-hl-lp-001/analysis.json`. A triagem de cardinalidade foi tecnicamente executada, mas o resultado não demonstra dominância geral de COMP+K sobre HL. Por esse motivo, uma AS22 separada testará normais não uniformes em suportes pequenos. Não autoriza MIP nem altera as decisões H2.
