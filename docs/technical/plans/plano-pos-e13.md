# Plano: commit do E13 e próximos passos

## Contexto

O E13 fechou com **veredito de gap primal** (7/13 com Δ_UB ≥ 5% sob `MIPFocus=1`, TL 1800 s — no
limiar). Pelo §7 de `resultados-e9-e10-pli.md`, isso deixa o E11 sem o gatilho que o condicionava.

A decomposição do gap, calculada agora a partir dos CSVs do E13, mostra que o veredito binário
esconde algo importante. Mesmo com o melhor UB encontrado, **o gap residual continua entre 10% e 44%**
e é maior que a queda primal em 11 das 12 instâncias não resolvidas (exemplos: `warehouse-m50`
81/117, 30,8% residual contra 7,1% de queda; `random-64` 41/63, 34,9% contra 7,4%). Sem OPT não dá
para dizer se esse residual está no LB ou no UB. O E13 provou que o UB não estava saturado. **Não
provou que o LB está bom.** Portanto "gap primal" não quer dizer "o lado dual está resolvido", e a
agenda não deve tratar assim.

Três pendências concretas saíram da leitura do código:

- `run_dificuldade.py` pula instâncias já presentes em `dificuldade_v1_fatiaK.csv`. Regerar exige
  tirar os CSVs antigos do caminho.
- `build_manifest.py` lê a dificuldade de `results/benchmark/dificuldade_v1*.csv` e **não** lê
  `reavaliacao_c4dm.csv`. Um rebuild hoje reverteria as 3 correções do C4-DM (b-b09 4→2 etc.) para os
  valores errados. A regeneração resolve isso de forma estrutural.
- O manifesto já tem as colunas `lb_melhor`/`ub_melhor`/`fonte_melhor`, alimentadas pelo dicionário
  `MELHORES` em `src/converters/build_manifest.py:91`. É o lugar certo para os melhores limites do E13,
  sem mexer na semântica de `lb`/`ub`, que valem só para o protocolo.

## Passo 0 — Commit do E13 (imediato)

Arquivos: `experiments/cuts/harness.py` (parâmetro `params` em `measure_mip`),
`experiments/benchmark/run_e13.py`, `experiments/benchmark/tabela_e13.py`,
`results/benchmark/e13_{base,longo}_fatia{1,2}.csv`, `docs/technical/reference/resultados-e13-pli.md`,
`docs/technical/reference/resultados-e9-e10-pli.md`.

Mensagem: `feat(e13): primal × dual via MIPFocus=1 em MAPF/Vienna — veredito gap primal (7/13, limiar)`,
com corpo curto (critério, inversão em relação à fase base, divergência de 9/13 com o manifesto) e a
linha `Co-Authored-By` vigente.

## Passo 1 — Adendo ao relatório do E13: gap residual

- Acrescentar a `tabela_e13.py` uma função `residual(base, longo)` que imprime, por instância,
  LB_melhor = max(LB dos três braços), UB_melhor = min(UB dos três braços), a queda primal e o gap
  residual `(UB_melhor − LB_melhor)/UB_melhor`, com as contagens "residual > queda primal".
- Colar a saída como §3.1 de `resultados-e13-pli.md`, com a leitura do Contexto acima: o veredito
  prioriza, mas não atribui o residual. Commit separado.

## Passo 2 — Frente B: regerar o benchmark-v1 (~6 h de máquina, 2 fatias)

1. `git mv results/benchmark/dificuldade_v1_fatia{1,2}.csv results/benchmark/historico/dificuldade_v1_pre_c4fix_fatia{1,2}.csv`.
   Isso preserva o "antes" e tira os arquivos do glob de `build_manifest.py`.
2. Rodar `run_dificuldade.py --fatia k/2`, sem alterar o script. Condições do original: TL 600 s,
   seed 42, 4 threads.
3. Adicionar a `MELHORES` as 13 do E13 que melhoraram LB ou UB em relação ao novo protocolo, com
   fonte "E13, COMP C1+C2+C4, MIPFocus=1, TL 1800 s — resultados-e13-pli.md".
4. Reconstruir o manifesto com `build_manifest.py` **completo** (sem `--sem-atributos`: esse caminho
   só copia `CAMPOS_RES` do manifesto antigo e pode deixar os atributos vazios).
5. Script de comparação (no molde de `reavaliar_c4dm.py`), gravando
   `results/benchmark/regeneracao_c4fix.csv` com antes/depois de `lb`, `ub` e `dificuldade`, mais a
   lista de instâncias que entraram ou saíram de D/A.
