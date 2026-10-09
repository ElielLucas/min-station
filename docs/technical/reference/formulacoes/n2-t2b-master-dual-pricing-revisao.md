# N2-T2B — Master F-CC+K, dual, pricing e certificação (revisão matemática, v2.1)

**Estado:** `REVISED v2.1 — PARECER INCORPORADO; GATE M (APROVAÇÃO MATEMÁTICA PARA IMPLEMENTAÇÃO) PENDENTE`.
Este documento **não constitui autorização automática**. O parecer independente foi `ACCEPTED WITH CONDITIONS`,
**não** `ACCEPTED` irrestrito. As correções matemáticas estão incorporadas; a autorização para desenvolver o
algoritmo depende exclusivamente do **Gate M**, documental e anterior ao código (§11.1 e §12.1). O aceite
operacional da implementação é um **Gate O distinto e posterior** (§11.2 e §12.2): não é pré-requisito do Gate M.
Nenhum código de geração de colunas pode ser escrito antes do registro formal do Gate M.
**Escopo:** N2, caminho B (`F-CC + K`), **raiz apenas**, colunas `(W,I,J)`. Sem variante de trios, sem caminho A,
sem branch-and-price, sem novos cortes. Nenhum resultado N2 foi medido.
**Data:** 2026-10-09. **Branch:** `novos_testes`, HEAD `c995b54`.

**Rastreabilidade.**

| Item | Identificação |
|---|---|
| Parecer independente | [`parecer-independente-N2-T2B.md`](parecer-independente-N2-T2B.md), SHA-256 `32a62d416e994de1d58f31e1d3b3aa61bf8d365e223025273728d52b9559a888`, conteúdo original preservado byte a byte |
| Versão auditada pelo parecer (v1, 445 linhas) | SHA-256 `e7741dd27200aedea8a2e429f0f694797a4c1980f21bd3467708eceb5a4f314e` (nunca foi commitada e foi sobrescrita por esta v2; a cópia auditada é o anexo do revisor, identificada por este hash; a minuta de N2-T1 permanece no Git) |
| Verificador auditado | `verify_n2_t2b_algebra.py`, SHA-256 `69fbbd4e84cb14020b8e21e6d43af9977bb8e99ac29a0404329d31638ae3ad63`; esta versão acrescenta uma asserção de status e a lista de limites (§9) |
| Minuta anterior (N2-T1) | commit `c995b54` |

**Fontes lidas para identificar o objeto implementado** (não alteradas): `fcc.py`, `fcc_k.py`,
`experiments/cuts/harness.py`, `experiments/cuts/cuts.py`, `formulacao-fcc-configuracoes-conectadas.md`,
`provas-fcc-fc3.md` (P1, P2, P7, P10), `revisao-mr-f3-n1.md`, decisão N1-T7, pré-registro N2-T1, a spec N2 e o
parecer.

**Rótulos.** `Demonstrado` = derivação escrita verificável aqui, no parecer ou em prova já aceita. `Condicional` =
vale sob hipótese explicitada. `Pendente` = exige prova, implementação verificada ou decisão ainda não feita.
Verificações numéricas (§9) apoiam a ausência de erro algébrico; **não** promovem rótulos.

---

## 0. Objetos distintos (não confundir)

1. **Problema de Das (MIN-STATION):** `G=(V,E)` simples, conexo, não dirigido, unitário; `S,T⊆V`, `|S|=|T|=m≥1`,
   `S∩T` permitido; robôs não rotulados; autonomia comum `r≥1`; estações em todo `V`; minimizar `|C|`.
2. **Formulação-base (U):** não usada nem alterada aqui.
3. **F-CC+K (objeto experimental selecionado por N1-T7).**
4. **Master restrito (RMP):** F-CC+K com subconjunto das colunas. Restrição do LP completo, **não** relaxação.
5. **Resultados:** nenhum valor N2 foi medido; valores LP F-CC+K citados são referências históricas N1.
6. **Domínio da prova:** grafo unitário não dirigido. A extensão a dados ponderados ou dirigidos não é autorizada.

---

## 1. Conjuntos, parâmetros e domínio

- `H=(V,E_r)`, `E_r={{u,v}: u≠v, d_G(u,v)≤r}`. `N_H[v]={v}∪N_H(v)`.
- `D={(s,t)∈S×T : s=t ou d_G(s,t)≤r}`. Para `s∈S∩T`, `(s,s)∈D` (permanência, P10).
- Para `∅≠W⊆V`: `B(W)=W∪N_H(W)`, `S_W=S∩B(W)`, `T_W=T∩B(W)`.
- **Configurações:** `Q={(W,I,J) : ∅≠W⊆V, H[W] conexo, I⊆S_W, J⊆T_W, |I|=|J|≥1}`. Em `S∩T`, `s∈I` e `s∈J` são
  condições independentes; `(W,{s},{s})∈Q` quando `s∈B(W)` (coluna válida, dominada por `d_ss`).
- **Relé:** um vértice só recarrega terceiros se pertencer a `W`. Um terminal em `B(W)\W` é apenas extremo de seus
  próprios papéis. Não existe relé gratuito.
- **K:** a lista exata `prepare_k(S,T,V,adj,A_r,r)` = `prepare_cuts(...,{'C1','C2','C4'})` ordenada por
  `cortes_ordenados`, com hash SHA-256 por instância; cada `Z∈K` (não vazio) gera `Σ_{v∈Z}y_v≥1`. Escreve-se
  `κ(v)=Σ_{Z∈K:v∈Z}κ_Z`.
- **Validade de K (K0, Demonstrado no parecer C.4):** pela monotonicidade da viabilidade em `C`,
  `y(Z)≥1` é válida para todas as instalações inteiras `⇔ V\Z` é inviável. É isso que `is_valid_cut` decide.
  Não é preciso que o LP F-CC implique K (P3/P4 seguem `HYPOTHESIS` e não são usados).

## 2. Master primal completo `P_Q`

Variáveis: `λ_q≥0` (`q∈Q`), `d_st≥0` (`(s,t)∈D`), `0≤y_v≤1`. Sem limites superiores explícitos em `λ`, `d`.

\[
z_Q=\min\ \sum_{v\in V}y_v
\]
\[
\sum_{q:\,s\in I_q}\lambda_q+\sum_{t:(s,t)\in D}d_{st}=1\ (\forall s\in S)\tag{R1}
\]
\[
\sum_{q:\,t\in J_q}\lambda_q+\sum_{s:(s,t)\in D}d_{st}=1\ (\forall t\in T)\tag{R2}
\]
\[
\sum_{q:\,v\in W_q}\lambda_q-y_v\le 0\ (\forall v\in V)\tag{R3}
\]
\[
\sum_{v\in Z}y_v\ge 1\ (\forall Z\in K)\tag{K}
\]
\[
y_v\le 1\ (\forall v\in V)\ \text{(limite de variável)}\tag{UB}
\]

R3 está escrita como no código (`quicksum(...) <= y[v]`); não há termo `|W_q|λ_q` no objetivo (o custo é pago por
`y`). Tamanho: `2m+n+|K|` linhas.

**Limites implícitos (Demonstrado).** Como `|I_q|≥1`, R1 dá `λ_q≤1`; analogamente `d_st≤1`. Somando R1 sobre `S`:
\[
\sum_q\lambda_q+\sum_Dd_{st}\le\sum_qk_q\lambda_q+\sum_Dd_{st}=m,\quad k_q=|I_q|. \tag{M1}
\]
Somando R3 sobre `V` com `|W_q|≥1`:
\[
\sum_q\lambda_q\le\sum_q|W_q|\lambda_q\le\sum_v y_v. \tag{M2}
\]
Valem no master completo **e** no restrito. Não impor `ub` explícito em `λ`, `d` no RMP (exigiria tratar os
multiplicadores desses limites e custos reduzidos negativos de variáveis no limite).

