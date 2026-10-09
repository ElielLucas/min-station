# N2-T2B — Master F-CC+K, dual e pricing (minuta para revisão matemática)

**Estado:** `DRAFT — REVIEW REQUIRED BEFORE CODING`. **Escopo:** N2 caminho B, raiz apenas, representação `(W,I,J)` exatamente como na `fcc.py`. **Sem autorização para rotular resultados como `CERTIFIED` com base nesta minuta.**

## 1. Definições e domínio

Seja `H=G^r` o grafo não dirigido de alcance, preservando a semântica do problema MIN-STATION de Das. O conjunto de pares diretos é `D={(s,t)∈S×T : s=t ou d_G(s,t)≤r}`; a igualdade `s=t` é permitida em `S∩T`, e uma origem que também é destino continua desempenhando **dois papéis distintos**. Não existe exigência de matching fixo.

Para cada conjunto **não vazio e conexo** `W⊆V(H)`, `B(W)=W∪{v∈V : v adjacente em H a algum w∈W}`. Uma configuração admissível é `q=(W,I,J)` com `I⊆ S∩B(W)`, `J⊆T∩B(W)`, `|I|=|J|≥1`. A coluna está proibida se `I=J=∅`. O conjunto de cortes `K` corresponde exclusivamente a `C1+C2+C4-DM` da N1, com desigualdades `Σ_{v∈Z} y_v ≥ 1`, `Z∈K`, sem gerar novos cortes post-hoc.

### 1.1 Primal completo (LP)

Variáveis: `λ_q≥0` para cada configuração; `d_st≥0` para cada par direto; `0≤y_v≤1` para cada vértice. Minimizamos

\[
\min\ \sum_{v\in V}y_v.
\]

Restrições (os índices `q` percorrem todas as configurações possíveis):

\[
\sum_{q:s\in I_q}\lambda_q+\sum_{t:(s,t)\in D}d_{st}=1\quad(\forall s\in S), \tag{R1}
\]
\[
\sum_{q:t\in J_q}\lambda_q+\sum_{s:(s,t)\in D}d_{st}=1\quad(\forall t\in T), \tag{R2}
\]
\[
 y_v-\sum_{q:v\in W_q}\lambda_q\ge 0\quad(\forall v\in V),\tag{R3}
\]
\[
\sum_{v\in Z}y_v\ge 1\quad(\forall Z\in K),\tag{K}
\]
\[
-y_v\ge -1\quad(\forall v\in V).\tag{UB}
\]

`R1/R2/R3` reproduzem a forma `qij` da `fcc.py`; `UB` mantém exatamente o limite superior de `y` presente no código. A equivalência com a forma separada (λ_W, α_sW, β_tW) depende da prova P7 da N1, não deve ser presumida por uma mudança de implementação.

### 1.2 Master restrito

Substitui-se o universo de configurações por `Q_R⊆Q` em R1/R2/R3, mantendo **todas** as variáveis `y`, os pares diretos, os cortes K e os limites superiores de `y`. Uma coluna inicial sempre disponível, sob `G` conexo e `r≥1`, é `(V,S,T)`: `H` é conexo, `B(V)=V`, `|S|=|T|=m≥1`. Com `λ_(V,S,T)=1`, `y_v=1` para todo `v`, e `d=0`, obtém-se solução factível do master restrito se `K` contém apenas conjuntos não vazios. Podem-se acrescentar colunas locais válidas, mas sem fixar previamente o matching.

**Advertência central:** `z_RMP ≥ z_LP_completo` em minimização. Portanto, `z_RMP` **não** é limite inferior para MIN-STATION; não pode aparecer em coluna chamada `certified_lb`.

## 2. Dual completo com sinais explícitos

Associam-se `π_s∈ℝ` a R1, `τ_t∈ℝ` a R2, `μ_v≥0` a R3, `κ_Z≥0` a K e `η_v≥0` a UB. Com a convenção de dual do primal `min` com linhas `≥`, o dual é

\[
\max\ \sum_{s\in S}\pi_s+\sum_{t\in T}\tau_t+\sum_{Z\in K}\kappa_Z-\sum_{v\in V}\eta_v
\]

sujeito a

\[
\pi_s+\tau_t\le 0\qquad ((s,t)\in D),\tag{D-d}
\]
\[
\sum_{s\in I_q}\pi_s+\sum_{t\in J_q}\tau_t-\sum_{v\in W_q}\mu_v\le 0\qquad(q\in Q),\tag{D-λ}
\]
\[
\mu_v+\sum_{Z\in K:v\in Z}\kappa_Z-\eta_v\le1\qquad(v\in V).\tag{D-y}
\]

