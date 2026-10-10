# MIN-STATION — Gate N2-T3: aceite da certificação rigorosa de limites inferiores

**Decisão registrada:** `APROVADO PARA PROSSEGUIR À N2-T4`, com ressalvas de rastreabilidade/revisão identificadas neste documento.  
**Data:** 10 de outubro de 2026 (`America/Sao_Paulo`).  
**Natureza:** aceite técnico e documental da **implementação N2-T3**, não o gate científico N2-T6 nem uma afirmação de desempenho positivo.  
**Fundamento da decisão:** solicitação explícita do responsável pela pesquisa para fechar a N2-T3 após a homologação apresentada nesta conversa. Não é assinatura digital nem atribuição automática de nome civil.

## 1. Identificação e escopo aceito

| Campo | Registro |
|---|---|
| Projeto | MIN-STATION |
| Branch obrigatória | `novos_testes` |
| Etapa | N2-T3 — certificação rigorosa dos limites inferiores |
| Implementação aceita | E1–E5, tarefas T1–T11, arquivos identificados pelo manifesto §7 |
| Pré-requisito | N2-T2B / Gate O aprovado, matemática v2.1, parecer independente e N2-T1 congelado |
| Commit da N2-T3 | **Não informado**; não inventar SHA. Vincular o commit local ao manifesto após incorporar estes documentos |
| Resultado | **APTO PARA AVANÇAR À N2-T4**, não `N2 PASS` |

O aceite abrange a capacidade de produzir **certificados condicionados à prova efetivamente verificada** para o LP completo F-CC+K e, quando K for demonstradamente válido para a instância, promover um limite ao problema físico MIN-STATION. Não significa que todo cenário executado produza certificado não trivial.

## 2. Base matemática e integridade

| Artefato/controle | Evidência | Estado |
|---|---|---|
| Revisão matemática v2.1 | SHA-256 `db1fb71b6e4afba421ccc9f8d4f244aee6700edb886dc1c0219ed7e812aa9237` | CONFERE |
| Parecer independente da N2-T2B | SHA-256 `32a62d416e994de1d58f31e1d3b3aa61bf8d365e223025273728d52b9559a888` | CONFERE |
| Gate M / Gate O | Registros históricos aprovados e preservados | ATENDIDO |
| Congelamento N2-T1 | `run_n2_t1.py check`: `PASS`; 2 famílias × 2 níveis; 164 Work | ATENDIDO |
| Seleção N1-T7 | `verify_n1_t7_gate.py`: `PROMOTE FCC + EXISTING CUTS`; caminho B raiz | ATENDIDO |
| Regressão offline N2-T1 | `test_n2_t1_offline.py`: 7/7 PASS | ATENDIDO |

**Proveniência:** para os três últimos controles e hashes, a presente conferência recompôs um checkout a partir do ZIP de projeto `min-station(20261010-030715).zip` e aplicou sequencialmente os pacotes E1–E5. Isso comprova a integridade **desse conjunto reconstruído**, não constitui inspeção automática de alterações não enviadas do checkout local do pesquisador. Os testes de Gurobi do §4 foram executados pelo pesquisador e fornecidos como log; não foram reexecutados neste container.

## 3. Entregas e contratos aprovados

| Entrega | Tarefas | Implementação | Resultado |
|---|---|---|---|
| E1 | T1–T3 | `RationalDual`, conversão em `Fraction`, projeção, Teorema L, N1, arredondamento conservador | VALIDADA |
| E2 | T4 | ENUM exato, TopK, cobertura completa e abstenção por cap/interrupção | VALIDADA |
| E3 | T5–T6 | P0–P5 racional e limite N2 por caixa com recálculo independente do solver | VALIDADA |
| E4 | T7–T8 | Integração opt-in à CG na raiz e histórico de certificados com identidade da iteração | VALIDADA |
| E5 | T9–T11 | K por instância, prova primal U, G2, B0 separado, consolidação e recertificação | VALIDADA |

**Invariantes preservados:** objetivo RMP `z_R` não é limite inferior certificado; MIP `ObjBound`/`ObjBoundC` não são prova; nunca usar duais de outra iteração; `CERTIFIED` requer verificador rigoroso da fonte; certificação do LP não implica automaticamente validade física; G2 demanda U primal racional e `U−LB_CG≤10⁻⁶`; B0 oficial exige prova própria, sem utilizar automaticamente uma prova de LP ou valor informado.

## 4. Resultado das validações

