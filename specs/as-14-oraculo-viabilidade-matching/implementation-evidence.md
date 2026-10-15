# AS14 — Evidências da implementação local

**Data:** 2026-10-14  
**Escopo:** `AS14-01…AS14-07`, tarefas T1–T4  
**Estado:** **IMPLEMENTADO / TESTES LOCAIS PASS / PARECER INDEPENDENTE PENDENTE**  
**Dependência:** AS13 R3 PASS e GO para AS14 (parecer reportado pelo pesquisador).  
**Fonte:** snapshot `min-station(20261014-175308).zip`, sem `.git` no pacote; hash do commit não disponível neste ambiente. Quando rodado no checkout real, `verify_as14_oracle.py` captura o commit via `git rev-parse HEAD`.

## Código entregue

| Entregável | Arquivo | Critérios |
|---|---|---|
| T1 — triestado e JSON de evidência | `experiments/cuts/h2_oracle_schema.py` | AS14-01,02,03 |
| T2 — oráculo físico + matching e testemunhas | `experiments/cuts/h2_oracle.py` | AS14-01,02,03,04,06,07 |
| T3 — cache com hash da instância e monotonicidade | `experiments/cuts/h2_oracle_cache.py` | AS14-05,07 |
| T4 — testes exaustivos, auditoria e discriminação | `experiments/cuts/test_h2_oracle.py`, `verify_as14_oracle.py`, `verify_as14_discrimination.py` | AS14-01…07 |

## Evidências observadas no snapshot

| Gate local | Resultado |
|---|---|
| Testes específicos AS14 | **35/35 PASS** |
| Regressão AS13 (`test_as13_foundations.py`) | **27/27 PASS** |
| Auditoria física independente | **742 máscaras** (68 controles e 674 HB/K4), 0 divergências |
| Validade e classificação H2 em controles | **36 suportes certificados** e conferidos contra viabilidade física independente |
| Mutantes reais em cópias isoladas | **7/7 mortos, 0 sobreviventes** |
| Validador estrutural da spec | **0 erros, 0 avisos** |
| Validador estrutural das tasks | **0 erros, 0 avisos** |
| Alterações nos validadores AS13, COMP+K ou resultados congelados | **Nenhuma** |
| `validation.md` independente | **Não criado/alterado** |
| Commit/push | **Nenhum** |

O relatório bruto da auditoria acompanha este patch em `specs/as-14-oraculo-viabilidade-matching/as14-oracle-evidence.json`; contém as fingerprints por instância, status e ν, custo por ν, amostras de certificados, métricas por chamada e status do gate independente.

## Rastreamento requisito → evidência

- **AS14-01:** `VIABLE` exige matching completo e testemunha origem→destino; testes de permanência `s=t`, vários pareamentos, terminais como estação, partilha e duas recargas; auditoria 742 configurações.
- **AS14-02:** `INFEASIBLE` exige ν menor que m e certificado de Hall (`|N(U)| < |U|`); verificação reconstrói `N(U)` em todas as máscaras inviáveis da auditoria.
- **AS14-03:** limite `budget_s` e falha na busca/matching retornam `UNKNOWN` sem certificado negativo; teste zero budget e exceções, sensor M3.
- **AS14-04:** complemento calculado sobre `V` físico da instância, não LP corrente; suporte e complemento reproduzidos independentemente, sensor M6.
- **AS14-05:** SHA da instância inclui V/E/S/T/r tipados; ordem de entradas é canônica e cache não mistura instâncias de mesmo tamanho, sensor M4.
- **AS14-06:** `Bhat` incorpora apenas adições individuais com `INFEASIBLE` provado; complementos `UNKNOWN` não geram cortes e candidatos `UNKNOWN` recebem coeficiente 2; sensor M5.
- **AS14-07:** comparação exaustiva de todos os pares de subconjuntos dos cinco microcontroles; cache rejeita conflitos de monotonicidade; sensor M7.

## Limites declarados

