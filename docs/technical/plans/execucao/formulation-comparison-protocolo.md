# Comparação formulação base × F-CC+K — protocolo experimental (novo, independente da N2)

**Estado:** `PILOTO HISTÓRICO EXECUTADO` (FC-04 corrige os critérios de auditoria, sem sobrescrever os CSVs antigos); bateria principal de 3.600 s/execução **não** executada
automaticamente (ver §8). **Independente da N2**: não reabre, não mede nem reinterpreta a decisão
`N2 FAIL` (`docs/technical/plans/execucao/n2-t6-gate-decisao-cientifica.md`). Não altera N1/N2, o
freeze N2-T1, resultados históricos, ou arquivos congelados.
**Branch:** `novos_testes`. **Commit no momento do piloto:** `fc9c1a2d87db63a95670e3510df6c5953b6d922f`
(`git status` sujo apenas pelos arquivos novos listados em §9; nenhum arquivo rastreado foi alterado).
**Código:** `experiments/formulation-comparison/`. **Resultados:** `results/formulation-comparison/`.

> **Atualização FC-03 (2026-10-10) — prevalece sobre rótulos históricos abaixo.**
> Os valores de `GRB.OPTIMAL`, `ObjBound` e `ObjVal` são **evidência numérica
> do solver**, não certificados racionais verificados independentemente. A nova
> publicação usa `solver_numeric_*`, `rational_verified_*` e `physical_feasible_ub`
> como eixos separados. `PAIR_VALID` significa integridade do par, e não
> otimalidade racionalmente demonstrada. Os CSVs antigos e o encerramento
> `N2 FAIL` ficam preservados. As medições e frases históricas deste documento
> são relatos da campanha anterior, não evidência racional adicional.

## 1. Objeto da comparação

**A. Formulação base (Das, variante U):** `baseline.construir_modelo_baseline` — `y` binário em
todo `V`, fluxo agregado `f` sobre o dígrafo de alcance `A_r`, balanço unificado que admite
`S∩T≠∅` (ver `docs/context-ai/base-formulation.md`). Não alterada.

**B. F-CC+K, forma completa (não a geração de colunas da N2):**
`experiments/alternative-formulations/fcc_k.build_fcc_plus_k`/`lp_fcc_plus_k` — configurações
conectadas `(W,I,J)` por **enumeração total**, mais os cortes `K = C1+C2+C4-DM`
(`experiments.cuts.harness.prepare_k`). Esta é a forma validada por P1/P7 e por 878 instalações
sem divergência contra `independent_validator.viavel` (N1-T3), **não** o master restrito/pricing da
N2-T2B (que a N2-T6 encerrou com `N2 FAIL` por ausência de ganho certificado sobre `B0`). Usar a
forma completa, em vez da geração de colunas, é uma decisão deliberada de design: só ela produz um
LP/IP **exato**, comparável ao LP exato da formulação base — o objetivo do master restrito da N2
não é, e nunca foi, um limite inferior certificado (ver revisão v2.1 §2.2, §6.1).

## 2. Auditoria matemática (antes de programar)

| Item | Base (U) | F-CC+K completo |
|---|---|---|
| Variáveis | `y_v∈{0,1}` todo `v`; `f_{u,v}≥0` inteiro sobre `A_r` | `y_v∈{0,1}`; `λ_q≥0` por configuração `q=(W,I,J)`; `d_{s,t}≥0` por par direto |
| Objetivo | `min Σy_v` | `min Σy_v` (idêntico) |
| Restrições | balanço de fluxo por vértice + ativação por `y` (`in≤b+(m-b)y`, `out≤a+(m-a)y`) | R1/R2 (atendimento de origem/destino), R3 (`Σλ≤y`), `K` |
| Domínio de `y` | binário (MIP) / contínuo `[0,1]` (LP) | idem |
| Autonomia/conectividade | arcos de `A_r` (`d_G≤r`) | `W` conexo em `H=G^r`; elegibilidade por `B(W)` |
| `S∩T` | balanço unificado, Lema 5 de Das (robô fica parado) | `d_{s,s}` nos pares diretos; papéis `I`/`J` independentes |
| Viabilidade física | emparelhamento bipartido fracionário integral (prova histórica da base) | P1 (`PROVEN`): `y` binário viável ⟺ instalação física viável |

