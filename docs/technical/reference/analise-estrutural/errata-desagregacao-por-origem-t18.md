# Errata T18 — Desagregação por origem e LP da base U

**Data da errata:** 2026-10-11  
**Status:** contraexemplo racional conferível; parecer matemático independente ainda pendente.  
**Documento histórico:** [desagregacao-por-origem.md](desagregacao-por-origem.md).  
**Código histórico:** `experiments/alternative-formulations/desagregacao.py` (**não alterado**).

## Correção específica

A frase histórica afirmando que, por soma das ativações individuais, a T18 relaxada *implica* as ativações agregadas de U, e daí `zLP(T18)≥zLP(U)`, **não é verdadeira em geral**. Somar `m` restrições com `y_v` individual permite `m·y_v` unidades de trânsito em um terminal, enquanto U impõe o coeficiente `m−1` para o fluxo agregado que o atravessa; a chegada final gratuita do destino não pode ser contabilizada `m` vezes.

O ganho da T18 nas pequenas instâncias medidas permanece um **fato experimental daqueles casos**, não uma garantia matemática universal. Esta errata não altera os resultados históricos nem conclui que a T18 com `y` binário seja inexata.

## Contraexemplo racional (`r=1`)

Tome a estrela `G` com `V={a,b,c,d}`, `E={{a,c},{b,c},{c,d}}`, `S={a,b}` e `T={c,d}`. No modelo T18 **relaxado**, todos os `y,p,f` têm limites `[0,1]` quando aplicável. Escolha:

\[
 y_c=\tfrac12,\quad y_a=y_b=y_d=0,
\]
\[
 p_{ac}=p_{ad}=p_{bc}=p_{bd}=\tfrac12,
\]
\[
 f^a_{ac}=f^b_{bc}=1,\qquad f^a_{cd}=f^b_{cd}=\tfrac12,
\]

e todos os outros fluxos zero.

Cada origem envia uma unidade; cada destino recebe uma unidade de atribuição. Para cada commodity, no vértice `c`, `in^s(c)=1=p_{sc}+y_c` e `out^s(c)=1/2=y_c`. Os demais limites são triviais. Assim o objetivo T18 é `1/2`. Na U, os dois robôs precisam atravessar a chegada em `c` para que haja atendimento de `d` (único vizinho de `d`), e `in_F(c)≥2`. Como `c∈T` e `m=2`, a ativação agregada exige `in_F(c)≤1+y_c`, logo `y_c≥1`. Tomando os caminhos `a→c` e `b→c→d`, a estação `c` é suficiente; portanto `zLP(U)=1`.

**Certificado de limite inferior da T18:** no destino `d` (que só é adjacente a `c`), a soma dos balanços das commodities dá `Σ_s(f^s_{cd}−f^s_{dc})=1`, portanto `Σ_s f^s_{cd}≥1`. Para cada `s∈{a,b}`, a ativação histórica de saída em `c` impõe `f^s_{cd}≤out^s(c)≤y_c`. Assim `1≤2y_c`, isto é, `y_c≥1/2`; como as demais instalações são não negativas, `zLP(T18)≥1/2`. Junto à testemunha primal, **`zLP(T18)=1/2`**.

**Certificado de limite inferior de U:** os balanços de `a` e `b` (únicos vizinhos: `c`) impõem `f_ac−f_ca=1` e `f_bc−f_cb=1`, logo `in_F(c)≥f_ac+f_bc≥2`. A capacidade de entrada em `c∈T` exige `in_F(c)≤1+y_c`, ou `y_c≥1`. Como existe testemunha com uma estação, **`zLP(U)=1`**.

Conclui-se `zLP(T18)=1/2 < 1 = zLP(U)`, sem solver e com aritmética racional. Este certificado depende da estrutura da estrela e da ausência de K.

## Escopo da correção

- **Sem K:** o exemplo refuta a dominância geral que foi alegada sem cortes. **Não** demonstra que o mesmo ponto sobrevive a C1+C2+C4-DM.
- **Inteiros:** não contradiz a igualdade de ótimos inteiros entre T18 e U observada nos casos históricos.
- **S∩T:** a estrela é disjunta, portanto a falha não depende de sobreposição.
- **Origem do erro:** ausência de acoplamento agregado de trânsito como A5 da nova proposta A.
- **Referências:** segundo parecer do Astra §5 e `docs/technical/reference/formulacoes/relacoes-lp-formulacao-a.md`.

## Teste reproduzível

`PYTHONHASHSEED=0 python3 -m unittest discover -s experiments/alternative-formulations -p 'test_as01*.py' -v`

O teste usa `fractions.Fraction`, lê as restrições históricas sem as modificar e confere ponto, objetivo e violação da restrição agregada de U.
