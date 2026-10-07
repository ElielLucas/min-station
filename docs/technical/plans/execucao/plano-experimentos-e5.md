# Plano: rodada E5 — fidelidade a Das, validade de cortes e branch-and-cut em y

## Contexto

As rodadas E0–E4 terminaram e o relatório `docs/technical/reference/resultados-e2-e4-pli.md`
já foi revisado. Duas investigações posteriores encontraram problemas de natureza diferente, e
esta rodada trata os dois antes de qualquer experimento novo.

**1. Erro de corretude em relação ao problema original.** A formulação base assume `S ∩ T = ∅`,
mas Das não impõe essa restrição. A prova do Lema 5 do artigo depende de um vértice que é
origem e destino ao mesmo tempo: *"every robot is starting from a target position"* e *"The
robot starting at s_i remains at s_i occupying the target t_o"* (p. 11–12 de
`docs/technical/reference/min-station-das.pdf`, verificado no texto do PDF). Com `v ∈ S ∩ T`, os
balanços 6.1 e 6.2 somados dão `0 = 2` e a PLI fica **inviável**, enquanto o MIN-STATION é
sempre viável (`C = V` resolve). É um **falso negativo**. O próprio repositório já havia
diagnosticado isso: `validacao-formulacao-base.md` classifica como **P1, "erro de modelagem"**,
e a questão **Q1** de `open-questions.md` continua aberta.

Decisão tomada: **adotar a variante U** (balanço unificado do §10.1 de `base-formulation.md`),
que é idêntica à formulação atual quando `S ∩ T = ∅` e restaura a fidelidade a Das.

**2. Cortes inválidos.** Na instância Chicago st15 com R=26, cujo OPT=0 está provado, o laço em
espaço-y subiu o LP para 1,0 gerando 30 cortes `y(Z) ≥ 1` violados pela solução ótima `y = 0`.
Os estágios S3 e S4 do E2 estão invalidados; E3 e E4 não foram afetados.

**Impacto nos resultados existentes: nenhum.** Verifiquei que as 22 instâncias têm
`|S ∩ T| = 0` — o gerador `escolher_ST_disjuntos` força disjunção por construção, e é por isso
que o defeito nunca apareceu. A revalidação é por **equivalência**, não por reexecução.

**3. Para onde atacar depois.** O núcleo de cobertura resolve hc9u na otimalidade em 2,1 s, mas
uma sonda indicou que a solução de 32 estações é **inviável** no problema real (max-flow 97 de
m=128). Se confirmado, `OPT(hc9u) > 32` estritamente e o núcleo está **esgotado** — nenhum
reforço dele move o número. O resíduo é de acoplamento Hall multi-salto, a família 𝒵 do
Teorema 6, separável por max-flow. Isso promove **A2** (branch-and-cut só em y com corte lazy) e
encerra **B2** (simetria).

Restrições mantidas: não introduzir custos heterogêneos, autonomias por robô ou elegibilidade
origem-destino; não reintroduzir estações apenas em vértices intermediários; não usar `lin23`,
`lin37`, `fnl4461fst`; não alterar scripts históricos sem necessidade; não commitar sem pedido;
documentar em português brasileiro.

**Passo 0, ao aprovar:** copiar este plano para
`docs/technical/plans/plano-experimentos-e5.md`. Nenhuma execução nesse passo.

---

## Bloco A — Verificação estrutural (~15 min)

Várias afirmações desta rodada vieram de sondas de subagente e **não estão auditadas**. Construir
o plano sobre elas repetiria o erro que produziu os limites falsos. Antes de tudo, transformar
cada uma em verificação própria, versionada.

Novo `experiments/cuts/verify_structure.py`, saída `results/cuts/e5_estrutura.csv`, sobre
`hc9u`, `hc10p`, `hc11p`, `hc12p`, `bip42p`:

| Medida | Por que importa |
|---|---|
| `\|S\|`, `\|T\|`, `\|S ∩ T\|`, `\|S ∪ T\|` | o plano E2–E4 §2 fala em "256 terminais" com m=128; esclarecer |
| grau por vértice; toda aresta liga ids que diferem em 1 bit | distingue Q_k de outro grafo |
| paridade de `S ∪ T`; arestas internas a `S ∪ T` | se não for exatamente uma classe de bipartição, vira cobertura parcial |
| **`\|A_r\|` vs `\|E\|`** | invariante crítico: hc10p–hc12p têm R=150 com pesos ~100–110; se `A_r = E`, o alcance é de 1 salto |
| nº e tamanho das linhas C1; linhas por variável | matriz biregular dá LP em forma fechada `2^(k-1)/k` |
| `set(C2) ⊆ set(C1)`? `set(C4) ⊆ set(C1)`? | se sim, o "núcleo C1+C2+C4" é só C1 nessas instâncias |
| classes de assinatura por variável | detecta gêmeos; decide a regra R3 antes de implementá-la |

