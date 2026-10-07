# Pré-registro R5 — diagnóstico de gap e platô (Spec C)

**Congelado em:** 2026-10-06T10:40:00-03:00
**Antes de:** qualquer medição desta spec (Γ novo, teste primal, anatomia do platô).
**Spec:** `specs/proxima-fase-c-diagnostico-gap-plato/spec.md`
**WorkLimit:** 164, de `docs/technical/reference/linha-de-base-pre-registro.md` §3. **Não** recalibrado aqui.
**GF1 (Spec B):** PASS (`docs/technical/reference/decisao-gf1.md`).

Este arquivo congela amostras, classes de Γ, teste primal, cap N, limiar de UB e a regra G1.

## 1. Definição de Γ

`Γ(I) = OPT(I) − OPT_core(I)`.

Núcleo = IP em `y` com C1+C2+C4-DM, o mesmo da linha de base.

### Classes (uma por instância; intervalo nunca vira valor)

| Classe | Quando | O que se reporta |
|---|---|---|
| `exact` | OPT e OPT_core ambos provados | o inteiro `Γ` |
| `lb` | OPT_core provado; OPT não; `LB*` existe | só o inteiro `max(0, LB* − OPT_core)`, marcado como limite inferior |
| `ub` | OPT_core provado; OPT não; `UB*` existe | o par de limites (`lb` e `ub` da tabela de intervalo), nunca um único número |
| `interval` | OPT_core provado; `LB*` e `UB*` da Spec A R4 existem; OPT não provado | `[max(0, LB* − OPT_core), UB* − OPT_core]` |
| `unknown` | núcleo **não** resolvido até otimalidade (status ≠ 2) | a palavra `unknown`; sem estimativa |

Na amostra D/A, R4 está disponível: a classe é `interval` (ou `exact` se algum braço da linha de base prova OPT, o que nas D/A de avanço **não** ocorreu). `lb`/`ub` isolados não se usam se os dois lados existem.

## 2. Amostra certificada de Γ

**Exact (OPT conhecido por certificado independente ou prova do solver):**

- Toda instância `principal` com `dificuldade = F` (ou legado) em que a linha de base tem `LB* = UB*` **e** o núcleo tem `mip_status = 2`. Fonte de OPT: solver da linha de base (`LB*=UB*`). Fonte do núcleo: braço `nucleo` status 2.
- SC-GF2 `k ∈ {3,4}`: OPT = `k` (teorema); núcleo esperado `k`.
- BP-"não": `q=2`, `B=10`, seeds de gerador `0` e `1` via `bp.plantar_nao` (`B=8` e `B=12` falham no gerador: sem tripleto ou a perturbação não quebra a partição). Certificado DP: sem partição ⇒ OPT = `2n+q+1`; núcleo esperado `2n+q`. Mais o caso minúsculo `[3,1]` `q=2` `B=2` (n=16) para o validador do platô.
- HB `q=4, ndir=2, p=1` e `q=5, ndir=2, p=1` (OPT por enumeração ou MIP da base, como F3).
- TR `k=2, L=5, r=2` (OPT pela fórmula; `Γ = 0`; instrumento de platô, não de `Γ > 0`).

**Interval (D/A, Spec A R4):** todas as `principal` com `dificuldade ∈ {D,A}` e `particao` contendo `desenvolvimento`, **exceto** `m ≥ 1000` (`hc12p.txt`, `puc-hc12p-seed-r1.txt`, `puc-w3c571-seed-r1.txt`).

F-class easy-by-selection: o relatório declara que `Γ` exacto em F pode subestimar D/A.

## 3. Teste primal (um fator)

| | Controle | Experimental |
|---|---|---|
| Modelo | COMP (U + C1+C2+C4-DM, `f` contínuo) | o mesmo |
| Orçamento | `WorkLimit = 164`, `TimeLimit = 1800` guarda | o mesmo |
| Threads | 4 | 4 |
| MIP start | nenhum | nenhum |
| Sementes | 42, 43, 44 | 42, 43, 44 |
| **Único fator** | `MIPFocus` padrão | `MIPFocus = 1` |

Controle: linhas `braco=comp` de `results/benchmark/linha_base.csv` (já executadas sob o mesmo contrato). Não se reexecuta o controle.

Instâncias: D/A da partição `desenvolvimento`, `m < 1000`.

Métricas: esquema T9 (LB, UB, gap, status, `NodeCount`, tempo primeiro/melhor incumbente, `Work`).

**Limiar de UB (congelado, primeira instância):** melhoria = `UB_controle − UB_foco ≥ 1` (uma estação; objectivo inteiro). Abaixo de 1 não conta.

Reprodução: a instância só conta se a melhoria vale nas **três** sementes. Uma semente só não reproduz (edge case da spec).

Família = prefixo do nome até o primeiro `-` (`mapf`, `puc`, `pucn`, `vienna`, `pace18`, …). `puc` e `pucn` são famílias distintas.

## 4. Platô (R7)

Instâncias (5):

1. `puc-cc9-2p-seed-r1.txt`
2. TR `k=2, L=5, r=2, m=2` (teste independente: 8 ótimos do núcleo, 2 viáveis — Apêndice B)
3. BP-"não" `[3,1]` `q=2` `B=2` (n=16; validador independente)
4. `mapf-maze-32-32-2-m10-f4.txt` (F, maze)
5. `lin-lin03-regiao-f4.txt` (F, lin)

`cc11-2u` fica de fora desta lista: n=2048, o cap N não cobriria o platô com custo comparável.

**Cap N = 200** ótimos do núcleo por instância. Se o pool truncar, reporta-se fracção coberta como desconhecida e os ≤200 gravados.

Por cada `C` gravado: estações, componentes de `H[C]`, corte `Z` do `integer_oracle`, origens sem emparelhamento, destinos incompatíveis; `viavel` do `independent_validator` se `n ≤ 16`.

**H-desc:** um `C` inviável é *caso H-desc* se o emparelhamento perfeito no grafo de pares realizáveis (directos em `D` ∪ bicliques `B(K)` das componentes de `H[C]`) falha. Veredito:

- CONFIRMED: todo `C` inviável gravado é caso H-desc, e nenhum `C` inviável deixa o emparelhamento viável
- PARTIALLY CONFIRMED: alguns sim, alguns não
- REFUTED: existe `C` inviável (oráculo ou validador) cujo emparelhamento por componentes seria viável

Sem CBI. Sem laço iterativo.

## 5. Regra G1 (congelada)

- **compatibility (LB) dominates** se, na amostra certificada *exact*, `Γ > 0` ocorre em pelo menos **duas famílias** **e** o teste primal **não** atinge o limiar de UB em pelo menos duas famílias → recomenda M-A; recomenda **também** M-F porque GF1 = PASS.
- **primal (UB) dominates** se o teste primal atinge o limiar em pelo menos duas famílias, reproduzido em 3 sementes, **e** na amostra *exact* `Γ` é zero em todas ou positivo em no máximo uma família → recomenda M-B.
- **both** se há `Γ > 0` em ≥ 2 famílias exact **e** o primal atinge o limiar em ≥ 2 famílias → LB-side primeiro (M-A, e M-F dado GF1), depois M-B.
- **no clear signal** caso contrário → nenhum método; devolve ao utilizador.

Não se abre método com leitura frouxa da regra.

## 6. Proveniência

Por linha: `sha256` da instância (manifesto ou gerador), commit, `sha256` de `cuts.py`, semente, threads, `work_limit`, fonte do certificado (solver / DP / enumeração / fórmula TR).
