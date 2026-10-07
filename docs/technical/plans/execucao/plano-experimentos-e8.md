# Plano: revisão pós-E7 e próximos passos (E8)

## Contexto

Rodadas E0–E7 concluídas. E0–E5 commitadas (`0a0a796`); E7 no working tree, sem commit.
O E7 concluiu "BC-y perde para o compacto em todos os regimes" e deixou em aberto uma divergência
entre dois critérios de decisão sobre A2. A revisão agora mostra que **o E7 não mede o método**:
ele tem três confundidores introduzidos na implementação (minha, rodada anterior):

1. **Cortes estáticos desiguais.** BC-Y recebeu só C1 (`prepare_static_c1`); COMP recebeu
   C1+C2+C4. O CSV mostra: 15 vs 24 (Chicago), 20 vs 28 (Barcelona), 10 vs 50 (Phil st5),
   46 vs 73 (Phil st25). O desenho de A2 em `direcoes` §13 exige "os mesmos cortes de A1" — é a
   comparação que isola a decomposição dos cortes.
2. **MIP start não garante viabilidade.** `_greedy_mip_start` para no orçamento de 5 s e devolve
   `y` parcial mesmo com flow < m. Em R-a (0 incumbentes em 4/4), o "sem incumbente" é provável
   artefato: toda solução que o Gurobi acha satisfaz só C1 e é rejeitada pelo lazy.
3. **Separação lenta e sem guarda de tempo.** Cada chamada reconstrói a rede inteira (todos os arcos
   de A_r) e roda Edmonds-Karp em Python puro: callback = 70–99,9% do tempo; em cc12-2p o TL de
   300 s virou 1544 s porque o Gurobi não interrompe callback em andamento.

Ainda: seed única com variância enorme no BC-Y (hc9u 56 vs 48; bip42p 208 vs 69 na reexecução),
e no CSV as linhas FEASIBLE de hc9u/bip42p combinam o obj da 1ª execução com o veredito da 2ª.

**Sinais medidos nesta revisão (só leitura):**

| Medida | Resultado | Leitura |
|---|---|---|
| Núcleo em y (C1+C2+C4), IP exato (E3) | Phil st25 0,008 s; Barcelona st50 0,002 s; cc10-2p 0,012 s; cc12-2p 0,1 s; hc9u 3 s | mestre em y é baratíssimo em R-a e R-c |
| Pool de ótimos do núcleo, Phil st25 | ≥500 soluções de 34; 50 testadas no oráculo, **0 viáveis**; oráculo 0,03 s | em R-a o núcleo é fraco (34 vs ref ≥42): Benders iterado precisaria de muitas iterações |
| Pool do núcleo, Barcelona st50 R6 | ≥500 soluções de 9; 50 testadas, **0 viáveis**; oráculo de rede inteira 0,42 s | mesmo padrão de Phil st25 |
| Pool do núcleo, cc12-2p | **não medido**: a análise foi encerrada sem produzir saída | primeiro teste do Bloco 1 (se alguma solução de 6 for viável, cc12-2p fecha em 6) |
| Oráculo de rede inteira em cc10-2p/cc12-2p | análise não terminou em 15 min (carga + checagens em Python) | confirma o gargalo do item 3; justifica o Bloco 1 |
| Dominância de vizinhança em A_r (`N⁺(u)⊆N⁺(w)`, `N⁻(u)⊆N⁻(w)`, u não terminal) | Chicago 22%, Phil 17–18%, Barcelona 7%, bip42p 5%, hc9u 0% | redução moderada, barata; não é o grande salto |
| Bibliotecas no ambiente | só `networkx` e `numpy` (sem scipy/ortools/igraph) | aceleração tem de vir do algoritmo, não de biblioteca C |

**Estado das instâncias abertas** (LB válido / UB válido): Phil st5 R2 = 41 (ref; COMP 300 s: 41/38);
Phil st25 R3 [42, 46] ref (nosso melhor 41/47); hc9u [32, 38]; bip42p R200 [36, 43]
(LB = bound do núcleo, E3/E6; UB = COMP E7); cc12-2p R500 [6, 7]. Fechadas: Chicago st15 R7 = 17,
Barcelona st15 R5 = 15, cc10-2p = 3.

**Onde está o avanço considerável.** Fechar instâncias abertas e ter um método que escale onde o
compacto sofre. O mestre em y resolve em milissegundos exatamente em R-c (onde o compacto tem
2,8 M arcos) e em R-b'. Um Benders combinatório com **mestre exato iterado** (resolver núcleo →
testar no oráculo → adicionar corte 𝒵 → repetir) nunca foi testado, e é barato. O callback do E7
foi a variante branch-and-Benders-cut, com implementação confundida.

---

## Bloco 0 — Registro do E7 (só documentação)

- `resultados-e7-pli.md`: nova seção "Confundidores" com os itens 1–3 e a variância de seed;
  rebaixar "resultado decisivo e negativo para R-a" para "não conclusivo: comparação desigual".
  Conclusão do §6 passa a ser: o E7 não decide A2; o E8 refaz a comparação em base justa.
