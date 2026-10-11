# AS-02 — Protótipo de A, oráculo físico e regressão Sec59

**Estado:** protótipo local testado com SciPy/HiGHS; **NÃO HOMOLOGADO**.  
**Branch de integração:** `novos_testes`.  
**Dependências:** AS-00 (universo D/A e pré-registro); AS-01 (provas matemáticas e revisão independente; última evidência recebida: pendente).  
**Spec:** `specs/as-02-prototipo-a/`.

## 1. Objetivo e fronteira

A AS-02 verifica, em instâncias pequenas, a exatidão física da formulação A por grupos e a regressão LP de Sec59. **Não** seleciona A2/A4 para benchmarking, não executa instâncias difíceis e não modifica `baseline.py`, `fcc.py`, T18, resultados FC/N1/N2 ou manifestos congelados. O gate AS-02 bloqueia qualquer promoção se as provas da AS-01 ou a verificação independente não forem aprovadas.

## 2. Código, contratos e origem de K

- `experiments/alternative-formulations/as02_model_a.py`: `Instance`, `compile_a`, `compile_u`, `build_A` (Gurobi), `prepare_K` e metadados. Partições inválidas são recusadas antes de criar o modelo Gurobi. O controle `compile_u` tem fluxo **contínuo**; seu objetivo LP equivale à relaxação da U histórica, sem sobrescrevê-la.
- `experiments/alternative-formulations/as02_solve.py`: `solve_gurobi` e backend **auxiliar de auditoria**, `solve_scipy`. Reporta `OPTIMAL`, `INFEASIBLE` ou `UNRESOLVED_*` sem imputar objetivos inexistentes.
- `experiments/alternative-formulations/as02_validation_gate.py`: estados explícitos, com `AS01_REVIEW_PENDING` padrão, `MATH_GATE_FAIL` se existe contraexemplo, `AS02_VALIDATION_FAIL`, `AS02_REVIEW_PENDING` e `PASS` somente quando todos os critérios externos são informados. Essa função **não cria atestados de revisão independente**.
- `experiments/alternative-formulations/test_as02_model_a.py`: enumeração de **todos os subconjuntos de estações** em sete instâncias pequenas, para dois tipos de partição; comparação de cada instalação contra `experiments/cuts/independent_validator.py::viavel`, que usa estados `(v,bateria)` no grafo original e matching bipartido, não o fluxo A ou U.
- `experiments/alternative-formulations/test_as02_sec59.py`: `Sec59(L=7,r=1)` do `experiments/cuts/synthetic.py`; K é exatamente a união deduplicada das famílias `C1+C2+C4-DM` produzidas pelos geradores históricos em `experiments/cuts/cuts.py`, validada por `assert_valid_cuts`. **K não contém C3 nem C6.**
- `experiments/alternative-formulations/test_as02_validation_gate.py`: falhas de matemática, revisão ausente, testes insuficientes e autorização.
- `experiments/alternative-formulations/run_as02_smoke.py`: teste pontual da tradução `build_A` para Gurobi, com Sec59; **não** publica resultados em `results/`.

## 3. Domínios e restrições

`y_v∈{0,1}` (ou `[0,1]` na relaxação), `f^B≥0`, `g^B≥0`, `p_{Bt}∈[0,1]`, `h^B_v∈[0,1]` para `v∈B∩T`. `f,g,p,h` permanecem contínuas mesmo no MIP. `A1`/`A2` são os dois balanços de grupo com permanência; `A3` impõe que cada destino receba 1 unidade no total; `A4` utiliza `c_{Bv}=|B|−1[v∈B]`; `A5` utiliza `κ_v=m−1[v∈S∪T]`; `A6` são os cortes K explícitos; `A7` minimiza `Σ y`.

**Importante:** a matriz `compile_a` define as mesmas linhas que o adapter `build_A` traduz para Gurobi. A validação local por SciPy executa essa mesma matriz, não uma fórmula alternativa da A. O adaptador propriamente dito exige teste no ambiente com licença Gurobi.

## 4. Evidência numérica local (não racional)

A regressão LP Sec59 esperada:

| Controle | Valor esperado | Observação |
|---|---:|---|
| U+K (= COMP+K) | 11/3 | Fluxo agregado contínuo, `y∈[0,1]` |
| A2+K, B₁={s1,s2}, B₂={s3} | 9/2 | Fluxo parcialmente desagregado |
| A com grupo único +K | 11/3 | Mesma projeção LP do controle U+K neste caso |

Comparações numéricas usam tolerância absoluta `1e−6`. **Não atribuir** força de certificado racional a `OPTIMAL` de LP.

## 5. Casos críticos

- Origem e destino sobrepostos `S∩T` e permanência de comprimento zero.
- Destino ou origem como vértice de trânsito que exige estação quando interior de caminho.
- Estação em terminal (permitida) e compartilhamento sem capacidade limite física.
- Grupos vazios, sobrepostos, origem omitida e duplicada dentro do mesmo grupo.
- Ausência de cortes vs `+K` é uma escolha explícita, não uma mudança silenciosa no braço.
- Sensor adverso: remover A5 reduz o LP da estrela de 1 para 1/2; o teste deve detectar a alteração.
- Status não resolvido, time limit e solver ausente **não** são tratados como viabilidade nem convertidos em resultado zero.

## 6. Validação no checkout real

```bash
python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-02-prototipo-a/spec.md
python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-02-prototipo-a/tasks.md
PYTHONHASHSEED=0 python3 -m unittest discover -s experiments/alternative-formulations -p 'test_as02*.py' -v
python3 experiments/alternative-formulations/run_as02_smoke.py
python3 -m ruff check experiments/alternative-formulations/as02*.py experiments/alternative-formulations/test_as02*.py experiments/alternative-formulations/run_as02_smoke.py
git diff --check
git status --short
```

O backend padrão dos testes é Gurobi quando `gurobipy` está instalado; caso contrário, é SciPy/HiGHS **se instalado**. A falha por ausência de ambos é um bloqueio explícito, não motivo para pular testes. Os testes não usam benchmark difícil, mas podem depender da licença Gurobi local.

## 7. Gate para avançar

1. AS-01 com parecer externo independente `PASS` (autor ≠ verificador), incluindo relações LP requeridas.
2. Matriz de rastreabilidade AS02-01..06 e checks por linha/domínio verificados com Gurobi no checkout.
3. Enumeração física e regressão Sec59 aprovadas, sem timeouts tratados como PASS.
4. Teste de discriminação e verificador independente AS-02 com evidências `file:line`.
5. Commits locais atômicos por tarefa conforme a skill (não executados neste pacote). Nenhum `git push` automático.

Na ausência de qualquer elemento: **NÃO PROMOVER** para AS-03/AS-05 ou campanha difícil.