| Conjunto | Executor/fonte | Casos | Falhas | Erros | Skips | Estado |
|---|---|---:|---:|---:|---:|---|
| N2-T3: E1–E5 (`test_n2_t3_cert_*.py`) | Ambiente local do pesquisador, Gurobi disponível; log fornecido | **115** | 0 | 0 | 0 | PASS |
| N2-T2B: master, pricing, CG e controles matemáticos (`test_n2_t2b_*.py`) | Ambiente local do pesquisador; log fornecido | **80** | 0 | 0 | 0 | PASS |
| N2-T1 offline (`test_n2_t1_offline.py`) | Checkout reconstruído nesta conferência | **7** | 0 | 0 | 0 | PASS |
| Ruff (módulos/testes da N2-T3 e controlador alterado) | Ambiente local do pesquisador; log fornecido | — | — | — | — | `All checks passed!` |
| Compilação Python dos módulos N2-T3 | Checkout reconstruído nesta conferência | — | — | — | — | PASS |
| Freeze N2-T1 e gate N1-T7 | Checkout reconstruído nesta conferência | — | — | — | — | PASS |

**Contagem:** são 195 testes das suítes N2-T3 + N2-T2B aprovados no mesmo log do pesquisador e 7 verificações adicionais de teste offline nesta conferência (202 aprovações entre ambientes). Não descrevê-los como uma única suíte de 202 executada no mesmo ambiente.

## 5. Matriz de aceite — 14 requisitos

| Requisito | Entrega/tarefa | Evidência funcional | Situação |
|---|---|---|---|
| `CERT-01`–`CERT-04` | E1 / T1–T3 | Frações exatas, projeção, Teorema L, exportação conservadora e N1 | ATENDIDO |
| `CERT-05` | E2 / T4 | ENUM completo, TopK racional, cap/interrupção não certificam | ATENDIDO |
| `CERT-06` | E3 / T5–T6 | Matriz racional P0–P5, paridade Gurobi e prova por caixa N2 | ATENDIDO |
| `CERT-07` | E1–E3 | ObjBound/ObjBoundC/incumbente não viram certificado | ATENDIDO |
| `CERT-08`–`CERT-10` | E4 / T7–T8 | Histórico, opt-in, snapshots corretos e limites de recursos | ATENDIDO |
| `CERT-11` | E5 / T9 | K/hash, G, H, alcance e validade de cortes | ATENDIDO |
| `CERT-12` | E5 / T10 | RMP primal racional e convergência G2 somente com U válido | ATENDIDO |
| `CERT-13` | E5 / T11 | B0 separado, ausência de certificação presumida | ATENDIDO |
| `CERT-14` | E1–E5 / T11 | Status, justificativa, proveniência e casos adversariais | ATENDIDO |

Os controles combinam testes adversariais, comparações com força bruta de pequenas instâncias, paridade P0–P5 no Gurobi real, integração de ponta a ponta e regressão dos módulos da N2-T2B. **Passar nos testes constitui evidência de implementação, não prova universal da ausência de defeitos de software**; a validade matemática fundamental está nas demonstrações normativas já revisadas.

## 6. Limitações preservadas e condições para fases seguintes

1. **B0 oficial:** o verificador E5 pode demonstrar limites físicos por exaustão em instâncias pequenas, mas isso não comprova automaticamente igualdade com `max(z_COMP^LP,z_core^IP)` do baseline congelado; para instâncias acima do cap sem prova específica, B0 continua `UNCERTIFIED`. N2-T5 deverá distinguir ausência de certificado de um ganho zero.
2. **N2 global por caixa:** a interface opcional com SciPy sugere multiplicadores numericamente; no controlador integrado, a rota N2 pode usar multiplicadores zero, válidos mas possivelmente fracos. A força e escalabilidade são questões de N2-T5, não deste aceite.
3. **ENUM:** só certifica com cobertura completa comprovada; cap alcançado, inclusive exatamente, ou interrupção impõem abstenção da rota.
4. **G2:** certificação de limite inferior é diferente de certificação de convergência. G2 não é presumido a partir de pricing ótimo numericamente ou de `ℓ≥−10⁻⁶`.
5. **Work/tempo:** as medidas do controlador têm a semântica registrada; preparação externa a solves e auditorias racionais precisam continuar separadas e descritas no protocolo experimental N2-T5. Não ampliar orçamento congelado.
6. **Proveniência Git:** o commit HEAD exato contendo E1–E5 e este fechamento ainda não foi fornecido. Associar o hash do commit ao manifesto §7 após incorporar/commitar, sem reescrever os hashes matemáticos congelados.
7. **Revisão independente:** o parecer independente existente avalia a matemática da N2-T2B. Não há parecer externo novo apresentado que audite linha a linha o código E1–E5. Registrar esta lacuna e buscar revisão separada antes de utilizar os resultados como demonstração científica publicada; ela não foi fabricada para o presente aceite técnico do responsável.

