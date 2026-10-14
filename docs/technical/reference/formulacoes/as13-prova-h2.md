# AS13 — Cortes H2: definição, prova de validade e controles

**Situação:** documento para correção do `FAIL` independente por ausência de prova no checkout. A argumentação requer nova revisão autor ≠ verificador; AS14 continua bloqueada.

## 1. Definição

Fixar um suporte `R⊆V` e disponibilizar **todas** as estações externas: `F=V\R`. O teste otimista precisa certificar `ν(F)<m`. A indisponibilidade de uma instalação em `F` é parte **necessária** da premissa; não é correto usar simplesmente o conjunto corrente de estações de uma solução candidata.

Particionar o suporte em:

\[
B_R=\{v\in R:\nu(F\cup\{v\})<m\},\qquad G_R=R\setminus B_R.
\]

A desigualdade é:

\[
\boxed{\sum_{v\in B_R}y_v+2\sum_{v\in G_R}y_v\ge2.}\tag{H2}
\]

O coeficiente `1` marca escolhas individuais **comprovadamente insuficientes**. O coeficiente `2` marca as demais escolhas, inclusive aquelas que por si só permitem uma solução quando todo `F` está equipado. **Não** significa que essas estações tenham capacidade dois.

## 2. Teorema H2 (validade sobre toda instalação física)

**Hipóteses:** `ν(F)<m`, `B_R` certificado exatamente pela definição e variáveis `y_v∈{0,1}` para instalações físicas.

**Prova:** Seja `C⊆V` uma instalação fisicamente viável. Se `C∩G_R≠∅`, há pelo menos um coeficiente `2` ativo, e H2 é satisfeita. Se `C∩G_R=∅` e H2 fosse violada, `|C∩B_R|≤1`. No caso zero, `C⊆F`, então `ν(C)≤ν(F)<m`, absurdo. No caso unitário `{v}`, `C⊆F∪{v}` e `ν(C)≤ν(F∪{v})<m`, igualmente absurdo. Consequentemente H2 é válida para toda instalação viável. ∎

A validade cobre `S∩T`, recarga em terminais, rota sem deslocamento e compartilhamento de estações, pois a única propriedade usada é P2 (monotonicidade) sob a caracterização física correta.

## 3. Certificação parcial segura

Pode-se testar somente uma parte dos candidatos, obtendo `\widehat B_R⊆B_R`, **desde que cada elemento incluído tenha inviabilidade certificada**. Tratar todos os não inspecionados como `\widehat G_R=R\setminus\widehat B_R`, com coeficiente `2`. A prova por casos anterior continua válida: nenhuma instalação viável pode estar inteiramente em `F` nem em `F` mais um dos vértices de `\widehat B_R`. Não se deve atribuir coeficiente `1` a testes com erro, timeout ou status desconhecido.

Para um `R` fixado, uma classificação completa requer no máximo `|R|+1` chamadas: `F` e `F∪{v}` para cada `v∈R`. Isso **não** fornece método polinomial para encontrar bons suportes `R`; essa é a tarefa posterior de AS15.

## 4. Casos-limite e relação com outros cortes

| Condição | Consequência |
|---|---|
| `ν(F)=m` | Nenhum H2 não trivial no suporte `R`: **abster-se**. |
| `R=∅` e problema fisicamente viável | A premissa falha, pois `F=V` é viável. |
| `B_R=∅` | H2 equivale a `y(R)≥1`: não é avanço sobre uma cobertura válida já conhecida. |
| `B_R=R` | H2 vira `y(R)≥2`, fortalecendo a cobertura. |
| `R` suporte minimal de cobertura física | Para cada `v∈R`, `F∪{v}` é viável, portanto `B_R=∅` e H2 degenera. |
| `ν(V)<m` | O problema inteiro é fisicamente inviável; não promover corte como ganho útil. |

H2 implica `y(R)≥1` também na relaxação, pois seu lado esquerdo é no máximo `2y(R)`. Portanto acrescentar H2 preserva a cobertura correspondente, mas **não substitui todos os cortes K gerados em suportes diferentes**.

Se `h=|B_R|≥2`, para cada `v∈B_R` é válida a cobertura `y(R\{v})≥1`. Somar essas coberturas dá:

\[
(h-1)y(B_R)+h\,y(G_R)\ge h.
\]

Para valores **inteiros**, se `y(G_R)≥1`, H2 vale; caso `y(G_R)=0`, a desigualdade exige `y(B_R)≥\lceil h/(h-1)\rceil=2`. Logo H2 é implicada pelo **fecho inteiro** dessas coberturas fisicamente válidas. Outra interpretação é dividir a soma por `h-1`, elevar os coeficientes de `G_R` até 2 (enfraquecimento seguro) e arredondar o lado direito para 2, já que o novo lado esquerdo é inteiro. **Esta derivação não certifica um posto CG específico de H2 a partir do K materializado**: ela usa coberturas `R\{v}` que podem não pertencer a K. Não alegar novidade poliédrica por mera agregação/arredondamento.