**Verificação de viabilidade do ótimo do núcleo** (a mais importante): resolver `solve_ip_yspace`
em hc9u, fixar `y` no conjunto resultante dentro do modelo compacto e checar o status. Se
`INFEASIBLE`, fica **provado que OPT(hc9u) > 32** — resultado novo e justificativa do Bloco D.

Registrar ⌈LP⌉ = ⌈2^(k−1)/k⌉ ao lado de cada limite inferior do E3. A sonda indicou que em hc12p
o limite 171 é exatamente ⌈2048/12⌉, isto é, contribuição zero do branch-and-bound. Se
confirmado, corrigir a redação do relatório, que hoje apresenta 171 como avanço de bound.

**Critério:** se qualquer medida refutar a leitura estrutural, parar e reescrever o diagnóstico.
Resultado negativo aqui é informação, não fracasso.

---

## Bloco B — Fidelidade a Das: variante U (~1 h)

Erro de corretude, então vem antes das demais correções. Tudo aqui é **conservador**: com
`S ∩ T = ∅` nada muda.

### B.1 Provar a equivalência antes de implementar

Registrar em `docs/technical/reference/validacao-formulacao-base.md` a verificação caso a caso
de que U generaliza a formulação atual, com `a_v = 1_S(v)` e `b_v = 1_T(v)`:

| Caso | `a,b` | Balanço U | Equivale a |
|---|---|---|---|
| `v ∈ S∖T` | 1,0 | `out − in = 1` | 6.1 |
| `v ∈ T∖S` | 0,1 | `in − out = 1` | 6.2 |
| `v ∉ S∪T` | 0,0 | `in = out` | 6.3 |
| `v ∈ S∩T` | 1,1 | `in = out`, com `in, out ≤ 1 + (m−1)y_v` | **caso novo** |

Semântica do caso novo: `in(v) = out(v) = 0` é o robô parado ocupando o próprio alvo (Figura 3
de Das); `= 1` é a troca — o robô de `v` parte e outro chega, válida sem estação.

### B.2 Implementar em `baseline.py`

Mudança mínima, só nas equações de balanço (linhas 110–129):

```
out(v) − in(v) = a_v − b_v        ∀ v ∈ V
in(v)  ≤ b_v + (m − b_v)·y_v      ∀ v ∈ V
out(v) ≤ a_v + (m − a_v)·y_v      ∀ v ∈ V
```

Equivalente à forma de "correção mínima" do §9 da validação: `S → S∖T`, `T → T∖S`, e `S∩T`
migra para a conservação. As ativações 7.1–7.4 **não mudam**.

Remover a guarda de `baseline.py:44-49` (`"Esta formulação assume S e T disjuntos"`), que é
exatamente o que restringe o problema. **Não** tocar nas guardas equivalentes dos scripts
lagrangeanos e do Benders — são históricos e estão fora de uso; apenas registrar que continuam
restritos.

Reusar a implementação existente: `experiments/preprocessing/modelo_min_station_das_preprocess.py:921-956`
já implementa U literalmente, e serve de referência cruzada.

### B.3 Corrigir o tratamento de `S ∩ T` nos cortes

Hoje o tratamento é **inconsistente entre famílias**, o que só não deu problema porque nenhuma
instância exercita o caso:

| Local | Hoje | Ação |
|---|---|---|
| `generate_C1`, `generate_C2` | iteram `S_set - T_set` e `T_set - S_set`, pulando `S∩T` | correto e conservador; manter |
| `generate_C4_DM` (`cuts.py:155-168`) | usa `S_set` completo dos dois lados; um `v ∈ S∩T` vira origem e destino não-emparelhados, gerando corte que o Lema 5 invalida (o robô pode ficar parado) | alinhar com C1/C2 |
| `_build_flow_net` (`cuts.py:210-217`) | `if v == s: continue` faz com que uma fonte em `S∩T` nunca receba arco para `τ`, ignorando "ficar parado" | tratar o caso |
| `_build_flow_net_aggregate` (`cuts.py:337-344`) | `if v in S_set: ... elif v in T_set:` — um `v ∈ S∩T` cai **só** no ramo de origem e nunca vira sumidouro, produzindo déficit de fluxo espúrio | dar os dois papéis ao vértice |