6. `benchmark-v1.md`: nova seção com a mudança de partição D/A e a ressalva de que E9/E10/E10b/E13
   usaram a partição anterior (não são refeitos).

## Passo 3 — E14: certificar OPT nas D/A de gap pequeno (atribui o residual)

Instrumento sem heurística e sem instância nova: em quatro instâncias com UB_melhor − LB_melhor = 2
estações (`room-32-32-4-m10-f8` 16/18, `room-32-32-4-m25-f4-rho` 17/19, `vienna-I056-regiao-f4`
9/11, `vienna-I065-intercalado-f2` 17/19), rodar o COMP com `Cutoff = UB_melhor − 0,5` e ênfase no
bound, TL 4 h, 2 fatias. Confirmar na documentação do Gurobi 12.0.3 a semântica de `Cutoff`, o status
retornado quando nenhuma solução melhor existe e o valor de `MIPFocus` para bound. Não preencher de
memória.

Critério pré-registrado, por instância:
- provado que não existe solução < UB_melhor → **OPT = UB_melhor**, e o residual era todo LB (dual);
- achou solução < UB_melhor → o UB ainda não estava saturado nem em 1800 s (primal);
- TL sem nenhum dos dois → inconclusivo; registrar o LB final.

Regra para o E11: se ≥ 3 das 4 certificarem OPT = UB_melhor, o E11 volta à fila com essa
justificativa. Ressalva a registrar: são as instâncias de gap *menor*, e o resultado não se estende
automaticamente às de 30–44% de residual.

Mudança de código mínima: `run_e14.py` usando `measure_mip(..., params={'Cutoff': ..., 'MIPFocus': ...})`,
que já existe em `harness.py:213`. UB_melhor e LB_melhor são lidos dos CSVs do E13.

## Passo 4 — Frente D: E12, CBI × COMP em PUC/PUCN (veredito sobre A2 para Das)

**Pergunta.** Nas famílias em que o núcleo inteiro já superou o LB do COMP de 600 s (E9: 6 linhas
de PUC/PUCN), o CBI com mestre corrigido — iterando cortes 𝒵 sobre o núcleo — dá LB final maior ou
prova o ótimo mais rápido que o COMP, no mesmo orçamento? E o ganho, se houver, vem da **iteração**
ou só do **núcleo**? No E8, os LBs do CBI em hc10p/bip42p vieram de uma única iteração sem cortes,
ou seja, só do núcleo.

### 4.1 Pré-requisitos

1. **Correção do mestre.** Feita e ainda não commitada em `bc_yspace.solve_cbi`:
   - sem pool;
   - o mestre é resolvido até o ótimo;
   - só a incumbente vai ao oráculo;
   - o corte 𝒵 é acrescentado se ela for inviável;
   - fica uma reserva de 5 s por optimize.

   A reconstrução do mestre a cada iteração **não** muda nesta rodada.
2. **Verificação da correção**, antes de qualquer bateria:
   - `verify_e8_cc12_opt.py` mantém OPT(cc12-2p) = 6;
   - `verify_c4_dm.py` e `verify_e8_oracle.py` saem com código 0;
   - em hc10p e bip42p, o CBI faz **mais de uma iteração e gera cortes 𝒵** (o sintoma a derrubar);
   - commit da correção sozinha, antes do `run_e12.py`, para que o hash registrado no CSV identifique
     o código avaliado.
3. **O E14 terminou**, para não disputar CPU.
4. **Só instâncias com S∩T = ∅.** O oráculo não representa a permanência em S∩T, gera falso negativo
   e, com isso, cortes 𝒵 inválidos (parecer consolidado §2.1). Todas as PUC/PUCN abaixo têm
   `rho_S_inter_T = 0`. Os controles MAPF também são escolhidos sem `-rho`.

### 4.2 Braços

Todos têm os mesmos cortes estáticos (C1+C2+C4) e **nenhum MIP start**. Sem start, o confundimento
de cc12-2p no E8 desaparece: lá o COMP recebeu um start de 4096 estações e o primal de 291 s ficou
fora do tempo.

| Braço | O que roda | Para que serve |
|---|---|---|
| `COMP` | `measure_mip`, base U + cortes, fluxo contínuo | referência do protocolo |
| `NUCLEO` | IP em y só com os cortes estáticos, sem iterar (equivale à 1ª iteração do CBI, até o TL) | isola o ganho do núcleo |
| `CBI` | `solve_cbi` corrigido, sem `ub_start` | mede o ganho da iteração com 𝒵 |

