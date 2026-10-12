# AS-05 — Protocolo diagnóstico pós-piloto

## Motivação e registro histórico

O primeiro piloto exploratório (`results/benchmark/as05-pilot-owner-exploratory-001/`) retornou `INVESTIGATE` para A2+K. Nos quatro casos completos, não houve ganho relativo LP de 1%. `puc-w3c571-seed-r1` ficou censurado na preparação e `vienna-I056-regiao-f4` em A2+K. O executor original prepara K inclusive para U, contaminando a comparação de tempos ponta a ponta. **Esse arquivo é análise posterior, não nova versão do pré-registro AS00/AS05.**

## Plano imutável

`results/benchmark/as05-diagnostic-plan-v1.json` contém SHA do `manifest.json`, `lp_gate.json` e `plan.json` originais, casos e versões de política. Validação com `--check-plan` verifica que a origem não mudou. Um novo experimento com outro budget exige plano novo, nunca editar este arquivo.

### Etapa cuts — por que a preparação demora?

Duas instâncias censuradas: `puc-w3c571-seed-r1` e `vienna-I056-regiao-f4`. Perfil em processo com deadline de 300 s por instância. Observáveis: `k_neighborhoods`, `k_c1`, `k_c2`, `k_c4_dm`, `k_canonicalize`, `k_validation_cached`; tempos da fase e quantidade de cortes C1/C2/C4-DM e únicos. Corte inválido encerra com erro, sem supor resultado LP.

**Otimização aplicada:** `assert_valid_cuts` recebe `N_plus`/`N_minus` calculados uma vez, em vez de recomputá-los para cada Z; todas as famílias de cortes e o validador original permanecem intactos. Em caso pequeno, o novo resultado e o SHA coincidem com `prepare_K` da AS02.

### Etapa censored — eliminar confusão de pré-processamento e solver

Nos mesmos dois casos, reexecutar `U`, `U_K`, `A2_K` com limite de 300 s por braço. Em U, **não calcular K**; em U_K e A2_K, calcular/validar K separadamente no budget. Associar o SHA de K ao contexto de comparação de U após obter U_K, nunca somar a U o tempo de K. Reportar tempo total e `solver_runtime_s` separadamente. Se K falhar, não há comparação +K válida.

### Etapa grouping — política, não apenas formulação

Nos quatro casos completos da AS05, repetir U_K e comparar três A2 com limite de 90 s por braço, seed 42 e quatro threads:

- `reachability_degree`: AS03 vigente;
- `balanced`: controle estrutural não informado por LP;
- `reachability_overlap`: controle novo, exclusivamente exploratório; usa Jaccard de vizinhanças no dígrafo de alcance, com divisão balanceada determinística.

Todas as partições são calculadas **antes da otimização** de seu braço. O ganho A2 é sempre em relação ao U_K pareado desse diagnóstico, não em relação a uma baseline de tempo não pareada.

## Resultados

Cada etapa gera `arms.csv`, `report.json`, `plan.json`, `manifest.json` e checkpoints por braço. A análise final requer **as três etapas íntegras** e gera `diagnostic_analysis.json`, `diagnostic_analysis.md`, `grouping.csv` e manifesto. Censuras permanecem sem objetivo LP e não são promovidas a `GO`.

## Limitações científicas

Não atualizar `as05-pilot-owner-exploratory-001/` nem reclassificar censuras passadas. A seleção de casos/políticas ocorre após observar o primeiro piloto: é desenvolvimento exploratório. Não executar casos de avaliação AS00 aqui. O modo autorizado pelo responsável permite investigar, mas não equivale a uma homologação independente das provas da AS01/AS02/AS04.