1. O orçamento é **cooperativo**: se a chamada de alcance física individual ultrapassar o prazo, a resposta é rebaixada a `UNKNOWN` na próxima checagem; não há interrupção preemptiva durante o cálculo indivisível.
2. Cache certificado é **em memória**, não persistido nem compartilhado entre processos. A auditoria JSON é append-only (`--output` recusa sobrescrita).
3. Não há separador de cortes, ligação ao Gurobi, execução MIP, nem implementação de β/HL, conforme Out of Scope da AS14.
4. A auditoria reutiliza referências da AS13 para a reconciliação; não constitui um **verificador independente autor ≠ verificador**. Uma terceira parte deve confirmar os ACs e testar mutações próprias antes de assinar o GO.
5. `source_commit` fica `null` quando executado a partir do ZIP sem histórico Git; isso é explícito, não um commit inventado.

## Reproduzir no checkout `novos_testes`

```bash
poetry run python -m unittest discover -s experiments/cuts -p 'test_h2_oracle.py' -v
poetry run python -m unittest discover -s experiments/cuts -p 'test_as13_foundations.py' -v
poetry run python experiments/cuts/verify_as14_oracle.py --output results/as14/as14-oracle-audit-RUN_ID.json
poetry run python experiments/cuts/verify_as14_discrimination.py
python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-14-oraculo-viabilidade-matching/spec.md
python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-14-oraculo-viabilidade-matching/tasks.md
```

Use um `RUN_ID` novo a cada auditoria. Para fechar a etapa, registrar o parecer de um revisor distinto em `validation.md`. **Não iniciar AS15 apenas com os PASS locais da AS14**; a AS13 também mantém quatro mutantes residuais a fechar antes da AS15.


## Correção pós-parecer R1 — evidências adicionais (2026-10-15)

**Status:** R1 continua **STOP** até revisão independente R2. Esta seção complementa,
não reescreve, o histórico da implementação inicial nem o `validation.md` do revisor.

O parecer R1 (§7) apontou seis exigências bloqueantes. Corrigidas localmente:

1. AS14-03: uma verificação de budget após a construção do resultado no acerto do cache;
   teste com relógio injetado após a construção do certificado (cache e caminho novo)
   e varredura de cruzamentos de prazo. R23 detectado.
2. AS14-01: dois microcasos específicos de **origem** e **destino** atravessados
   sem estação, contra seus respectivos casos com estação. R09/R10 detectados.
3. AS14-05: instâncias com vértices `int` e `str` e mesmo `str(v)` não podem
   compartilhar fingerprint/cache. R29 detectado.
4. AS14-07: teste direto da API `CertifiedCache.put`: INFEASIBLE de conjunto
   maior seguido de VIABLE de seu subconjunto deve lançar `AssertionError`.
   R30 detectado.
5. Ruff: importações sem uso retiradas e imports após `sys.path` anotados
   com `# noqa: E402`; **execução do Ruff ainda obrigatória** no checkout real.
6. Proveniência: `verify_as14_oracle.py` inclui `source_files_sha256` para
   todos os principais arquivos de código/testes usados; `source_commit`
   fica `null` enquanto o conteúdo não puder ser atribuído ao HEAD.

**Resultados reproduzidos neste snapshot corrigido:** 41/41 AS14, 27/27 AS13,
11/11 microcasos independentes, 7/7 testes adversariais de budget, auditoria
independente com 17.360 máscaras/0 divergências, auditoria do autor com
742 máscaras e 36 suportes H2, 7/7 mutantes originais e **5/5 mutantes R1
bloqueantes detectados por mutação real em cópias temporárias**.

**Limitações:** este ambiente não dispõe do Ruff; o runner completo de 33
mutantes do revisor ultrapassou o limite desta execução. A auditoria de fonte
já tem hashes exatos em `as14-r1-correction-evidence.json`. Não houve commit
no checkout do usuário. O orçamento é cooperativo; D2 (fingerprint anterior
ao relógio) e a recursão de Kuhn seguem como melhorias não bloqueantes do §8.

Antes de fechar: executar Ruff e o `verifier-r1/review_mutants.py` no ambiente
do usuário, versionar o código (apenas com autorização do usuário) e solicitar
revisão independente restrita às seis correções. **AS15 permanece bloqueada.**
