# AS-01 — Checklist para o verificador independente (T5)

**Uso:** roteiro para um revisor distinto do autor dos documentos. **Não** é um parecer emitido.

## Requisitos para PASS

1. Verificar diretamente no `baseline.py` as capacidades de U, inclusive `v∈S∩T`, e confirmar a equivalência com a interpretação física para `y` binário. Procurar contraexemplos com troca de ocupantes, circulação e permanência.
2. Verificar A1–A7 símbolo por símbolo para todos os tipos de vértices (`S\T`, `T\S`, `S∩T`, demais), incluindo `m=1`, `S=T` e blocos unitários.
3. Tentar refutar **ambas** as direções da exatidão inteira de A, separando a direção caminho→A da projeção A→U. Não assumir o teorema da U sem conferir o alcance exato de suas hipóteses.
4. Auditar o levantamento LP U→A com um grupo: `h=max(0,1−in)` e `g=max(0,in−1)` no overlap, verificando os limites de `y` fracionário e coeficientes terminais.
5. Auditar o mapa de soma no refinamento de blocos, inclusive os limites de `p` e `h`; **não** inferir ordem entre partições incomparáveis.
6. Auditar a decomposição A unitária↔B em caminhos simples, especialmente retornos à origem que também é destino e possíveis fluxos circulantes. Produzir prova fechada ou marcar `UNPROVEN`.
7. Conferir `formulacao-fcc-configuracoes-conectadas.md` e `provas-fcc-fc3.md` versus a construção F-CC→B, principalmente `R3`, terminais em `W`, pares diretos e sobreposição S/T. Produzir prova fechada ou marcar `UNPROVEN`.
8. Reproduzir a estrela T18 por aritmética racional e as **duas direções** de bound `zLP(T18)=1/2` e `zLP(U)=1` sem depender de solver; observar que a testemunha é **sem K**.
9. Reproduzir as testemunhas Sec59 de objetivos `11/3` e `9/2`, conferir os limites inferiores estruturais e **distinguir** os dois cortes explicitados do conjunto K completo. Não afirmar F-CC=5 ou OPT=7 como resultados executados nesta fase.
10. Conferir que nenhuma evidência N1/N2/FC foi alterada; que T18 recebeu **apenas aviso de errata**; e que rótulos `PROVEN`/`UNPROVEN` refletem suporte real.

## Sensor de discriminação

Em uma cópia isolada, modificar uma das checagens do teste `test_as01_rational.py` para **não impor A5** e verificar que o caso fracionário da estrela deixa de ser rejeitado; restaurar imediatamente a cópia real. De modo análogo, enfraquecer o limite de entrada terminal U e verificar que a testemunha errada deixa de produzir a falha esperada. Não executar mutações no checkout real.

## Entrega de revisão

Atualizar `validation.md` com PASS/FAIL por AS01-01...AS01-07, referências `arquivo:linha`, provas ou contraexemplos e decisão final. Qualquer lacuna relevante em AS01-02 a AS01-05 é bloqueante para AS-02, ainda que a suíte automática passe.
