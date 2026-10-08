# R11 — conclusão dos certificadores de classes especiais

**Data:** 2026-10-07  
**Spec:** `specs/proxima-fase-d-certificadores-classes-especiais/spec.md`  
**Pré-registro:** `docs/technical/reference/experimentos/pre-registro-r11-certificadores.md`  
**Resultados:** `docs/technical/reference/experimentos/resultados-r11-certificadores.md`  
**Auditoria:** `docs/technical/reference/validacao-e-correcoes/auditoria-r11-divergencias.md`  
**CSV:** `results/structural/r11-certificadores.csv`

## Veredito

# CONFIRMED DIVERGENCE

O lote pré-registrado contém divergências confirmadas entre procedimentos publicados/lidos literalmente e a definição de MIN-STATION usada e validada no projeto.

O veredito se apoia em referências exatas consistentes e em contraexemplos pequenos/reduzidos.

---

## 1. Caminhos

`path-alg1`, implementação literal de Das Algorithm 1, teve:

```text
3 agreement
12 suboptimal
0 infeasible
0 unspecified
```

A divergência é estrutural e pode ser reduzida ao caminho `v0-v1`, `S={v0}`, `T={v1}`, `r=1`: o procedimento coloca uma estação em `v0`, enquanto `OPT=0`.

Logo, **Algorithm 1 literal não pode ser usado como certificador exato do MIN-STATION corrente**.

---

## 2. Ciclos

`cycle-alg2` teve:

```text
2 agreement
9 suboptimal
```

Algorithm 2 resolve cada quebra chamando Algorithm 1 e herda sua supercontagem. O mecanismo reduz a um ciclo de três vértices com alvo adjacente à origem e `r=1`, onde Algorithm 2 retorna 1 e `OPT=0`.

Logo, **Algorithm 2 literal também não pode ser usado como certificador exato**.

---

## 3. Aranhas

Não há uma única leitura executável fechada pela fonte em todos os casos. As três leituras R11 produziram:

- `spider-A`: 6 agreements, 1 suboptimal, 8 soluções inviáveis, 3 unspecified;
- `spider-B`: 5 agreements, 10 suboptimal, 3 unspecified;
- `spider-U`: 3 agreements, 5 soluções inviáveis, 10 unspecified.

O caso SP-R2 é suficiente para mostrar a limitação:

- A/U devolvem apenas `{c}`, conjunto inviável, contra `OPT=2`;
- B devolve conjunto viável de cardinalidade 3, contra `OPT=2`.

Assim, **nenhuma das leituras R11 pode ser promovida a certificador exato universal**.

A conclusão sobre aranhas é deliberadamente mais restrita do que “o Teorema 1 é falso”: o texto publicado não especifica um único procedimento completo para todos os silêncios identificados. A evidência confirma divergência das leituras executáveis testadas e insuficiência da fonte para o papel de certificador independente sem reconstrução adicional.

---

## 4. Validade das referências

O veredito não depende de uma única formulação:

- enumeração independente foi usada em todo o estrato micro;
- baseline terminou `OPTIMAL` em todo o lote;
- F-CC binária terminou `OPTIMAL` e coincidiu com o ótimo em todo o lote;
- não houve `reference_failure`;
- F-C3 permaneceu `OPEN`.

Portanto não há, na evidência R11, sinal de que as divergências principais sejam artefatos da referência exata.

---

## 5. Consequências para o projeto

1. **R11 está encerrada.** O objetivo de verificar se caminhos/ciclos/aranhas poderiam servir como certificadores exatos independentes foi respondido negativamente no estado literal das fontes.

2. **Path/cycle publicados não entram como oráculos exatos** em R8/R9/R10 sem uma nova formulação combinatória corrigida e uma nova prova/validação.

3. **Aranhas não entram como oráculo exato** enquanto o procedimento completo não for formalizado além das lacunas SP-R1–SP-R5.

4. Os casos R11 passam a ser **testes negativos/regressões estruturais** úteis para qualquer futura correção dos algoritmos.

5. Baseline, enumeração e F-CC continuam sendo as referências exatas disponíveis dentro de seus respectivos caps/protocolos.

6. F-C3 continua `OPEN`; R11 não altera esse estado.

7. O veredito não reabre GF1 ou G1.

---

## 6. Comunicação

Os resultados podem ser usados internamente para orientar a pesquisa.

Antes de qualquer alegação pública de erro, erratum ou refutação de resultado publicado:

```text
COMMUNICATION REQUIRED BEFORE PUBLIC CLAIM
```

A comunicação/revisão com os autores é uma atividade posterior e não faz parte do escopo encerrado desta spec.

---

## 7. Critério de encerramento

A R11 satisfaz o stop criterion porque:

- leituras e variantes estão versionadas;
- geradores/certificadores foram verificados localmente;
- regressões BP/HB/SC/TR e F-CC passaram;
- lote e hashes foram congelados antes da execução oficial;
- as 44 instâncias produziram as 80 linhas esperadas;
- não houve falha de referência;
- divergências foram auditadas e reduzidas por mecanismo quando prático;
- o relatório de resultados existe;
- esta conclusão existe.

**Estado final: COMPLETE — CONFIRMED DIVERGENCE.**