**Factibilidade e finitude (Demonstrado).** `G` conexo e `r≥1` ⇒ `H` conexo ⇒ `(V,S,T)∈Q`. O ponto
`λ_{(V,S,T)}=1`, `d=0`, `y=1` é viável (K não vazio por construção). `Q` é finito; o objetivo é limitado por 0.
Master e RMP inicial têm ótimo finito e dualidade forte.

### 2.1 Correspondência com a implementação

**Divergência registrada.** `fcc_k.build_fcc_plus_k` usa `forma='separada'` (variáveis `Λ_W, α_sW, β_tW`,
`α,β≤Λ_W`, `Σα=Σβ`, sem CA5). Os LPs de referência N1-T5/T6 (23 controles; nível 1 do `n2-t1-freeze.json`) foram
calculados nessa forma. O master `P_Q` é a forma `qij`. São modelos diferentes com a mesma projeção em `y`.

**Proposição E1 (Demonstrado).** `z_Q` (`qij`+K+UB) = LP de `build_fcc_plus_k`.
*Prova.* P7 (`PROVEN`) dá a mesma projeção em `y`; K e UB só envolvem `y`; o objetivo só depende de `y`. ∎
*Reforço independente do passo poliédrico (parecer C.3, substitui o argumento de totalmente unimodular da v1):*
para `Λ_W>0`, normalize `(a,b)=(α,β)/Λ_W` em `P_W={(a,b)∈[0,1]^{|S_W|+|T_W|}: Σa=Σb}`. Um vértice de `P_W` tem
no máximo uma coordenada fracionária (uma única igualdade); com exatamente uma, a igualdade e as demais
coordenadas inteiras a tornariam inteira. Logo os vértices são as incidências `(1_I,1_J)` com `|I|=|J|`,
incluindo o par vazio. Decompor o ponto em vértices, multiplicar por `Λ_W` e **descartar** a massa do par vazio
preserva `α,β,d,y` e só diminui a soma de pesos que usa as estações de `W`. A volta (agregar colunas por `W`) é
imediata. As projeções em `(y,d)` coincidem.

**Consequências para o código N2.** (i) A regressão N2-T4 compara o master `qij` convergido com referência
calculada na forma `separada`; a igualdade vem de E1, não de identidade de código. (ii) O RMP deve ser montado em
`qij` com o mesmo `K` congelado (`prepare_k` + conferência de hash + `add_cuts_to_model`), sem alterar `fcc.py` nem
`fcc_k.py` e sem reutilizar `build_fcc_plus_k`. (iii) **Atenção à geração parcial:** restringir uma lista de
triplas `(W,I,J)` **não** é o mesmo que manter alguns `W` com todas as suas marginais livres (a forma `separada`
representa implicitamente todas as combinações elegíveis de um `W`). A equivalência dos modelos completos não
autoriza confundir os dois RMPs; o RMP N2 é sempre sobre triplas.

**Relação com OPT (Condicional a H-K).** `z_Q≤OPT`: para `C` ótimo, `y=1_C` estende-se a uma solução de F-CC (P1) e
satisfaz K se cada `Z∈K` for válido (K0). `assert_valid_cuts` verifica isso na montagem; N1-T3 testou 878
instalações sem divergência.

### 2.2 Master restrito `P_R`

Para `Q_R⊆Q`, `P_R` é `P_Q` com `Q`→`Q_R` em R1–R3, mantendo **todas** as `y`, `d`, o `K` e UB. Contém sempre
`(V,S,T)` e, opcionalmente, colunas locais válidas, sem fixar pareamento. K pode permanecer estático: toda coluna
de configuração tem coeficiente zero nas linhas K.

**Proposição R1 (Demonstrado).** `z_Q≤z_R`. *Prova:* toda solução de `P_R` completada com `λ_q=0` é viável em `P_Q`. ∎
**`z_R` não é LB.** O LB buscado é `z_Q`; `z_R` é cota **superior** de `z_Q` e pode exceder até OPT.
*Exemplo (Demonstrado).* Caminho `a–b–c`, `r=1`, `S={a}`, `T={c}`, `D=∅`, `K={{b}}`: `z_Q=OPT=1`; o RMP com
apenas `(V,S,T)` vale `3`. A frase "o RMP inicial vale `n`" só é verdadeira quando `D` não contém matching direto
perfeito: se contém, o valor pode ser zero. Portanto `z_R` é registrado apenas como `rmp_objective`.

---

## 3. Dual completo

Multiplicadores: `π_s,τ_t∈ℝ` (R1, R2; igualdades), `μ_v≥0` (R3 lida como `y_v-Σλ≥0`), `κ_Z≥0` (K), `η_v≥0`
(UB lida como `-y_v≥-1`).

\[
\max\ \Phi=\sum_s\pi_s+\sum_t\tau_t+\sum_Z\kappa_Z-\sum_v\eta_v
\]
\[
\pi(I_q)+\tau(J_q)-\mu(W_q)\le 0\ (q\in Q)\tag{D-λ}
\]
\[
\pi_s+\tau_t\le 0\ ((s,t)\in D)\tag{D-d}
\]
\[
\mu_v+\kappa(v)-\eta_v\le 1\ (v\in V)\tag{D-y}
\]

O dual do RMP impõe D-λ apenas em `Q_R`; D-d e D-y são completos.

**Derivação (Demonstrado).** Lagrangiano com igualdades como "1 menos atendimento" e desigualdades como "lado
direito menos esquerdo":
\[
\mathcal L=\Phi+\sum_q\bar c_q\lambda_q+\sum_D\bar c_{st}d_{st}+\sum_v\bar c_vy_v,
\]
e a finitude do ínfimo sobre variáveis não negativas exige cada coeficiente `≥0`: isso produz D-λ, D-d e D-y e
justifica os sinais (igualdade ⇒ livre; `≥` em `min` ⇒ `≥0`).

**Eliminação de `η` (Demonstrado).** Fixados `μ,κ`, a melhor escolha em D-y e no objetivo é
`η_v=max{0, μ_v+κ(v)-1}`. Define-se a função dual reduzida
\[
L(\pi,\tau,\mu,\kappa)=\sum_s\pi_s+\sum_t\tau_t+\sum_Z\kappa_Z-\sum_v\max\{0,\ \mu_v+\kappa(v)-1\}.
\]
Omitir `-Ση` superestima o dual sempre que algum `μ_v+κ(v)>1`. *Controle exato (Demonstrado):* caminho `a–b–c`,
`π_a=2, τ_c=0, μ_b=2, μ_a=μ_c=0, κ=0`; toda configuração contém `b`, logo `c*=0`; `η_b=1` e `L=1=z_Q`; sem `η`
daria 2, um falso LB acima de `OPT=1` (teste dirigido, §9).

### 3.1 Convenção do Gurobi (gurobipy 12.0.3 no venv do projeto)

Em `min`, `Pi≥0` em `≥`, `Pi≤0` em `≤`, livre em `=`, `RC_j=c_j-A_j^TPi`. Com R3 como no código:
`π_s=Pi(R1_s)`, `τ_t=Pi(R2_t)`, `μ_v=-Pi(R3_v)`, `κ_Z=Pi(K_Z)`. Com UB nativo, `η` **não** aparece em `Pi`; para
um certificado, `η` é **recalculado pela fórmula** a partir do vetor `(μ,κ)` já projetado. Usar ao mesmo tempo o
UB nativo e uma segunda penalização não é a derivação acima. Confirmado por teste (V2–V3); qualquer
implementação repete o teste, porque usar `Pi(R3)` como `μ` inverte o sinal de `μ(W)`.

### 3.2 Identidade primal-dual (Demonstrado)