Note que este último ponto **substitui** o que eu havia planejado antes: em vez de adicionar uma
guarda rejeitando `S ∩ T`, tratar o caso corretamente.

### B.4 Gabarito com `S ∩ T ≠ ∅`

Nenhuma instância exercita o caso, então criar em `synthetic.py`:

- `make_StayPut()`: caminho `a–b–c` com `S = {a, b}`, `T = {b, c}`, `r = 1`. O robô em `b` fica
  parado ocupando o próprio alvo. Asserção: modelo **viável** (hoje seria inviável) e OPT
  conferido à mão.
- Caso de troca: estrela `K_{1,4}` com `S ∩ T = {v}`, onde a validação (§412) registra que a
  troca funciona com `y_v = 0` para um robô, mas dois robôs chegando forçam `y_v = 1`.

### B.5 Regressão por equivalência

Conforme decidido, não reexecutar a bateria. Verificar que U reproduz os números anteriores:

1. Todos os gabaritos existentes (F1 ×2, F2 ×2, Tri, Sec59) com valores idênticos.
2. Subconjunto real — hc9u, Philadelphia st25, Barcelona st25, cc10-2p — comparando LP, bound de
   raiz e OPT contra `results/cuts/e1_raiz.csv` e `e4_arvore.csv`. **Qualquer diferença é bug**,
   porque `|S ∩ T| = 0` em todas.

### B.6 Documentação

- `open-questions.md` **Q1: fechar**, registrando a decisão e a justificativa em Das.
- `base-formulation.md` §10.1: U deixa de ser "não adotada" e passa a ser a formulação corrente.
- `direcoes-pli-min-station.md`: remover a divergência registrada na linha 612 (item 4), já que
  documentação e código passam a coincidir.
- `validacao-formulacao-base.md`: P1 deixa de ser problema aberto. Corrigir também a referência
  obsoleta a `modelo_min_station_fluxo_2.py`, arquivo que não existe mais.
- `RESEARCH.md` e `project-overview.md`: registrar explicitamente que `S ∩ T ≠ ∅` é permitido.

**Efeitos colaterais a registrar** (já previstos na documentação, não são regressões):
ciclos de custo zero passam a existir, então vale "existe um ótimo acíclico" e não "todo ótimo é
acíclico" (`direcoes:121`); a identidade `δ = m − k` do §4 precisa incluir arcos de permanência
(`direcoes:249`); e há Big-M mais forte disponível para `v ∈ S∩T`: `in(v) ≤ 1 + (m−2)y_v`
(`validacao:329`) — registrar, não implementar agora.

---

## Bloco C — Validade dos cortes (~2 h)

Seis defeitos, em ordem verificável isoladamente.

### C.1 Gabaritos de regressão primeiro (antes de corrigir nada)

- `make_Direct0()`: `S={s1,s2}`, `T={t1,t2}`, arestas `s1–t1`, `s2–t2`, `r=1`. **OPT=0.** É a
  Chicago-R26 em miniatura. Asserção: nenhuma família gera corte; LP final = 0.
- `make_TermRelay()`: `S={s1,s2}`, `T={t1,t2}`, arestas `s1–t1`, `s2–t1`, `t1–t2`, `r=1`.
  **OPT=1**, única solução `y_{t1}=1`: o destino `t1` precisa ser estação para relaiar o robô de
  `s2`, sem ser cobrado pelo robô que termina nele.

Rodar **antes** de corrigir: ambos devem falhar. É o que prova que a regressão é real.

### C.2 Arco terminal na rede agregada

`cuts.py:342`: trocar `arc(f'{v}_out', '_t', 1.0)` por `arc(f'{v}_in', '_t', 1.0)`. O nó `t_in`
passa a repartir sua entrada entre a unidade que termina ali (≤1, grátis) e o trânsito
(≤ `(m−1)y_t`), que é exatamente `Σ f_{u,t} ≤ 1 + (m−1)y_t`. Alinha com a rede canônica de
`direcoes-pli-min-station.md` §3.1, com a docstring da própria função, e com
`benders_min_station.py:montar_rede_fluxo`, que já implementa a rede correta. As origens estão
corretas e não mudam.