**Mesmo problema de otimização?** Sim, para o MIN-STATION de Das com estações em todo `V` e
autonomia comum — ambas minimizam `|C|` sujeitas à mesma noção de viabilidade física. P2
(`PROVEN`, `provas-fcc-fc3.md`) prova `z_LP(base) ≤ z_LP(F-CC)`; com `K` idêntico nos dois lados,
a cadeia observada é `lp_base ≤ lp_comp ≤ lp_fcc_k ≤ OPT`, confirmada empiricamente em todas as
instâncias tratáveis (§5).

**Comparação direta é válida no estado atual da implementação?** Só a forma **completa** de
F-CC+K (LP e IP por enumeração total) é diretamente comparável, formulação a formulação, à base.
A geração de colunas da N2 **não** produz esse valor: o objetivo do master restrito é uma cota
*superior* do LP completo (nunca inferior), e a única tentativa de certificar um limite inferior
global a partir dela (N2-T3) terminou sem ganho sobre `B0` (N2-T6). Reutilizar esse mecanismo aqui
confundiria formulação, relaxação e algoritmo de solução — exatamente o erro que este protocolo
deve evitar.

## 3. Modalidades efetivamente comparáveis

- **Modalidade A — LP completo.** `lp_base` (base sem cortes), `lp_comp` (base + `K`, = COMP da N1),
  `lp_fcc_k` (F-CC+K com enumeração completa). `GRB.OPTIMAL` libera o valor como
  `solver_numeric_lp_objective`, sob tolerâncias numéricas; `rational_verification`
  permanece `NOT_CERTIFIED` na ausência de verificador independente.
- **Modalidade B — MIP completo.** `comp_mip` (`y` binário, fluxo contínuo,
  com K) e `fcc_k` (com o mesmo K) compõem o par principal; `baseline` sem K é
  apenas ablação. `ObjBound` de um MIP completo pode constituir
  `solver_numeric_mip_lb` mesmo se `TIME_LIMIT`, inclusive sem incumbente,
  mas **não** é certificado racional. MIP restrito/incompleto e pricing nunca
  publicam seu bound como LB global. A incumbente numérica é separada do
  `physical_feasible_ub`, que depende de `independent_validator.viavel` e
  corresponde à cardinalidade inteira da instalação validada. Sem LB racional
  independente mais UB físico, `certified_gap_status=INCONCLUSIVE`.
- **Modalidade C — evolução.** Coletada como subproduto do mesmo solve de Modalidade B, via um
  único callback compartilhado pelas duas formulações (`fc_core.EvolutionTracker`), nos marcos
  1/5/10/30/60/120/300/600/1800/3600 s. Cada ponto registra o **tempo real observado** na primeira
  chamada de callback em que esse marco já foi cruzado — nunca interpolado para trás.

**Limite reconhecido:** Modalidade A/B de F-CC+K só se aplica onde a enumeração de `(W,I,J)` é
tratável (§4). Acima do cap, a linha é `NOT_MEASURED_CAP_EXCEEDED` — nunca 0, nunca omitida, nunca
substituída pelo diagnóstico da N2.

## 4. Sondagem de tratabilidade (achado central)

Antes de escolher instâncias, sondou-se `fcc.enumerar_conexos` (contagem de `W` conexos em
`H=G^r`, sem resolver LP/IP) em 18 candidatas, cap `max_W=200000`, guarda de parede de 15 s:

| Instância | classe | n | m | r | `n_W` | Resultado |
|---|---|---:|---:|---:|---:|---|
| bp-nao-q2-B2-s0 | estrutural | 16 | 4 | 1 | 2836 | tratável |
| hb-q4-ndir2-p1-k1-L2 | estrutural | 16 | 6 | 1 | 9341 | tratável (= `n_W_raw` congelado N1-T5) |
| tr-k2-L5-r2-sig2-m2 | estrutural | 18 | 2 | 2 | 152971 | tratável |
| bp-sim-q2-B2-s0 | estrutural | 19 | 4 | 1 | 16238 | tratável |
| hb-q5-ndir2-p1-k1-L2 | estrutural | 21 | 8 | 1 | 163616 | tratável |
| sc-gf2-k3 / sc-rigida-k3-s0 | estrutural | 21 | 7 | 1 | >200000 | **acima do cap** |
| bp-nao-q2-B3-s0 | estrutural | 23 | 6 | 1 | 167618 | tratável (maior ponto encontrado) |
| hb-q6-ndir1-p6-k1-L2 | estrutural | 23 | 11 | 1 | 130148 | tratável |
| hb-q6-ndir1-p2-k1-L2 | estrutural | 25 | 11 | 1 | >200000 | acima do cap |
| tr-k3-L5-r2-sig2-m2 | estrutural | 25 | 2 | 2 | >200000 | acima do cap |
| bp-sim-q2-B3-s0 | estrutural | 26 | 6 | 1 | >200000 | acima do cap |
| hb-q6-ndir1-p1-k1-L2 | estrutural | 28 | 11 | 1 | >200000 | acima do cap |
| hb-q8-ndir1-p1-k1-L2 | estrutural | 38 | 15 | 1 | >200000 | acima do cap |
| sc-gf2-k4 | estrutural | 45 | 15 | 1 | >200000 | acima do cap |
| b-b06-intercalado-f2 | **principal** | 50 | 12 | 2 | >200000 | acima do cap |
| pucn-cc6-2n-seed-r1 | **principal** | 64 | 6 | 1 | >200000 | acima do cap |
| pace18-t2-001-regiao-f2 | **principal** | 74 | 12 | 4 | >200000 | acima do cap |

**Conclusão empírica, reproduzida em `test_comparison.py::InstancePoolTests` e em
`fc_instances.tractability_probe`:** a enumeração completa de `(W,I,J)` deixa de ser tratável por
volta de `n≈23–26` para as famílias HB/BP (dependendo da densidade específica), e já falha no
**menor** tamanho disponível das famílias SC e TR mais densas. As **três instâncias `classe=principal` efetivamente sondadas** neste levantamento
(`b-b06-intercalado-f2`, `pucn-cc6-2n-seed-r1` e
`pace18-t2-001-regiao-f2`) ultrapassaram o cap utilizado. **As demais
instâncias do universo de 75 não foram sondadas** e não devem ser declaradas
intratáveis a partir desses três resultados. Nas famílias HB/BP examinadas,
a fronteira depende da estrutura específica: há casos tratáveis com 23 vértices
e casos acima do cap com 25 ou mais. Não há teorema nem evidência de
inviabilidade universal para a F-CC+K completa no benchmark-v1.

Isso **não** é uma reinterpretação do `N2 FAIL`: é uma constatação independente, sobre uma
propriedade diferente (a enumeração completa, não a geração de colunas), que explica por que as
duas abordagens de F-CC+K (completa e via CG) têm limites de escala distintos e ambos aquém do
benchmark-v1.

## 5. Lotes de instâncias

- **Piloto** (`fc_instances.PILOT_NAMES`, 2): `hb-q4-ndir2-p1-k1-L2` (referência histórica N1-T5),
  `bp-nao-q2-B2-s0`.
- **Principal** (`MAIN_NAMES`, 6 = piloto + 4): adiciona `hb-q5-ndir2-p1-k1-L2`,
  `hb-q6-ndir1-p6-k1-L2`, `bp-sim-q2-B2-s0`, `bp-nao-q2-B3-s0` — duas famílias estruturais (HB, BP),
  dois níveis de tamanho cada, todos confirmados tratáveis em §4.
- **Escalabilidade** (`SCALABILITY_NAMES`, 10): predominantemente instâncias **acima** do cap (HB em 3 tamanhos, BP,
  SC em 2 controles da mesma família, TR em 2 tamanhos) mais duas `classe=principal` reais
  (`b-b06-regiao-f2`, `pucn-cc6-2n-seed-r1`) para medir a formulação base isoladamente na escala do
  benchmark oficial, documentando onde F-CC+K completo para de responder.

`lin23`/`lin37` excluídas por instrução explícita (e são `classe=historico`, fora de
`principal`/`estrutural`). Nenhuma instância foi criada, gerada ou alterada.

## 6. Configuração

| Parâmetro | Piloto (executado) | Principal (parcial, ver §8) | Bateria completa (não executada) |
|---|---|---|---|
| Solver | Gurobi 12.0.3 | idem | idem |
| Threads | 4 | 4 | 4 |
| Seed | 42 | 42 | 42 |
| `TimeLimit` (Modalidade B) | 120 s | 120 s | **3600 s** |
| `TimeLimit` LP (Modalidade A) | 60 s | 60 s | 600 s (teto de segurança) |
| `max_W` (cap de enumeração F-CC+K) | 200.000 | 200.000 | 200.000 |
| Memória | `resource.ru_maxrss` do processo (KB, Linux, cumulativo — **não** isolado por chamada) | idem | idem |
| SO / Python | Linux 6.8.0-146-generic / Python 3.12.3 | idem | idem |

