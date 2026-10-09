# N1-T6 — Protocolo de microinstâncias condicionais

**Estado da entrega:** `IMPLEMENTED — NOT MEASURED` (execução do runner depende do Gurobi).  
**Autoridade:** `specs/proxima-fase-n1-informacao-compatibilidade/spec.md`, Story 6 / N1-T6.  
**Antecedente:** `docs/technical/plans/execucao/n1-t5-diagnostico.md`.

## Por que a tarefa foi ativada

N1-T5 mediu 18 instâncias. Com `Γ > 1e-6` e `LP F-CC+K < OPT - 1e-6`, restou **uma** estrutura (`sec59`). Pela condição congelada da Story 6 (menos de duas famílias distintas), a N1-T6 está ativada. A decisão promocional N1-T7 continua pendente.

## Pares congelados pelo runner

São **três** pares determinísticos, todos com `m = 3`, `r = 1`, `n ≤ 10`:

| Par | Base | Obstrução específica | Controle (única substituição de aresta) |
|---|---|---|---|
| `T6-TRI-01` | Tri (9 vértices) | Sobreposição cíclica dos três relés | `s1-b` → `s1-c` |
| `T6-F2-01` | F2(k=1,L=3) (7 vértices) | Competição de origens pelo destino `c1` | `b1-c1` → `b1-g1` |
| `T6-SEC59-01` | Sec59(L=4) (10 vértices) | Destino compartilhado e corredor longo até `t2` | `s2-t1` → `s2-t2` |

Os controles com atalho direto *intencional* podem ter `OPT=0` e continuam válidos como controles negativos. A exclusão por perda de obstrução com `OPT=0` aplica-se à variante **obstruction**, não ao controle planejado. Ambos devem possuir certificado independente, preservando as regras de terminais e permanência do validador original.

O código não escolhe instâncias a partir dos resultados, não tenta novas sementes e não cria pares substitutos. Qualquer perda de certificação ou da obstrução antes das medições exclui o par; uma exclusão não abre vaga para outro.

## Protocolo (executar na raiz do projeto)

```bash
PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p test_n1_t6_offline.py -v

# 1. Congela A REGRA, os pares, os modelos e as evidências T5, antes de criar grafos.
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n1_t6.py freeze

# 2. Instancia apenas os pares já congelados e checa tamanho/obstrução.
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n1_t6.py generate

# 3. Certifica OPT de cada variante, registra C* e atalhos de terminais.
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n1_t6.py certify

# 4. Com Gurobi e licença válida: mede o mesmo K em ambos os modelos.
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n1_t6.py measure

# 5. Só se houver todas as seis linhas: consolida o relatório.
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n1_t6.py report

# 6. Confere os registros e os testes após o freeze.
PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p test_n1_t6_offline.py -v
wc -l results/alternative-formulations/n1-t6-diagnostico.csv
```

Esperado no CSV completo: **sete linhas** (cabeçalho + seis variantes). O runner salva um checkpoint **após cada variante**. Uma execução interrompida de `measure` pode ser retomada repetindo o mesmo comando; só o sufixo pendente é processado, com verificação dos hashes e da ordem. Não altere os módulos nem os dados do T5 após o freeze.

## Artefatos

- `experiments/alternative-formulations/n1-t6-freeze.json`: protocolo e SHA de entradas anteriores **antes** da geração dos grafos;
- `results/alternative-formulations/n1-t6-pares.json`: grafos e diagnósticos de atalhos;
- `results/alternative-formulations/n1-t6-certificados.json`: OPT independente, instalação ótima testemunha e efeito de estações em terminais;
- `results/alternative-formulations/n1-t6-diagnostico.csv`: LPs/caps/estados, incrementos e comparações;
- `docs/technical/plans/execucao/n1-t6-diagnostico.md`: relatório gerado, não pré-escrito.

## Critérios científicos e limites

- Mesmas instâncias, dimensões e K (hash) entre braços da mesma variante; `OPT` só da enumeração independente.
- `F-C3 ≥ F-CC`, `F-C3+K ≥ F-CC+K`, e todos os LPs `≤ OPT`, quando medidos.
- `NOT MEASURED` por cap/limite de tempo não significa ganho nulo. O limite por otimização nesta rodada é de **600 segundos**, congelado antes das medições; o tempo de construção do modelo não está incluído nesse limite.
- O `core IP` usa o limite interno do solver histórico; caso não certifique ótimo, reportar `NOT MEASURED`.
- O status de N1-T6 não autoriza afirmar que F-C3 é globalmente melhor nem que é mais rápida.
- N1-T7 deve seguir literalmente os critérios de promoção já congelados na spec: evidência por **duas estruturas distintas**, testemunha/mecanismo, e, para F-C3, pelo menos um caso com `core IP < OPT` e residual F-CC+K. **Nenhum novo experimento após observar os resultados.**

## Arquivos preservados

Não alterar `run_n1_t5.py`, `n1-t5-freeze.json`, o diagnóstico T5, `fcc.py`, `fc3.py`, `fcc_k.py`, `run_f3.py`, `baseline.py`, `f3-fcc.csv`, fontes SOURCE e todos os pré-registros já congelados.
