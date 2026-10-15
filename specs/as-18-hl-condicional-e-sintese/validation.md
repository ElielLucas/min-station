# AS18 — Validação do encerramento condicional

**Data:** 15/10/2026  
**Resultado:** síntese documentada; HL `NOT_AUTHORIZED`, AS17 `NOT_AUTHORIZED`.  
**Gate automático AS16:** `INVESTIGATE` preservado; **decisão de pesquisa** AS16 `STOP` mantida separadamente.

## Matriz de aceitação

| AC | Verificação / estado |
|---|---|
| AS18-01 | Gate de autorização documentado, não há hipótese estrutural independente aprovada; `NOT_AUTHORIZED` |
| AS18-02 | Não executado: nenhum suporte R selecionado porque o gate está fechado; precondição ν(V\R) documentada |
| AS18-03 | Não executado: nenhum teste de ν(V\R)=m realizado nesta fase |
| AS18-04 | Não executado: nenhum β exato calculado para HL |
| AS18-05 | Não executado: nenhuma enumeração HL nem padrões UNKNOWN gerados |
| AS18-06 | Não executado: nenhum coeficiente HL racionalizado |
| AS18-07 | Não medido: quatro relés 2, 8/3, 3 não reproduzidos nesta fase |
| AS18-08 | Não medido: nenhuma comparação LP/MIP de HL contra pool H2 |
| AS18-09 | Síntese documental produzida; separa resultados LP H2, ausência MIP/HL, argumentos teóricos, hipótese analítica e limites bibliográficos |

## Verificação local

- `experiments/cuts/verify_as18_gate.py`: confere 36 registros, seis casos com grafos brutos distintos, braços, status, censuras, cálculo de ganhos e preservação de gate.
- `experiments/cuts/test_as18_gate.py`: testes adversariais para fraude de contagem, braço duplicado, divergência de objetivo, censura alterada, ausência de fonte e origem indevidamente repetida.
- `specs/as-18-hl-condicional-e-sintese/as18-gate-evidence.json`: saída reproduzível que registra cinco comparações ótimas, zero ganhos e um censurado, logo máximo um ganho possível para exigência de dois.

```bash
python -m unittest discover -s experiments/cuts -p 'test_as18_gate.py' -q
python experiments/cuts/verify_as18_gate.py --as16-dir results/benchmark/as16-lp-h2-001
python .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-18-hl-condicional-e-sintese/spec.md
python .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-18-hl-condicional-e-sintese/tasks.md
```

**Limites de conclusão:** os testes do gate **não** constituem revisão matemática independente, certificação de HL ou execução MIP. T2 e T3 são deliberadamente não executadas, não concluídas. Os scripts formais estruturais não certificam conteúdo matemático. Revisão por autor diferente do verificador ainda sem evidência; não alegar aprovação independente.