Na campanha histórica, a ordem de execução intercalava `baseline`/`fcc_k` e alterna qual roda primeiro por instância
(`run_comparison._order_tasks`), para reduzir viés de aquecimento. A partir da FC-01 o limite de tempo é **global de parede por braço**, desde
inicialização e preparação até resolução e validação; não é somente o
`TimeLimit` de `model.optimize()`. Os relatos anteriores descrevem uma
versão antiga do executor.

## 7. Resultados do piloto (reais, 2026-10-10)

`results/formulation-comparison/pilot-20261010T071017Z/` (`results.csv`, `evolution.csv`,
`manifest.json`, `run.log`). **0 falhas.**

| Instância | lp_base | lp_comp | lp_fcc_k | OPT base | OPT F-CC+K | Validação física |
|---|---:|---:|---:|---:|---:|---|
| hb-q4-ndir2-p1-k1-L2 | 0,3333 | 1,0 | 2,0 | 2,0 | 2,0 | ambas `True` |
| bp-nao-q2-B2-s0 | 3,0 | 6,0 | 7,0 | 7,0 | 7,0 | ambas `True` |

`lp_base=1/3`, `lp_comp=1`, `lp_fcc_k=2` para `hb-q4-ndir2-p1` **reproduzem exatamente** os valores
congelados em `results/alternative-formulations/n1-t5-diagnostico.csv` (regressão automatizada em
`test_comparison.py::ModalityATests::test_reproduces_frozen_n1_values`). As duas formulações
chegam ao mesmo ótimo inteiro nas duas instâncias, e as instalações encontradas por cada uma
passam independentemente no oráculo `independent_validator.viavel`.

Itens de verificação do piloto (§8 do pedido): ambas representam a mesma instância (mesmo
`instance_sha256`, mesmo `S,T,V,adj,A_r` passados às duas); resultados consistentes entre si e com
a história; soluções validadas fisicamente; nenhum limite inferior racional atribuído sem verificador independente
(os resultados `GRB.OPTIMAL` são numéricos); tempo/Work contabilizados e plausíveis;
orçamento (120 s) nunca atingido; CSV/JSON/log gerados e íntegros; nenhum resultado inconclusivo
classificado como sucesso (testado explicitamente com `sc-gf2-k3`, que devolve
`NOT_MEASURED_CAP_EXCEEDED`, nunca um valor).

### 7.1 Evidência adicional de escala reduzida (não é a bateria de 1 hora)

Para reforçar o piloto sem comprometer o teto de 3.600 s, executaram-se também os lotes
`scalability` (`TimeLimit=60s`) e `main` (`TimeLimit=120s`) — ainda dentro do regime de piloto
(≤120 s/execução), não a bateria principal:

- **`scalability-20261010T071119Z`** (10 instâncias, 0 falhas): o
  `results.csv` contém **9/10 instâncias distintas com `fcc_k=CAP_EXCEEDED`**
  (18 linhas CAP em A/B) e **1/10 com `fcc_k=OPTIMAL`**
  (`tr-k2-L5-r2-sig2-m2`). A contagem histórica 8/10 estava incorreta;
  contar por instância evita dupla contagem. As
  instâncias acima do cap de F-CC+K terminam `NOT_MEASURED_CAP_EXCEEDED` antes
  mesmo de montar o MIP; a formulação base resolve as 10, inclusive as duas `classe=principal`
  reais (`b-b06`: OPT=3 em 0,05 s; `pucn-cc6-2n`: OPT=6 em 0,20 s), e `tr-k2-L5-r2-sig2-m2`
  (tratável) reproduz `lp_fcc_k=OPT=3`, igual à base — um caso em que F-CC+K **não** melhora o LP.