### C.3 Definição de Z

`separate_classical_fracs` exclui `S ∪ T` de Z. O Teorema 6 define
`Z(X) = {v : v_in ∈ X, v_out ∉ X}` **sem exclusão**; terminais participam com `κ_v = m−1`.
Remover elementos fortalece a desigualdade além do que o teorema garante, tornando-a
possivelmente inválida. Extrair helper `_extract_Z(...)`, usado nos três pontos de separação.
Única exclusão legítima: `m = 1`, quando terminais têm `κ_v = 0`.

Registrar no docstring a leitura que justifica: um terminal só entra em Z quando o arco
`t_in→τ` está saturado, isto é, quando precisa servir de recarga para fluxo adicional. Com a
rede errada isso era inobservável, o que explica por que a exclusão parecia funcionar.

### C.4 `generate_C5_threshold` emite conjunto errado

Defeito independente, mesma consequência. O código emite `y(C_θ) ≥ 1`, onde `C_θ` é o conjunto
**candidato a solução** — desigualdade sem teorema por trás, falsa sempre que existe solução
viável fora de `C_θ`. O §5.5(ii) especifica outra coisa: `C_θ` é o candidato, roda-se a
separação **inteira** sobre ele, e o corte é o `Z` do certificado de inviabilidade, disjunto de
`C_θ`. Além disso o teste de separador usa `allowed = S ∪ T ∪ Z`, que responde "Z sozinho
basta?" em vez de "V∖Z é inviável?" — e é a BFS que a Proposição 3.1 marca como errada.

Reescrever o miolo reusando a rede corrigida e `_extract_Z`.

### C.5 `Z = ∅` silenciado

Se o fluxo é deficiente e `Z = ∅`, a capacidade do corte independe de `y`: a instância é
inviável mesmo com `y ≡ 1`. Hoje retorna lista vazia e o laço reporta um LP como se tivesse
convergido. Trocar por exceção explícita.

### C.6 Validador de cortes

Não existe nenhum teste automatizado nem validador no repositório. Critério: `Z` é válido ⟺
`V∖Z` é inviável ⟺ toda solução viável intersecta `Z`. A Proposição 3.1 dá o teste exato:
com `y_v = 1` fora de `Z`, nenhuma capacidade de trânsito fica ativa e o max-flow iguala o
emparelhamento máximo. Logo:

> `Z` é válido ⟺ o bipartido `{(s,t) : s alcança t usando só intermediários de V∖Z}` não tem
> emparelhamento perfeito.

`is_valid_cut(S, T, A_r, Z, N_plus=None, N_minus=None)` em duas fases: BFS reversa O(|A_r|) que
retorna cedo no caso comum; só quando o corte é suspeito paga as `m` BFS e o emparelhamento,
reusando `_max_matching` de `cuts.py:121`. O teste do C5 atual é apenas condição **suficiente**
(Hall com `|S'|=1`), serve de atalho, não de validador.

**Onde plugar:** no funil de entrada — `harness.add_cuts_to_model` e `yspace._add_cuts` — o que
pega todas as famílias, inclusive as estáticas. **Política: abortar, não descartar em silêncio.**
Todas as famílias em uso são provadamente válidas, então corte inválido só pode ser bug.
Coerente com o `sys.exit(1)` já usado em `run_e2.py:124`. Parâmetro `validate_cuts=True` por
padrão, desligável por instância, com o desligamento aparecendo no log e no CSV.

**Verificação do validador:** nos gabaritos pequenos, comparar contra oráculo independente —
fixar `y` no modelo compacto e conferir `INFEASIBLE` no Gurobi.

### C.7 Override de autonomia R

`load_instance(path, R=None)` em `harness.py:231`. Corrigir também o truncamento
`int(float(dados['R']))`, que transforma `R=2.5` em `2` e amplia o alcance efetivo.

Em `run_e4.py` o slot já está reservado — `INSTANCES` são tuplas `(fname, None, ref_opt)` cujo
campo do meio é descartado. Preencher (Chicago st15 → 7, Barcelona st15 → 5, Barcelona st25 → 5,
Philadelphia st5 → 2, Philadelphia st25 → 3) e consumir no laço. Acrescentar coluna `r_origem`.
Fazer o mesmo em `run_e2.py`, senão E2 e E4 rodam em regimes diferentes e não são comparáveis.

