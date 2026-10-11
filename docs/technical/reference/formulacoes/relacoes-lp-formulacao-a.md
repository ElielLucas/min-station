# Hierarquia LP da formulação A e fronteiras do que se sabe

**Estado:** argumentos matemáticos preparados para revisão independente; não há campanha experimental nova.

## Comparações fundamentadas

Para instâncias com o mesmo `G,S,T,r,A_r`, objetivo e K, tomando uma cadeia de refinamentos `𝓑₁≼𝓑₂≼⋯≼𝓑_unit`, valem as inclusões de projeções em `y` demonstradas em [provas-formulacao-a.md](provas-formulacao-a.md). Sob a definição de F-CC de `formulacao-fcc-configuracoes-conectadas.md`, a cadeia candidata é:

\[
 z_{LP}(U+K)=z_{LP}(A(\{S\})+K)
 \le z_{LP}(A(\mathcal B)+K)
 \le z_{LP}(A(\mathcal B_{unit})+K)
 =z_{LP}(B+K)
 \le z_{LP}(F\!-\!CC+K)\le OPT.
\]

**Justificativa para F-CC→B.** Na configuração F-CC `(W,I,J)` com peso `λ`, escolha bijeção `I→J` e caminhos simples em `H` com internos em `W`, como no argumento P2 de `provas-fcc-fc3.md`. Cada origem de `I` gera peso `λ`; os pares diretos `d_st` geram caminho de um arco ou permanência. Em qualquer `v≠s`, o peso de caminhos com origem `s` e `v` interno não ultrapassa `Σ_{q:v∈W_q}λ_q≤y_v` pela ativação R3 (cada origem aparece no máximo uma vez em cada configuração). Globalmente, no máximo `m−1` caminhos da configuração podem ter internamente um terminal `v∈S∪T`, e no máximo `m` caminhos podem ter internamente um vértice não terminal. Isso fornece B3 e B4 com o mesmo y. A correspondência requer a definição de configuração e o vínculo R3 **como formalizados na F-CC histórica**, não uma F-CC simplificada ou uma variante VI.

**Ponto a auditar:** a derivação de F-CC→B importa premissas do teorema P2 da documentação F-CC; a conclusão não deve ser homologada sem revisar as condições sobre caminhos, incidências e conjuntos conectados. A cadeia é uma **proposta de teorema**, não um certificado computacional.

## Relação com a proposta de cortes do primeiro parecer

Se o conjunto anterior de cortes corresponder à **formulação completa** com matching fracionário compartilhado, fluxos unitários para **todas** as origens e acoplamento à base, uma solução B induz tais fluxos e o mesmo matching. Isso indica `zLP(B+K)≥zLP(COMP+K+cortes completos)` sob exatamente essa definição. **Não** se demonstrou uma relação geral entre A com poucos grupos e aquela proposta. A versão parcial separada apenas para algumas origens, com orçamento, não deve ser confundida com a versão completa ao discutir dominância.

## T18 histórica não ocupa uma posição de dominância comprovada

O modelo T18 `experiments/alternative-formulations/desagregacao.py` usa ativação *por commodity* (`in^s≤p_st+y` em destinos e `out^s≤y` fora da origem), mas **não impõe A5**. Somar as ativações por commodity leva, em geral, a um múltiplo de `y` maior do que o coeficiente da U; portanto a afirmação `LP(T18)≥LP(U)` na documentação anterior é inválida. O contraexemplo fracionário exato está em [errata-desagregacao-por-origem-t18.md](../analise-estrutural/errata-desagregacao-por-origem-t18.md). Isso **não** invalida a exatidão inteira da T18 nem afirma qualquer resultado novo com os cortes K.

## Instância Sec59(L=7) — Ganho estrito versus U+K

Usando a descrição no segundo parecer do Astra:

- `S={s1,s2,s3}`; `T={t1,t2,t3}`; `r=1`.
- Cadeia `w1−w2−⋯−w7`; ligações `s1−t1`, `s2−t1`, `s1−w1`, `s2−w1`, `w7−t2`, `t2−s3`, `s3−t3`.
- Cortes efetivamente relatados no parecer: `y_t1+y_w1≥1` e `y_s3+y_w7≥1`.

Qualquer solução precisa encaminhar pelo menos uma unidade do lado esquerdo através de cada `w_i` para abastecer os dois destinos do lado direito, pois somente `t1` é acessível sem cruzar a cadeia. Para U, `w2,...,w6` são não terminais e suas capacidades são `3y_wi`, implicando `y_wi≥1/3`; com os dois cortes K, `zLP(U+K)≥2+5/3=11/3`. A distribuição de caminhos com **metade de cada `s1,s2` em `t1` e metade de cada uma em `t2`**, e `s3→t3`, tem `y_w1=y_w7=1`, `y_w2...w6=1/3` e realiza igualdade: `11/3`.

Na partição `{{s1,s2},{s3}}`, o primeiro grupo precisa atravessar a cadeia com pelo menos uma unidade. Por A4, `g^{\{s1,s2\}}_{w_i}≤2y_{w_i}` e, para os cinco interiores, `y_wi≥1/2`. Usando os mesmos cortes, `zLP(A2+K)≥2+5/2=9/2`; a mesma distribuição fracionária de caminhos com `y_w2...w6=1/2` atinge `9/2`. Trata-se de **testemunha racional de um caso**, não de evidência empírica de superioridade geral. O parecer relata `zLP(F-CC+K)=5` e `OPT=7`; estes dois últimos valores **não** foram reproduzidos nesta entrega.

O verificador determinístico `experiments/alternative-formulations/test_as01_rational.py` confere a factibilidade racional das duas testemunhas, suas funções objetivo e o par de cortes acima. Ele não substitui a prova universal de limite inferior, auditoria do K completo ou otimização Gurobi.

## Partições incomparáveis

Se `𝓑1` não refina `𝓑2` e vice-versa, a prova por soma não estabelece inclusão. **Não preencher uma tabela com `A4 > A4` por contagem de blocos.** Reportar comparação somente por instância ou por uma prova específica.

## Matriz de evidência

| Afirmação | Natureza | Situação AS-01 |
|---|---|---|
| Exatidão inteira de A | Demonstração com dependência da exatidão da U | Revisão externa pendente |
| Um grupo = projeção U LP | Prova por levantamento explícito | Revisão externa pendente |
| Refinamento ordena LP | Prova por soma de blocos | Revisão externa pendente |
| A unitária = B em `y` | Decomposição de fluxos/caminhos | Revisão externa pendente |
| F-CC LP domina B | Prova por construção de caminhos em configurações | Revisão externa pendente |
| T18 LP não domina U LP | Testemunha racional completa | Verificação local automatizada; revisão externa pendente |
| Sec59 mostra ganho A2+K > U+K | Limites analíticos + testemunhas racionais | Verificação local parcial; K completo pendente |
| A2 versus cortes anteriores | Sem inclusão demonstrada | `UNPROVEN` |
| Escalabilidade de A | Hipótese computacional | AS-03 a AS-06 |