Para qualquer `u=(π,τ,μ≥0,κ≥0,η≥0)` e qualquer `(λ,d,y)` viável em `P_Q`, com `σ_v=y_v-Σ_{q∋v}λ_q≥0`,
`σ_Z=y(Z)-1≥0`:
\[
\sum_vy_v-\Phi(u)=\sum_q\bar c_q\lambda_q+\sum_D\bar c_{st}d_{st}+\sum_v\bar c_vy_v+\sum_v\mu_v\sigma_v+\sum_Z\kappa_Z\sigma_Z+\sum_v\eta_v(1-y_v),\tag{ID}
\]
\[
\bar c_q=\mu(W_q)-\pi(I_q)-\tau(J_q),\quad\bar c_{st}=-\pi_s-\tau_t,\quad\bar c_v=1-\mu_v-\kappa(v)+\eta_v .
\]
A expansão cancela os coeficientes auxiliares por R1/R2 e vale **sem** factibilidade dual. Com `u` dual-factível,
todos os termos à direita são `≥0`: dualidade fraca. No ótimo, todos se anulam (folgas complementares).

---

## 4. Custo reduzido

\[
\boxed{\ \bar c(W,I,J)=\sum_{v\in W}\mu_v-\sum_{s\in I}\pi_s-\sum_{t\in J}\tau_t\ }
\]

R1 contribui `-π_s` por origem; R2, `-τ_t` por destino; R3, `+μ_v` por estação de `W`. K e UB não incidem em `λ` e
contribuem zero diretamente; agem por D-y e por `L`. Custo objetivo de `λ`: 0. Orientação: `min`; entra se
`\bar c_q<-ε_in`. D-λ é exatamente `\bar c_q≥0` (Demonstrado; conferido contra `RC` do Gurobi em V3).
Em degeneração, inserir coluna com `\bar c<0` não garante queda estrita do objetivo na reotimização seguinte: o
teste de sinal é correto; a promessa de ganho imediato não é.

---

## 5. Problema de pricing

Dado `(π,τ,μ)` com `μ≥0`: `c^*(π,τ,μ)=min_{q∈Q}\bar c_q`. Nenhuma restrição é acrescentada ou removida em relação
a `Q`: conectividade em `H`, `W≠∅`, elegibilidade por `B(W)` fechado, `|I|=|J|≥1`, papéis separados em `S∩T`,
pareamento livre (não há matching fixado).

### 5.1 Forma fechada por `W` (Demonstrado)

Com `k_W=min(|S_W|,|T_W|)` (sem coluna se `k_W=0`) e listas em ordem decrescente `π_{(1)}≥…`, `τ_{(1)}≥…`:
\[
\min_{I,J}\bar c(W,I,J)=\mu(W)-\max_{1\le k\le k_W}\big(\operatorname{Top}_k(\pi;S_W)+\operatorname{Top}_k(\tau;T_W)\big)
=\mu(W)-\Big[(\pi_{(1)}+\tau_{(1)})+\sum_{k=2}^{k_W}\max\{0,\pi_{(k)}+\tau_{(k)}\}\Big].
\]
*Prova.* Para `k` fixo, `I` e `J` só se ligam por `|I|=|J|=k`; o máximo é a soma dos `k` maiores de cada lista
(inclusive negativos). `f(k)=Σ_{i≤k}(π_{(i)}+τ_{(i)})` tem incrementos não crescentes, logo é côncava; o máximo
com `k≥1` toma o primeiro incremento (obrigatório) e os incrementos positivos seguintes. Não se pode descartar
prêmios negativos de forma indiscriminada. ∎ (V4.)

### 5.2 Formulação MIP de pricing (P0–P5) e sua exatidão

Binárias `x_v,ρ_v,a_s,b_t`; contínuas `g_v≥0`, `f_{uv}≥0` nos dois sentidos de cada aresta de `H` (`A_H`);
`n=|V|`:
\[
c^*=\min\ \sum_v\mu_vx_v-\sum_s\pi_sa_s-\sum_t\tau_tb_t\tag{P0}
\]
\[
a_s\le\sum_{v\in N_H[s]}x_v\ (s\in S),\quad b_t\le\sum_{v\in N_H[t]}x_v\ (t\in T)\tag{P1}
\]
\[
\sum_sa_s=\sum_tb_t,\quad\sum_sa_s\ge1\tag{P2}
\]
\[
\sum_v\rho_v=1,\quad\rho_v\le x_v,\quad0\le g_v\le n\rho_v\tag{P3}
\]
\[
g_v+\sum_{u:(u,v)\in A_H}f_{uv}-\sum_{w:(v,w)\in A_H}f_{vw}=x_v\ (v\in V)\tag{P4}
\]
\[
0\le f_{uv}\le(n-1)x_u,\quad f_{uv}\le(n-1)x_v\ ((u,v)\in A_H)\tag{P5}
\]
O fluxo é certificado auxiliar de conectividade, não fluxo de robôs, e não precisa ser inteiro.

**Proposição P-PROJ (Demonstrado; substitui a "bijeção" da v1, R-06).** Vale a igualdade por **projeção**
\[
\operatorname{proj}_{x,a,b}\{\text{soluções inteiras viáveis de P1–P5}\}=\{(1_W,1_I,1_J):(W,I,J)\in Q\}.
\]
A correspondência **não** é bijetiva: raiz e fluxo não são únicos (no grafo de dois vértices ligados, `W=V` admite
as duas raízes; em grafos com ciclos há várias árvores).
*(⇒)* Com `W={x=1}`, `I={a=1}`, `J={b=1}`: P3 dá uma única raiz em `W`, logo `W≠∅`; P1 dá `I⊆S∩B(W)`,
`J⊆T∩B(W)`; P2 dá `|I|=|J|≥1`. Se `H[W]` fosse desconexo, uma componente `U⊆W` sem a raiz teria, somando P4
sobre `U`, os fluxos internos cancelados, nenhum fluxo cruzando entre componentes (não há aresta) nem entre `W` e
não selecionados (P5), e `g=0` em `U` (P3): `0=Σ_{v∈U}x_v=|U|>0`, contradição. Logo `(W,I,J)∈Q`.
*(⇐)* Para `(W,I,J)∈Q`, `k=|W|`: raiz `v_0∈W`, árvore geradora de `H[W]`; `g_{v_0}=k`, demais `g=0`; em cada
arco pai→filho envie o tamanho da subárvore do filho, zero nos demais. Cada arco leva `≤k-1≤n-1`, `g_{v_0}=k≤n`;
P4 vale. Cobre `|W|=1` e `n=1` (`g=1`, sem arcos). O objetivo P0 é `\bar c(W,I,J)`. ∎
A quebra de simetria `ρ_v+x_u≤1` (`u<v`) é válida (toda configuração tem uma menor estação que pode ser raiz) e
também não cria bijeção. Em `S∩T` existem `a_s` e `b_s` independentes; o par `d_ss` permanece no master; terminal
fora de `W` é extremo elegível, nunca relé gratuito; não se exige `I=J`, nem terminais em `W`, nem uma só
componente na instalação global. Testado exaustivamente em instâncias minúsculas (§9, `ControlesProjecaoPricing`).

**Tamanho.** `2n+|S|+|T|` binárias, `n+2|E_r|` contínuas. Para `r` grande `H` é denso; a spec proíbe reduzir `H`
sem prova.

**Complexidade (Demonstrado, sobre vetores arbitrários).** Com `r=1`, `S=T=V`, `π=τ≡M` (`2M>n-1`), `μ≡1`,
`\bar c=|W|-2M|B(W)|` e o mínimo é `|W^*|-2Mn`, `W^*` conjunto dominante conexo mínimo (NP-difícil). Esses
vetores **violam D-d** nos pares de permanência, logo **não** se demonstra dureza para a subfamília de duais
factíveis do RMP; essa ressalva é parte do enunciado. (V7.)

