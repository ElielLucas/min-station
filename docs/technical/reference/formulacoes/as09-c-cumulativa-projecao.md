# AS-09 — Formulação C cumulativa corrigida: contrato e projeção LP

**Status:** demonstração construtiva para revisão matemática independente (`PROOF_REVIEW_REQUIRED`).  
**Implementação associada:** `experiments/alternative-formulations/as09_model_c.py`.  
**Não substituir por:** `experiments/cumulative/cumulativo_min_station.py` (ativação histórica por nível).

## Escopo

O grafo físico `G=(V,E)` é **não direcionado, de arestas unitárias**, sem laços; `r>=1` é inteiro. `H=(V,A_r)` inclui exatamente os pares ordenados distintos cuja distância física é <=r. `S,T subseteq V`, sem repetição interna, `|S|=|T|=m`; `S∩T` é permitido e o pareamento OD é anônimo. `a_v=1[v∈S]`, `b_v=1[v∈T]`, `κ_v=m-1[v∈S∪T]`.

O mesmo vetor `y_v∈[0,1]` (LP; binário no MIP) e os mesmos cortes `K: Σ_{v∈Z} y_v>=1` são usados em U e C. Fluxos, recargas e absorções são não negativos e contínuos. A versão C não introduz variáveis binárias extras.

## Variáveis e restrições C

- `F^q_{uv} >=0`: deslocamento de `(u,q)` para `(v,q+1)`, `q=0,...,r-1`, para cada orientação da aresta física `{u,v}`.
- `z_v^q>=0`: recarga de `(v,q)` para `(v,0)`, `q=1,...,r`.
- `e_t^q ∈[0,1]`: absorção em `t∈T` e estado `q=0,...,r`. Absorção em `q=0` representa inclusive permanência `s=t`.
- `y_v∈[0,1]` na LP, `y_v∈{0,1}` na IP; `min Σ_v y_v`.

**C1, conservação**, para cada `(v,q)`:

\[
\sum_{u:\{u,v\}\in E}F^{q-1}_{uv}
+\mathbf 1_{q=0}\left(a_v+\sum_{\ell=1}^{r}z_v^\ell\right)
=\sum_{w:\{v,w\}\in E}F^{q}_{vw}
+\mathbf 1_{q\ge1}z_v^q+e_v^q.
\]

Termos `F^{-1}`/`F^r` são ausentes; `e_v^q=0` se `v∉T`.

**C2, atendimento:** `Σ_{q=0}^r e_t^q=1`, para `t∈T`.

**C3, ativação cumulativa:** `Σ_{q=1}^r z_v^q≤κ_v y_v`, para `v∈V`.

**K:** os mesmos cortes sobre `y` de COMP+K, preparados e verificados separadamente.

## Relação com U (COMP) e demonstração construtiva

Escreva `f_{uv}` para o fluxo de U em `A_r`, `in_f(v)`/`out_f(v)` para seus graus ponderados. U impõe:

\[
 out_f(v)-in_f(v)=a_v-b_v,\quad
 in_f(v)\le b_v+(m-b_v)y_v,\quad
 out_f(v)\le a_v+(m-a_v)y_v.
\]

### C → U (esboço construtivo)

1. Considere a rede expandida com arcos físicos `(u,q)→(v,q+1)`, de recarga `(v,q)→(v,0)` e arcos de absorção ao sumidouro. A conservação C1/C2 expressa `m` unidades de fluxo origem→destino, juntamente com possíveis circulações. Elimine as circulações (sem aumentar nenhuma variável `F,z`, nem `y`).
2. Decomponha o fluxo remanescente em caminhos origem→destino. Cada trecho entre uma origem/recarga e a recarga/absorção seguinte contém no máximo `r` arestas físicas e define um arco de `A_r`. Uma permanência `s=t` sem movimento produz trecho vazio, não um arco com laço.
3. Denote `g_v` a quantidade recarregada no vértice após eliminar circulações e `h_v` a quantidade que permanece em `v` com `s=t`. O fluxo comprimido em `H` satisfaz `in_f(v)+h_v=b_v+g_v` e `out_f(v)+h_v=a_v+g_v`.
4. Como `0≤h_v≤min(a_v,b_v)` e `g_v≤κ_v y_v`, resultam as três famílias de U. Em vértices não terminais `κ_v=m`; em terminais `κ_v=m-1`, exatamente o teto exigido. O mesmo `y` e K são preservados.

