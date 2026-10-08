# N1-T3 — Implementação da F-C3 e validação independente

**Data de criação:** 2026-10-07. **Estado:** `IMPLEMENTED — NOT COMPUTATIONALLY VERIFIED`.

## Autoridades e preservação

- Spec: `specs/proxima-fase-n1-informacao-compatibilidade/spec.md`, story 3.
- Definição matemática: `docs/technical/reference/formulacoes/formulacao-fc3-canonica-v1.md` (v1.0.1), após MR-F3 aceito documentalmente.
- SOURCE: `docs/technical/reference/formulacoes/formulacao-fc3-componentes-trios.md` (inalterada).
- Não alterar `baseline.py`, `experiments/alternative-formulations/fcc.py`, `experiments/alternative-formulations/run_f3.py`, modelos históricos ou CSVs históricos.
- A verificação `viavel` é a referência independente; não usar F-C3 para certificar OPT.

## Arquivos desta etapa

| Arquivo | Responsabilidade |
|---|---|
| `experiments/alternative-formulations/fc3.py` | F-CA: CA0–CA6, redes C31–C34, F-C3 + K, caps, APIs LP |
| `experiments/alternative-formulations/verify_fc3_n1.py` | Equivalência por instalação (F-C3, F-C3 + K, F-CC + K), invariantes LP e OPT por enumeração |
| `experiments/alternative-formulations/source_controls_fc3_n1.py` | Controles exatos SOURCE §§8–9 e instalação com duas componentes |
| `experiments/alternative-formulations/test_fc3_structure_n1.py` | Testes estruturais independentes de Gurobi |

## Como executar

Da raiz do repositório, com Gurobi instalado/licenciado, execute na seguinte ordem:

```bash
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/alternative-formulations -p test_fc3_structure_n1.py -v

PYTHONHASHSEED=0 python experiments/alternative-formulations/verify_fc3_n1.py

# Controles analíticos, somente APÓS validação completa:
PYTHONHASHSEED=0 python experiments/alternative-formulations/verify_fc3_n1.py --source-regressions
```

O segundo comando verifica **todas as instalações** de cada instância da bateria, das viáveis e inviáveis, em ambas as direções. Uma única divergência aborta antes do diagnóstico LP; investigar a instalação e o sentido. `--source-regressions` pode ser caro: reconstrói os exemplos SOURCE g=2 e ciclo C5 e respeita todos os caps. Se algum exceder tamanho, registrar `NOT MEASURED`, nunca `sem ganho`.

Após sucesso, o script gera **arquivos novos** (não inclusos neste patch porque não foram executados com Gurobi):

- `n1-t3-validacao.csv`
- `n1-t3-lp-invariantes.csv`
- `n1-t3-source-regressoes.csv` (quando a opção for usada)

## Protocolo e critérios de aceite

1. Conferir MR-F3 documentalmente aceito; isso não é validação por solver.
2. Executar `test_fc3_structure_n1.py` (arcos `R=∅`, 35 arcos por etapa em elegibilidade plena, caps, controles SOURCE).
3. Executar `verify_fc3_n1.py`: casos Direct0, TermRelay, TermRelayForced, StayPut, StayPutIsolado, CaminhoABC, SharedTerminal, MultiComp-N1 e Tri. Abrange `S∩T`, permanência, terminal como relé, `m≥3`, solução multicomponente e instalações ótimas/não ótimas (por enumeração).
4. Exigir **zero** divergências `viavel→F-C3`, `F-C3→viavel`, `viavel→F-CC+K` e `F-CC+K→viavel` (também é checada F-C3+K). Qualquer divergência suspende medições.
5. Só após passar todas as instalações, calcular LP com mesmo K; testar `F-C3≥F-CC−1e-6`, `F-C3+K≥F-CC+K−1e-6`, e todas as quatro relaxações `≤ OPT+1e-6`.
6. Nos dois controles SOURCE, conferir valor 4 para g=2 e 2.5 para C5 **apenas se couberem nos caps**. Divergência exige investigação, não adaptação da fórmula.
7. Não usar os LPs de N1-T3 como diagnóstico congelado N1-T5: essa tarefa exige pré-registro, reprodução F3 e conjunto fixo de instâncias.

## Registro de execução (preencher após testes locais)

| Verificação | Estado antes de executar com Gurobi | Evidência |
|---|---|---|
| Código importável/compilável | `COMPUTATIONALLY VERIFIED` (estático) | `py_compile` |
| Testes estruturais sem solver | consultar log de execução | teste `test_fc3_structure_n1.py` |
| Equivalência por instalação F-C3/F-CC+K | `NOT MEASURED` | CSV de validação |
| Dominância LP e `LP≤OPT` | `NOT MEASURED` | CSV de invariantes |
| Exemplos SOURCE §§8–9 | `NOT MEASURED` | CSV de regressões |

**N1-T3 não é considerada concluída** até execução bem-sucedida do script com Gurobi e revisão dos resultados. Sem medição de LP, não iniciar N1-T5.