### 5.3 Heurística versus oráculo certificador

Uma heurística de pricing (gulosa, enumeração truncada, MIP sem bound global verificado) **só** acrescenta colunas
com `\bar c<-ε_in` e nunca fundamenta ausência de coluna melhorante (story 2B AC4). Toda coluna proposta por
qualquer rota é **conferida combinatoriamente** (pertinência a `Q`) antes de entrar no master. Um **oráculo
certificador** é um procedimento que devolve `ℓ≤c^*(π,τ,μ)` com demonstração de que `ℓ` cobre **todo** `Q`
(inclusive colunas já no RMP) **e** que é avaliado de modo seguro (§6.3). O valor de uma coluna encontrada satisfaz
o sentido oposto, `c^*≤\bar c(q)`, e **nunca** serve como `ℓ` (contraexemplo em §6.1).

---

## 6. Certificação do limite inferior

### 6.1 Teorema L (Demonstrado; D-1 `ACCEPTED` no parecer)

**Convenção (L0, R-04).** Para `π,τ` quaisquer, `μ≥0`, `κ≥0` finitos e `ℓ≤c^*(π,τ,μ)` (mesmo vetor):
\[
a=\min\{0,\ell\},\qquad \delta=\min\Big(\{0\}\cup\{-\pi_s-\tau_t:(s,t)\in D\}\Big),
\]
de modo que `δ=0` quando `D=∅` (sem a união, a fórmula só valeria adotando, sem declarar, `min ∅=+∞`).
`L` como em §3, com `η_v=max{0,μ_v+κ(v)-1}`. Então
\[
\boxed{\ z_Q\ \ge\ LB_{CG}:=\max\Big\{0,\ \ L+m\min\{a,\delta\},\ \ \frac{L+m\,\delta}{1-a}\Big\}\ }\tag{L1}
\]
e, sob H-K, `LB_{CG}≤z_Q≤OPT`.

*Prova.* Seja `(λ,d,y)` **qualquer** ponto viável de `P_Q`, `A=Σλ_q`, `B=Σd_st`, `z=Σy_v`. Por (M1) `A+B≤m`; por (M2)
`A≤z`. Por (ID) com a escolha de `η` (que dá `\bar c_v≥0`), todos os termos além dos custos reduzidos de `λ` e `d`
são `≥0`; com `\bar c_q≥ℓ≥a`, `\bar c_{st}≥δ` e `λ,d≥0`:
\[
z\ge L+aA+\delta B.\tag{L4}
\]
(a) Como `a,δ≤0`: `aA+δB≥min(a,δ)(A+B)≥m·min(a,δ)`. (b) Por `A≤z`, `B≤m`: `aA+δB≥az+mδ`, logo
`z(1-a)≥L+mδ`, com `1-a≥1`. (c) `z≥0`. Vale para todo ponto viável, logo para `z_Q`. Nenhum uso de dualidade
forte. Sob H-K, toda instalação física viável se estende a um ponto do master (P1), logo `z_Q≤OPT`. ∎

**Hipóteses necessárias.** `π,τ` finitos livres; `μ,κ` finitos não negativos; `ℓ` finito **comprovado** para o
mesmo vetor `(π,τ,μ)`; `L` com a penalização de UB; H-K. **Não** exigem: RMP ótimo, factibilidade dual nas
colunas do RMP, solução completa do pricing, nem `π_s+τ_t≤0` (a violação é o que `δ` paga). A cobertura global de
`ℓ` **não pode** ser removida.

**Observações.** (i) `(b)` é análogo ao limite de Farley, obtido por (M2); não é a lagrangiana da baseline antiga
(story 3 AC3). (ii) Nenhum dos ramos domina. (iii) Se `ℓ≥0` e `δ=0`, `LB_{CG}=max{0,L}`; com RMP ótimo e pricing
exato, `L=z_R=z_Q`. (iv) **Corrigida (R-02).** A afirmação da v1, "`ℓ∈[-ε,0)` ⇒ `LB_{CG}≥L-mε`", é **falsa** sem
controlar `δ`. *Contraexemplo (Demonstrado):* dois vértices `a,b` ligados, `r=1`, `S=T={a}`, `K=∅`, `D={(a,a)}`,
`z_Q=OPT=0`; `π_a=1, τ_a=0, μ_a=1-ε/2, μ_b=1`: `L=1`, `ℓ=-ε/2`, `δ=-1`, `LB_{CG}=0`, mas `L-mε=1-10^{-6}>0`.
**Versão correta:** se `ℓ≥-ε` **e** `δ≥-γ`, então `LB_{CG}≥max{0, L-m·max(ε,γ)}`. O caso usual de dual exato do
RMP tem `δ=0`, mas isso não pode ser presumido para todos os vetores que o teorema admite. (v) Multiplicadores do
Gurobi com sinal ligeiramente errado são projetados (`μ←max{0,μ}`, `κ←max{0,κ}`) **antes** do pricing; `L`, `δ`,
`ℓ`, `η` usam exatamente o mesmo vetor projetado.

**Contraexemplo ao uso de busca parcial como `ℓ` (Demonstrado).** Caminho `a–b–c`, `S={a}`, `T={c}`, `K={{b}}`,
`z_Q=OPT=1`; `π_a=3, τ_c=0, μ≡1, κ=0` (dual ótimo do RMP `{(V,S,T)}`, `L=3`). Os `W` válidos `{b},{a,b},{b,c},V`
têm custos `-2,-1,-1,0`. Uma busca restrita a `V` devolve `0`, que é cota **superior** de `c^*`; usá-lo como `ℓ`
dá o falso certificado `3>OPT`. O valor global `ℓ=-2` dá `LB_{CG}=1`. (Teste dirigido, §9.)

### 6.2 Hipóteses e como verificá-las

| Hipótese | Uso | Verificação |
|---|---|---|
| H-K: todo `Z∈K` válido | `z_Q≤OPT` | `assert_valid_cuts` na montagem; hash de K igual ao congelado; K0 |
| H-P7: projeção em `y` igual | regressão contra referência `separada` | P7 `PROVEN`; E1 |
| H-SIGN: convenção de sinais | `μ`, `κ`, `η` corretos | V2/V3 e controle de `η>0` antes de medir |
| H-COV: o oráculo cobre todo `Q` | `ℓ≤c^*` | ENUM: enumeração completa (§6.3); N1/N2: prova abaixo |
| H-ARIT: avaliação segura | `L`, `δ`, `ℓ`, `LB` | racionais exatos ou intervalos com arredondamento dirigido (§6.3) |

### 6.3 Oráculos de `ℓ` e política de certificação

**Princípio.** Para o rótulo `CERTIFIED` não basta um número `ℓ` fornecido por um solver em ponto flutuante: é
preciso **demonstrar `ℓ≤c^*`** e **avaliar com segurança** `L`, `δ`, `ℓ` e `LB_{CG}`.

**(ENUM) Enumeração completa com aritmética exata — elegível a `CERTIFIED`.** Contrato (R-05):

1. Rejeitar NaN e infinitos; registrar o vetor recebido sem perda (hexadecimal ou pares numerador/denominador).
2. Converter cada float finito ao racional binário exato; impor exatamente `μ←max(0,μ)`, `κ←max(0,κ)`.
3. Fixar **um único vetor** racional para a iteração: `L`, `δ` e `ℓ` usam o **mesmo** vetor pós-projeção. Nunca misturar
   `L` pré-projeção com custos reduzidos pós-projeção, nem usar `ℓ` de outra iteração.
4. Recalcular `κ(v)`, `η`, `L`, `δ`, todos os prêmios e todos os custos reduzidos (inclusive a ordenação TopK, ou
   decisão exata/por intervalos de quais termos entram) em aritmética exata; o `\bar c` do solver não é usado.
