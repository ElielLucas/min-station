# AS05 — Protocolo de investigação fatorial A2/A4 × K

**Classificação:** pós-hoc exploratória, exclusivamente desenvolvimento AS00.  
**Origem:** piloto LP AS05 e reensaio diagnóstico v2.  
**Gate científico:** `PENDING`, promoção `NOT_AUTHORIZED`.

## Motivação

Os seis resultados A2+K do desenvolvimento AS05 (incluindo os dois reensaios v2) não mostraram ganho LP material de 1% sobre U+K. Ainda falta separar efeito de **grupos A2/A4** de **cortes K**, pois as quatro combinações da formulação A não haviam sido comparadas com e sem K sobre as mesmas instâncias.

## Desenho fixado antes da execução

| Braço | Grupos | K | Papel |
|---|---:|---|---|
| U | Agregado | Não | Baseline ablação |
| U_K | Agregado | Sim | Referência fortalecida |
| A2 | 2 | Não | Desagregação isolada |
| A2_K | 2 | Sim | Desagregação + K |
| A4 | 4 | Não | Refinamento isolado |
| A4_K | 4 | Sim | Refinamento + K |

- **Instâncias:** seis casos de desenvolvimento da AS05, sem substituição ou filtragem por desempenho.
- **Agrupamento:** política `reachability_degree`, seed 42; A4 = `refine_four(A2)`, explicitamente aninhado, com hashes pai/filho preservados.
- **K:** famílias C1+C2+C4-DM, validador exato `bitset-v2`; preparação independente por braço +K e nenhuma preparação K nos braços sem K.
- **Solver:** Gurobi LP, seed 42, 4 threads, sem warm start; orçamento **300 s ponta a ponta por braço**.
- **Recursos:** máximo 2.000.000 variáveis e restrições, proxy heurístico de memória 8 GiB (não limite certificado) e `RLIMIT_AS` conforme plano.
- **Censura:** timeout, erro, memória ou modelo não construído preservam linha e têm `lp_opt_value = null`.
- **Resultados:** 36 linhas nominais (6×6), com estados mesmo se não resolvidos; contraste só para LP ótimo numérico em ambos os braços.

## Perguntas/efeitos

1. U→U+K: efeito K no baseline.
2. U→A2: efeito dos dois grupos isoladamente.
3. A2→A4 e U→A4: força do refinamento sem cortes.
4. A2→A2+K e A4→A4+K: efeito K em cada desagregação.
5. A2+K→A4+K: força incremental do refinamento sob K.
6. U+K→A2+K e U+K→A4+K: ganho líquido sobre a referência principal.
7. **Interação** `[z(A4+K)-z(A2+K)]-[z(A4)-z(A2)]`: K altera a utilidade do refinamento?

O estudo **não** declara que diferenças de LP se traduzam em menor gap/tempo MIP; isso exigirá comparação inteira posterior.

## Leitura e decisões

- Limites maiores representam relaxações mais fortes, mas considerar custo total, tempo de solver, variáveis, restrições, não zeros, tamanho e censuras.
- `>=1%` é indicador **descritivo** oriundo da AS05, não novo gate confirmatório.
- Ganho material A4 exige replicação prospectiva e verificação da aplicabilidade antes de qualquer promoção à AS06.
- Se censuras permanecerem, não transformar ausência de ótimo em resultado `0` ou `STOP`.
- Manter COMP+K como baseline MIP até evidência em contrário.

## Integridade/proveniência

O plano `results/benchmark/as05-factorial-plan-v1.json` fixa os hashes do plano original, manifesto, relatório original, plano e análise v2, a política e a seed. Checkpoints individuais com SHA e manifesto completo permitem retomada fiel e reconstituição de `arms.csv`/contrastes. Executar em `results/benchmark/as05-factorial-001/`, nunca em pastas históricas.

## Execução

Consultar `AS05-FACTORIAL-INTEGRACAO.md` no pacote de entrega. Sem autorização automática de divulgação, revisão matemática ou promoção científica.