### 4.3 Orçamento e condições (iguais para os três braços)

- **TL = 600 s de relógio por execução**, contado do início do método até o retorno. Inclui as
  iterações, as chamadas ao oráculo e a reconstrução do mestre no CBI. A carga da instância e a
  geração dos cortes estáticos são comuns aos três braços e ficam fora, em coluna própria
  (`t_cortes_s`).

  600 s é o TL do protocolo de dificuldade e do E9. Assim o braço `COMP` também serve de verificação
  contra o manifesto regerado (divergência esperada de ±1 por ordem de construção e parada por tempo;
  parecer §3).
- Gurobi 12.0.3, **4 threads, 2 fatias** (nunca 3) e seed 42.
- **`PYTHONHASHSEED=0`** em todas as execuções. Não torna o modelo determinístico (o que exige ordenar
  a construção, parecer §9, Etapa 2), mas impede que a ordem dos cortes varie entre os três braços de
  uma mesma instância.

### 4.4 Instâncias

#### 4.4.1 Critérios de inclusão (fixados antes do E12, só com dados anteriores)

O E12 testa a **iteração** do CBI, não a vantagem do núcleo sobre o COMP, que o E9 já mediu. Por
isso a propriedade que importa numa instância é se o mestre **termina rápido o bastante para
iterar**. Quando o mestre não termina, o CBI no TL de 600 s faz uma única iteração e coincide com o
braço `NUCLEO`.

Os critérios usam só o E9 (núcleo, TL 60 s) e o protocolo regerado (COMP, 600 s). Nenhum depende de
quem vence entre CBI e COMP no E12.

1. **Família e partição:** PUC/PUCN, classe D ou A no protocolo regerado, `particao = avaliacao` e
   S∩T = ∅.
2. **Exclusão por tamanho: m ≥ 1000 robôs.** São as duas maiores instâncias do benchmark, e nas duas o
   COMP de 600 s está parado por escala, não por estrutura:
   - `hc12p-seed` (n = 4096, m = 1024): sem incumbente, com LB = ⌈raiz⌉ = 171 (o B&B não sai da
     raiz). O núcleo também não termina (217 s, incumbente 512).
   - `w3c571-seed` (n = 3997, m = 1142): UB 1131 ≈ m, ou seja, o primal não sai do trivial.
3. **Exclusão por vazamento:** uma variante cujo grafo de origem é usado no desenvolvimento do próprio
   E12. `bip42p-seed` usa o mesmo grafo de `bip42p-regiao`, que serviu para verificar a correção do
   CBI. Não roda.
4. **Classe F não entra.** O ganho de "tempo até o ótimo" em instâncias que o COMP resolve em
   segundos é dominado por ruído.

Duas exclusões **não** foram feitas, de propósito:
- **Instâncias em que o núcleo hoje perde para o COMP não saem.** São justamente onde a iteração
  precisa mostrar que sobe o LB.
- **Instâncias de desenvolvimento não são promovidas a avaliação**, mesmo as que mostram o núcleo à
  frente (`bip42p-regiao` +2, `hc10p` +2, `pucn-cc3-10n` +1). Promover depois de ver o E9 enviesaria o
  veredito a favor de A2.

#### 4.4.2 Conjunto resultante

Dados do E9 (núcleo, TL 60 s) e do protocolo regerado (COMP, 600 s), usados só para caracterizar as
instâncias. O E12 roda o próprio COMP.

| Instância | Grafo | Classe | n | m | \|A_r\| | Núcleo E9: LB (status, t) | COMP 600 s LB/UB | Mestre iterável? |
|---|---|---|---|---|---|---|---|---|
| `puc-cc9-2p-seed-r1` | cc9-2p | D | 512 | 32 | 4608 | 27 (ótimo, 0,3 s) | 30/31 | sim |
| `puc-cc11-2u-seed-r1` | cc11-2u | D | 2048 | 122 | 22526 | 92 (ótimo, 5,6 s) | 92/102 | sim |
| `puc-cc12-2u-seed-r1` | cc12-2u | A | 4096 | 236 | 49148 | 164 (ótimo, 25 s) | 165/204 | sim |
| `puc-hc9u-regiao-f4` | hc9u | D | 512 | 128 | 4608 | 36 (ótimo, 2,5 s) | 36/39 | sim |
| `puc-hc9u-seed-r1` | hc9u | A | 512 | 128 | 4608 | 32 (ótimo, 2,8 s) | 32/41 | sim |
| `puc-hc11p-seed-r1` | hc11p | A | 2048 | 512 | 22528 | 97 (TL, 84 s) | 96/160 | **não** |
| `puc-w23c23-seed-r1` | w23c23 | A | 1081 | 276 | 6348 | 139 (TL, 63 s) | 140/156 | **não** |
| `pucn-cc7-3n-regiao-f2` | cc7-3n | A | 2187 | 111 | 214326 | 10 (ótimo, 8,4 s) | 9/14 | sim |
| `pucn-cc7-3n-seed-r1` | cc7-3n | A | 2187 | 111 | 30616 | 66 (ótimo, 7,0 s) | 69/83 | sim |