- `e7_comparative.csv`: nas linhas BC-Y de hc9u/bip42p, trocar `bcy_sol_feasible` por
  `FEASIBLE(reexec obj=48)` / `FEASIBLE(reexec obj=69)` — não misturar execuções em silêncio.
- `direcoes` §13 (nota de divergência): a divergência deixa de precisar de decisão agora, porque
  o E7 não é base válida para nenhum dos dois critérios. O E8 elimina a condição "callback caro"
  que gera a divergência; aplica-se então o critério de §13.

## Bloco 1 — Oráculo inteiro rápido (pré-requisito de tudo abaixo)

Para `y` binário, viabilidade = existe emparelhamento perfeito S→T no grafo de alcance que passa só
por estações. Não precisa da rede inteira:

- Rede restrita a `S ∪ T ∪ C` (C = estações), arcos filtrados de `N⁺` pré-computado uma vez.
  Mesma semântica de `_build_flow_net_aggregate` (terminal: arco `σ→v_out` / `v_in→τ`,
  trânsito `(m−1)·y`; `S∩T` com os dois arcos).
- `Z` sem materializar A_r: após o max-flow, `X` = alcançáveis no residual;
  `Z = {v ∉ C, não terminal : v ∈ N⁺(u) para algum u com u_out ∈ X}` ∪ `{v ∈ C∪S∪T : v_in ∈ X, v_out ∉ X}`
  (mesma regra de `_extract_Z`, inclusive o caso m<2).
- Múltiplos cortes por ponto inviável: `Z` do lado da fonte e do lado do sumidouro (rede reversa,
  como `check_C3_violations_dest`).
- Função nova em `cuts.py`: `integer_oracle(S, T, N_plus, C) -> (viavel, [Z...])`. Reusa
  `_edmonds_karp`, `_reachable_set`, `_extract_Z` (lógica), `build_neighborhoods`.
- Guarda de tempo no callback: `if modelo.cbGet(GRB.Callback.RUNTIME) > TL: modelo.terminate()`.

**Primeiro uso (barato, alto sinal):** testar todo o pool de ótimos do núcleo de cc12-2p (6
estações) no oráculo restrito. Uma solução viável fecha cc12-2p = 6. Se o pool completo for
inviável, o LB sobe para 7 = UB e a instância também fecha.

**Verificação:** em gabaritos e em 200 `y` aleatórios por instância real (Chicago, Phil st25,
hc9u, cc10-2p), veredito e `Z` iguais aos de `_build_flow_net_aggregate`+`_extract_Z`; todo `Z`
aprovado por `is_valid_cut`. Medir tempo por chamada (alvo: ≥10× mais rápido; em cc12-2p, segundos
→ milissegundos, já que |C| ≈ 6–7).

## Bloco 2 — Heurística primal por oráculo (UB e MIP start)

`experiments/cuts/primal.py`:
- Construção sempre viável: parte de `y ≡ 1` (viável se a instância é) e faz *reverse-delete*
  (remove estação se continua viável), em ordem de menor grau em A_r primeiro; várias ordens
  aleatórias com seed.
- Busca local: remoção simples e troca 2-por-1 (tira duas, põe uma) enquanto houver melhora.
- Substitui `_greedy_mip_start` em `bc_yspace.py`. O mesmo start é dado a COMP, BC-Y e CBI no E8
  (justiça).

**Verificação:** toda solução confirmada no compacto (fixando `y`) e no oráculo. Metas de UB:
Chicago 17, Barcelona 15, Phil st5 41 (referências), e melhorar Phil st25 (<47), hc9u (≤38),
bip42p (<43), cc12-2p (6?).

## Bloco 3 — Pré-processamento (dominância, vértices mortos, obrigatórios)

`experiments/cuts/preprocess.py`:
- **Dominância:** u não terminal, w ≠ u com `N⁺[u] ⊆ N⁺[w]` e `N⁻[u] ⊆ N⁻[w]` ⇒ fixar `y_u = 0`
  (qualquer rota que recarrega em u recarrega em w). Gêmeos: manter um por classe.
- **Mortos:** não alcançável a partir de S ou que não alcança T em A_r ⇒ `y = 0`.
- **Obrigatórios (R2):** `V∖{v}` inviável no oráculo ⇒ `y_v = 1`.
- No compacto, vértice não terminal com `y=0` fixo sai do modelo com seus arcos.
- Justificativa escrita (lema curto) em `docs/technical/reference/` antes de usar; é experimental,
  não entra na base sem decisão.

**Verificação:** OPT inalterado em Chicago 17, Barcelona 15, cc10-2p 3 e gabaritos; medir
redução de variáveis/arcos e efeito no COMP (mesmo TL/seed do E4). Expectativa honesta: ganho
moderado em R-a (7–22% das variáveis), nulo em hc9u.

## Bloco 4 — E8: comparação justa + Benders com mestre iterado

`experiments/cuts/run_e8.py`, TL=300 s, mesmas 7 instâncias do E7 + hc10p:

