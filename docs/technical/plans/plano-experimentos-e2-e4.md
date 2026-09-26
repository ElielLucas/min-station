# Plano: próximos experimentos após E0/E1'/E1 (E2, E3, E4)

## Contexto

E0, E1' e E1 terminaram. Este plano consolida o que foi aprendido (com as referências
históricas levantadas no repositório), corrige erros do relatório
`docs/technical/reference/resultados-e0-e1-pli.md` e propõe a próxima rodada. O foco é
evidência rápida para decidir **qual linha de PLI testar em seguida**: consolidar o compacto
com cortes (A1), branch-and-cut só em y (A2) ou núcleo de cobertura e simetria (B2).

Restrições mantidas: não usar `lin23` nem `lin37`; não alterar a formulação base nem os
scripts históricos; não usar Benders clássico nem Lagrangeana nova; não commitar sem pedido.

**Passo 0, ao aprovar:** salvar este plano em `docs/technical/plans/plano-experimentos-e2-e4.md`
e o plano anterior em `docs/technical/plans/plano-experimentos-e0-e1.md`; corrigir o relatório
(§1.4). Nenhuma execução nesse passo.

---

## 1. O que foi aprendido

### 1.1 E1' (sintéticos): implementações conferem com a teoria
- F1: `2k+1` → `2m+2k−1` com C1 → `2mk+1` = OPT com C1+C2.
- F2: `1/3` → `k` = OPT só com C4-DM. Confirma D2 (acoplamento de Hall).
- Tri: `1` → `1,5` com C1; o resíduo até 2 exige posto 2.
- §5.9 (L=7): `7/3` → `11/3` com C4-DM; OPT = 7; C3 gera 0 cortes. O resíduo é **Hall
  multi-salto (C5)**: cada `{w_i}` sozinho é separador, logo `y_{w_i} ≥ 1` e LP_cov = 7. Serve
  de gabarito para a separação de C5.

### 1.2 E0: inconclusivo nas instâncias não triviais
- O LP é igual em BASE-I e BASE-C por construção (a relaxação torna f contínuo nos dois), então
  isso não é evidência para a Prop. 3.2.
- Só 2 das 5 provaram ótimo, e as duas são triviais na R do arquivo: Chicago st5 R32 (0) e
  Barcelona st15 R24 (1). cc10-2p, hc9u e lin23 bateram o limite de 120 s.
- hc9u em 120 s: BASE-C chegou a bound 30 / UB 44, contra 28 / 45 da BASE-I. Sinal fraco,
  com uma única seed.

### 1.3 E1 (raiz) contra as referências históricas
| Instância | Base | +C1 | +C2 | +C4 | +C3 (só LP) | Raiz padrão | Referência histórica | Gap fechado |
|---|---|---|---|---|---|---|---|---|
| hc9u R1 | 1,0 | 28,44 | = | = | = | 29 | [31, 40] | 93% |
| hc10p R150 | 1,0 | 51,2 | = | = | = | 52 | [52, 80] | **100%** (raiz = melhor LB conhecido) |
| Philadelphia st25 R3 | 2,32 | 28,04 | 33,60 | = | 35,34 | 35 | [42, 46] | 82% |
| cc10-2p R500 | 0,149 | 2,57 | = | 2,62 | = | 3 | UB 3 | **100%**: OPT=3 provado (raiz 3 + UB 3) |
| cc12-2p R500 | 0,106 | 4,74 | — | — | — | inválida (TL) | [1, 7] | **LB 1 → 5** |

Leituras:
- **A1 confirmada na raiz nos três regimes** (critério: fechar ≥ 20% em ≥ 2 regimes). C1 domina
  em R-b e R-c. C2 contribui em R-a. C4-DM fica perto de 0 nas instâncias reais. C3 dá +1,74
  no LP de Philadelphia, mas esse ganho não chegou à raiz: os cortes não foram adicionados ao
  MIP, o que é falha da medição, não da técnica. O C3 implementado cobre só o lado das origens.
- Sobre as linhas de cobertura, o Gurobi não acrescenta nada em hc9u e hc10p (raiz padrão =
  ⌈LP⌉) e só +1 em Philadelphia.
- Em cc12-2p (|A_r| = 2,8 M), o compacto não fecha a raiz em 120 s.
- Chicago st5 (R32) e Barcelona st15 (R24) são triviais na R do arquivo. As referências
  históricas usam outras R, mas o harness só lê a R do arquivo.