5. Enumerar **todos** os conjuntos conexos de `H`, sem exclusões não demonstradas. **Cobertura:** o certificado
   registra `truncated=False` com cap estritamente maior que o total (`enumerar_conexos` devolve `True` também
   quando o cap é atingido exatamente; isso é conservador). Cap atingido ⇒ **sem certificado**. Em enumeração
   parcial, o mínimo visitado é cota **superior** de `c^*`.
6. Calcular `ℓ=min_Q\bar c` e `LB_{CG}` (L1) em racionais; `1-a≥1`, o denominador é sempre positivo.
7. Preservar o racional final no certificado. Ao exportar para decimal ou float, arredondar **para baixo**
   (arredondamento dirigido), não pela conversão usual. Com intervalos, publicar a extremidade inferior de um
   enclosure de toda a expressão; soma de floats seguida de arredondamento isolado não limita o erro acumulado.
8. `⌈LB-10^{-6}⌉` (convenção congelada) só para `LB` certificado; é válido porque `OPT∈ℤ`; não valida um LB
   anteriormente não certificado.

Pode-se usar floats para: resolver o RMP, propor multiplicadores, heurísticas de pricing e ordem de exploração,
tempo/Work/gráficos. Não para `L`, `δ`, `ℓ`, `LB` que sustentam `CERTIFIED`. Elegibilidade e conectividade de `H`
no problema unitário usam distâncias inteiras.

**(N1) Limite analítico (Demonstrado; implementação pendente).**
\[
\ell_{N1}=\min_{v\in V}\mu_v-\max_{1\le k\le m}\big(\operatorname{Top}_k(\pi;S)+\operatorname{Top}_k(\tau;T)\big)\ \le\ c^*.
\]
*Prova.* Para `q=(W,I,J)`, `W≠∅` e `μ≥0` dão `μ(W)≥min_vμ_v`; com `|I|=|J|=k≤m`, `π(I)≤Top_k(π;S)` e
`τ(J)≤Top_k(τ;T)`. ∎ Válido em qualquer tamanho; **fraco** no caso geral.

**(N2) Limite de relaxação com caixa (Demonstrado; implementação pendente).** Escreva P0–P5 como
`min c^Tw` sujeito a `Aw=b` (igualdades), `Bw≥h`, `0≤w≤u` (`u=1` nas binárias relaxadas, `n` em `g`, `n-1` em `f`).
Para `θ` livres e `ν≥0` racionais **quaisquer**:
\[
\ell_{N2}=\theta^Tb+\nu^Th+\sum_ju_j\min\{0,\ c_j-(A^T\theta)_j-(B^T\nu)_j\}\ \le\ z_{LP(\text{pricing})}\le c^*.
\]
*Prova.* Para `w` viável: `c^Tw=(c-A^T\theta-B^T\nu)^Tw+\theta^TAw+\nu^TBw\ge(c-A^T\theta-B^T\nu)^Tw+\theta^Tb+\nu^Th`
(`Aw=b`, `Bw≥h`, `ν≥0`), e `(c-\dots)^Tw\ge\sum_ju_j\min\{0,c_j-\dots\}` porque `0≤w_j≤u_j`. Como `Q` projeta no
conjunto das soluções inteiras (P-PROJ), `ℓ_{N2}≤c^*`. ∎ Os multiplicadores podem vir de um solver em ponto
flutuante e ser tratados como racionais exatos; **não** precisam ser duais ótimos (a caixa paga a violação), mas
matriz, objetivo e limites usados na verificação devem ser os do modelo racional original. Cobertura global: o
modelo contém todo `Q` (P-PROJ). **Validade ≠ utilidade (R-07):** a relaxação do fluxo com big-M é fraca; nada aqui
prevê se `ℓ_{N1}` ou `ℓ_{N2}` produzem `LB_{CG}>B0`.

**(MIP) MIP numérico — `UNCERTIFIED` (R-01, rejeitado como certificado autossuficiente).** `ObjBound`, `ObjBoundC`,
status `OPTIMAL`, `MIPGap=0` ou uma margem fixa subtraída **não** demonstram `ℓ≤c^*`: as tolerâncias de
factibilidade, integralidade e otimalidade do solver não fornecem uma desigualdade global `|b-c^*|≤ε_ℓ`, e não há
no repositório um erro absoluto `E` demonstrado com `b-E≤c^*` (por isso não se adota margem: D-2 do v1 é
descartado, não "decidido com margem"). Recalcular exatamente o objetivo de um incumbente dá cota **superior** e
não verifica os nós descartados. O MIP **pode** gerar colunas e diagnósticos (conferidas combinatoriamente, §5.3).
`ObjBoundC` é preferível a `ObjBound` apenas para **registro** do candidato numérico (a documentação do Gurobi
distingue o fortalecimento por objetivo inteiro, que aqui não vale: os coeficientes são duais reais); isso é
informação do parecer (referências G1–G3), **não** reverificada nesta revisão, e não transforma o candidato em
prova. Um MIP só passa a produzir `CERTIFIED` por um dos caminhos N1/N2 aplicados a multiplicadores exatos, ou por
um certificado verificável que cubra todos os nós; hoje nenhum está definido.

| Ramo | Condição | Status de `LB_{CG}` |
|---|---|---|
| ENUM completo, vetor único racional (ou intervalos rigorosos), cap > total, exportação para baixo | contrato acima cumprido e implementado | **elegível a `CERTIFIED`** |
| Limite analítico N1 | implementação e verificação rigorosa da derivação (aritmética exata) | `Condicional`: `CERTIFIED` só após implementar, verificar e registrar |
| Limite de relaxação N2 | idem, com `θ,ν` racionais e modelo racional original | `Condicional`: idem |
| MIP numérico sem bound global verificado | `ObjBound`/`ObjBoundC`/status/margem | **`UNCERTIFIED`** (colunas e diagnóstico apenas) |
| Pricing heurístico, enumeração truncada | qualquer | `UNCERTIFIED` |
| `z_R`, `L` com `ℓ` não comprovado | qualquer | estimativa heurística: diagnóstico, nunca em coluna de LB |

### 6.4 Regra de certificação para N2-T3

Por iteração `k`, com multiplicadores `u_k`:

1. Se um oráculo elegível (tabela acima) forneceu `ℓ_k` **e** a avaliação foi segura: calcular `LB_{CG}(u_k,ℓ_k)`;
   a linha é `CERTIFIED` com justificativa que nomeia o ramo (`ENUM`, `N1` ou `N2`), `ℓ_k`, `δ`, `L`, o ramo do
   máximo usado, `truncated=False`, e o vetor racional.
2. O **limite certificado corrente** é o máximo sobre iterações certificadas (máximo de limites válidos é válido).
   Não é o `z_R` da última iteração.
3. Iterações com pricing heurístico ou MIP numérico não geram limite e não alteram o corrente.
4. **Interrupção** (WorkLimit total, parede, memória, falha de solver ou de pricing): conservar **somente** limites
   previamente certificados e suas evidências; um `ℓ` novo só vale se sua validade global já estiver verificada.
   Sem nenhum limite certificado, `UNCERTIFIED`. Um `ObjBound` finito de MIP interrompido **não** certifica.
5. O resultado final é `CERTIFIED` ou `UNCERTIFIED` (a spec não admite outro rótulo na coluna), sempre com campo
   de justificativa não vazio.
6. Inteiro: `⌈LB-10^{-6}⌉` só para `LB` certificado.

Três categorias, nunca agregadas: **certificado** (§6.3, ramo elegível); **estimativa heurística** (`z_R`, `L`
com `ℓ` não comprovado, `ObjBound` numérico); **ausência de certificação**.

### 6.5 Convergência do valor do LP (R-03)

