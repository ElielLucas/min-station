# AS-00 — Pré-registro v1 (sem solves)

**Estado:** CONGELADO para AS-00; execuções futuras dependem dos gates AS-01..AS-06.  
**Protocolo SHA-256:** `ee328a128b05a37907921ee1b269fb6963e28b0d68097034be519340f87953c2`  
**Manifesto SHA-256:** `218c490bd3ba3e34740bc23f13b07ba864f0d624755aca9b992a8f23f6afad08`

## Universo

- D/A: **31**, desenvolvimento **14**, avaliação **17**.
- Piloto: `mapf-room-32-32-4-m10-f8`, `puc-bip42p-regiao-f2`, `puc-cc9-2p-seed-r1`, `puc-w3c571-seed-r1`, `pucn-cc3-10n-seed-r1`, `vienna-I056-regiao-f4`.
- Se a construção da F-CC exceder o cap ou a memória, o caso permanece no denominador.
- São preservados G, S, T, r, A_r, hash do arquivo e vínculos com a fonte.
- Variantes do mesmo mapa e cenário MAPF são relacionadas, ainda que mudem m/r.

## Hipóteses pré-registradas

- A2+K melhora o limite LP sobre U+K em famílias independentes.
- A2+K melhora LB/gap MIP no mesmo orçamento total sem custo excessivo.
- Maior força LP não garante menor tempo MIP.

## Critérios de promoção

- Ganho reproduzido em pelo menos **2 grafos brutos independentes**.
- Comparações pareadas entre as mesmas instâncias, com orçamento total incluindo preparação.
- Controles: U sem K, U+K, núcleo IP quando aplicável; F-CC apenas controle pequeno.
- A4, cortes, B e C são condicionais e não entram automaticamente no estudo.
- Avaliação final: **10 casos** estratificados e congelados nesta versão, antes dos solves.
- Casos de avaliação relacionados ao desenvolvimento: **1**, nunca rotular como validação independente.
- Seleção principal de avaliação: `mapf-den312d-m50-f2-rho`, `mapf-empty-32-32-m25-f4`, `mapf-random-32-32-10-m50-f8`, `mapf-random-64-64-20-m100-f4`, `mapf-warehouse-10-20-10-2-1-m25-f4`, `puc-hc9u-regiao-f4`, `puc-hc10p-seed-r1`, `puc-hc11p-seed-r1`, `puc-hc12p-seed-r1`, `pucn-cc7-3n-regiao-f2`.
- Restante da avaliação: **7** casos preservados no universo e cobertura.
- Falhas/cap/memória/budget/errors ficam registrados, não substituídos por 0.
- LP do solver não é certificado racional; incumbentes devem passar no validador físico.

## Orçamento pré-registrado (por braço)

- LP diagnóstico: 90 s.
- MIP piloto: [300, 600] s.
- Campanha final: 3600 s.
- Threads: 4; seeds piloto [42]; repetições [42, 43, 44].
- Limite de memória: 16 GiB.
- A execução de qualquer braço exige autorização por gates futuros.
- Alterações: gerar nova versão/diretório e registrar desvio; nunca sobrescrever este snapshot.

## Limites de interpretação

Os estratos D/A e sua dificuldade são históricos, não medidas novas. O protocolo
não declara sucesso de A, não reabre `N2 FAIL` e não altera N1, N2 ou FC.