- **Alerta histórico:** os cortes "camadas" levaram a raiz de hc9u a 24,03, e o resultado final
  em 3600 s ficou igual ao baseline (31/42). Por outro lado, só 30 cortes "diversidade" baixaram
  Barcelona st25 R5 de 270–310 s para 190 s.

### 1.4 Erros a corrigir no relatório
1. "OPT≈44" em hc9u não tem base: 44 e 45 são incumbentes de 120 s. A referência é [31, 40]; a
   variante VI dá UB 38, e esse valor também vale aqui, porque uma solução VI é viável na
   variante all-vertices (inferência).
2. E0 diz "3/5 provados": o certo é 2/5, ambos triviais. cc10-2p parou por limite de tempo, com
   bound 1.
3. Tirar a frase "LP idêntico confirma Prop. 3.2", que não prova nada.
4. Incluir cc12-2p, F1 só com C1 (7 e 9, que batem com `2m+2k−1`), as referências históricas e
   a coluna de gap fechado.
5. No §5.9, registrar que o resíduo de 11/3 até 7 vem de Hall multi-salto.

---

## 2. Diagnóstico do resíduo (hipóteses)

- **R-b, hc9u: núcleo de código de cobertura.** Os 256 terminais são exatamente os vértices
  pares, e cada vértice ímpar tem 9 vizinhos, todos pares. As 256 linhas C1 pedem que todo par
  tenha um ímpar escolhido como vizinho. Tirando a última coordenada (os pares de Q9 viram Q8),
  isso é **exatamente** cobrir Q8 com bolas de raio 1: é o código de cobertura K(8,1).
  - Valor na literatura, **ainda a conferir**: K(8,1) = 32 (Cohen, Honkala, Litsyn e Lobstein,
    *Covering Codes*, 1997; tabelas de Östergård).
  - Se o valor se confirmar, o IP só com as linhas C1 já dá **OPT(hc9u) ≥ 32**, acima do LB
    histórico de 31.
  - Pela mesma estrutura, se ela se verificar: hc10p ≥ K(9,1) (literatura: 62, contra LB 52).
    Já o LP das linhas C1 daria hc11p ≥ ⌈1024/11⌉ = 94 (contra LB 88) e hc12p ≥ ⌈2048/12⌉ = 171
    (contra LB 149).
- **Previsão [Esboço]: C3 e C5 não sobem hc9u.** Com `y = 1/9` uniforme nos ímpares, toda a
  família 𝒵 parece satisfeita, porque separar exige remover os 9 vizinhos de algum terminal.
  Se for isso, o resíduo de hc9u é integralidade e simetria do núcleo de cobertura (B2), e não
  falta de cortes de posto 1.
- **R-a, Philadelphia: 35,3 contra LB 42.** C3 ainda sobe o LP, e o lado dos destinos nunca foi
  separado. O resto pode ser C5, porque há Hall multi-salto, como no §5.9.
- **Pergunta estrutural:** o fluxo contribui para o bound? Se o LP só em y com separação
  alcança o compacto, as variáveis de fluxo não pesam no bound e A2 fica natural,
  principalmente em R-c.

---

## 3. Experimentos (ordem de execução)

### E2: laço de planos de corte só em y, contra o compacto (LP; ~20–30 min)
- **Objetivo:** medir quanto o fluxo agrega ao bound e se C3 nos dois lados e C5 fecham o
  resíduo em R-a.
- **Modelo:** `min Σ y`, com `y ∈ [0,1]^V` e sem f. Estágios cumulativos, registrando o LP em
  cada um:
  1. C1 + C2 + C4-DM a priori;
  2. + C3 iterativo, **origens e destinos**;
  3. + cortes clássicos fracionários `Σ_{Z} κ_v y_v ≥ δ(X)`, separados por max-flow em N(y*),
     com a versão arredondada `y(Z) ≥ 1`. Isso garante bound ≥ z_LP (`direcoes-pli` §5.9);
  4. + C5 heurístico (`direcoes-pli` §5.5):
     - limiar `C_θ` com θ ∈ {0,5; 0,3; 0,1; 0⁺};
     - min-cut paramétrico com λ ∈ {1, 2, 4, …, m};
     - aceitar `Z` se `y*(Z) < 1`;
     - minimalizar `Z` com o teste correto (`V∖(Z∖{v})` inviável), apenas quando `|Z| ≤ 50`.
- **Comparação:** LP compacto com os mesmos cortes estáticos. A raiz do solver no compacto com
  os cortes de C3/C5 encontrados resolve a falha de medição do E1.