O sinal e a presença de `η` são essenciais: o código impõe `y_v≤1`, de modo que o dual que omitisse os respectivos limites superiores seria o dual de outro master. Alternativamente, pode-se trabalhar com variáveis limitadas no solver e um dual de custos reduzidos de bound, desde que se demonstre equivalência.

## 3. Custo reduzido e pricing

Para coluna `q=(W,I,J)`, o custo objetivo é zero e o custo reduzido sob qualquer vetor dual do master restrito é

\[
\bar c(W,I,J)=\sum_{v\in W}\mu_v-\sum_{s\in I}\pi_s-\sum_{t\in J}\tau_t.
\]

Os multiplicadores de K **não aparecem diretamente** no custo reduzido de `λ`, porque K só incide sobre `y`; **aparecem indiretamente** via (D-y) e pelo valor dual do master. O pricing exato procura

\[
\min_{\substack{\emptyset\ne W\subseteq V\\H[W]\text{ conexo}}}\left[\sum_{v\in W}\mu_v-\max_{1\le k\le\min(|S_W|,|T_W|)}\left(\operatorname{TopK}(\{\pi_s:s\in S_W\},k)+\operatorname{TopK}(\{\tau_t:t\in T_W\},k)\right)\right],
\]

com `S_W=S∩B(W)`, `T_W=T∩B(W)`. `TopK` soma os `k` maiores elementos, **mesmo que negativos**. A fórmula decorre de escolher livremente `I` e `J` balanceados para cada `W`, mantendo `|I|=|J|≥1`, sem pareamento predefinido. Conectividade vale em `H`, não diretamente em G, e vértices de terminal não são relés gratuitos quando a estação ou deslocamentos precisarem ser representados.

**Critério de otimalidade:** pricing exato provando `min_q \bar c_q ≥ -10^{-6}` (com tratamento numérico compatível com tolerâncias do LP e prova de otimalidade global) torna o dual do master completo factível até a tolerância especificada; a solução do master pode então ser confrontada com o LP completo. Pricing heurístico pode adicionar colunas, **nunca** certificar ausência de coluna melhorante.

## 4. Política de certificação para N2-T3

1. Se todas as linhas duais de `d`, `y`, `K`, `UB` e `λ` forem satisfeitas globalmente por pricing **exato**, usar o valor **dual factível** como LB contínuo, com tolerância e estado `CERTIFIED` registrados. A igualdade com `z_RMP` depende de solução ótima do master e de residuais/tolerâncias validados.
2. Se pricing for incompleto, não rotular `z_RMP` como LB. O limite já certificado `B0` poderá ser preservado, caso a certificação dos componentes COMP/core esteja devidamente registrada para a instância. Sem tal certificado: `UNCERTIFIED`.
3. Uma regra alternativa sob pricing incompleto (Farley/Lagrangiana/equivalente) **não faz parte desta minuta** e exigirá prova separada revisada antes de código. Não reutilizar automaticamente a Lagrangiana do baseline antigo.
4. O objetivo inteiro permite `ceil(L−10^{-6})` **somente para L já certificado**, nunca para `z_RMP` não certificado.
5. Registrar o motivo de certificação por linha, inclusive quando o pricing esgotar o orçamento.

## 5. Obrigações de revisão antes de implementar geração de colunas

- Confrontar a forma `(W,I,J)` com P1/P2/P7 da N1 e conferir se o dual acima reproduz numericamente o dual Gurobi em instâncias enumeráveis.
- Verificar explicitamente `S∩T≠∅`, `d_ss`, balanço `|I|=|J|`, `W` conexo em H, elegibilidade e cortes K idênticos aos da N1.
- Testar pricing exato contra mínimo por enumeração **sobre todas as colunas admissíveis** em casos pequenos; testes de RMP devem reproduzir todo LP F-CC+K conhecido (`1e-6`).
- Formalizar controle de orçamento conjunto (`WorkLimit` incluindo todo solve), custo de montagem, memória, wall e falha segura se pricing interromper.
- O revisor precisa registrar uma decisão **`ACCEPTED`** para esta derivação antes da N2-T2B computacional. Esta minuta **não equivale** a tal aprovação.

**Não implementar caminho A, variante trio, branch-and-price, nem novas desigualdades para recuperar uma falha do caminho B.**