**Critério de aceitação:** Chicago st15 R7 → **17**, Barcelona st15 R5 → **15**,
Philadelphia st5 R2 → **41**.

### C.8 Max-flow

O diagnóstico anterior estava incompleto. O gargalo dominante não é o Edmonds-Karp (o fluxo é
≤ m, logo há poucos aumentos), e sim **reconstruir a rede a cada origem e a cada rodada** —
centenas de reconstruções de uma rede de 2,8 M arcos. A causa estrutural é que `_edmonds_karp`
destrói `cap` in-place.

`networkx 3.6.1` **já é dependência declarada** (`pyproject.toml:12`) e já é usada para corte
mínimo no mesmo problema (`benders_min_station.py:475`). Passo A: construtores emitem
`nx.DiGraph`; `_min_cut` devolve `(valor, lado_fonte)` com a mesma semântica de
`_reachable_set`. Passo B, **condicionado a medição**: só se C3 continuar caro, cachear o
esqueleto por instância. Parte do problema sai de graça com C.7: com R=7 em vez de 26, `|A_r|`
de Chicago despenca. Manter `_edmonds_karp` durante a troca para comparar; remover depois.

### C.9 Dedup em `prepare_cuts`

`harness.py:49` concatena famílias com `+=` sem deduplicar, ao contrário de `yspace.py`. Isso
inflou o E4 (768 cortes em hc9u = 256×3). Uma linha, mantendo `counts` bruto e acrescentando
`counts['unicos']`.

---

## Bloco D — E6: branch-and-cut em y com corte lazy (A2, ~1 h)

Só faz sentido se o Bloco A confirmar que o ótimo do núcleo de hc9u é inviável no problema real.

Não existe **nenhum** callback em `experiments/cuts/` — este é o primeiro. Os separadores já têm
assinatura uniforme `(S, T, A_r, y_star) -> list[frozenset]`, compatível com `cbLazy`.

Novo `experiments/cuts/bc_yspace.py`, runner `run_e6.py`, saída `results/cuts/e6_bc_y.csv`.

- Modelo: IP em y reusando `_build_ymodel`, com C1 estático a priori.
- `Params.LazyConstraints = 1`, callback em `GRB.Callback.MIPSOL`.
- No callback: ler `ȳ` inteiro, montar a rede **já corrigida** (Bloco C.2), rodar max-flow. Se
  `flow < m`, extrair `Z` e adicionar `cbLazy(Σ_{v∈Z} y_v ≥ 1)`.
- Para `ȳ` inteiro inviável, o corte mínimo dá `Z` disjunto do conjunto escolhido (Teorema 6),
  então o corte é válido e o limite inferior é legítimo **sem ressalva**.

Instâncias: `hc9u` e `bip42p`, TL 900 s. Configurações: núcleo puro sem lazy (controle) e
núcleo + lazy.

| Resultado | Leitura |
|---|---|
| **LB(hc9u) ≥ 33** | sucesso. Primeiro número que não pode vir do núcleo, cujo teto é 32 |
| LB = 32, cortes separados, árvore progredindo | parcial: mecanismo funciona, falta força |
| nenhum corte lazy separado | bug no callback, não fracasso do método |

---

## Bloco E — Encerramento documentado de B2

Registrar, com a evidência do Bloco A, por que a linha de simetria não se sustenta nas hc*:
grupo vértice-transitivo (fixação orbital rende 1 variável), ausência de gêmeos (R3 elimina 0
variáveis), `Symmetry=2` empatando com o padrão. Atualizar §1.6 e a linha B2 de
`direcoes-pli-min-station.md`.

`Symmetry=2` é sonda **binária** (mudou / não mudou): não distingue "não achei grupo" de "achei
e não ajudou", e afeta também heurísticas e presolve.

---

## Pendência sua: bibliografia de códigos de cobertura

A redução do núcleo das hc* ao código binário de cobertura de comprimento `k−1` e raio 1 é
**demonstrável** e será provada e registrada (bijeção entre a classe par de Q_k e 𝔽₂^(k−1)).

