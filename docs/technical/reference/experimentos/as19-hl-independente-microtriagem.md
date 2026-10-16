# AS19 — Microtriagem independente de HL sobre COMP+K

**Data:** 15/10/2026  
**Decisão:** HL permanece em investigação **separada de H2**. `MICRO_VALIDATED` no K4, **sem GO computacional em instâncias reais**.

## Por que a AS19 existe

A AS16 demonstrou ausência de benefício marginal de H2 sobre COMP+K em cinco comparações LP ótimas. O gate AS18 bloqueou HL **naquele protocolo condicional**, que usava H2 como premissa operacional. Matematicamente HL é mais geral: combina padrões com mais de uma estação instalada e pode cortar soluções LP que satisfazem a família H2 inteira. O pesquisador autorizou explicitamente uma microinvestigação independente de HL; não se alteraram os resultados ou gates anteriores.

## Construção e certificado

Quatro relés `W={w1,w2,w3,w4}` recebem seis pares exclusivos de origem/destino, cada par conectado apenas a seus dois relés. A condição física demonstrada na AS13 é `|C∩W|≥3`. A geração HL toma `R=W` e `F=V\W`. O oráculo físico examinou **os 16 padrões** de `R` e certificou que `β_W(1)=3`; portanto:

\[
\sum_{w\in W} y_w\ge 3.
\]

No ponto fracionário `y_w=2/3` para os quatro relés (zero nos demais vértices), a família H2 não o elimina conforme prova AS13, mas a linha HL tem violação `3-8/3=1/3`. O microteste foi reproduzido resolvendo o **COMP+K compilado pelo projeto**, com scipy/HiGHS, em vez de usar números preenchidos manualmente.

| Relaxação LP | Limite inferior medido | Interpretação |
|---|---:|---|
| COMP+K | 2 | Seis coberturas de pares K |
| COMP+K + H2 dos quatro trios | 2,66666667 | H2 fortalece K no K4 |
| COMP+K + os quatro H2 + HL | 3 | HL fortalece adicionalmente |

**Risco de originalidade:** no K4, a linha HL pode ser derivada por arredondamentos de K. Isso **não** demonstra nova desigualdade além do fecho inteiro/CG de K nem ganho prático em outra instância.

## Custo e limites

- 16 chamadas ao oráculo por suporte de tamanho quatro (o complemento também corresponde ao padrão vazio), em ordem determinística.
- A execução registra tempos de certificação, solve LP de cada formulação e hashes estáveis em `results/benchmark/as19-hl-micro-k4-001.json`. Consultar o arquivo para números exatos: uma execução local é ruidosa e não autoriza inferência de aceleração.
- Suportes de tamanho até oito por padrão; cada aumento de uma posição duplica o máximo de padrões. `UNKNOWN`, erro ou orçamento insuficiente **não** são prova de inviabilidade.
- O runner não usa e não altera Gurobi, resultados AS16, K existente ou MIP. Nenhum benchmark real foi executado.

## Próxima decisão científica

**Avançar apenas à triagem real de baixo custo**, em uma próxima etapa pré-registrada: selecionar suportes de até oito posições nas mesmas instâncias de desenvolvimento AS16 (sem tocar no conjunto de avaliação), obter `y*` de COMP+K e comparar o incremento exato de cortes HL sobre COMP+K e COMP+K+pool H2 sob o mesmo orçamento. Relatar proporção de abstenções, custo total (preparação, oráculo e reotimização), cortes certificados, ganhos e censuras. Se não aparecer ganho sobre K em grafos independentes, encerrar HL; se houver sinal, propor piloto pareado com controles e revisão externa.

**Classificação final:** `MICRO_VALIDATED / PRACTICAL_EFFECT_UNTESTED`; não confundir prova de validade do corte, testemunha LP sintética e eficácia em benchmark.
