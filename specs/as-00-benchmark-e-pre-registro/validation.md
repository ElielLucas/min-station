# AS-00 — Relatório de implementação e verificação preliminar

**Data:** 2026-10-11  
**Veredito de implementação:** testes funcionais PASS; **gate de encerramento PENDENTE**.  
**Verificador independente (autor ≠ verificador):** não executado neste ambiente.  
**Commits locais por tarefa:** não executados no repositório original; os arquivos foram preparados a partir de um ZIP, em cópia de trabalho isolada.

## Cobertura dos critérios de aceite

| Requisito | Resultado observado | Evidência de teste |
|---|---|---|
| AS00-01 | 31 casos, hashes de G/S/T/A_r, 2 aliases equivalentes e 1 par divergente, integridade dos hashes | `experiments/benchmark/test_as00_protocol.py:29`, `experiments/benchmark/test_as00_protocol.py:49`, `experiments/benchmark/test_as00_protocol.py:51`, `experiments/benchmark/test_as00_protocol.py:63` |
| AS00-02 | Cap, memória, budget e erro não retiram instâncias do denominador e não imputam zero | `experiments/benchmark/test_as00_protocol.py:70`, `experiments/benchmark/test_as00_protocol.py:73`, `experiments/benchmark/test_as00_protocol.py:81` |
| AS00-03 | MAPF room m10/m25 relacionados; proveniência ausente rejeitada | `experiments/benchmark/test_as00_protocol.py:89`, `experiments/benchmark/test_as00_protocol.py:93`, `experiments/benchmark/test_as00_protocol.py:99` |
| AS00-04 | Piloto, 10 grafos brutos distintos na avaliação, budgets, seeds, hashes e bloqueio de overwrite | `experiments/benchmark/test_as00_protocol.py:104`, `experiments/benchmark/test_as00_protocol.py:117`, `experiments/benchmark/test_as00_protocol.py:130`, `experiments/benchmark/test_as00_protocol.py:136` |
| AS00-05 | Checksums de artefatos N1/N2/FC preservados durante geração | `experiments/benchmark/test_as00_protocol.py:145` |

## Gates executados

- `validate_spec.py`: 0 erros, 0 avisos.
- `validate_tasks.py`: 0 erros, 0 avisos.
- `unittest discover -s experiments/benchmark -p 'test_as00*.py'`: **13/13 PASS**, sem skips (execução final isolada).
- `compileall`: PASS.
- `sha256sum -c protocol.sha256`: PASS.
- Sensor de discriminação em scratch: **2/2 mutações detectadas**, árvore original preservada.
  - `comparison_eligible=True` convertido em `False`: teste AS00-02 falhou como esperado.
  - `mkdir(exist_ok=False)` convertido em `True`: teste AS00-04 falhou como esperado.

## Bloqueios antes de declarar AS-00 concluída

1. O gate full exige `python -m ruff check experiments/benchmark`, mas **Ruff não está instalado** neste ambiente. Compilação não substitui lint exigido.
2. A skill exige um verificador independente, autor distinto do implementador. A checagem local e o sensor de mutações não satisfazem essa independência formal.
3. A skill exige **um commit local atômico por tarefa**. Este pacote não foi aplicado ao checkout Git real do usuário; nenhuma alteração remota e nenhum commit no repositório original foram realizados.
4. `validate_state.py` exige a estrutura `.specs/features`; o projeto utiliza `specs/` e permanece sem migração automática.

## Próximos passos de fechamento no checkout real

- Integrar os arquivos sem sobrescrever os resultados congelados.
- Instalar/disponibilizar Ruff e executar o gate completo.
- Fazer a revisão independente, confrontando ACs e resultados. Registrar veredito PASS/FAIL com evidências.
- Reconciliar a política de commits da skill com o checkout real e atualizar `tasks.md`/rastreabilidade antes de cada commit.

**Conclusão:** implementação testada e artefatos gerados, mas **AS-00 ainda não deve ser marcada como oficialmente concluída** até sanar os bloqueios do gate.
