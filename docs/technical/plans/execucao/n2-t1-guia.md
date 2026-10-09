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

**Depois do freeze:** revisar formalmente `docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md`. A escrita do código N2-T2B depende da **autorização matemática formal Gate M** (§11.1/§12.1 da revisão v2.1), registrada pelo responsável em um arquivo separado e versionável. Não é necessário concluir a implementação para aprovar sua matemática. A futura implementação deverá conferir os hashes N2 e preservar inalterados os resultados N1.

## Estado da N2-T2B (2026-10-09)

A revisão matemática `docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md` está na **v2.1**, com parecer independente `ACCEPTED WITH CONDITIONS` (`docs/technical/reference/formulacoes/parecer-independente-N2-T2B.md`) preservado. O núcleo matemático foi revisado, as dez correções R-01 a R-10 foram rastreadas e os controles matemáticos dirigidos foram executados no ambiente do pesquisador: **18 testes `OK`, sem skipped (2,612 s)**. Esses testes não demonstram que a futura implementação já funciona.

**Dois gates não circulares:**

1. **Gate M — Aprovação matemática para implementar (APROVADO em 2026-10-09):** deve ocorrer **antes de escrever código**, com base no parecer, na revisão v2.1, nos controles já executados e na política de certificação. Requer decisão formal humana, com identificador/SHA-256 do documento e escopo aprovado. Não depende de gerar colunas, implementar ENUM nem repetir testes sobre código ainda inexistente.
2. **Gate O — Aceite operacional da N2-T2B (PENDENTE):** ocorre **após** implementar o master, pricing e a geração de colunas somente na raiz, executar testes contra as funções reais e validar o contrato de saída. O aceite da N2-T2B **não** significa N2-T3 concluída nem aprova medições experimentais.

**Depois do Gate O:** N2-T3 implementa/verifica a certificação (ENUM com aritmética exata e/ou bounds globais N1/N2 rigorosos, G2, H-K, B0); N2-T4 realiza a regressão prospectiva dos 23 controles históricos; N2-T5 mede sob o freeze e N2-T6 decide o gate científico. `ObjBound`/`ObjBoundC` de MIP numérico, sem verificação independente, permanecem `UNCERTIFIED`.

**Gate M aprovado e registrado** em `n2-t2b-decisao-aprovacao-matematica.md`, para a revisão matemática v2.1 identificada por SHA-256. A implementação N2-T2B está autorizada sob as condições do registro. **Primeira entrega:** `n2-t2b-implementacao-master-dual.md` (RMP e dual, sem pricing ou campanha experimental). O Gate O permanece pendente. A palavra `PENDENTE` na revisão matemática é o estado histórico da própria revisão aprovada, preservada byte a byte para manter seu hash. O freeze N2-T1 permanece inalterado.

## Observações

- `WorkLimit=164` com `Threads=4` corresponde à referência calibrada da Spec A, com guarda de parede de 1800s. A unidade Work não é tempo em segundos; a medição futura precisa contabilizar **todos** os subsolves dentro do mesmo orçamento.
- N2-T1 não gera séries de curva, CSV N2 ou valores de bound. Os resultados só existem após T2B/T3/T4 serem implementados, auditados e validados.
- Se o freeze falhar por uma divergência de hash ou evidência N1 alterada, **não** contornar o bloqueio nem substituir valores com defaults.
