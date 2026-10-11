# MIN-STATION — FC-05: protocolo para nova rodada de piloto e decisão de gate

**Situação:** executor implementado; rodada FC-05 com Gurobi **ainda não executada nesta entrega**. Não confundir com os pilotos anteriores de FC-02, FC-03 ou FC-04.

## 1. Pergunta e âmbito

Avaliar se o procedimento de comparação inteira **COMP+K × F-CC+K** está operacionalmente pronto para investigação ampliada, após reparos FC-01–FC-04. Verificar orçamento total por braço, hashes de instâncias/cortes/arquivos, enumeração completa, validade física de incumbentes e interpretação de evidência do solver.

Esta execução **não** estuda geração de colunas da N2; o fechamento científico `N2 FAIL` permanece inalterado. Nenhum ganho teórico ou de escalabilidade é presumido.

## 2. Desenho pré-especificado

| Campo | Escolha |
|---|---|
| Tier | `pilot` |
| Instâncias | `hb-q4-ndir2-p1-k1-L2.txt`; `bp-nao-q2-B2-s0.txt` |
| Modalidade A | `lp_base`, `lp_comp`, `lp_fcc_k` completos |
| Par MIP primário | `comp_mip` (estações binárias, fluxo contínuo, K) × `fcc_k` (formulação completa com o mesmo K) |
| Ablação | `baseline` sem K, registrada separadamente |
| Tempo por LP | 60 segundos end-to-end |
| Tempo por MIP | 120 segundos end-to-end |
| Orçamento para extra | Nenhum; `--tier main` e FC-06 nunca são disparados pelo gate |
| Ordenação | Alternância entre as formulações principais conforme índice da instância |
| Custos observados | `wall_total_s`, `solver_runtime_s`, `work`, preparação, validação e status |
| Arquivos | Novo `results/formulation-comparison/pilot-<timestamp>/`, com SHA-256 e sidecar |

## 3. Gate verificável

O executor publica `pilot_gate.json` e `pilot_report.md` **antes** do fechamento do manifesto. São artefatos candidatos, incluídos no inventário de arquivos. O verificador separado `verify_comparison_pilot.py` reabre `results.csv` + `manifest.json`, confere a auditoria FC-04 dos bytes, recalcula os requisitos e somente então decide:

- **`READY_FOR_EXTENDED`**: inventário íntegro; todas as instâncias e braços previstos presentes; resultados `OPTIMAL` completos; identidades de entrada e K concordantes; K inteiramente aplicado e validado; tempos totais dentro dos tetos; incumbentes MIP inteiras fisicamente validadas; valores LP numericamente coerentes com as UBs; nenhuma linha escondida ou erro global.
- **`NOT_READY`**: algum dos requisitos acima não atendido, incluindo timeout/cap, ausência de braço, testemunha não validada, artefato alterado, manifesto inconsistente ou estatística incompleta. Cada instância permanece no denominador e são registrados motivos específicos.

`READY` atesta somente **prontidão operacional desta amostra**, sem certificação racional matemática, superioridade estatística ou obrigação de prosseguir.

## 4. Comandos de execução

```bash
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py \
  --tier pilot --modalities A,B \
  --formulations comp_mip,fcc_k,baseline \
  --lp-time-limit 60 --time-limit 120 --plots
```

Depois, substituindo `<RUN_REAL>` pelo caminho que o comando efetivamente imprimiu:

```bash
python experiments/formulation-comparison/verify_comparison_artifacts.py <RUN_REAL>
python experiments/formulation-comparison/verify_comparison_pilot.py <RUN_REAL>
```

## 5. Registro de execução — preencher após rodada real

**Rodada FC-05:** não disponível nesta entrega. **Diretório:** não disponível. **Commit e estado Git:** ver manifesto da rodada. **SHA do manifesto:** não disponível. **Gate final:** ainda não avaliado com Gurobi.

Transcrever *somente* números e status de `results.csv`, `manifest.json`, `pilot_gate.json` e da verificação final correspondente à mesma rodada. Citar datas, diretório e checksums. Para cada instância incluir LP base/COMP/FCC, MIP COMP+K/FCC+K, wall, Work, status, K, UB física e razão de censura, quando houver. Evitar proporção de sucesso com denominador que exclua linhas incompletas.

## 6. Interpretação e decisão sobre 3.600 segundos

Um gate `READY_FOR_EXTENDED` é condição necessária, **mas não suficiente** para FC-06. Antes de investir uma hora por braço, exigir casos **não triviais**, orçamento total viável, hipótese de ganho definida e plano registrado de comparação justa. A rodada atual **não** aciona FC-06, nem modifica o benchmark histórico ou os dados congelados da N2.
