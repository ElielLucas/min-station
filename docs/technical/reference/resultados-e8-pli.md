# Resultados E8 — COMP × BC-Y' × CBI em condições equivalentes

**Data:** 2026-09-26
**Formulação:** baseline, variante U (`baseline.py`), dígrafo de alcance, fluxo contínuo no COMP
**Ambiente:** Gurobi 12.0.3, Python 3.12, 4 threads, seed 42, TL de solver 300 s, commit `0a0a796-dirty`
**Plano:** `docs/technical/plans/plano-experimentos-e8.md` (inclui a revisão pré-execução)
**Dados:** `results/cuts/e8_comparative.csv`; verificações em `results/cuts/e8_verificacao.txt`

## 1. Pergunta

O E7 não decidiu a linha A2 (branch-and-cut só em y) porque tinha confundidores
(`resultados-e7-pli.md` §5.1). O E8 refaz a comparação com os três métodos nas
mesmas condições e acrescenta o CBI (Benders combinatório com mestre exato
iterado), que nunca tinha sido testado.

| Método | Descrição |
|---|---|
| COMP | modelo compacto (fluxo contínuo) + C1+C2+C4 |
| BC-Y' | espaço-y + C1+C2+C4, corte lazy 𝒵 pelo oráculo restrito, user cuts nos nós rasos (desligados se \|A_r\| > 500 mil) |
| CBI | núcleo (IP em y) + C1+C2+C4 resolvido até o fim, pool de ótimos testado no oráculo, cortes 𝒵 acrescentados, repete |

Os três recebem os mesmos cortes estáticos e a mesma solução primal
(`primal.py`, candidatos em todo V), calculada uma vez por instância fora do TL:
MIP start no COMP e no BC-Y', incumbente inicial no CBI.

## 2. Preparação e verificações

A primeira bateria do E8 foi descartada. Uma revisão independente achou:
heurística primal restrita a V∖(S∪T), COMP sem MIP start, BC-Y' com tempo extra,
CBI com LB −∞ e OPT declarado sem mestre ótimo, oráculo nunca testado com
estação em terminal, `find_mandatory` inválido e `ref_opt` de cc12-2p sem
registro. Tudo foi corrigido antes desta bateria (tabela no plano).

| Verificação | Resultado |
|---|---|
| Oráculo restrito vs. rede completa: exaustivo (todo C ⊆ V) em 9 gabaritos, inclusive S∩T≠∅, relé obrigatório em terminal e m=1; amostras sobre V em 4 instâncias reais | 0 divergências, 0 cortes inválidos |
| Pré-processamento (não usado no E8): OPT com e sem fixações | igual em 10 gabaritos e Chicago; o contraexemplo TermRelayForced agora passa |
| Smoke do E8: primal, COMP, BC-Y', CBI em 7 gabaritos | todos no OPT e viáveis no compacto |
| Toda solução de BC-Y' e CBI na bateria, fixada no compacto | todas FEASIBLE |

## 3. Resultado novo: OPT(cc12-2p) = 6

Certificado por `experiments/cuts/verify_e8_cc12_opt.py`
(`results/cuts/e8_certificado_cc12.txt`):

- UB: solução de 6 estações viável no modelo compacto com y fixado;
- LB: núcleo C1 + C4-DM com ótimo 6 (só C1 dá 5), com os 50 cortes validados;
- a validação usa um validador por componentes conexas, equivalente a
  `is_valid_cut` quando A_r é simétrico (cc12-2p é não dirigida). Ele foi
  conferido contra `is_valid_cut` em 1275 cortes de instâncias menores, sem
  divergência. `is_valid_cut` direto levava ~130 s por corte em cc12-2p.

A instância, dada como aberta em `[6, 7]` desde o E3, estava fechada desde
então: nenhuma solução ótima do núcleo tinha sido testada no problema real.
O valor vale para a extensão ponderada (pesos 101–310, R = 500), não para uma
autonomia em passos.

## 4. Bateria

UB / LB (status). Tempo de solver até 300 s em todas as linhas salvo indicação.

| Instância | Métrica | Primal | COMP | BC-Y' | CBI |
|---|---|---|---|---|---|
| Chicago st15 R7 | ponderada+dirigida | 22 | **17 / 17 (OPT, 287 s)** | 22 / 14 | 22 / 14 |
| Barcelona st15 R5 | ponderada+dirigida | 29 | **15 / 15 (OPT, 108 s)** | 29 / 10 | 29 / 10 |
| Philadelphia st5 R2 | ponderada+dirigida | 68 | **42 / 37** | 68 / 29 | 68 / 29 |
| Philadelphia st25 R3 | ponderada+dirigida | 71 | **48 / 41** | 71 / 34 | 71 / 34 |
| hc9u R1 | Das | 59 | **40** / 32 | 49 / 32 | 59 / 32 |
| hc10p | Das (A_r = E) | 915 | **78** / 52 | 97 / 52 | 915 / **53** |
| bip42p R200 | Das (A_r = E) | 767 | **43** / 33 | 70 / 34 | 767 / **35** |
| cc12-2p R500 | ponderada | 4096 | 282 / 6 | **6 / 6 (OPT, 292 s)** | **6 / 6 (OPT, 7,5 s)** |