- **Gabaritos, antes das instâncias reais:**
  - §5.9: estágio 1 = 2, estágio 3 ≥ 7/3, estágio 4 = 7;
  - F1 = OPT, F2 = k, Tri = 1,5.
- **Instâncias:** hc9u, hc10p, Philadelphia st25 R3, Barcelona st25 R5 (16*), Chicago st15 R7
  (17*), Barcelona st50 R6 [12, 14] e cc10-2p. cc12-2p só se couber no limite de tempo: o
  max-flow é em Python puro, porque não há scipy nem networkx no ambiente.
- **Custo controlado:** no máximo 30 rodadas ou 10 min por instância. Registrar se o laço
  convergiu.
- **H2:** no estágio 3, o LP fica ≥ LP compacto − 0,5% em todas as instâncias.
- **H3:** o estágio 4 sobe Philadelphia acima de 35,34 e fecha o §5.9. Em hc9u fica em 256/9
  (previsão do §2).
- **Decisão:**
  - H2 verdadeira: o fluxo não agrega bound e A2 (BC-y) é viável quanto ao bound. H2 falsa por
    mais de 5%, ou sem convergência: manter o compacto com cortes (BC-comp).
  - H3 verdadeira em R-a: C5 é a família do resíduo. Separá-la na árvore exige callbacks, o que
    reforça A2.

### E3: núcleo de cobertura inteiro (IP só em y; ~30 min)
- **Objetivo:** medir o limite do núcleo de cobertura (é o mestre do BC-y antes dos cortes lazy)
  e testar a ligação com códigos de cobertura em R-b.
- **Modelo:** `min Σ y` com `y ∈ {0,1}^V`, as linhas a priori e os cortes coletados no E2. Sem
  fluxo. Limite de 600 s, 4 threads.
- **Verificação estrutural antes de resolver:**
  - número e tamanho das linhas C1;
  - em quantas linhas aparece cada não terminal;
  - se os terminais formam um conjunto independente.

  Isso confirma ou refuta a analogia com K(n,1) em hc10p, hc11p e hc12p.
- **Instâncias:**
  - R-b: hc9u, hc10p, hc11p, hc12p, bip42p. Leves no espaço de y: só precisam das vizinhanças
    dos terminais, não do compacto;
  - R-a: Philadelphia st25 R3, Barcelona st50 R6;
  - R-c: cc10-2p, cc12-2p.
- **Hipóteses:**
  - hc9u: IP ≥ 32 (> LB 31);
  - hc10p: IP > 52;
  - hc11p e hc12p: LP ≥ 94 e ≥ 171, acima dos LBs históricos.

  São hipóteses; o valor K(n,1) da literatura só serve para conferência.
- **Decisão:**
  - IP ≥ LB de referência em R-b: registrar os novos limites. A dificuldade de R-b fica no núcleo
    de cobertura. Se o Gurobi não conseguir provar nem o IP de hc9u, com 256 variáveis úteis, a
    simetria é o gargalo, e B2 (quebra de simetria/orbital, estrutura do hipercubo) vem antes de
    A2.
  - IP muito abaixo da referência em R-a: a estrutura de fluxo/Hall multi-salto importa ali, e
    A2 precisa de C5 lazy.

### E4: árvore curta, para ver se o ganho da raiz sobrevive (≤ 100 min, em background)
- **Objetivo:** ver se compacto + cortes (C1+C2, mais C3/C5 estáticos se E2 render) melhora o
  LB final, o gap e o tempo até o ótimo, dado o alerta de "camadas".
- **Configurações:**
  - BASE-I, que é o controle no mesmo ambiente;
  - BASE-C, que fecha B3/E0;
  - BASE-C + o melhor conjunto estático.

  Limite de 300 s, 4 threads, seed 42, execução sequencial.
- **Sonda B2 opcional:** hc9u com `Symmetry=2` na melhor configuração. É parâmetro do solver,
  não propriedade do modelo.
- **Instâncias:**

  | Instância | Referência | Tempo histórico do baseline |
  |---|---|---|
  | Chicago st15 R7 | 17* | 19–91 s |
  | Barcelona st15 R5 | 15* | 76 s |
  | Barcelona st25 R5 | 16* | 270–310 s |
  | Philadelphia st5 R2 | 41* | 1777 s |
  | Philadelphia st25 R3 | [42, 46] | aberta |
  | hc9u | [31, 40] | aberta |