Certificar um limite e declarar convergência são afirmações distintas. Seja `U` o custo de uma solução primal do
RMP **cuja viabilidade foi verificada**; como é viável também em `P_Q`:
\[
LB_{CG}\le z_Q\le z_R\le U.\tag{G1}
\]
**Critério certificado de convergência:**
\[
\boxed{\,U-LB_{CG}\le\varepsilon_{\rm abs}\,},\quad\varepsilon_{\rm abs}=10^{-6}\ \text{(tolerância congelada)}.\tag{G2}
\]
O teste `ℓ≥-10^{-6}` **isolado não** é critério: (1) o teorema admite multiplicadores arbitrários; no caminho
`a–b–c` o vetor nulo tem `ℓ=δ=L=0` e o RMP `{(V,S,T)}` vale 3 contra `z_Q=1`; (2) mesmo com dual ótimo do RMP,
`δ=0`, `L=z_R`, só se obtém `z_R-z_Q≤mε`, não `ε`. Sem `U` validado pode existir `LB_{CG}` certificado sem
certificado de convergência. Um `ObjVal` quase viável **não** é cota superior exata sem verificar resíduos ou
reconstruir uma solução viável. Para a **regressão N2-T4** (numérica, não certificação): `|z_R-z_ref|≤10^{-6}` e
`LB_{CG}≤z_ref+10^{-6}`; ambos são conferências, e a primeira não substitui G2. Se a parada do laço for decidida
sem G2, a linha registra `convergence_status=NUMERIC_UNCERTIFIED`.

### 6.6 `B0`

`B0=max(LP COMP, core IP)` é registrado em campo e justificativa próprios; o ganho é `LB_{CG}-B0`. Um fallback `B0`
é limite para o **MIN-STATION**, mas **não** necessariamente para o LP completo F-CC+K (decisão N1-T7: `Tri` tem
`B0=OPT=2` e LP F-CC+K `=1,5`); portanto um fallback `B0` **nunca** é comparado a `z_Q` nem entra em `LB_{CG}`. Se o
core IP for interrompido, seu incumbente é cota superior do core, não LB: só o ótimo comprovado ou cota inferior
validada do core compõe `B0`; valor parcial não é rebatizado de `B0`. A certificação de `B0` no nível 2 é
`Pendente` (N2-T3; fora desta derivação).

---

## 7. Compatibilidade com escopo e critérios da N2

- Story 2B AC1–AC5: primal, dual, custo reduzido, pricing (conectividade em `H`, `S_W/T_W`, balanço, linhas de
  ligação, duais de K), rótulos exato/heurístico, colunas iniciais viáveis, sem branching. AC6 (trios): não se aplica.
- Story 3 AC1–AC6: `z_R` nunca é LB; regra §6.4; limite derivado específico (Teorema L), não a lagrangiana antiga;
  interrupção §6.4-4; nenhuma simplificação proibida (TopK e P0–P5 têm prova de exatidão).
- Story 4: `LB_{CG}≤z_Q` (Teorema L); `z_Q` ligado às referências `separada` por E1.
- Pré-registro N2-T1: compatível com "CERTIFIED only with full exact pricing dual feasibility **or an independently
  reviewed globally valid derived bound**"; o Teorema L é esse limite e depende do registro de aprovação.
- **Correção (R-07).** A v1 afirmava que, acima do cap de enumeração, "só (M) certifica". Isso não é consequência
  matemática: qualquer `ℓ≤c^*` **demonstrado** serve (N1, N2). Mas validade não é utilidade. **Risco científico
  declarado:** no nível 2 a enumeração é inviável; se nem N1 nem N2 forem implementados e verificados, as linhas do
  nível 2 serão `UNCERTIFIED` e o gate resulta em `N2 FAIL` por ausência de certificado (stop criterion da spec);
  se forem, o LB certificado pode ser fraco. Nenhum dos dois desfechos altera arquitetura, pré-registro ou
  caminho; nenhum ajuste posterior é permitido para evitar `N2 FAIL`.

---

## 8. Auditoria e matriz de rastreabilidade

### 8.1 Minuta de N2-T1 → v1 (já incorporado)

A1 forma `qij` vs `separada`; A2 `η` e UB; A3 sinal de R3; A4 dual só `ε`-factível; A5 regra sob pricing
incompleto; A6 RMP ótimo não necessário; A7 `B0` separado; A8 oráculos exatos e complexidade; A9 sem `ub` em
`λ,d`; A10 semântica de relé; A11 H-K; A12 tolerâncias do solver. Todas sem mudança de arquitetura.

### 8.2 Parecer independente → v2

| ID | Gravidade | Achado | Incorporação (seção) | Estado |
|---|---|---|---|---|
| R-01 | Bloqueante p/ MIP | `ObjBound`/status ótimo levado a `CERTIFIED` sem H-NUM | §5.3, §6.3 (ramo MIP e tabela), §6.4-4, §11 | **Incorporada**; MIP numérico = `UNCERTIFIED`; N1/N2 pendentes de implementação |
| R-02 | Importante | observação (iv) omite `δ` | §6.1 (iv): contraexemplo e versão com `δ≥-γ`; teste dirigido | **Incorporada** |
| R-03 | Importante | parada por `ℓ≥-10^{-6}` não dá gap absoluto | §6.5 (G1, G2, `NUMERIC_UNCERTIFIED`); teste dirigido | **Incorporada**; validação de `U` pendente (P-4) |
| R-04 | Importante | `δ` com `D` vazio | §6.1 (L0); teste dirigido | **Incorporada** |
| R-05 | Importante antes de ENUM | aritmética racional sem contrato | §6.3 (ENUM: 8 itens); teste dirigido | **Incorporada** como contrato; implementação pendente (P-1) |
| R-06 | Secundário | "bijeção" falsa no MIP | §5.2 (P-PROJ, duas provas); teste exaustivo | **Incorporada** |
| R-07 | Importante | "só M certifica acima do cap" | §6.3 (N1, N2), §7; testes de validade | **Incorporada**; utilidade = pendente (P-3) |
| R-08 | Secundário | argumento TU por menores 2×2 | §2.1 (argumento de vértices) | **Incorporada** |
| R-09 | Secundário | "RMP inicial vale `n`" | §2.2 (condição e exemplo `a–b–c`) | **Incorporada** |
| R-10 | Importante p/ validação futura | verificador em floats e amostras aleatórias | §9 (limites, asserção de status, controles dirigidos) | **Incorporada** em parte: controles feitos; regressão nos 23 controles N1 é pós-implementação |

**Condições do parecer:** (a) corrigir regra de `ObjBound` — feito (R-01); (b) L0 — feito; (c) observação (iv) —
feito; (d) G2 — feito; (e) contrato ENUM — feito no texto, implementação pendente; (f) projeção do MIP — feito;
(g) validade vs utilidade — feito; (h) `ACCEPTED WITH CONDITIONS` **não** convertido em `ACCEPTED`.

---

## 9. Verificação auxiliar (não é medição N2)

**`experiments/alternative-formulations/verify_n2_t2b_algebra.py`** (Gurobi 12.0.3, `PYTHONHASHSEED=0`, semente
`20261009`): 60 instâncias aleatórias com `n≤8`, `m≤3`, `r∈{1,2}`, fora do corpus N2-T1; V1 (E1/P7), V2 (sinais,
`L`=`z`), V3 (custo reduzido = `RC`), V4 (TopK = força bruta), V5 (`LB_{CG}≤z_Q`, inclusive duais de RMPs
aleatórios), V6 (MIP = enumeração), V7 (redução). Resultado: `PASS`. **Limites (parecer D.2):** usa floats e
otimização; é regressão, não prova; não testa bound de MIP interrompido, `ℓ<c^*` deliberado, enumeração
truncada, exportação racional nem a observação (iv); `eta_pos=0` nas 60 instâncias; as contagens de casos estritos
variam com base/dual do solver e nenhuma asserção depende delas; remover UB não alterou o LP (isso não prova
redundância). Nesta versão, V1 também assere `Status==OPTIMAL` do modelo `separada`.

