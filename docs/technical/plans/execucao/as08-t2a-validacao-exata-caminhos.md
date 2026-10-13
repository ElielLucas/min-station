# AS-08 · T2a — Validação exata de B por enumeração de caminhos

**Status:** IMPLEMENTADO · CONTROLE EXPLORATÓRIO · revisão científica independente pendente.

## Relação com a spec

Complementa a T1 (formalização e prova B ≡ A unitária, pendente de revisão independente) e precede a T2 (pricing) de `specs/as-08-formulacao-b-caminhos/tasks.md`. **Não altera ou marca como concluída** nenhuma tarefa da spec original. Deve ser registrada como etapa de verificação T2a antes de autorizar T2b/T3/T4.

## Entregáveis

- `experiments/alternative-formulations/as08_b_exact.py` — enumerador exato de **todos os caminhos simples** no dígrafo de alcance para cada origem e destino; inclui `(s)` se `s∈T`, permite destinos como vértices internos, e recusa truncamento ao alcançar o cap. Compila B0–B4 e cortes BK. Para eficiência, B4 é instanciada em `T\S` (equivalente à versão completa pela prova de T1). `global_links=False` existe **somente como controle mutante F-h**, não como alternativa autorizada.
- `experiments/alternative-formulations/run_as08_t2a.py` — runner reprodutível com 10 instâncias pequenas, comparação LP B × A unitária × COMP, repetida sem K e com o **mesmo K C1+C2+C4-DM**; verificação de fibras por instalações `y` binárias exaustivas e amostragem determinística de fibras fracionárias; MIP B comparado com ótimo por enumeração e validador físico original.
- `experiments/alternative-formulations/test_as08_t2a.py` — testes de contratos, exemplo que refuta F-h sem B4, validação física, casos `S∩T`, sensores de integridade e de truncamento.

## Controles e interpretação

1. B é **completa** nos casos executados: caminhos são enumerados sem omissões; um cap excedido retorna `INCOMPLETE` e **nunca** um LP aparentemente ótimo de um master restrito.
2. `LP(B)=LP(A_unit)` é testada numericamente (valor e viabilidade para diversas fibras `y`), mas **não é prova** de igualdade de projeções. A prova matemática de T1 permanece sujeita a review autor≠verificador.
3. `LP(B) >= LP(COMP)` é um controle de dominância, não uma igualdade esperada. Todos os braços com K compartilham os mesmos cortes.
4. A viabilidade física independente no grafo original é testada para **todas as instalações binárias** em cada caso, até o limite seguro de tamanho.
5. A enumeração de soluções inteiras físicas determina `OPT`, e o MIP B com `y` binário deve concordar.
6. `OPTIMAL` é status **numérico do solver**; não confundir com certificado racional, nem com LB global de geração de colunas.
7. O output é append-only em diretório novo, com `results.json`, SHA256 e `analysis.md`. `--verify` verifica hash, schema, conjunto de casos e a coerência do estado. Não refaz todo o solve: a validação é realizada na execução.

## Execução (a partir da raiz do repositório)

```bash
PYTHONPATH=. poetry run python -m unittest discover \
  -s experiments/alternative-formulations -p 'test_as08_t2a.py' -v

PYTHONPATH=. poetry run python \
  experiments/alternative-formulations/run_as08_t2a.py \
  --backend gurobi \
  --output-dir results/benchmark/as08-t2a-exact-001

PYTHONPATH=. poetry run python \
  experiments/alternative-formulations/run_as08_t2a.py \
  --verify --output-dir results/benchmark/as08-t2a-exact-001
```

Para computadores sem Gurobi, `--backend scipy-highs` é alternativa de teste se SciPy estiver disponível. O projeto original trabalha principalmente com Gurobi.

## Resultados no ambiente de desenvolvimento (SciPy/HiGHS)

- Testes T2a: **16/16 PASS**.
- Suíte `experiments/alternative-formulations -p test_as*.py`: **62 PASS**.
- Suíte `experiments/formulation-comparison -p test_as*.py`: **141 PASS**, com arquivos de referência do ZIP disponíveis.
- Runner local: **10/10 casos `PASS`**, **com e sem K**, comparando LPs, fibras inteiras e fracionárias, MIP e viabilidade física.
- Uma instalação com falta de caminho, linha B4 mutada ou caminhos truncados é capturada por sensores de teste.
- A execução com Gurobi deve ser repetida no ambiente do pesquisador; o ambiente de desenvolvimento desta entrega **não tem Gurobi**.

## Limites e continuidade

A enumeração pode ter crescimento exponencial. O runner **não** foi concebido para `puc-w3c571` ou `vienna-I056` e não deve ser usado como evidência de escalabilidade. Casos maiores requerem um oráculo de pricing validado contra este enumerador (T2b), seguido de master restrito, auditoria dos duais e certificador LB global (T3); só então um piloto de custo de representação (T4).

**Gate desta etapa:** `PASS_EXPLORATORY` nas 10 instâncias e testes específicos aprovados, sujeito a execução independente no ambiente do projeto. Isso **não** autoriza automaticamente promover B para benchmark final nem marca a spec AS-08 como concluída.