## 5. Leitura por regime

**R-a (redes TNTP, extensão ponderada e dirigida).** O compacto vence em tudo.
Fecha Chicago e Barcelona; em Philadelphia tem o melhor UB e o melhor LB. BC-Y'
e CBI não melhoram o UB do primal e ficam com LB de 4 a 7 estações abaixo do
compacto. Agora a comparação é justa (mesmos cortes, mesmo start, mesmo TL), então
isto é uma medida do método: nessas instâncias o fluxo carrega informação que os
cortes 𝒵 separados sob demanda não recuperam em 300 s. É consistente com o que já
se via no núcleo (Philadelphia st25: ≥500 soluções ótimas de 34, todas inviáveis).

**R-b e R-b' (hc9u, hc10p, bip42p; instâncias de Das).** LB: empate em hc9u (32);
o CBI dá o melhor LB em hc10p (53 contra 52) e bip42p (35 contra 34 e 33). UB: o
compacto é claramente melhor (40, 78, 43). O CBI fez uma única iteração em hc10p
e bip42p: com `PoolSearchMode=2` o mestre não termina em 300 s (no E3 o núcleo de
bip42p também não fechou em 600 s), então nenhum corte foi gerado e o UB ficou no
primal.

**R-c (cc12-2p, extensão ponderada).** Os métodos em espaço-y provam o ótimo; o
compacto não. O CBI prova em 7,5 s de solver, com uma iteração e 9 chamadas ao
oráculo; o BC-Y' em 292 s. O compacto termina com UB 282 e LB 6.

## 6. Decisão sobre A2

Critério do plano E8 (§13 de `direcoes-pli-min-station.md`, agora aplicável): A2
segue se BC-Y' ou CBI superar o COMP em LB final ou em tempo até o ótimo em pelo
menos um regime.

**Satisfeito: A2 continua.** Em R-c o CBI prova o ótimo em 7,5 s e o compacto
não prova em 300 s; em hc10p (R-b) e bip42p (R-b') o CBI tem o melhor LB.

**Proposta de escopo (a decidir):** seguir com A2 só fora de R-a, com o CBI como
variante principal, e manter o compacto com cortes estáticos como método de R-a,
onde ele venceu em todas as quatro instâncias. O critério do plano é por regime e
não diz como recortar o escopo; o recorte fica registrado como proposta, não como
decisão tomada.

## 7. Limitações

1. **Uma seed.** A variância de seed já foi grande no E7 (hc9u 48 vs. 56). As
   diferenças de LB de uma unidade em hc10p e bip42p não são conclusivas sem
   repetição (`run_e8.py --seeds 42 43 44`).
2. **Um único caso em R-c.** O ganho em cc12-2p é grande, mas é uma instância, e
   nela o ótimo do núcleo já era viável. Falta testar em outras instâncias de
   cobertura densa, inclusive onde o núcleo não é justo.
3. **Heurística primal fraca em instâncias grandes.** Partindo de C = V, o
   reverse-delete fica caro quando C ainda é grande: em cc12-2p gastou 291 s e
   devolveu as 4096 estações; em hc10p e bip42p, 915 e 767. O start foi, na
   prática, inútil nessas instâncias para os três métodos.
4. **Efeito do start no COMP em cc12-2p.** No E7, sem start, o compacto achou UB 7;
   aqui, com o start de 4096 estações, terminou com 282. Com uma seed não dá para
   separar o efeito do start da variância.
5. **CBI em hc10p/bip42p.** O mestre com `PoolSearchMode=2` não termina no TL.
   Mestre sem pool (ou com pool só depois do ótimo) é um ajuste óbvio a testar.
6. **Métrica.** As conclusões de R-a valem para a extensão ponderada e dirigida;
   as de R-c, para a extensão ponderada. As de R-b/R-b' valem para o problema de
   Das (open-questions Q2 e Q7).

## 8. Próximos passos sugeridos

1. Repetir hc9u, hc10p, bip42p e cc12-2p com 3 seeds.
2. CBI: resolver o mestre sem pool até o ótimo e só então enumerar; testar em hc10p/bip42p.
3. Heurística primal que parta de um C pequeno (por exemplo, o ótimo do núcleo)
   e repare, em vez de partir de C = V.
4. Mais instâncias de cobertura densa (cc10-2u, cc12-2u, hc11p, hc12p) para
   verificar se o ganho do CBI em R-c se repete.