**Fora de escopo do Gate N2-T3:** N2-T4 (23 controles N1), N2-T5 (medições pré-registradas), N2-T6 (`N2 PASS/FAIL`), branching, N3, novos cortes, mudanças de baseline, K ou pré-registro. Nenhuma medição desses itens é reivindicada aqui.

## 7. Manifesto SHA-256 do código avaliado

Caminhos completos dos arquivos abaixo começam em `experiments/alternative-formulations/`. Os hashes resultam do conjunto **reconstruído dos pacotes E1–E5** e permitem confrontar o futuro commit local da N2-T3 sem inventar um commit ainda desconhecido.

| Arquivo | SHA-256 |
|---|---|
| `n2_t3_cert_core.py` | `3b55efe86a4dc5749dcc40a91a07bf207601764c8c2ff4a96c97469df3a38212` |
| `n2_t3_cert_enum.py` | `51cd71f5ba15f22097d94e089351ad7ebef6f5457cbab9cd3ce3951e1b75a2be` |
| `n2_t3_cert_box.py` | `4b720bc28154f474055bea061358d4de5324b95614e71d5a5fde2ac03b92e73c` |
| `n2_t3_cert_integration.py` | `9f7c20bd491edc8bc7abe704cd8275e6e8ec352e4a6dcce090428a63aa116974` |
| `n2_t3_cert_validation.py` | `a9b941941fcc9c443de41052334429b6f94f029806d1d8e3bee94f9662016f27` |
| `n2_t2b_column_generation.py` | `d3f6e2a70922e7c893562bdb81a659cdb88dae942dd2f6f0a2d321f7737a827e` |
| `test_n2_t3_cert_core.py` | `72a599e08e6096db84f734c4ae62683fbb99c6eb71581353ac0e1cad871cbbc8` |
| `test_n2_t3_cert_enum.py` | `fffd4e003b174da95f8841c91af6dd89fc1472561100c0fc45a2c14bac47c883` |
| `test_n2_t3_cert_box.py` | `8632d1184edd9060f1509899f119d11f18311deb812dbd6d1328613468dc0d7e` |
| `test_n2_t3_cert_integration.py` | `f892d29608a907072514aeca45f6b5d9f0372a0839be032524fa93aecc2e0fe0` |
| `test_n2_t3_cert_validation.py` | `e90887ff91cff9aa024e2545ec669d696521b2e1f4f9ac869ce66e8f4b764ba3` |

Após incorporar os documentos de fechamento, executar `sha256sum` desses arquivos no repositório local; qualquer divergência requer revisão antes de reutilizar as evidências. O manifesto não cobre arquivos pré-existentes congelados: sua integridade é conferida pelo freeze e pelos hashes normativos (§2).

## 8. Decisão e limite do aceite

| Campo | Registro |
|---|---|
| Recomendação técnica | **`APTO PARA ACEITE OPERACIONAL`** com ressalvas §6 |
| Decisão solicitada pelo responsável | **`APROVADO PARA PROSSEGUIR À N2-T4`** |
| Responsável | Pesquisador responsável pelo MIN-STATION, conforme pedido explícito de encerramento nesta conversa; nome/assinatura não inferidos |
| Data | 2026-10-10 (America/Sao_Paulo) |
| Escopo | Aceite das interfaces e mecanismos de certificação, condicionado à verificação efetiva de prova em cada instância |
| Bloqueios científicos remanescentes | N2-T4, N2-T5 e N2-T6 ainda não executadas |
| Branch de referência | `novos_testes` |
| Commit da N2-T3 | **Pendente de vinculação**, pois não foi informado; manifesto SHA-256 fornece identificação intermediária |

**Conclusão:** a **N2-T3 está encerrada quanto à implementação e aos testes de aceite apresentados**, e está autorizada a preparação/exe­cução da **N2-T4** dentro dos critérios já congelados. Esta decisão **não** concede a etiqueta `CERTIFIED` a uma execução individual sem os verificadores respectivos e **não** é o gate científico `N2 PASS`.

## 9. Próximas verificações no checkout local

```bash
# Confirme que os arquivos Python coincidem com o manifesto §7 e que os gates históricos continuam válidos.
sha256sum experiments/alternative-formulations/n2_t3_cert_*.py \
  experiments/alternative-formulations/test_n2_t3_cert_*.py \
  experiments/alternative-formulations/n2_t2b_column_generation.py
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t1.py check
PYTHONHASHSEED=0 python experiments/alternative-formulations/verify_n1_t7_gate.py

git status --short
git branch --show-current
```

O usuário deve conferir o diff dos arquivos documentais, realizar o commit somente quando desejado e depois registrar o hash desse commit em um acompanhamento de rastreabilidade (sem autoeditar o próprio documento para incluir seu hash).
