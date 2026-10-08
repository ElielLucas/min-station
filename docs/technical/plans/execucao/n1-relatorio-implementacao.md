# N1 — Registro de implementação e próximos gates

**Data:** 2026-10-07. **Branch-alvo:** `novos_testes`. **Sem commit criado.**
**Authority:** `specs/proxima-fase-n1-informacao-compatibilidade/spec.md` e análise consolidada de 07/10.

| Tarefa | Estado da entrega | Evidência e ressalvas |
|---|---|---|
| N1-T0 | `DONE` para migração documental e notas de §15 | 208 ocorrências de caminhos com basename único, 7 links relativos; 16 notas datadas; registro de SOURCE; `check_paths_n1.py` passa. Coletor histórico `run_r7_plato.py` preservado mesmo com uma referência textual obsoleta; exemplos geradores sem arquivo criado não são links de entrada |
| N1-T1 | `DONE` quanto à prova escrita/rotulagem | P2/P7 reescritas como `PROVEN`; P3/P4 reclassificadas `HYPOTHESIS` (sem inventar testes). Revisão independente de provas é recomendável |
| N1-T2 | `PARTIAL` | Documento canônico v1, auditoria §§2–12, pontos O1–O5 e `d_ss` definidos; registro MR-F3 feito como `OPEN`. O gate de aceitação não foi satisfeito |
| N1-T3 | `PARTIAL` | Novo módulo `fcc_k.py` com K idêntico à COMP/hash + script `verify_fcc_k_n1.py`, **não executados** sem Gurobi. F-C3 não implementada: proibida pelo gate MR-F3 aberto |
| N1-T4 | `DONE` para os pools registrados | 610 linhas, 3 novos CSV, testemunhas Hall, 0 divergências com o `oracle_viavel` registrado, cc9 frequência 21 versus cobertura 27; 4 testes unitários offline passaram |
| N1-T5 | `BLOCKED` | Não existe pre-registro adicional com hashes K/OPT nem medição nova. Antes de qualquer braço novo: MR-F3, equivalência por instalação, reprodução F3 (`1e-6`), então congelar hashes K e fontes OPT |
| N1-T6 | `BLOCKED` | Gatilho só pode ser avaliado com valores medidos N1-T5; nenhum par novo criado |
| N1-T7 | `BLOCKED` | Não há decisão de promoção sem CSV certificado. N2 continua `CONDITIONAL` |

## Restrições respeitadas

- `baseline.py`, `experiments/alternative-formulations/fcc.py`, `run_f3.py`, `run_r7_plato.py`, `results/benchmark/r7-plato.csv` e `r7-plato-resumo.csv` não modificados.
- Documento SOURCE preservado com SHA-256 `fd5e9a0054ef6d10ba9f791f2cc77df55389c8cf72bcac3ccf56376558ef49f4`.
- Pré-registros existentes preservados. Não foi criado commit, não foram geradas instâncias nem executados novos LPs.
- Os rótulos `PROVEN`, `HYPOTHESIS`, `OPEN`, `COMPUTATIONALLY VERIFIED` e `NOT MEASURED` são usados com os sentidos da spec.
- A ausência de Gurobi neste ambiente impede certificar F3, F-CC + K e F-C3. **Não** interpretar ausência de medição como ausência de efeito.

## Comandos disponíveis

A partir da raiz do projeto, em ambiente com Python e `gurobipy`/licença Gurobi quando necessário:

```bash
# Releitura R7 já executada, independente do solver
python experiments/benchmark/audit_r7_n1.py
python -m unittest discover -s experiments/benchmark -p test_audit_r7_n1.py -v
python experiments/benchmark/check_paths_n1.py
sha256sum docs/technical/reference/formulacoes/formulacao-fc3-componentes-trios.md

# Pendente, em ambiente com Gurobi
PYTHONHASHSEED=0 python experiments/alternative-formulations/verify_fcc.py
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_f3.py
PYTHONHASHSEED=0 python experiments/alternative-formulations/verify_fcc_k_n1.py
```

**Antes de rodar `run_f3.py`:** preservar cópia do CSV histórico para comparação de cada valor com tolerância `1e-6`, pois esse runner escreve no arquivo de saída histórico. Não sobrescrever evidências anteriores sem registrar e comparar os hashes.

**Próxima etapa lógica:** revisão matemática independente e aceitação explícita do MR-F3; só depois implementar F-C3 segundo as redes C31–C34 e validar toda instalação para cada modelo novo. Em paralelo, executar os testes F-CC + K e reprodução F3 em Gurobi. Não iniciar T5 sem os gates anteriores.
