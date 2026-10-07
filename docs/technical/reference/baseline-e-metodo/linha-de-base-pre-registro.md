# Pré-registro da linha de base — Spec A R3

**Congelado em:** 2026-10-04T15:08:42-03:00
**Antes de:** qualquer linha do CSV da linha de base.
**Protocolo:** `protocolo-comparacao-pareada.md`.
**Partição:** `regra-particao-origem.md` (congelada, sem tag).

Este arquivo é o contrato da execução. Depois do primeiro `optimize` de célula
da linha de base, só se altera a §3 com o `WorkLimit` medido na calibração.
Nenhum braço, instância, semente ou métrica entra depois de ver resultado.

## 1. Braços

| Braço | Modelo | `f` | Cortes |
|---|---|---|---|
| `base` | formulação de `baseline.py`, variante U | inteiro | nenhum corte estático |
| `comp` | U + C1+C2+C4 | contínuo | `prepare_cuts` com C4 = C4-DM |
| `nucleo` | IP só em `y` (`yspace._build_ymodel`) | — | C1+C2+C4-DM |

Sem MIP start em qualquer braço. Sem braço experimental. Os três braços são
a referência (`LB*` / `UB*` = melhor LB / melhor UB entre braços e sementes).

## 2. Instâncias

As 75 linhas `classe = principal` de `instances/manifest.csv`.
Instâncias estruturais ficam de fora.

**Fora da avaliação de avanço** (correm, não entram em AV-1..AV-4):

| Instância | `m` | Motivo |
|---|---|---|
| `hc12p.txt` | 1024 | estagnação por escala, como no E12 |
| `puc-hc12p-seed-r1.txt` | 1024 | idem |
| `puc-w3c571-seed-r1.txt` | 1142 | idem |

## 3. Orçamento

Calibração, que **não** é célula da linha de base:

- instância pré-declarada: `instances/estrutural/bp/bp-nao-q8-B60-s0.txt`
  (a mesma do piloto da fase P, `bp-q8-nao-s0`);
- braço `base`, sem cortes;
- 4 threads (único fator que muda em relação ao piloto);
- `TimeLimit = 20` s, parâmetros padrão do solver, seed 42;
- fórmula do piloto: `WorkLimit = 600 × Work / parede`.

| Medida | Valor |
|---|---|
| Status | 9 (`TIME_LIMIT`) |
| `Work` | 5,5253 |
| Parede (s) | 20,232 |
| Taxa (work/s) | 0,2731 |
| `WorkLimit` | 164 |

`WorkLimit = 600 × 5,5253 / 20,232 = 163,85`, arredondado a 164 como o
piloto arredondou 296,8 a 297. A taxa é menor que a de 1 thread (0,4945):
`Work` do Gurobi não escala linearmente com as threads. Reusar 297 com 4
threads mudaria o orçamento em silêncio.

`TimeLimit = 1800` s fica só como guarda de parede. Se a guarda disparar
antes do trabalho, a linha permanece e ganha `guarda_parede=1`.

Threads: 4.

## 4. Sementes

Valores fixos: `42`, `43`, `44`.

- `dificuldade ∈ {D, A}`: as três sementes.
- `dificuldade ∈ {F, M}` ou vazia (as 5 legado sem classe de dificuldade):
  só a semente 42.

## 5. Métricas (esquema T9)

`schema-instrumentacao-mip.md`: LB (`mip_bound`), UB (`mip_obj`), gap,
status, `NodeCount`, tempo até o primeiro incumbente, tempo até o melhor,
tempo até a prova, `Work`. Mais `time_modelo_s` e `time_mip_s`.

## 6. Proveniência por linha

`sha256` da instância (coluna do manifesto), commit (`git rev-parse --short`
+ `-dirty` se a árvore estiver suja), `sha256` de `experiments/cuts/cuts.py`
(versão do gerador de cortes), semente, threads, `work_limit`, `guarda_s`,
`fonte_certificado=solver`.

## 7. AV-1..AV-4 — PENDING USER CONFIRMATION

Copiados de `plano-proxima-fase.md` §2. Não são requisitos imutáveis.

Condições comuns: mesmo `WorkLimit` em todos os braços, 3 sementes, sem MIP
start, protocolo pareado. Referências = melhor LB e melhor UB de qualquer
braço desta linha de base.

| # | Critério |
|---|---|
| AV-1 | Provar o ótimo de **≥ 3 instâncias D/A** que nenhum braço de referência prova, em ≥ 2 famílias |
| AV-2 | Reduzir a **mediana do gap certificado** `(UB−LB)/UB` das D/A em **≥ 25% relativos** contra a melhor referência, em ≥ 2 famílias, reproduzindo em 3 sementes |
| AV-3 | Formulação ou família de desigualdades **provada** que reduz `Γ` (§7) em **≥ 50%** nas amostras certificadas com `Γ > 0`, em ≥ 2 níveis de tamanho |
| AV-4 | Fechar `hc9u` ou estreitar `[32, 38]` em ≥ 3 unidades |

## 8. Checklist do protocolo pareado

Os três braços são o controle. Não há braço experimental nesta spec.

1. Variável entre braços: só o modelo (base / COMP / núcleo). Instância, hash,
   commit, gerador de cortes, seed, threads e orçamento são os mesmos na
   célula. **Cumprido.**
2. Um fator por comparação de braços. **Cumprido.**
3. D/A usam 3 seeds; margem de 1–2 unidades não fecha com 1 seed. **Cumprido.**
4. `NodeCount` e tempos de incumbente com `coletar_incumbente=True`. **Cumprido.**
5. Mesmo `WorkLimit` nos três braços; `TimeLimit` só como guarda. **Cumprido.**
6. Cada linha grava hash, versão dos cortes, commit, seed, threads e
   `fonte_certificado=solver`. **Cumprido.**

## 9. Como reproduzir

```text
python experiments/benchmark/run_linha_base.py --calibrar
# gravar WorkLimit na §3, depois:
python experiments/benchmark/run_linha_base.py --medir --work-limit 164
python experiments/benchmark/tabela_linha_base.py
```

Resume pelas linhas já gravadas em `results/benchmark/linha_base.csv`.
A ordem de execução é `n` crescente; o conjunto de células não muda.