- **H4:**
  - com cortes, o ótimo sai com pelo menos 2× menos tempo ou nós nas resolvidas;
  - Philadelphia st5 R2 resolve em 300 s;
  - hc9u chega a LB ≥ 31 em 300 s.
- **Decisão:**
  - H4 verdadeira em R-a: a contribuição central é A1 no compacto; seguir para B4/B5.
  - hc9u estagna com UB longe: gargalo de simetria/núcleo, então B2 (junto com E3).
  - Tempo dominado pelo LP dos nós, ou raiz que não fecha (R-c): A2 e B7 (A_r preguiçoso).
  - LB forte com UB longe (hc10p: 52–62 contra 80): heurísticas primais B5 (H2–H4 de
    `direcoes-pli` §11).

### E5 (condicional, não implementar nesta rodada)
Planejar em detalhe A2 (BC-y: lazy C5, user cuts C3, clássicos e C5) ou B2 (simetria), conforme
as decisões de E2–E4.

---

## 4. Não repetir sem justificativa nova

| Abordagem | Por que não repetir |
|---|---|
| Lagrangeana L1 (subgradiente, bundle, Kelley) | Bound ≤ z_LP (Geoffrion); histórico todo ≤ LP |
| Relaxação lagrangeana de "caminhos" (tipo L3) | hc9u 21–24, abaixo de LP+C1 (28,44); não prioriza B6 |
| Benders clássico sem arredondamento | Relaxação = z_LP (Teorema 8) |
| Cortes Hall "com capacidade" não arredondados | Ganho 0 (Teorema 5) |
| Multicommodity com x, p binários (VI) | Até 2,4 M variáveis, raiz não termina |
| Separação dinâmica de C4 (Picard–Queyranne) | C4-DM ≈ 0 nas reais; manter só DM a priori |
| Zero-half/clique do Gurobi sobre a cobertura | Raiz padrão = ⌈LP⌉ em hc9u/hc10p |
| Pré-processamento só de tamanho | LB nunca melhorou; speedup só em Barcelona st25 R5 |
| κ local, camadas/cumulativa, desigualdades por arco em f | Mesma projeção ou contornadas (prioridade C); cumulativa: 40/31 |
| B1 (F-b-cut multicommodity) | Adiado até E2 mostrar resíduo de multiplicidade |

Instâncias fora desta rodada:
- lin23 e lin37, por pedido do usuário;
- fnl4461fst;
- hc11p e hc12p no compacto (entram só no E3, em y);
- Chicago st5 e Barcelona st15 na R do arquivo, porque são triviais.

---

## 5. Implementação (após aprovação)

Tudo em `experiments/cuts/`, sem tocar nos scripts históricos.
- `harness.py`:
  - `load_instance(path, R=None)`, para sobrescrever a R;
  - `measure_root` passa a aceitar cortes extras vindos do laço.
- `cuts.py`:
  - C3 do lado dos destinos (a rede reversa de `_build_flow_net`);
  - rede N(y) com κ: `σ→s_out` 1; `s_in→s_out` (m−1)y_s; `t_in→t_out` (m−1)y_t; `t_in→τ` 1;
    `v_in→v_out` m·y_v; arcos de alcance INF;
  - separação clássica;
  - C5 por limiar e paramétrico;
  - minimalização de Z.

  Reusar `_edmonds_karp`, `_reachable_set`, `check_C3_violations`, `generate_C1/C2/C4_DM`.
- `yspace.py`: modelo só em y (LP e IP) e o laço de separação.
- `run_e2.py` (E2 e E3) e `run_e4.py`.
- Saídas:
  - `results/cuts/e2_yspace.csv`, `e3_cobertura_ip.csv`, `e4_arvore.csv`;
  - relatório `docs/technical/reference/resultados-e2-e4-pli.md`.

## 6. Verificação
- Gabaritos sintéticos (§3, E2) antes das reais. Se algum falhar, parar e diagnosticar.
- Cada corte novo passa por um max-flow que confirma que `V ∖ Z` é inviável; qualquer corte
  inválido aborta a execução.
- E4: os ótimos das instâncias resolvidas precisam bater com as referências (17, 15, 16, 41).
- E3: todo novo LB acima da referência vem com o log do Gurobi (status, bound) e a verificação
  estrutural. A comparação com K(n,1) é só conferência.
- Todo CSV registra commit, R, seed, threads, limite de tempo e versão do Gurobi (Q6).
