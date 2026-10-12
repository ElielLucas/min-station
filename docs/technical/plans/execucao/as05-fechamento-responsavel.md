# AS-05 — Fechamento técnico por autorização do responsável

**Data:** 2026-10-11  
**Classificação:** `OWNER_AUTHORIZED_EXPLORATORY`  
**Plano pré-registrado:** `results/benchmark/as05-prospective-plan-v1.json`  
**SHA-256 canônico:** `193a0fb1812c10e502d2e086d9dc2e1f857b724046955bbb0684ad99c038ef3b`

## Decisão de gestão do projeto

O responsável solicitou expressamente finalizar a AS-05 e autorizou avançar com a execução. Esta autorização permite **concluir a implementação e rodar a triagem LP exploratória** nas seis instâncias de desenvolvimento já pré-registradas, mesmo com homologações AS-01/AS-02/AS-04 pendentes.

A autorização **não é** a revisão matemática independente, não atribui `PASS` à AS-01/AS-02/AS-04 e não certifica a validade universal dos modelos/cortes. O fluxo de execução científica `--execute` original permanece restrito. O fluxo excepcional usa `--execute-exploratory` e grava a autorização junto ao relatório com hash de integridade. Não habilita AS-06 nem altera registros históricos.

## Escopo fixo

- **6 instâncias** de desenvolvimento AS-00, sem avaliação.
- **3 braços:** `U`, `U_K`, `A2_K`.
- **Orçamento por braço:** 90 s de parede; **Gurobi**, quatro threads; seeds 42, 43 e 44 quando a reprodução for exigida.
- **Partição constante** entre seeds; **A4 OFF** no plano atual.
- Manter dados censurados e observações sem solução no denominador; não imputar limites.
- O resultado preliminar `screening_decision.verdict` pode ser `GO`, `STOP` ou `INVESTIGATE`, mas `decision.verdict` da execução exploratória fica em `INVESTIGATE` por não haver homologação externa.

## Status real

| Marco | Estado |
|---|---|
| Implementação AS-05 | Fechada para triagem exploratória pelo responsável |
| Testes / validação local | Aprovados nos cenários executados |
| Pré-registro AS-00/AS-05 | Preservado, sem alteração |
| Parecer independente AS-01/AS-02/AS-04 | Pendente (sem declaração fictícia) |
| Campanha LP real no Gurobi do responsável | Não executada neste ambiente |
| Decisão científica para AS-06 | Pendente dos resultados e homologação |

## Execução local autorizada

```bash
PYTHONPATH=. python3 experiments/formulation-comparison/run_as05_pilot.py \
  --check-plan results/benchmark/as05-prospective-plan-v1.json

PYTHONPATH=. python3 experiments/formulation-comparison/run_as05_pilot.py \
  --execute-exploratory \
  --plan results/benchmark/as05-prospective-plan-v1.json \
  --gate-file docs/technical/plans/execucao/as05-gate-evidence-REVISADO.json \
  --owner-authorization docs/technical/plans/execucao/as05-owner-authorization-exploratory.json \
  --output-dir results/benchmark/as05-pilot-owner-exploratory-001
```

O último comando inicia de fato os *solves* no computador que tem o Gurobi, caso a autenticação e as dependências estejam disponíveis. Usar novo diretório de saída em cada tentativa; os relatórios são append-only.

## Verificação de integridade

```bash
PYTHONPATH=experiments/formulation-comparison:. python3 - <<'PY'
from pathlib import Path
from as05_pilot import verify_pilot
report = verify_pilot(Path('results/benchmark/as05-pilot-owner-exploratory-001'))
print('Classe:', report['execution_class'])
print('Triagem:', report['screening_decision']['verdict'])
print('Homologacao cientifica:', report['scientific_homologation'])
print('Casos:', len(report['cases']))
PY
```

## Condições para alegações na dissertação

Só utilizar o resultado exploratório como **triagem/desenvolvimento preliminar** com a ressalva de ausência de revisão independente. Não publicar `GO` científico nem conclusões de superioridade generalizada a partir do piloto. Para promoção científica, preservar o histórico e obter os pareceres externos necessários.