- **`main-20261010T071251Z`** (6 instâncias, **0 falhas**, confirmado em `manifest.json`):
  revela que, mesmo dentro do cap de enumeração, o **custo** de F-CC+K completo cresce
  rapidamente — `hb-q5-ndir2-p1` levou **141,8 s** só para o LP (`n_vars` da ordem de `10^5`)
  contra `0,004 s` da base, e **47,7 s** para o IP (`Work=38,9`) contra `0,015 s`/`Work=0,002` da
  base; `bp-nao-q2-B3` levou **92,4 s** (LP) e **35,1 s** (IP). Em todas as 6 instâncias as duas
  formulações reportaram o mesmo ótimo numérico (`GRB.OPTIMAL`, sem certificado racional independente) e a
  instalação encontrada por cada uma passou em `independent_validator.viavel`. Gráficos reais
  (`fc_plot_evolution.py`, pontos exatamente como gravados, sem interpolação):
  `results/formulation-comparison/main-20261010T071251Z/evolution-hb-q5.png` e
  `evolution-bp-nao-q2-B3.png` — mostram a base em `LB=UB=OPT` desde `t≈0` enquanto F-CC+K completo
  ainda tem `LB=0`/`UB` alto por dezenas de segundos antes de fechar o gap.

  | Instância | lp_base | lp_comp | lp_fcc_k | Δ(comp→fcc_k) | OPT (ambas) |
  |---|---:|---:|---:|---:|---:|
  | hb-q4-ndir2-p1 | 0,3333 | 1,0 | 2,0 | +1,0 | 2 |
  | bp-nao-q2-B2 | 3,0 | 6,0 | 7,0 | +1,0 | 7 |
  | hb-q5-ndir2-p1 | 0,375 | 1,0833 | 3,0 | +1,9167 | 3 |
  | hb-q6-ndir1-p6-k1 | 0,4545 | 1,0 | 1,0 | **0** | 1 |
  | bp-sim-q2-B2 | 3,0 | 8,0 | 8,0 | **0** | 8 |
  | bp-nao-q2-B3 | 3,0 | 8,0 | 9,0 | +1,0 | 9 |

  Em 4 das 6 instâncias `lp_fcc_k>lp_comp` (ganho de LP sobre COMP, consistente com o padrão
  `Δ_FCC+K>0` de N1-T7 nas famílias HB/BP); em 2 (`hb-q6-ndir1-p6-k1`, `bp-sim-q2-B2`) o LP
  completo de F-CC+K **iguala** COMP, sem ganho adicional — um resultado negativo real, registrado
  como tal, não omitido. Em todas as 6, `lp_fcc_k=OPT` (o LP completo já fecha o gap inteiro nestas
  instâncias pequenas), mas a base precisa do MIP (tempo desprezível) para fechar o mesmo gap.

## 8. Avaliação de prontidão para a bateria principal (3.600 s)

**Apto para iniciar, com uma ressalva de custo.** O piloto não revelou nenhum problema de
corretude matemática, certificação indevida ou contabilidade; a cadeia `lp_base≤lp_comp≤lp_fcc_k≤OPT`
e a identidade de instância entre formulações se confirmam em todos os casos tratáveis testados.
A ressalva: o Modality-A/B de F-CC+K completo é **caro** mesmo dentro do cap de enumeração (minutos
por instância em `n≈21-23`), então a bateria de 3.600 s/execução deve ser orçada por família×nível
(principal: 6 instâncias × 2 formulações × {A,B} ≈ até 12 execuções de até 1 h cada na pior
hipótese, embora a Modalidade A costume terminar bem antes do teto). Recomenda-se:

1. Rodar primeiro a bateria principal **só** para o lote `main` (6 instâncias), com
   `--time-limit 3600`, monitorando;
2. Rodar `scalability` com tempos mais curtos (ela já documenta o cap, não precisa de 1 h por
   execução para instâncias que falham na enumeração antes de montar o modelo);
3. **Não** executar indiscriminadamente F-CC+K completo nas demais
   instâncias `classe=principal` antes de uma sondagem controlada. Nas três
   instâncias principais sondadas o cap foi ultrapassado; **isso não equivale
   à impossibilidade de enumerar todas as 75**. Aumentar `max_W` mudaria
   custo e escopo experimental e exigiria novo pré-registro.

## 9. Comandos de execução local

```bash
# Piloto (já executado nesta sessão; pode ser reexecutado)
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py --tier pilot

# Bateria principal (3.600 s por execução de MIP; Modalidade A tem teto de segurança de 600 s)
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py --tier main \
    --time-limit 3600 --lp-time-limit 600 --threads 4 --seed 42

# Escalabilidade (documenta a fronteira do cap; tempos menores já bastam)
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py --tier scalability \
    --time-limit 600 --lp-time-limit 120

# Testes
PYTHONHASHSEED=0 python -m unittest discover -s experiments/formulation-comparison \
    -p test_comparison.py -v

# Lint
python -m ruff check experiments/formulation-comparison/*.py
```