**`experiments/alternative-formulations/test_n2_t2b_controles_matematicos.py`** (novo; `unittest`; aritmética em
`Fraction`; instâncias minúsculas definidas no arquivo). Cobre os controles da seção D.3 do parecer:

| Controle | Teste |
|---|---|
| `D=∅`, `δ=0`, custos `{-2,-1,-1,0}`, `LB=1` | `test_D_vazio_delta_zero_e_custos_reduzidos`, `test_pricing_completo_certifica_um_e_busca_parcial_falsifica` |
| Pricing parcial inválido produz certificado falso `3>OPT` | idem |
| Permanência com `δ<0` (observação (iv)) | `ControlePermanencia` |
| `η>0` necessário | `test_eta_positivo_e_necessario` |
| RMP acima de OPT (`3` vs `1`) | `test_rmp_acima_do_lp_completo_e_convergencia_g2` |
| Parada com vetor zero; G2 recusa; G2 aceita após a coluna `({b},{a},{c})` | `test_parada_com_vetor_zero_nao_e_convergencia`, `test_rmp_acima…` |
| Cobertura ENUM, cap atingido não certifica | `ControlesEnumeracao`, `test_enum_truncado_nao_certifica` |
| Float exato, projeção, NaN/inf, exportação para baixo, arredondamento inteiro | `ControlesAritmetica` |
| N1 e N2 válidos (`ℓ≤c^*`) em racionais, com multiplicadores arbitrários e duais do LP | `ControlesLimitesGlobais` |
| Projeção do pricing: `W` unitário, `W` desconexo, conectividade via terminal, terminal fora de `W`, `S∩T`, `n=1`, incidências fixadas, exaustivo | `ControlesProjecaoPricing` |

**Evidência reproduzida no ambiente do pesquisador (2026-10-09):** comando
`PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p test_n2_t2b_controles_matematicos.py -v`;
**18 testes `OK`, 0 ignorados, 2,612 s**, com `gurobipy` disponível. Saída fornecida pelo pesquisador; não foi
reexecutada nesta atualização documental. Sem `gurobipy`, o teste possui controles em Python puro e pode ignorar
8 testes (`skipped=8`). `test_n2_t1_offline.py`: 7 testes `OK`; `run_n2_t1.py check`: `PASS` nos controles
anteriores. Esses testes sustentam o **Gate M como evidência auxiliar**, mas **não** substituem a aprovação
matemática nem a verificação contra a futura implementação, tampouco a regressão prospectiva nos 23 controles N1
(N2-T4).

## 10. Classificação dos resultados

| Resultado | Rótulo |
|---|---|
| Master `P_Q`: domínios, (M1), (M2), factibilidade com `(V,S,T)` | Demonstrado |
| E1: `z_Q` (`qij`) = LP `build_fcc_plus_k` (`separada`) | Demonstrado (P7 `PROVEN`; argumento de vértices) |
| `z_Q≤OPT` | Condicional a H-K |
| `z_R≥z_Q`; `z_R` não é LB | Demonstrado |
| Dual, eliminação de `η`, identidade (ID) | Demonstrado |
| Convenção de sinais do Gurobi 12.0.3 | Condicional (verificada empiricamente; repetir no código) |
| Custo reduzido; forma TopK | Demonstrado |
| P-PROJ: exatidão do MIP P0–P5 por projeção | Demonstrado |
| NP-dificuldade (vetores arbitrários) | Demonstrado; não vale para a subfamília de duais factíveis |
| Teorema L com L0 (ramos a, b, c) | Demonstrado (D-1 `ACCEPTED` no parecer); aprovação formal Pendente |
| `ℓ_{N1}≤c^*`; `ℓ_{N2}≤c^*` | Demonstrado; **implementação verificada: Pendente** |
| Certificação ENUM | Condicional a H-K, H-COV (cap>total) e contrato de aritmética exata; implementação Pendente |
| Certificação N1/N2 | Condicional; só após implementação, verificação e registro |
| Certificação por `ObjBound`/status/margem de MIP | **Não autorizada** (`UNCERTIFIED`) |
| G2 (convergência certificada) | Demonstrado como critério; validação de `U` Pendente |
| Utilidade de `LB_{CG}` (força, custo, escala) | Pendente (sem evidência; decide o gate N2) |
| Certificação de `B0` no nível 2 | Pendente (N2-T3) |

## 11. Dois gates independentes: autorização matemática e aceite operacional

**Regra de precedência, sem dependência circular:**

```text
N2-T1 FROZEN (já concluída)
    ↓
Revisão matemática v2.1 + parecer independente + controles prévios
    ↓
GATE M: decisão humana documentada de autorização matemática para implementação
    ↓ (somente se APROVADO; respeitando o escopo autorizado)
N2-T2B: desenvolvimento do master restrito, pricing e geração de colunas na raiz
    ↓
GATE O: aceite operacional da implementação N2-T2B
    ↓
N2-T3: certificação e evidências por instância
    ↓
N2-T4: regressão prospectiva dos 23 controles N1
    ↓
N2-T5: medições pré-registradas → N2-T6: gate científico
```

**O Gate M não depende do código que autoriza construir.** A validade matemática demonstrada, o escopo seguro e
as decisões de certificação vêm primeiro; conformidade do software com essas definições se verifica depois, no
Gate O e nas tarefas seguintes. `ACCEPTED WITH CONDITIONS` é evidência para decidir, não decisão automática.

### 11.1 Gate M — Aprovação matemática para iniciar código (pré-implementação)

Todos os itens abaixo são avaliáveis **sem implementar ou medir a N2**:

| ID | Condição de autorização | Evidência/estado nesta versão |
|---|---|---|
| M-1 | N1-T7 seleciona exclusivamente `PROMOTE FCC + EXISTING CUTS`; freeze N2-T1 íntegro, sem alteração | Evidências da N1 e N2-T1; verificação de integridade deve continuar válida no momento da decisão |
| M-2 | Master, dual, custos reduzidos, pricing P0–P5 e Teorema L formalizados, com a revisão independente disponível | §§2–6 e parecer `ACCEPTED WITH CONDITIONS`; D-1 e D-4 aceitos com correções incorporadas |
| M-3 | Todas as correções documentais R-01–R-10 atendidas ou explicitamente reservadas à implementação posterior | §8.2; não exigir implementação futura para declarar correção **documental** |
| M-4 | Contrato matemático de certificação fechado **antes de codificar**: ENUM só com cobertura/aritmética rigorosas; N1/N2 só após verificação da implementação; `ObjBound`/`ObjBoundC` não certificam; interrupção não inventa LB | §§5.3, 6.3–6.5; D-2 rejeitado como certificado isolado; D-3 condicional incorporado |
| M-5 | Testes matemáticos dirigidos já existentes executados sem falhas e limitações reconhecidas | §9; pesquisador informou **18/18 `OK`, 0 skipped** em 2026-10-09; não equivalem à regressão futura |
| M-6 | Uma pessoa responsável registra **expressamente** `APROVADO PARA IMPLEMENTAÇÃO`, `NÃO APROVADO` ou `DEVOLVIDO PARA CORREÇÃO`, identificando a revisão exata, data, responsável, escopo e ressalvas | **PENDENTE**; modelo de registro em §12.1 |

