# N2 — Próxima implementação autorizada

A N1-T7 selecionou `PROMOTE FCC + EXISTING CUTS`; portanto, a N2 é o caminho B e **somente na raiz**. A implementação deve seguir N2-T1 → revisão formal N2-T2B → código de geração de colunas → N2-T3 → regressões T4 → medição T5 → gate T6.

## Primeiro passo: N2-T1

Na raiz do repositório, depois de copiar o patch (que não contém resultados congelados):

```bash
PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p test_n2_t1_offline.py -v
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t1.py freeze
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t1.py check
```

O comando `freeze` recalcula e verifica a decisão N1-T7, rejeita resultados N2 prévios, congela famílias `hb` e `bp-nao` com dois níveis, gera `experiments/alternative-formulations/n2-t1-freeze.json` e `docs/technical/plans/execucao/n2-t1-pre-registro.md`, ambos em **modo criação exclusiva**, e não otimiza nenhum LP. O `check` verifica hashes e estrutura sem alterar arquivos.

Os números N1-T5 dos casos pequenos são **referências históricas**, não resultados obtidos na N2. O nível 2 fixa os parâmetros de `hb.construir(q=6,ndir=2,p=1,k=1,L=2)` e `bp.construir(items=[2,2,2],q=2,B=3)`. O pre-registro registra dados sem chamar Gurobi.

**Depois do freeze:** revisar formalmente `docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md`. Não iniciar o código T2B enquanto o parecer não estiver aceito. A futura implementação deverá conferir os hashes N2 e preservar inalterados os resultados N1.

## Observações

- `WorkLimit=164` com `Threads=4` corresponde à referência calibrada da Spec A, com guarda de parede de 1800s. A unidade Work não é tempo em segundos; a medição futura precisa contabilizar **todos** os subsolves dentro do mesmo orçamento.
- N2-T1 não gera séries de curva, CSV N2 ou valores de bound. Os resultados só existem após T2B/T3/T4 serem implementados, auditados e validados.
- Se o freeze falhar por uma divergência de hash ou evidência N1 alterada, **não** contornar o bloqueio nem substituir valores com defaults.