Cada execução cria `results/formulation-comparison/<tier>-<timestamp>/`, sem sobrescrever
execuções anteriores.

## 10. Arquivos

- `experiments/formulation-comparison/fc_instances.py` — carregamento e seleção de instâncias.
- `experiments/formulation-comparison/fc_config.py` — configuração e manifesto de ambiente.
- `experiments/formulation-comparison/fc_core.py` — Modalidades A/B/C (reusa `baseline.py`,
  `experiments/cuts/harness.py`, `experiments/alternative-formulations/fcc.py`/`fcc_k.py`,
  `experiments/cuts/independent_validator.py`).
- `experiments/formulation-comparison/fc_reporting.py` — CSV/JSON/manifesto de reprodutibilidade.
- `experiments/formulation-comparison/run_comparison.py` — CLI.
- `experiments/formulation-comparison/test_comparison.py` — 23 testes (todos executados; ver §12).
- `experiments/formulation-comparison/README.md` — guia rápido.
- `results/formulation-comparison/pilot-20261010T071017Z/`,
  `.../scalability-20261010T071119Z/`, `.../main-20261010T071251Z/` — artefatos reais desta sessão.

Nenhum arquivo de `experiments/alternative-formulations/`, `experiments/cuts/`, `baseline.py`,
N1/N2, `instances/manifest.csv` ou `results/alternative-formulations/` foi alterado.

## 11. Limitações explícitas

1. F-CC+K completo (A/B) só é comparável onde a enumeração de `(W,I,J)` é tratável (§4); fora
   dela, a linha é `NOT_MEASURED_CAP_EXCEEDED`, nunca uma estimativa.
2. Memória é `resource.ru_maxrss` do processo Python inteiro, cumulativa entre chamadas — não um
   isolamento preciso por execução; serve como indicador grosseiro, não como medição de pico por
   instância isolado.
3. A sondagem efetivamente mediu **três instâncias `classe=principal`**, todas acima do cap;
   **72 não foram testadas pela sondagem**. Não extrapolar 3/75 para 75/75.
   O limite de enumeração observado é experimental e não demonstra impossibilidade
   matemática ou computacional nas outras 72.
4. A bateria de 3.600 s/execução não foi executada (§8); os números de §7.1 usam orçamentos
   reduzidos (60–120 s) e já indicam custo crescente rápido de F-CC+K completo mesmo dentro do cap.
5. Esta comparação não usa, não mede e não certifica a geração de colunas da N2; qualquer
   conclusão sobre "F-CC+K" aqui se refere à forma completa por enumeração, e deve ser lida como
   tal — não como uma reabertura ou resultado adicional da N2.

## 12. Testes executados (reais)

```
PYTHONHASHSEED=0 python -m unittest discover -s experiments/formulation-comparison \
    -p test_comparison.py -v
...
Ran 23 tests in 35.808s
OK

python -m ruff check experiments/formulation-comparison/*.py
All checks passed!
```

## FC-03 — Contrato de evidência e leitura dos novos relatórios

A partir da versão `evidence_schema=FC03-v1`, a coluna legada `certification`
publica `NOT_CERTIFIED` por padrão. Apenas uma prova racional externa
**efetivamente aceita** por verificador independente, vinculada ao contexto
verificado e à instância, permitiria `RATIONAL_VERIFIED`. O executor atual
**não executa** tal verificador. `model_context_sha256` é o hash da identidade
canônica de contexto (instância, formulação, modalidade, K e completude), **não**
um hash da matriz de restrições ou uma prova da correção matemática da
formulação.

| Eixo | Campos novos | Interpretação |
|---|---|---|
| Numérico | `solver_evidence`, `solver_numeric_status`, `solver_numeric_lp_objective`, `solver_numeric_mip_lb`, `solver_numeric_mip_incumbent`, `solver_numeric_gap_*`, `solver_optimality_reported` | Dados de ponto flutuante de modelo completo; não são uma prova racional |
| Racional | `rational_verification`, `rational_verified_lb_exact`, `rational_proof_id`, `rational_proof_sha256`, `rational_verifier_id`, `rational_checked_*` | Vazios/`NOT_CERTIFIED` até verificador matemático independente |
| Viabilidade física | `physical_ub_status`, `physical_feasible_ub`, `physical_ub_provenance` | Valor inteiro do conjunto de estações validado pelo oráculo físico |
| Gap certificado | `certified_gap_status`, `certified_gap_abs_exact`, `certified_gap_rel_exact` | `INCONCLUSIVE` sem LB racional global e UB físico da mesma instância |