Os **valores tabelados** de K(n,1) ficam como pendência marcada, conforme sua decisão. Não vou
afirmar número que não tenha sido provado aqui. Fica registrado que, se confirmados por você,
tornam-se limites inferiores válidos para hc10p, hc11p e hc12p sem custo de CPU, porque o núcleo
é relaxação (Teorema 6). Cuidado de indexação: hc_k corresponde a comprimento **k−1**.

---

## Verificação end-to-end

1. `verify_structure.py` bate com as medidas esperadas — ou refuta, e o diagnóstico é reescrito.
2. Variante U: gabaritos existentes com valores idênticos; `make_StayPut` viável (hoje seria
   inviável); subconjunto real reproduzindo LP, bound e OPT dos CSVs anteriores.
3. `make_Direct0` e `make_TermRelay` **falham** antes das correções e **passam** depois.
4. Validador conferido contra o oráculo Gurobi, exaustivamente sobre singletons e pares.
5. `run_e2` na Chicago **R=26**: zero cortes, LP=0 nos quatro estágios.
6. Gabarito §5.9 (L=7) fecha em 7 **já no estágio 3**, sem depender do C5.
7. `run_e4` com override: 17, 15 e 41.
8. E6: cortes lazy efetivamente separados em hc9u; LB comparado com 32.

Ao final, regerar `results/cuts/e2_yspace.csv` e `e4_arvore.csv` e atualizar
`resultados-e2-e4-pli.md`, mantendo o registro do defeito (§1.4) como histórico.

Todo CSV registra commit, R e sua origem, seed, threads, limite de tempo, versão do Gurobi e
formulação (U), conforme Q6.

---

## Não fazer nesta rodada

| Item | Motivo |
|---|---|
| Pré-processar `v ∈ S∩T` como "robô parado, remover de S e T" | **inválido**, provado por contraexemplo CE1' (`validacao:231`); é o que o Benders faz hoje |
| Alterar guardas de `S∩T` nos lagrangeanos e no Benders | scripts históricos fora de uso; apenas registrar |
| Big-M reforçado `in(v) ≤ 1 + (m−2)y_v` para `S∩T` | registrar como oportunidade; implementar agora misturaria fidelidade com fortalecimento |
| Quebra de simetria em hc* (B2) | grupo vértice-transitivo, zero gêmeos, `Symmetry=2` sem efeito |
| Zero-half / mochila C6 sobre o núcleo de hc9u | núcleo já resolvido na otimalidade; não há relaxação a fortalecer |
| hc11p e hc12p em B&B | fechar o núcleo equivale a determinar valores em aberto na literatura |
| Cortes "camadas" | raiz de hc9u a 24,03 e resultado final igual ao baseline em 3600 s |
| Lagrangeana (L1) e Benders clássico | bound ≤ z_LP (Geoffrion) e = z_LP (Teorema 8) |
| Introduzir pytest | gabaritos + aborto já são o mecanismo vigente |
| `lin23`, `lin37`, `fnl4461fst` | fora de escopo |

---

## Arquivos a modificar

- `baseline.py` — variante U nos balanços; remoção da guarda de `S∩T`
- `experiments/cuts/cuts.py` — rede agregada, `_extract_Z`, `is_valid_cut`, `_min_cut`, C5,
  tratamento de `S∩T` em `generate_C4_DM` e nas duas redes de fluxo
- `experiments/cuts/harness.py` — `load_instance(path, R=None)`, dedup, validação no funil
- `experiments/cuts/yspace.py` — propagação de `validate_cuts`, reuso de `N_plus`/`N_minus`
- `experiments/cuts/synthetic.py` — `make_StayPut`, `make_Direct0`, `make_TermRelay`
- `experiments/cuts/run_e2.py`, `run_e4.py` — overrides de R, expectativas de gabarito
- **novos**: `verify_structure.py`, `bc_yspace.py`, `run_e6.py`
- **documentação**: `open-questions.md` (Q1), `base-formulation.md` (§10.1),
  `validacao-formulacao-base.md` (P1), `direcoes-pli-min-station.md` (§1.6, linha 612, B2),
  `RESEARCH.md`, `project-overview.md`, `resultados-e2-e4-pli.md`,
  `docs/technical/plans/plano-experimentos-e5.md`

Consulta, não alterar: `min-station-das.pdf`, `direcoes-pli-min-station.md` §3.1–§5.5,
`modelo_min_station_das_preprocess.py:921-956` (variante U já implementada),
`benders_min_station.py:400-505` (rede correta e padrão `nx.minimum_cut`).