**Contagem por grafo:** 9 instâncias, **7 grafos independentes** (6 PUC e 1 PUCN). Variantes do mesmo
grafo contam como uma evidência: {`hc9u-regiao-f4`, `hc9u-seed`} e {`cc7-3n-regiao`, `cc7-3n-seed`}.
`w23c23-seed` conta: a outra variante do grafo (`w23c23-intercalado-f2-rho`) é de desenvolvimento,
mas não é usada no E12.

**Instâncias com mestre não iterável** (`hc11p`, `w23c23`):
- por construção, nelas o CBI ≈ NUCLEO;
- servem ao ramo "o ganho é do núcleo", não ao ramo "a iteração acrescenta";
- **por isso não podem satisfazer a condição "vence também o NUCLEO"**, e isso fica registrado assim,
  não como derrota do CBI.

**Desenvolvimento** (smoke test e verificação de implementação; **não entram no veredito**):
- `puc-bip42p-regiao-f2` e `puc-hc10p-seed-r1`, já usadas na verificação da correção;
- `pucn-cc3-10n-seed-r1`.

**Controles MAPF** (não entram no veredito):
- `mapf-random-32-32-10-m50-f8` (núcleo 43 contra COMP 53) e `mapf-empty-32-32-m25-f4` (11 contra 14);
- os dois são de avaliação, com S∩T = ∅;
- o núcleo fecha em < 1 s e fica abaixo do COMP, então a expectativa é que o CBI perca.

**Folga do veredito, para constar.** Contra o COMP regerado, o núcleo do E9 está à frente em só dois
grafos de avaliação, ambos por 1 estação:
- `hc11p`, com mestre não iterável;
- `cc7-3n-regiao`, em que a variante `seed` do mesmo grafo aponta o contrário.

Chegar a 3 grafos depende da iteração subir o LB onde o núcleo hoje empata ou perde. É exatamente a
hipótese de A2, e o critério não é afrouxado por isso.

### 4.5 Fases e custo

| Fase | Conteúdo | Pior caso (relógio, 2 fatias) |
|---|---|---|
| D — desenvolvimento | 3 instâncias × 3 braços × 1 seed | ≈ 45 min |
| A — avaliação | 9 instâncias + 2 controles = 11 × 3 braços × seed 42 | ≈ 2,75 h |
| R — re-seeds | seeds 43 e 44, nas instâncias de avaliação cujo veredito fique na margem (abaixo) | ≤ 2,5 h |

Entre a fase D e a fase A, o código é **congelado** (commit registrado no CSV). Depois de ver a fase
A, nenhum parâmetro muda.

**Margem que dispara re-seed.** A diferença de LB entre CBI e COMP é ≤ 1 estação, ou a razão dos
tempos até o ótimo fica entre 1/1,5 e 1,5.

### 4.6 Medidas (CSV `results/benchmark/e12_fatia{1,2}.csv`)

Por execução:
- instância, braço, seed e fase;
- `n`, `m`, \|A_r\|, número de cortes estáticos e `t_cortes_s`;
- LB final (`ObjBound`; no CBI, o maior entre as iterações), UB, gap e status;
- `t_metodo_s` e tempo até o ótimo, quando houver;
- só no CBI: iterações, chamadas ao oráculo, cortes 𝒵, tempo no mestre e tempo no oráculo;
- NodeCount, quando disponível. É preciso acrescentar `NodeCount` ao retorno de `measure_mip`, uma
  mudança aditiva;
- `PYTHONHASHSEED`, threads, TL e commit.

### 4.7 Critério pré-registrado

Herdado de `plano-pos-e8-adiado.md` e tornado operacional.

