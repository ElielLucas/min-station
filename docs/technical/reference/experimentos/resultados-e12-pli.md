# Resultados E12 — CBI × núcleo × COMP em PUC/PUCN

**Data:** 2026-10-02
**Formulação:** baseline, variante U, fluxo contínuo no COMP, cortes estáticos C1+C2+C4 nos três braços
**Ambiente:** Gurobi 12.0.3, `PYTHONHASHSEED=0`, seed 42 na fase A, seeds 43 e 44 na fase R, 4 threads, TL 600 s, 2 fatias
**Plano:** passo 4 de `docs/technical/plans/execucao/plano-pos-e13.md` (§4.7)
**Dados:** `results/benchmark/e12_fatia{1,2}.csv`
**Tabelas e veredito:** saída de `experiments/benchmark/tabela_e12.py`. `LB*` = ⌈LB − 10⁻⁶⌉. Nenhum número foi copiado à mão.

Instâncias de avaliação e desenvolvimento: PUC/PUCN, classe `principal`, S∩T vazio. Os dois controles são MAPF da mesma classe e não entram no veredito.

## 1. Pergunta

Onde o núcleo inteiro já tinha sido medido contra o COMP (E9), o CBI com o mestre corrigido — iterando cortes 𝒵 — dá LB final maior ou prova o ótimo mais rápido que o COMP, no mesmo orçamento? Se houver ganho, ele vem da iteração ou só do núcleo?

Braços, sem MIP start: `COMP` (protocolo), `NUCLEO` (IP em y só com os cortes estáticos), `CBI` (`solve_cbi` sem `ub_start`). O critério de vitória, derrota, grafo com variantes e o veredito de A2 estão no §4.7 do plano. `hc11p` e `w23c23` não podem contar como vitória contra o núcleo: o script reescreve esse voto para empate.

## 2. Tabelas

Saída de `tabela_e12.py`.

### Avaliação, seed 42

| Instância | seed | COMP LB* | UB | st | t | NUCLEO LB* | UB | st | t | CBI LB* | UB | st | t | iter | n_z | vs COMP | vs NUCLEO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `puc-cc9-2p-seed-r1` | 42 | 30 | 31 | TL | 600,0 | 27 | 27 | ótimo | 0,0 | 27 | — | TL | 600,1 | 860 | 860 | perde | empate |
| `puc-cc11-2u-seed-r1` | 42 | 92 | 101 | TL | 600,0 | 92 | 92 | ótimo | 0,0 | 92 | — | TL | 600,6 | 467 | 467 | empate | empate |
| `puc-cc12-2u-seed-r1` | 42 | 165 | 199 | TL | 600,0 | 164 | 164 | ótimo | 0,1 | 164 | — | TL | 600,1 | 317 | 317 | perde | empate |
| `puc-hc9u-regiao-f4` | 42 | 36 | 39 | TL | 600,0 | 36 | 36 | ótimo | 2,0 | 36 | — | TL | 600,1 | 137 | 137 | empate | empate |
| `puc-hc9u-seed-r1` | 42 | 32 | 41 | TL | 600,1 | 32 | 32 | ótimo | 2,0 | 32 | — | TL | 600,1 | 124 | 124 | empate | empate |
| `puc-hc11p-seed-r1` | 42 | 95 | 159 | TL | 600,1 | 102 | 134 | TL | 600,1 | 101 | — | TL | 603,0 | 2 | 2 | vence | perde |
| `puc-w23c23-seed-r1` | 42 | 141 | 157 | TL | 600,0 | 139 | 139 | ótimo | 59,0 | 139 | — | TL | 600,3 | 12 | 12 | perde | empate |
| `pucn-cc7-3n-regiao-f2` | 42 | 9 | 12 | TL | 600,0 | 10 | 10 | ótimo | 0,3 | 10 | 26 | TL | 600,4 | 337 | 336 | vence | empate |
| `pucn-cc7-3n-seed-r1` | 42 | 68 | 83 | TL | 600,0 | 66 | 66 | ótimo | 0,0 | 66 | — | TL | 600,7 | 552 | 552 | perde | empate |

### Re-seeds 43 e 44