| Config | Descrição |
|---|---|
| COMP | compacto + C1+C2+C4, start do Bloco 2 |
| BC-Y' | y-space + C1+C2+C4 estáticos, start do Bloco 2, lazy pelo oráculo (2 cortes/ponto), user cuts só na raiz, guarda de TL |
| CBI | mestre exato iterado: resolve núcleo, testa soluções do pool no oráculo, adiciona todos os Z, repete; LB = ótimo do mestre a cada iteração; para ao achar viável (ótimo provado) ou no TL |

- 3 seeds para COMP e BC-Y' nas instâncias com gap.
- Métricas: UB, LB, gap, tempo até ótimo, iterações/cortes, fração de tempo no oráculo,
  metadados Q6 (`gurobi`, `tl_s`, `formulacao=U`, commit).
- Decisão (critério de §13, agora sem o confundidor do callback): A2 segue se BC-Y' ou CBI superar
  COMP em LB final ou tempo até o ótimo em ≥1 regime; caso contrário, A2 encerrada.
- Expectativa: CBI fraco em R-a (pool com ≥500 ótimos inviáveis), promissor em R-b'/R-c.

## Bloco 5 — Tentativa de fechamento (condicional ao E8)

Com o melhor método por regime, TL de 3600 s em cc12-2p, bip42p e Phil st25. Resultado registrado
só com certificado: UB conferido no compacto, LB do solver/mestre exato.

---

## Ordem e verificação

1. Bloco 0 (docs). 2. Bloco 1 + testes de equivalência. 3. Bloco 2. 4. Bloco 3.
5. Smoke do E8 nos gabaritos (inclui StayPut/SharedTerminal para `S∩T`) e bateria.
6. `resultados-e8-pli.md`; atualizar `direcoes` §13 com a decisão sobre A2. Commit só com aprovação.

## Não fazer

Teste específico de nível em hc9u; nova dependência (scipy/ortools) sem pedir; B1/F-b-cut
(fica para depois do E8); Benders clássico, Lagrangeana, zero-half; `lin23`, `lin37`,
`fnl4461fst`; alterar a formulação base; push.

## Arquivos

- Corrigir: `resultados-e7-pli.md`, `e7_comparative.csv`, `direcoes-pli-min-station.md` (§13)
- Estender: `cuts.py` (`integer_oracle`), `bc_yspace.py` (start novo, oráculo, guarda de TL)
- Novos: `primal.py`, `preprocess.py`, `run_e8.py`, `resultados-e8-pli.md`
- Reusar: `build_neighborhoods`, `_edmonds_karp`, `_reachable_set`, `_extract_Z`, `is_valid_cut`,
  `harness.load_instance`/`prepare_cuts`/`measure_mip`, `yspace._build_ymodel`,
  `baseline.construir_modelo_baseline`

---

## Revisão pré-execução (antes da bateria definitiva)

Uma primeira bateria do E8 foi interrompida e descartada: rodava com as
assimetrias e defeitos abaixo, encontrados numa revisão independente.

| Problema | Correção |
|---|---|
| `primal.py` só considerava estações em V∖(S∪T): devolvia None em TermRelay/SharedTerminal e nunca usava terminais | candidatos em todo V, partida de C = V; gabarito novo `TermRelayForced` (ótimo exige estação em destino) |
| COMP sem MIP start; BC-Y' com start calculado dentro do método e até 30 s fora do TL; CBI sem start | primal calculado uma vez por instância, fora do TL, e entregue ao COMP (`measure_mip(y_start=...)`), ao BC-Y' (`y_start`) e ao CBI (`ub_start`); tempos de solver, total e primal em colunas separadas |
| CBI reportava `bound=-inf` quando a última iteração do mestre parava no TL, e declarava OPT mesmo com mestre não ótimo | LB = maior `ObjBound` finito entre iterações; OPT só com mestre `OPTIMAL` e solução do pool viável, ou UB = LB |
| `verify_e8_oracle.py` nunca colocava terminais em C | bateria exaustiva (todo C ⊆ V) nos gabaritos pequenos, inclusive S∩T≠∅ e m=1, e amostragem sobre V nas reais: 0 divergências, 0 cortes inválidos |
| `preprocess.find_mandatory` testava só não terminais (TermRelayForced: OPT 1 virava 2) | testa V∖{v}; terminal só domina com m ≥ 2. `preprocess.py` não é usado pelo E8 |
| `ref_opt=6` de cc12-2p sem registro | `ref_opt=None` até o certificado `verify_e8_cc12_opt.py` passar |
| User cuts do BC-Y' montam a rede agregada completa | desligados quando \|A_r\| > 500 mil (cc12-2p), registrado em `params_metodo` |
| Métrica das instâncias não registrada | coluna `metrica`; classificação em `open-questions.md` Q2/Q7. Correção de leitura: hc10p–hc12p e bip42p têm `A_r = E`, logo são Das com r=1, não extensão |

Escopo: hc10p entrou; 3 seeds ficam disponíveis por `--seeds`, mas a bateria
padrão usa uma seed (limitação registrada no relatório).
