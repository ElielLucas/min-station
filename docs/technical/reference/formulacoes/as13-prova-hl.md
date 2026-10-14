# AS13 — Cortes HL: projeção exata, validade e hierarquia

**Situação:** prova entregue novamente após `FAIL` por ausência no checkout; requer reavaliação independente. Nenhum gerador HL foi implementado; HL permanece candidato **condicional** e AS14 continua bloqueada.

## 1. Definição do casco de padrões físicos

Fixar `R⊆V` e `F=V\R`. Para `z∈{0,1}^R`, definir:

\[
\Phi_R=\left\{z\in\{0,1\}^R:\nu\big(F\cup\{v\in R:z_v=1\}\big)=m\right\},
\quad Q_R=\operatorname{conv}(\Phi_R).
\]

Quando a instância global é viável, `Φ_R` é não vazio (tome a projeção de `C=V`). Para qualquer vetor racional `α∈Q_{≥0}^R`, definir:

\[
\beta_R(\alpha)=\min_{z\in\Phi_R}\alpha^\top z,
\qquad \boxed{\sum_{v\in R}\alpha_v y_v\ge\beta_R(\alpha).}\tag{HL}
\]

`α=1` fornece uma desigualdade de cardinalidade regional com RHS igual ao menor número de vértices instalados **dentro de R**, considerando otimisticamente todas as estações fora de R como presentes.

## 2. Teorema HL (projeção exata e validade)

Seja `\mathcal F=\{C⊆V:\nu(C)=m\}` o conjunto de instalações fisicamente viáveis. Então:

\[
\boxed{\Phi_R=\{\mathbf 1_{C\cap R}:C\in\mathcal F\}.}
\]

**Prova da inclusão da direita na esquerda:** para `C` viável, `C⊆F∪(C∩R)`. Por monotonicidade `F∪(C∩R)` também é viável; logo sua projeção pertence a `Φ_R`.

**Prova da inclusão da esquerda na direita:** para qualquer `z∈Φ_R`, por definição `C=F∪supp(z)` é uma instalação viável que projeta exatamente em `z`. ∎

Consequentemente cada HL é válida para todas as instalações físicas, e `Q_R` descreve o **casco exato das projeções inteiras** no suporte selecionado. A desigualdade `α^Ty≥β` é consequência imediata da definição de mínimo. **Por que coeficientes não negativos bastam para separar pontos da caixa:** `Φ_R` é crescente por inclusão. Logo, `Q_R=conv(Φ_R)` também é crescente dentro de `[0,1]^R`: para `p∈Q_R`, elevar uma coordenada até `1` preserva `Q_R` (eleva-se a coordenada em cada padrão binário da mistura; o valor intermediário é combinação convexa). Aplicando o argumento sucessivamente a todas as coordenadas, obtemos `Q_R=(Q_R+ℝ_+^R)∩[0,1]^R`. Se `y∈[0,1]^R` não pertence a `Q_R`, uma separação estrita desse fecho superior possui normal não negativa na orientação `αᵀy≥β`. Isto pressupõe `Φ_R≠∅`, monotonicidade e a caixa; não vale como afirmação irrestrita fora desse domínio. Para usar HL computacionalmente, ainda é obrigatório certificar `β=min_{z∈Φ_R}αᵀz` exatamente ou por uma cota inferior conservadora válida.

Se `ν(F)=m`, então todo padrão em R é viável, `Φ_R={0,1}^R`, `Q_R=[0,1]^R`; não existe corte HL não trivial apoiado apenas nesse suporte. **Testar o complemento primeiro** evita enumeração inútil.

## 3. Relação matemática com H2 e K

- Como H2 é válida e seu suporte é `R`, a desigualdade H2 restringe `Q_R`; não implica que qualquer **lista finita** de HL represente todas as facetas de `Q_R`.
- Qualquer corte K com suporte `Z⊆R` válido fisicamente também é satisfeito por `Q_R`.
- A hierarquia de força descreve famílias **completas** em suporte fixo; o resultado computacional depende da seleção de suportes, tempo de prova e quantidade de cortes gerados.
- Não afirmar originalidade geral de cascos de padrões nem de técnicas de local cuts. O possível resultado novo seria um oráculo e política de separação úteis **neste problema**, validados experimentalmente.

## 4. Testemunha dos quatro relés

Construir relés `W={w1,w2,w3,w4}`. Para cada par `i<j`, construir uma origem `s_ij` e um destino `t_ij`; ambos adjacentes **somente** a `w_i` e `w_j`, com `r=1`. Tem-se `n=16` e `m=6`.

