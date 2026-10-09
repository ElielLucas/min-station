# N1-T6 — Microinstancias condicionais

**Estado:** `COMPUTATIONALLY VERIFIED` somente para valores medidos; `NOT MEASURED` para caps e timeouts. Este documento NAO aplica o gate N1-T7.

**Freeze SHA-256:** `60f4b533d76fdb1e6e05cd59123aa163ec50fe39e926e67edcd368aa5c50517c`
**Grafos SHA-256:** `ce4ce8d9672812043c2f97b25f1149bd3e006ba6b4fca626a64d189bf4ea9e40`
**Certificados SHA-256:** `405a1517c0d8a6ec49e2578c36b226daefa12e0429fa781621131abd683f323c`
**Pares pre-registrados:** 3; sem substituicoes pos-medicao.

## Protocolo e verificacao

- Cada par conserva V, S, T, n, m, r e o numero de arestas.
- O controle troca exatamente uma aresta unitaria definida no freeze.
- OPT certificado por `opt_por_enumeracao` (independente dos LPs).
- Atalhos e uso de terminais como estacoes auditados no JSON de certificados.
- O controle pode conter um atalho INTENCIONAL; nao e uma prova de ganho.

## Resultados

| Par | Familia | Variante | OPT | core IP | FCC+K | FC3+K | Δ trio | Status |
|---|---|---|---:|---:|---:|---:|---:|---|
| T6-TRI-01 | tri | obstruction | 2 | 2.0 | 1.5 | 2.0 | 0.5 | CERTIFIED |
| T6-TRI-01 | tri | control | 2 | 2.0 | 2.0 | 2.0 | 0.0 | CERTIFIED |
| T6-F2-01 | f2 | obstruction | 1 | 1.0 | 1.0 | 1.0 | 0.0 | CERTIFIED |
| T6-F2-01 | f2 | control | 0 | 0.0 | 0.0 | 0.0 | 0.0 | CERTIFIED |
| T6-SEC59-01 | sec59 | obstruction | 4 | 2.0 | 3.5 | 3.5 | 0.0 | CERTIFIED |
| T6-SEC59-01 | sec59 | control | 0 | 0.0 | 0.0 | 0.0 | 0.0 | CERTIFIED |

## Limites de interpretacao

- Resultados somente para os pares pre-registrados; nao ha busca sistematica.
- Uma diferenca positiva no LP nao e ganho computacional de tempo.
- Nenhuma linha com `NOT MEASURED` pode ser tratada como ganho zero.
- N1-T7 deve aplicar o gate PRE-EXISTENTE da spec, combinando T5 e T6.
- Se nenhuma promocao satisfizer os criterios, parar sem inventar outra familia.