| Instância | seed | COMP LB* | UB | st | t | NUCLEO LB* | UB | st | t | CBI LB* | UB | st | t | iter | n_z | vs COMP | vs NUCLEO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `puc-cc11-2u-seed-r1` | 43 | 92 | 101 | TL | 600,0 | 92 | 92 | ótimo | 0,0 | 92 | — | TL | 600,3 | 459 | 459 | empate | empate |
| `puc-cc11-2u-seed-r1` | 44 | 92 | 103 | TL | 600,0 | 92 | 92 | ótimo | 0,0 | 92 | — | TL | 600,3 | 513 | 513 | empate | empate |
| `puc-cc12-2u-seed-r1` | 43 | 165 | 202 | TL | 600,3 | 164 | 164 | ótimo | 0,0 | 164 | — | TL | 601,0 | 367 | 367 | perde | empate |
| `puc-cc12-2u-seed-r1` | 44 | 165 | 201 | TL | 600,0 | 164 | 164 | ótimo | 0,1 | 164 | — | TL | 599,9 | 313 | 313 | perde | empate |
| `puc-hc9u-regiao-f4` | 43 | 36 | 39 | TL | 600,0 | 36 | 36 | ótimo | 2,4 | 36 | — | TL | 600,1 | 114 | 114 | empate | empate |
| `puc-hc9u-regiao-f4` | 44 | 36 | 39 | TL | 600,0 | 36 | 36 | ótimo | 2,5 | 36 | — | TL | 600,1 | 135 | 135 | empate | empate |
| `puc-hc9u-seed-r1` | 43 | 32 | 41 | TL | 600,1 | 32 | 32 | ótimo | 2,2 | 32 | — | TL | 600,0 | 119 | 119 | empate | empate |
| `puc-hc9u-seed-r1` | 44 | 32 | 38 | TL | 600,0 | 32 | 32 | ótimo | 1,7 | 32 | — | TL | 600,1 | 139 | 139 | empate | empate |
| `pucn-cc7-3n-regiao-f2` | 43 | 9 | 14 | TL | 608,3 | 10 | 10 | ótimo | 0,4 | 10 | 26 | TL | 600,5 | 257 | 256 | vence | empate |
| `pucn-cc7-3n-regiao-f2` | 44 | 9 | 13 | TL | 600,0 | 10 | 10 | ótimo | 0,3 | 10 | 26 | TL | 600,4 | 356 | 355 | vence | empate |

### Agregado por instância (vitória ou derrota exige 2 de 3 seeds)

| Instância | contra COMP | contra NUCLEO |
|---|---|---|
| `puc-cc9-2p-seed-r1` | perde | empate |
| `puc-cc11-2u-seed-r1` | empate | empate |
| `puc-cc12-2u-seed-r1` | perde | empate |
| `puc-hc9u-regiao-f4` | empate | empate |
| `puc-hc9u-seed-r1` | empate | empate |
| `puc-hc11p-seed-r1` | vence | perde |
| `puc-w23c23-seed-r1` | perde | empate |
| `pucn-cc7-3n-regiao-f2` | vence | empate |
| `pucn-cc7-3n-seed-r1` | perde | empate |

### Controles MAPF, seed 42

| Instância | seed | COMP LB* | UB | st | t | NUCLEO LB* | UB | st | t | CBI LB* | UB | st | t | iter | n_z |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `mapf-random-32-32-10-m50-f8` | 42 | 53 | 72 | TL | 600,0 | 43 | 43 | ótimo | 0,0 | 43 | — | TL | 600,2 | 743 | 743 |
| `mapf-empty-32-32-m25-f4` | 42 | 14 | 18 | TL | 600,0 | 11 | 11 | ótimo | 0,0 | 11 | — | TL | 600,3 | 1334 | 1334 |

### Desenvolvimento, seed 42

Fora do veredito.