Por segurança, os campos legados ambíguos `lb_best`, `ub_best`, `gap_abs`,
`gap_rel`, `optimality_proven`, `time_to_proof_s` permanecem vazios no CSV
FC03-v1. Para os tempos numéricos usar `solver_time_to_optimal_s`. As colunas
`lb`/`ub` de `evolution.csv` são apenas **amostras numéricas do callback**,
sinalizadas com `evidence_source=SOLVER_NUMERIC_CALLBACK_NOT_RATIONAL`.

`results/formulation-comparison/` anterior à FC-03 **não é migrado nem
reescrito**; comparar saídas de versões diferentes exige distinguir o schema.
A fase N2 continua fechada com `N2 FAIL`.


## FC-04 — Identidade por bytes, manifesto e contagens verificáveis

**Regra normativa para novas execuções (`artifact_schema=FC04-v1`):**

1. `fc_instances.load_instance` confere os dois hashes presentes no manifesto
   de entrada: `sha256` cobre **todos os bytes brutos**, enquanto
   `sha256_conteudo` cobre o texto sem linhas `# meta:` conforme a regra
   original do projeto. Ambos são recomputados. Campos ausentes recebem
   `NOT_DECLARED`, não são tratados como conferidos.
2. O loader confere `n`, `m`, `r`, `r_arquivo`, `r_usado`,
   `arestas_nao_dirigidas` e `arcos_arquivo` contra os dados lidos, além
   dos cabeçalhos `N`/`M` do arquivo. Divergência gera `INTEGRITY_ERROR`
   **antes do solver**. Métricas derivadas não recalculadas (por exemplo
   planaridade e treewidth) aparecem como `UNSUPPORTED`, nunca `MATCH`.
3. `manifest.json` enumera SHA-256 de `code_files_sha256`,
   `input_files_sha256`, `generated_files_sha256` com caminhos relativos à
   raiz do repositório. Cobre os módulos `fc_*.py`, código base/cortes/F-CC+K,
   CSVs, log, resumo e PNGs produzidos **antes de finalizar**.
   `manifest.sha256` contém o hash externo do próprio JSON, evitando
   referência circular. Ele detecta corrupção acidental do manifesto, mas
   **não é assinatura criptográfica autenticada**; arquive a cópia/assinatura
   em local independente se precisar de proteção contra adulteração maliciosa.
4. Execute `verify_comparison_artifacts.py <run_dir>` para uma auditoria
   **somente leitura**. Um arquivo medido ou script modificado, ausente,
   desconhecido ou com caminho fora do repositório causa `INTEGRITY_FAIL`.
   Um gráfico adicionado depois da finalização também invalida o inventário;
   use `--plots` no executor para publicar PNGs antes do manifesto.
5. O lote `scalability` publica `scalability_summary.json` calculado a partir
   de `results.csv`, agrupando por **instância única** e considerando tanto
   `lp_fcc_k` (A) quanto `fcc_k` (B), com categorias
   `CAP_EXCEEDED`, `OPTIMAL_NUMERIC`, `INCONCLUSIVE` e `NOT_TESTED`. A
   auditoria recompõe o resumo independentemente do gerador. **Os casos
   não selecionados não são inferidos**. No arquivo histórico
   `scalability-20261010T071119Z/results.csv`, foram 9/10 instâncias acima
   do cap (não 8/10); isso não atesta 75/75 principais.

Comandos para novas execuções (não auditam retroativamente manifestos antigos):

```bash
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py \
  --tier pilot --modalities A,B --formulations comp_mip,fcc_k,baseline \
  --time-limit 120 --lp-time-limit 60 --plots

python experiments/formulation-comparison/verify_comparison_artifacts.py \
  results/formulation-comparison/pilot-<TIMESTAMP>/

PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/formulation-comparison -p 'test_fc04_*.py' -v
```

**Limite de interpretação:** a auditoria FC-04 demonstra consistência e
recomputabilidade dos bytes e das contagens, **não demonstra otimalidade
racional**. Permanecem vigentes `NOT_CERTIFIED` e `INCONCLUSIVE` da FC-03,
e a decisão congelada `N2 FAIL`.