## 5. Testemunha HB: H2 fornece informação física ausente no núcleo inteiro K

Instância gerada sem alteração por `experiments/structural/hb.py`, `construir(q=4,ndir=2,p=1,k=1)`: `n=16`, `m=6`, `r=1`, quatro relés `x0_0` a `x0_3`, duas saídas distantes. O gerador C1+C2+C4-DM produz **4 cortes K**. Sua lista canônica e hashes estão em `as13-math-evidence.json`.

- `C={x0_0}` satisfaz todas as **4 desigualdades inteiras K**, mas é fisicamente inviável: quatro origens `A` disputam dois destinos diretos e uma única saída adicional via `x0_0`; falta **um** pareamento: três das quatro origens de `A` podem ser atendidas (duas em `c0_*` e uma via `x0_0`), dando `ν({x0_0})=5<m=6`.
- Com `R=V`, o complemento é vazio e **nenhuma estação isolada** torna a instância viável; assim, `B_R=V` e H2 é `y(V)≥2`.
- `C={x0_0,x0_1}` é fisicamente viável, logo o ótimo inteiro é exatamente `2`.
- A relaxação COMP+K tem valor `1`: as quatro linhas K exigem `≥1`, e a distribuição `y_x0_0=y_x0_1=1/2` admite fluxo fracionário (a mesma conclusão é reproduzida pelo LP compilado). H2 eleva o LP a `2`.

A prova `OPT≥2` é física, não simplesmente um arredondamento de gap. Isto **não** prova que H2 acrescente pontos ausentes do modelo inteiro COMP, apenas do **núcleo de instalações descrito por K**.

## 6. Controles negativos obrigatórios

- `s-a-b-t`, `r=1`: uma estação isolada não resolve; `{a,b}` resolve. Impede somar ganhos individuais como se fossem submodulares.
- Dois robôs `s1-w-t1`, `s2-w-t2`: `{w}` resolve ambos. Impede traduzir deficiência de Hall diretamente em número de estações.
- `S∩T` com permanência: `s=t` exige zero estações.
- Disponibilizar `F=V\R` é obrigatório; uma análise de uma solução específica `C*` não certifica uma desigualdade global.

**Aplicação AS15:** implementar apenas após parecer independente autor≠verificador e com contratos de `UNKNOWN`/timeout que produzam abstenção, nunca falso corte.

## 7. Separação precisa entre K materializado, fecho inteiro e arredondamentos

**HB.** O ponto inteiro `y=1_{\{x0_0\}}` satisfaz as quatro linhas de cobertura de `K` e os limites `0≤y≤1`, mas viola `y(V)≥2`. Logo, H2 **não** é consequência de `K` e dos limites de caixa, nem de qualquer sequência de cortes válidos para o fecho inteiro dessas linhas: tal sequência deve preservar *todos* os pontos inteiros viáveis para o núcleo `K`. Essa afirmação **não** significa que o ponto seja viável no MIP completo `COMP+K` com fluxo.

**K4.** Em contraste, para cada trio `R=\{w_i,w_j,w_k\}` o próprio `K` contém as três linhas de pares desse trio:

\[
y_i+y_j\ge1,\quad y_i+y_k\ge1,\quad y_j+y_k\ge1.
\]

Somando, `2y(R)≥3`. Pela integralidade da soma `y(R)` em instalações inteiras, obtemos `y(R)≥2`. Esta é exatamente a desigualdade H2-card desse trio, e **pode ser obtida por um arredondamento de Chvátal–Gomory de primeira rodada sobre as linhas K já disponíveis**. Portanto, o ganho LP `2→8/3` em K4 demonstra a força *da desigualdade adicionada ao LP inicial*, mas **não** uma informação fisicamente nova além do fecho inteiro de K.

Somando os quatro H2 triplos, cada relé ocorre três vezes: `3 y(W)≥8`. Mais uma vez, pela integralidade da soma, obtém-se `y(W)≥3`, a linha HL de cardinalidade de K4. Isso mostra que, **neste exemplo**, HL é recuperável mediante arredondamentos sucessivos de K. **Não é uma prova de que HL seja sempre consequência de uma quantidade fixa de rodadas CG**, nem de que H2/HL sejam inúteis em instâncias difíceis.

**Consequência metodológica:** medir separadamente (i) ganho contra LP inicial com K, (ii) ganho frente à geração genérica de cortes na raiz e (iii) informação que não seja consequência do núcleo inteiro K. O exemplo HB atesta (iii) para H2; K4 atesta a hierarquia de forças no LP inicial, mas não (iii).