**Definições:**
- `LB*` = ⌈LB − 10⁻⁶⌉, porque o objetivo é inteiro.
- O CBI **vence** numa instância se:
  - `LB*_CBI ≥ LB*_COMP + 1`, ou
  - os dois provam o ótimo, `t_COMP ≥ 10 s` e `t_CBI ≤ t_COMP / 1,5`. O piso de 10 s evita que ganhos
    de segundos, dominados por ruído, contem como vitória.
- O CBI **perde** numa instância na situação simétrica: `LB*_CBI ≤ LB*_COMP − 1`, ou os dois provam o
  ótimo e `t_CBI ≥ 1,5 · t_COMP`, com `t_CBI ≥ 10 s`. Qualquer outro resultado é empate.
- Com re-seeds, vitória ou derrota precisam ocorrer em pelo menos 2 das 3 seeds; caso contrário, é
  empate.
- **Um grafo com várias variantes** (hc9u, cc7-3n) conta como vitória somente se o CBI vencer em pelo
  menos uma variante e não perder em nenhuma.
- A mesma regra vale para "vence o `NUCLEO`", com `NUCLEO` no lugar de `COMP`.

**Veredito:**

| Resultado | Leitura |
|---|---|
| CBI vence em **≥ 3 grafos independentes** da avaliação, **incluindo PUCN** (cc7-3n), e vence também o `NUCLEO` em pelo menos uma dessas | **A2 segue para Das:** a iteração com 𝒵 acrescenta algo ao núcleo |
| CBI vence o COMP pelo mesmo critério, mas empata com o `NUCLEO` em todas as vitórias | **o ganho é do núcleo, não da iteração.** A2 como CBI é encerrada para Das; o núcleo segue como mecanismo de LB (parecer consolidado §9, Etapa 3) |
| Qualquer outro desfecho | **A2 encerrada para Das** |

Os controles MAPF não entram no veredito. Se o CBI vencer num controle, o resultado é registrado como
surpresa e investigado antes do relatório.

### 4.8 Entregáveis

- `experiments/benchmark/run_e12.py` (`--fase D|A|R`, `--fatia k/2`), retomável como os anteriores;
- `experiments/benchmark/tabela_e12.py`, que gera as tabelas e o veredito a partir dos CSVs;
- `docs/technical/reference/resultados-e12-pli.md`.

## Fora desta rodada

- **E11 (C4 mochila δ≥2):** depende do E14. A ordem obrigatória (derivação escrita, depois validador
  próprio para RHS δ≥2, depois medição) continua valendo.
- **Frente primal dedicada:** não abrir. O E10b mostrou que um start melhor não move o LB, e o foco do
  projeto são os limites. Registrar os melhores UBs em `ub_melhor` (passo 2.3) basta.
- **Frente E (instâncias sintéticas):** segue planejada. É o único instrumento para atribuir o residual
  nas instâncias de gap grande, e fica para quando for pedida.

## Ordem e CPU

0 → 1 (sem CPU) → 2 (8 threads, ~6 h; a correção do passo 4 é feita em paralelo) → 3 (~8 h) → 4
(fases D, A e R: ≤ ~6 h de relógio no pior caso). Nunca 3 fatias. O E14 não roda junto com a
Frente B, e o E12 não roda junto com o E14.

## Verificação

- Passo 0: `git status` limpo depois do commit, sem arquivos fora da lista.
- Passo 1: a tabela residual vem de `tabela_e13.py`, e nenhum número é digitado à mão.
- Passo 2: `verify_regeneracao.py` sai com código 0. O diff do manifesto toca **só** `dificuldade`,
  `lb`, `ub`, `fonte_lb_ub`, `lb_melhor`, `ub_melhor` e `fonte_melhor`. Qualquer outra coluna
  alterada aborta a aplicação. As 3 correções do C4-DM (b-b09, den312d-m50, room-m25) aparecem com os
  valores corrigidos, agora vindos do CSV regerado.
- Passo 3: nenhuma instância é declarada "OPT certificado" sem o status que a documentação do Gurobi
  define para "nenhuma solução melhor que o Cutoff".
- Passo 4, antes da bateria:
  - `verify_e8_cc12_opt.py`, `verify_c4_dm.py` e `verify_e8_oracle.py` saem com código 0;
  - o CBI faz mais de uma iteração e gera cortes 𝒵 em hc10p e bip42p.
- Passo 4, depois da bateria:
  - o veredito vem de `tabela_e12.py`, nunca de leitura manual;
  - cada linha do CSV tem o commit congelado da fase A;
  - nenhuma instância com S∩T ≠ ∅ aparece no CSV.
