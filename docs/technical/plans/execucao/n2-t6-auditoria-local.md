# MIN-STATION — N2-T6: evidências da auditoria local

**Data:** 2026-10-10  
**Proveniência:** transcrição dos resultados informados pelo pesquisador após execução no checkout local.  
**Limite de verificação:** o redator deste relatório não teve os bytes originais do CSV, curvas e manifesto para cálculo independente; o resultado abaixo foi gerado pelo verificador local do projeto.

## Comandos e respostas observados

```bash
PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p 'test_n2_t6_gate.py' -v
# Ran 13 tests ... OK

python -m ruff check experiments/alternative-formulations/verify_n2_t6_gate.py experiments/alternative-formulations/test_n2_t6_gate.py
# All checks passed!

python experiments/alternative-formulations/verify_n2_t6_gate.py
# decision: N2 FAIL
# audit_status: VERIFIED_ARTIFACT_BYTES_AND_TABULAR_INVARIANTS
```

## Razões explícitas de bloqueio retornadas

1. `HB-q4-ndir2-p1`: recuperação `−1/2 < 1/2`; LB `1/2` não excede B0 `1`.
2. `BP-nao-[3,1]-q2`: recuperação `−5 < 1/2`; LB `1` não excede B0 `6`.
3. `HB-q6-ndir2-p1`: LB `2/3` não excede B0 `11500000000000001/10000000000000000`.
4. `BP-nao-[2,2,2]-q2`: LB `18/13` não excede B0 `8`.

## Hashes confrontados pelo verificador local

| Arquivo | SHA-256 retornado |
|---|---|
| `n2-t5-medicoes.csv` | `2e1215e135561d4af962318f15eeaa96be0d04aed09a8e801765ae577958bac5` |
| `n2-t5-lb-versus-work.csv` | `c0be65a1fe79f7da59be50bc3b184e0143f6c97a7f0153e66464c26a43563d5d` |
| `n2-t5-custos.md` | `0b6700ed47b257e1fb5aa368d5bd1b5ec17bbf832d691b89625c912601258d0a` |
| `n2-t5-lb-versus-work.svg` | `520f82c4e0e64dec45c3d4d11ce5c61abfe150aaaedc76c5bd9cecd0f55f9920` |

Freeze SHA-256 informado no resultado: `b036e9d0fe8f446dfcaca2716df85054c73dbb8702484aacce3c807e6574de71`.

## Restrição da auditoria

O verificador declarou: “Verificação de arquivo e invariantes não substitui reauditoria das provas E5”. Além disso, B0 é referência histórica/numérica, não LB físico independentemente certificado.

**Conclusão auditada localmente:** `N2 FAIL`; ausência de melhoria sobre B0 em 4/4 casos e recuperação abaixo de 50% nos dois casos de nível 1.

**Identificadores ainda não informados:** SHA-256 do manifesto N2-T5 e HEAD Git da execução. Preservar como pendência, não simular o valor.