**Conclusão de preparação:** a documentação está `READY FOR GATE M DECISION`, **não** formalmente aprovada.
O parecer não autoriza sozinho o início do código. Se M-1 a M-5 forem confirmados e M-6 registrar `APROVADO PARA
IMPLEMENTAÇÃO`, poderá começar **somente** o desenvolvimento do caminho B autorizado; a decisão não certifica
nenhum LB de execução, não fecha N2-T2B e não muda N2-T1. A aprovação deve declarar explicitamente as
limitações `UNCERTIFIED` dos MIPs numéricos e as provas exigidas para ENUM/N1/N2.

### 11.2 Gate O — Aceite operacional N2-T2B (pós-implementação)

Estes itens **não** são pré-requisitos do Gate M. São exigências verificáveis apenas quando o código existir:

| ID anterior | Condição posterior | Etapa / classificação |
|---|---|---|
| P-2 | Reexecutar controles de master, dual, pricing e validade de colunas contra **as funções reais da geração de colunas**, além das referências isoladas já testadas. Os testes de certificação permanecem na N2-T3 | **N2-T2B / Gate O** |
| P-6 | Registrar versão/parâmetros do Gurobi nas rotas de pricing; validar toda coluna combinatoriamente; operar na raiz sem branching e sem mudar K | **N2-T2B / Gate O** |

**Critérios adicionais do Gate O:** master restrito inicial viável; custo reduzido reproduzível; pricing rotulado
`exact`/`heuristic` com resultado rastreável; nenhuma rotina emite `CERTIFIED` sem prova (o padrão é
`UNCERTIFIED` até a N2-T3); integridade da N2-T1 reverificada; testes automatizados correspondentes aprovados.
A implementação pode ser aceita operacionalmente **como algoritmo de geração de colunas** antes de concluir a
certificação da N2-T3, mas não pode publicar um resultado como certificado. Um pricing MIP numérico pode gerar
colunas, porém não se torna certificador por ter sido implementado.

**Dependências subsequentes, NÃO integrantes do Gate M nem confundidas com a conclusão da N2-T2B:**

| ID anterior | Condição posterior | Etapa / momento limite |
|---|---|---|
| P-1 | Implementar efetivamente o contrato ENUM: vetor racional único, enumeração integral comprovada, `truncated`, cálculo seguro e exportação para baixo; caso contrário `UNCERTIFIED` | **N2-T3**, antes de emitir certificados por ENUM |
| P-3 | Definir e verificar quais bounds globais `ℓ` (ENUM/N1/N2) estarão disponíveis nos níveis pré-registrados; se não houver bound verificável, registrar `UNCERTIFIED`, sem reabrir o pré-registro | **N2-T3**, antes de qualquer medição que dependa de certificação; nunca ajustar os critérios de gate a posteriori |
| P-4 | Implementar/verificar `U` primal factível para aplicação de G2, com resíduos demonstrados ou reconstrução viável; sem `U`, não declarar convergência | **N2-T3**, antes de alegar convergência |
| P-5 | Registrar hash de K e execução de `assert_valid_cuts` por instância nos certificados (H-K) | **N2-T3**, antes de emitir `CERTIFIED` para MIN-STATION |
| P-7 | Certificar `B0` em campo/justificativa próprios, distinguindo-o de `LB_{CG}` | **N2-T3**, antes de produzir as comparações que exigem B0 |
| P-8 | Executar regressão prospectiva nos 23 controles N1; conferir master convergido e tolerância absoluta sem confundir teste numérico com prova exata | **N2-T4**, antes das medições N2-T5 |
| P-9 | Registro formal da decisão anteriormente única | **Substituído por M-6 (autorização anterior ao código) e pelo registro separado do Gate O (§12)** |

**Proibição permanente:** a ausência de implementação ou de um bound global verificado **nunca** permite
preencher um campo `CERTIFIED` por padrão. Não alterar o orçamento, instâncias, critérios congelados, baseline,
K ou o caminho selecionado para contornar falhas. No caso de falha científica, aplicar o stop criterion da spec.

**Decisões matemáticas do parecer preservadas:** D-1 (Teorema L) `ACCEPTED`, com L0 e observação (iv) corrigida;
D-2 (`ObjBound`) `REJECTED` como certificado autossuficiente; D-3 (ENUM) `ACCEPTED WITH CONDITIONS` (aritmética
exata/intervalos, cobertura, vetor único); D-4 (pricing MIP) `ACCEPTED` por equivalência por projeção; D-5
(verificador) conservar como regressão auxiliar. Nenhuma dessas decisões, isoladamente, substitui M-6.

## 12. Registros formais distintos

### 12.1 Gate M — Decisão sobre autorização matemática para implementação

| Campo | Estado nesta versão |
|---|---|
| Tipo | **Autorização matemática para iniciar N2-T2B (Gate M)** |
| Parecer independente | `ACCEPTED WITH CONDITIONS` (2026-10-09), referência na tabela inicial |
| Revisão examinada | **v2.1**, este documento; registrar o SHA-256 no **ato** de decisão, fora deste arquivo, evitando autorreferência |
| Evidência auxiliar | Testes matemáticos: 18 `OK` / 0 `skipped` informados pelo pesquisador; freeze N2-T1 anteriormente `PASS` |
| Pré-requisitos | M-1 a M-5 (§11.1): conferir novamente no ato de aprovação |
| Decisão | **PENDENTE — NÃO É AUTORIZAÇÃO DE IMPLEMENTAÇÃO** |
| Responsável / data / revisão exata / condições | **PENDENTE** |

Para aprovar, criar **um registro separado e versionável**, por exemplo
`docs/technical/plans/execucao/n2-t2b-decisao-aprovacao-matematica.md`, contendo **responsável, data, decisão
explícita, SHA-256 do documento revisado, escopo autorizado e restrições**. A aprovação só é eficaz se os itens
M-1 a M-5 estiverem conferidos, o resultado registrado for `APROVADO PARA IMPLEMENTAÇÃO` e nenhuma ressalva
bloqueante estiver aberta. Reprovação ou devolução mantém o código bloqueado. A decisão é humana; não é produzida
automaticamente por este texto, por testes ou por um agente de IA. **Não inserir o SHA deste arquivo nele próprio.**

**Escopo que poderá ser autorizado:** master qij + K; RMP inicial viável; pricing exato/heurístico rotulado;
geração de colunas exclusivamente na raiz; mecanismo de cálculo de `LB_{CG}` apenas com bound global comprovado
(ENUM racional e/ou N1/N2 verificados); validação de colunas; limite global de Work e rastreabilidade. Sem MIP
`ObjBound` autossuficiente, branching, trio, caminho A, novos cortes ou medições antes dos gates correspondentes.

### 12.2 Gate O — Decisão de aceite operacional da implementação N2-T2B

| Campo | Estado nesta versão |
|---|---|
| Tipo | **Aceite operacional de código já implementado (Gate O)** |
| Pré-requisito | Gate M aprovado com registro versionado; desenvolvimento concluído no escopo autorizado |
| Critérios | P-2, P-6 e demais critérios operacionais do §11.2, com testes/evidências da implementação; P-1 reservado à N2-T3 |
| Decisão | **PENDENTE — NÃO EXISTE IMPLEMENTAÇÃO N2-T2B ACEITA** |
| Responsável / data / commit / evidências | **PENDENTE** |

O aceite do Gate O será registrado **após o código e seus testes**; não retroage para substituir o Gate M e
**não** aprova automaticamente N2-T3, N2-T4, medições N2-T5 nem o gate N2-T6. Cada etapa segue sua spec e as
regras científicas já congeladas. Pendências P-1/P-3/P-4/P-5/P-7/P-8 bloqueiam a etapa correspondente, **não** a
autorização matemática para começar a desenvolver N2-T2B.

**Fora de escopo, mantido:** caminho A, variante trio, branch-and-price, N3, novos cortes, mudança de baseline,
de COMP, do núcleo, de `fcc.py`/`fcc_k.py` ou de qualquer arquivo congelado.
