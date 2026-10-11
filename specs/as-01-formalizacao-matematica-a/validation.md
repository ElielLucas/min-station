# AS-01 — Registro de validação local (não é parecer independente)

**Data:** 2026-10-11.  
**Estado de encerramento:** **PENDENTE — NÃO PROMOVER AS-02** até a revisão matemática autor ≠ verificador e gates do checkout.

## Evidências por requisito

| AC | Evidência produzida | Resultado local | Pendente |
|---|---|---|---|
| AS01-01 | `formulacao-a-grupos-origens.md` contém dados, índices, domínios, A1–A7, permanência e overlap | Preparado | Verificação simbólica independente |
| AS01-02 | `provas-formulacao-a.md` prova ambas direções apoiando-se na exatidão da U | Preparado | Auditoria do lema U e `S∩T` |
| AS01-03 | Levantamento explícito U→A({S}) por tipos de vértice | Preparado | Revisão independente |
| AS01-04 | Agregação de subblocos e identidade `Σ c_{B'v}=c_{Bv}` | Preparado | Revisão independente |
| AS01-05 | `relacoes-lp-formulacao-a.md` apresenta cadeia condicionada e relações não provadas | Preparado | Verificar rigorosamente F-CC→B e B↔A unitária |
| AS01-06 | Estrela T18 com limites `1/2` e `1`, prova racional e teste exato | Aritmética local aprovada | Revisão independente, se necessário confrontar LP real com solver |
| AS01-07 | Nenhum parecer independente autor≠verificador foi emitido | **PENDENTE** | Bloqueia promoção AS-02 |

## Testes locais executados

`PYTHONHASHSEED=0 python3 -m unittest discover -s experiments/alternative-formulations -p 'test_as01*.py' -v` executou **9 testes**, todos aprovados no ambiente de preparação, com aritmética exata `fractions.Fraction`. Os testes verificam testemunhas; não certificam os teoremas universais ou resultados experimentais de F-CC.

## Limitações conhecidas

1. O validador da AS-01 **não executou Gurobi** e não reproduziu `zLP(F-CC+K)=5` nem `OPT=7` em Sec59.
2. A prova de equivalência B↔A unitária usa remoção de ciclos e transformação de retornos à origem em permanência; requer revisão de outro responsável.
3. A implicação F-CC→B usa definições de configurações e acoplamento R3 de documentos históricos; requer confronto com implementação se usada como teorema no artigo.
4. O benchmark AS-00 foi usado somente como pré-condição documental; não houve execução de LP/MIP novo.
5. **Não houve commits** desta entrega na branch do usuário nem aplicação ao checkout original.
6. `ruff` não estava instalado no ambiente de preparação: gate lint **não executado**.
7. Integridade histórica não pode ser certificada no checkout do usuário até comparar `git status` e hashes da branch.

## Gate

**PENDING**, não `PASS`. A AS-01 só poderá ser concluída quando o verificador independente emitir parecer por AC com evidências rastreáveis, os scripts de gate executarem no checkout real e as tarefas forem registradas conforme `/tlc-spec-driven`.