### U → C (esboço construtivo)

1. Comece com qualquer solução `(f,y)` de U. Remova circulações no digrafo `H`; os limites de entrada/saída permanecem satisfeitos. É importante que essa operação não altere `y`.
2. Em cada vértice com `a_v=b_v=1`, defina a parcela de permanência `h_v=max(0,1-in_f(v))`. Nos demais vértices, defina `h_v=0`. Tome `g_v=in_f(v)+h_v-b_v=out_f(v)+h_v-a_v`. Pela conservação, `g_v≥0` em todos os casos.
3. Verifique a ativação: se `v∉S∪T`, `g_v=in_f(v)≤m y_v`; se `v∈S\T`, `g_v=in_f(v)=out_f(v)-1≤(m-1)y_v`; se `v∈T\S`, `g_v=out_f(v)=in_f(v)-1≤(m-1)y_v`; se `v∈S∩T`, `g_v=max(0,in_f(v)-1)≤(m-1)y_v`. Portanto `g_v≤κ_v y_v`.
4. Divida o fluxo incidente em `H` localmente em parcelas de absorção `b_v-h_v`, novas partidas `a_v-h_v` e trânsito que exige recarga `g_v`. A conservação permite escolher uma decomposição de caminhos (com possível remoção de ciclos redundantes). Expanda cada arco de `A_r` por um caminho físico de comprimento até `r`, recomeçando no estado zero entre arcos e absorvendo em qualquer estado final. Isso fornece uma solução C para o mesmo `y`.

**Conclusão candidata:** sob todas as hipóteses de escopo e com `H` sendo *exatamente* o grafo de alcance, as projeções LP sobre `y` coincidem, antes e depois de adicionar cortes K idênticos. Os argumentos acima requerem revisão de uma segunda pessoa, especialmente do passo de decomposição local nos vértices `S∩T` e da eliminação de circulações. Até esse parecer, registrar a propriedade como `PROOF_REVIEW_REQUIRED`, não como teorema homologado.

### Consequências e limitações

- Igualdade de projeções LP **não implica** igualdade de tempo, tamanho, memória ou desempenho MIP.
- O estudo C **não busca** limites LP melhores do que COMP+K; busca custo total menor em regimes com `|A_r| >> 2r|E|`.
- A especificação rejeita grafos direcionados, pesos não unitários ou `r` não integral; não converter silenciosamente.
- Se `H` for uma aproximação com arcos ausentes ou extras, a prova não se aplica.
- O conjunto K deve ser produzido pelo mesmo pipeline auditado de U. Mesmo que C use arestas de G, o custo de construir H para K deve constar na comparação.

## Evidências iniciais e critérios de avanço

- Testes automatizados: ver `test_as09_model_c.py`. Cobrem instâncias pequenas, instalação binária confrontada com o oráculo físico, `S∩T`, trânsito por destino, a-v-b, ativação cumulativa e comparação numérica C/U de ótimo LP e fibras fracionárias.
- A verificação numérica em uma amostra finita **não é** prova de equivalência de projeções para todos os grafos.
- **Gate matemático T1:** revisão independente do argumento; registrar PASS com justificativa ou `UNPROVEN` com lacuna específica. Não autorizar uma conclusão de equivalência até PASS.
- **Gate T3:** benchmarking instrumentado de preparação H, K, construção de ambos os modelos, solução LP, limites de memória; sem isso, não emitir decisão de economia real.
