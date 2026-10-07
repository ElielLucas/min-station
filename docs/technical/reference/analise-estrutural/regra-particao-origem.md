# Regra de partição por grafo de origem

**Status:** escrita em 2026-10-04, **antes** de qualquer reatribuição de `particao`.
**Tarefa:** Spec A R2 / `plano-proxima-fase.md` R2.
**Não usa** LB, UB, gap, tempo, nós ou qualquer outro resultado de método.

## 1. O que a regra decide

Cada linha de `instances/benchmark-v1/` recebe `desenvolvimento` ou `avaliacao`.
Todas as variantes com o mesmo `instancia_original` caem no mesmo lado.

Linhas em `instances/estrutural/` continuam `estrutural`.
As demais linhas (legado em `instances/*.txt`) continuam `legado`.

## 2. Função

Seja `o` o valor de `instancia_original` (string UTF-8).

```
h = SHA-256(o)
lado(o) = desenvolvimento  se  int_be(h) ≡ 0 (mod 3)
          avaliacao        caso contrário
```

`int_be` lê o digest de 32 bytes como inteiro sem sinal, big-endian.

A fração esperada é cerca de 1/3 desenvolvimento e 2/3 avaliação, no conjunto
dos grafos de origem. A regra **não** é ajustada depois para forçar essa
fração em famílias pequenas. A razão obtida por família é só relatada.

## 3. O que a regra não faz

- Não olha `dificuldade`, `lb`, `ub`, `lb_melhor`, `ub_melhor` nem CSVs de resultado.
- Não move uma variante para o lado oposto da irmã.
- Não reescreve correções manuais (C4-DM, colunas H17).
- Não cria a tag `benchmark-v1.0` (só com autorização explícita de commit).

## 4. Família

Família = segundo componente do caminho (`instances/benchmark-v1/<família>/...`).
A tabela antes/depois entra na §5 depois da reatribuição; esta seção 1–4
congela a regra.

## 5. Resultado da reatribuição

Aplicada em 2026-10-04 por `build_manifest.py --repartir-origem`, depois de
`--estrutural` ter acrescentado as 12 SC da Fase E. A regra das §§1–4 não
mudou. Tag `benchmark-v1.0`: **congelado, sem tag** (sem autorização de commit).

Verificador: `experiments/benchmark/verify_t8_consolidacao.py` → `ok`, 0 vazamento.
Duas aplicações seguidas da regra reproduziram a coluna `particao` byte a byte.

12 linhas novas, todas `classe=estrutural`: `sc-gf2-k8`, `sc-gf2-k9`,
`sc-rigida-k{8,9}-s{100..104}`. Total do manifesto: 149 (75 `principal`,
57 estruturais). Correções C4-DM e colunas H17 intactas.

### Antes (partição por variante, 1 em 3)

| Família | Variantes D/A | Origens D/A |
|---|---|---|
| mapf | 5 / 8 | 5 / 8 |
| pace2018 | 2 / 4 | 2 / 4 |
| puc | 6 / 12 | 6 / 11 |
| pucn | 2 / 4 | 2 / 3 |
| steinlib-b | 3 / 5 | 3 / 5 |
| steinlib-i | 2 / 4 | 2 / 3 |
| steinlib-lin | 2 / 2 | 2 / 2 |
| urbano | 2 / 3 | 2 / 3 |
| vienna | 2 / 2 | 2 / 2 |

11 grafos com vazamento. Snapshot: `specs/proxima-fase-a-fundacao/particao-antes-r2.csv`.

### Depois (SHA-256 de `instancia_original`)

| Família | Variantes D/A | Origens D/A | Fração D (origens) |
|---|---|---|---|
| mapf | 1 / 12 | 1 / 12 | 0,08 |
| pace2018 | 3 / 3 | 3 / 3 | 0,50 |
| puc | 11 / 7 | 8 / 4 | 0,67 |
| pucn | 4 / 2 | 4 / 1 | 0,80 |
| steinlib-b | 6 / 2 | 3 / 2 | 0,60 |
| steinlib-i | 0 / 6 | 0 / 5 | 0,00 |
| steinlib-lin | 2 / 2 | 1 / 2 | 0,33 |
| urbano | 1 / 4 | 1 / 3 | 0,25 |
| vienna | 3 / 1 | 2 / 1 | 0,67 |

Conjunto das 56 origens de `benchmark-v1`: 23 desenvolvimento, 33 avaliação
(fração D = 0,41). Variantes: 31 / 39.

`steinlib-i` ficou inteira em avaliação. A regra não foi ajustada
(caso previsto: famílias pequenas podem desviar). 29 linhas já existentes
mudaram de lado.

### Fora do D/A

`legado` e `estrutural` não entram na fração. `hc9u.txt` continua legado;
`puc-hc9u-seed-r1.txt` é duplicata estrutural e recebeu o lado do hash de `hc9u`.