**Teorema estrutural:** `C` é viável se, e somente se, `|C∩W|≥3`, mesmo permitindo estações adicionais em todos os terminais.

**Necessidade:** se pelo menos dois relés `w_i,w_j` estiverem ausentes, a origem `s_ij` tem como vizinhos apenas esses relés. Como `r=1`, sem estação no primeiro salto ela não alcança **nenhum** destino, mesmo se todos os terminais tiverem estação. Portanto a instância não admite matching perfeito.

**Suficiência:** se ao menos três relés estão instalados, para cada par `(i,j)` pelo menos um de seus relés `w_i,w_j` está instalado. O robô de `s_ij` pode seguir `s_ij-w_i-t_ij` ou `s_ij-w_j-t_ij` usando o relé disponível. Os destinos `t_ij` são distintos; assim o matching de cada origem ao destino do mesmo par é perfeito. ∎

**Efeito no LP:** K possui as seis coberturas `y_wi+y_wj≥1`. Sua soma implica `3y(W)≥6`, portanto `zLP(COMP+K)≥2`; o ponto `y_w=1/2` para todo relé, zero nos terminais, admite fluxo COMP e satisfaz K, dando `zLP=2`.

Para cada trio de relés `W\{w_i}`, H2 exige `y(W\{w_i})≥2`. Somando os quatro trios, `3y(W)≥8`, portanto `zLP(COMP+K+H2)≥8/3`. O ponto `y_w=2/3` para cada relé e zero para os terminais é viável em COMP e satisfaz **todos os H2 de qualquer suporte `R⊆V`**:

- `|R∩W|≤1`: `F=V\R` já tem ≥3 relés; nenhum H2 se aplica;
- `|R∩W|=2`: cada relé desse par, sozinho, é suficiente contra `F` (`G_R` os inclui); o lado esquerdo no ponto é `2·(2·2/3)=8/3≥2`;
- `|R∩W|=3`: nenhum único relé restante repara `F`, e o lado esquerdo é `3·2/3=2`;
- `|R∩W|=4`: o lado esquerdo é `4·2/3=8/3≥2`.

Como a viabilidade só depende dos relés, os suportes podem conter quaisquer terminais sem mudar o argumento. Esta verificação por casos também foi conferida para os **65.536 suportes possíveis**, dos quais **45.056** produzem H2 não trivial.

Em `R=W`, todo padrão de `Φ_R` instala ≥3 relés. Portanto HL com `α=1` fornece `y(W)≥3`. Assim:

\[
\boxed{z_{LP}(COMP+K)=2<z_{LP}(COMP+K+H2)=8/3<z_{LP}(COMP+K+H2+HL)=3=OPT.}
\]

Isto prova estrita hierarquia **para a construção descrita**, não superioridade computacional geral. A varredura exaustiva de 65.536 **conjuntos de instalações** também verificou o predicado `|C∩W|≥3` com o oráculo físico por bateria.

## 5. Certificação e custo (reserva para AS18)

Se `|R|=k`, enumerar `Φ_R` custa até `2^k` verificações de viabilidade. Para um corte `y(R)≥3` basta, pela monotonicidade, certificar inviabilidade de todos os subconjuntos com `0`, `1` ou `2` estações: `1+k+binom(k,2)` testes, desde que `F` esteja corretamente fixado.

Um `α` numérico proposto por LP auxiliar **não** constitui certificado. Transformar coeficientes em racionais, recalcular `β=min_{z∈Φ_R} α^Tz` exatamente ou por limite conservador válido, e só então aceitar o corte. Com padrão não resolvido, é inseguro tratá-lo como inviável: **abster-se** ou tratá-lo como admissível conservadoramente. Essas questões são de AS18, não fazem parte da AS13 implementada.

## 6. Limite de originalidade e relação exata com arredondamentos de K no exemplo K4

O corte HL `y(W)≥3` **não é informação física ausente do núcleo inteiro K no K4**. Todas as seis coberturas `y_i+y_j≥1` exigem que, em uma instalação inteira que as satisfaça, no máximo um relé esteja ausente. Portanto, o fecho inteiro de K já satisfaz `y(W)≥3`.

Mais construtivamente, um arredondamento das três coberturas de cada trio produz `y(W\{w_i})≥2`. A soma dos quatro trios é `3y(W)≥8`, e a integralidade permite arredondar para `y(W)≥3`. Assim, **no K4**, o efeito HL `8/3→3` também admite derivação por arredondamentos sucessivos baseados em K. O exemplo continua válido como testemunha de que a coleção explícita de H2 gera um LP menos forte que um corte HL; não demonstra que HL supere todo o fecho CG de K nem prova originalidade de família poliédrica.