| Instância | seed | COMP LB* | UB | st | t | NUCLEO LB* | UB | st | t | CBI LB* | UB | st | t | iter | n_z |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `puc-bip42p-regiao-f2` | 42 | 33 | 44 | TL | 600,0 | 35 | 37 | TL | 600,0 | 35 | — | TL | 600,2 | 2 | 2 |
| `pucn-cc3-10n-seed-r1` | 42 | 17 | 26 | TL | 600,0 | 18 | 18 | ótimo | 0,0 | 18 | — | TL | 600,2 | 445 | 445 |
| `puc-hc10p-seed-r1` | 42 | 52 | 85 | TL | 600,0 | 56 | 64 | TL | 600,0 | 57 | — | TL | 600,5 | 2 | 2 |

### Commits por fase

- fase A: `1849e17-dirty`
- fase D: `1e4f433-dirty`
- fase R: `1849e17-dirty`

### Checagem

- instâncias no CSV: 14
- S∩T não vazio no manifesto: 0
- linhas: 72

O sufixo `-dirty` é a árvore de trabalho suja no momento da execução (arquivos alheios ao runner). As fases A e R registram o commit em que o runner foi congelado, `1849e17`. A fase D rodou antes desse commit. Nenhum parâmetro mudou depois da fase A. A lista "Margem (re-seed)" abaixo é o gatilho calculado na seed 42; essas cinco instâncias já rodaram nas seeds 43 e 44, e o agregado acima inclui os três votos.

## 3. Veredito

```
| Grafo | contra COMP | contra NUCLEO |
|---|---|---|
| `cc7-3n` | empate | empate |
| `hc9u` | empate | empate |
| `puc-cc11-2u-seed-r1` | empate | empate |
| `puc-cc12-2u-seed-r1` | perde | empate |
| `puc-cc9-2p-seed-r1` | perde | empate |
| `puc-hc11p-seed-r1` | vence | perde |
| `puc-w23c23-seed-r1` | perde | empate |

Vitórias contra COMP: 1 ['puc-hc11p-seed-r1']
Também vencem o NUCLEO: []
Veredito: A2 encerrada para Das
```

**A2 encerrada para Das.** Uma vitória contra o COMP, em um grafo, e nenhuma vitória contra o núcleo. O critério pede pelo menos três grafos independentes, incluindo o PUCN (`cc7-3n`), e uma vitória contra o núcleo entre elas.

## 4. Leitura

1. Onde o núcleo fecha, o CBI não sobe o LB* acima dele. Nas linhas de avaliação em que o núcleo está ótimo, o LB* do CBI é o do núcleo. Os cortes 𝒵 cortam incumbentes inviáveis e não movem o limite.
2. A única vitória contra o COMP é `hc11p` (LB* 101 contra 95). O núcleo, no mesmo TL, chega a 102. O CBI faz 2 iterações e 2 cortes 𝒵 e fica em 101, sem incumbente. A guarda das instâncias marcadas como não iteráveis só reescreve uma vitória contra o núcleo para empate. Aqui o voto foi derrota, e a guarda não alterou a linha. Essa vitória não entra no ramo "a iteração acrescenta".
3. `w23c23` estava marcada como mestre não iterável a partir do E9 (núcleo em TL com orçamento de 60 s). No E12 o núcleo prova ótimo 139 em 59,0 s. O CBI faz 12 iterações e 12 cortes 𝒵 e permanece em 139, dois abaixo do COMP (141). O voto contra o núcleo é empate, então a guarda também não reescreveu essa linha.
4. `pucn-cc7-3n-regiao` vence o COMP por 1 nas três seeds (LB* 10 contra 9) e empata com o núcleo, que já está ótimo em 10. É a única da avaliação em que o CBI devolve incumbente: UB 26, pior que o UB do COMP (12, 14 e 13). A outra variante do mesmo grafo, `cc7-3n-seed`, perde (66 contra 68). O grafo empata. O PUCN não conta como vitória.
5. Os controles MAPF repetem o esperado: o CBI fica no núcleo e abaixo do COMP (43 contra 53; 11 contra 14). Não há vitória de controle para investigar.
6. No desenvolvimento, fora do veredito, `hc10p` é a única linha do CSV em que o LB* do CBI passa o do núcleo (57 contra 56), com 2 cortes 𝒵. `bip42p-regiao` empata com o núcleo em 35, acima do COMP (33). `cc3-10n` fica no ótimo do núcleo (18) depois de 445 cortes 𝒵, sem incumbente. Essas três não entram na contagem.
