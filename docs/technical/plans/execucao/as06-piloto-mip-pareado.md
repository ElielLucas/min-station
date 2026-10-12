# AS-06 — Piloto MIP pareado de COMP × COMP+K

**Natureza:** experimento exploratório pós-AS-05, desenvolvimento apenas.  
**Estado:** infraestrutura implementada, execução MIP real pendente.  
**Scientific gate:** `PENDING`; nenhuma promoção automática de formulação ou homologação independente.

## Problema e decisão de escopo

A AS-05 fatorial demonstrou fortalecimento LP por K e ganhos pequenos de A4+K nos seis casos. A AS-06 testa se K melhora o **desempenho inteiro**, não apenas o LP. Usamos `compile_u(..., relax=False)` com e sem cortes; a única variável discreta é `y_v ∈ {0,1}`. A4+K é controle exploratório secundário em três casos já observados. Não continuar a seleção de políticas A2/A4 por instância.

## Estágio 1 — 300 s, seed 42

| Papel | Formulações | Casos | Total de runs |
|---|---|---:|---:|
| Primário | COMP (U), COMP+K (U_K) | 6, mesmo conjunto AS-05 | 12 |
| Secundário, não confirmatório | A4+K | MAPF room, PUC w3c571, Vienna I056 | 3 |

São **15 workers independentes**. Cada worker paga spawn, carregamento e alcance, K quando usado, build, Gurobi, callback e validação física no mesmo deadline (300 s). Orçamento idêntico, mesmo número de threads (4), seed e configuração do solver; Gurobi recebe o *tempo restante* em vez de 300 s além do custo de preparação. Memory cap 16 GiB de RLIMIT_AS; estimativa pré-build no A4, sem tratar proxy como medição real.

K: `C1+C2+C4-DM`, verificador binário exato `bitset-v2`; comparar hash K com o reensaio. COMP não prepara, valida nem recebe K. Partição A4 = refinamento aninhado de A2 por `reachability_degree` seed 42. Em caso de ausência de Gurobi, timeout, OOM, erro ou problema físico, registrar status e manter o denominador.

## Medições

- Por braço: status, hash da fonte e de K, solver version, número de variáveis/linhas/NZ, `Runtime`, `Work`, `NodeCount`, peak RSS do worker, wall por fase e wall total.
- No callback MIP: amostras do melhor LB e da incumbente **numéricos** em intervalos de aproximadamente 5 s; eventos `MIPSOL` até 24 snapshots. O relatório sinaliza quando excede esse limite. Não interpolar eventos ausentes.
- Para cada snapshot de `y` capturado: validar com `experiments/cuts/independent_validator.py`, que usa grafo físico original, bateria e matching, sem confiar na relaxação. A solução final é sempre validada separadamente. O plano reserva 30 s/60 s (estágio 1/2) para validação, debitados no mesmo deadline. Se qualquer incumbente capturada for fisicamente inválida, o braço é `VALIDATION_FAIL` e não publica UB/gap físico.
- Gap de comparação = `max(0, (UB_física - LB_numérica) / max(1, |UB_física|))`, **somente** quando existe UB física validada e LB numérica finita. É medida do gap MIP, não certificado racional do LP nem ótimo global quando o solver é interrompido.
- Tempos para primeira e melhor incumbente validada são tempos do solver obtidos retrospectivamente. Não inventar um timestamp para a incumbente final se seu evento não foi observado.

## Gate antes de replicação

A decisão ocorre somente após verificar os seis pares COMP/COMP+K, não após observar apenas os casos favoráveis. Todos devem ser comparáveis e ter UB física validada de ambos os braços.

`GO_REPLICATION_EXPLORATORY` requer: benefício material em **duas fontes gráficas e dois grafos brutos independentes**, sem nenhuma regressão severa (>1 ponto percentual de gap). Benefício material por par é redução absoluta de gap de pelo menos **2 pontos percentuais**, **ou** redução relativa de pelo menos **25%** do gap existente, com redução estritamente positiva. Esses limiares são adendo exploratório específico da AS-06, não foram homologados pelo AS-00.

`STOP_SEVERE_REGRESSION` quando uma regressão supera 1 p.p.; `INCONCLUSIVE_CENSORED` quando algum par não é comparável; `STOP_NO_REPRODUCIBLE_MULTIFAMILY_BENEFIT` quando não há suporte em duas fontes. Não promover apenas por tempo de solver ou média que exclui censuras.

## Estágio 2 — somente com GO

Se o gate do estágio 1 for `GO_REPLICATION_EXPLORATORY`, criar **um plano novo** imutável de replicação: COMP × COMP+K nos **mesmos seis casos**, seeds `42, 43, 44`, 600 s totais por braço (**36 execuções**). A4 não participa por ser controle secundário. A replicação precisa de benefício material em ao menos 2/3 seeds por grafo em duas fontes independentes, nenhum par censurado e nenhuma regressão severa. Este gate permanece exploratório e não libera automaticamente AS-11.

## Integridade, reprodutibilidade e limitações

A entrada é verificada contra os artefatos AS-05 fatorial, incluindo manifesto, plano e hashes originais. Resultados vão a pasta nova (`as06-mip-screening-001/`, nunca a AS05) com checkpoint por braço, SHA lado a lado, manifesto final, CSV e análise vinculada ao report. Uma tentativa de retomada com checkpoint adulterado ou mudança no plano é recusada. O SHA é controle de integridade local, **não assinatura externa**. `--verify --audit-physical` executa verificação física independente das instalações finais presentes no relatório.

O desenho seleciona os três casos secundários *após* observar LP AS-05; portanto nenhum ganho deles vale como validação externa. Não usamos split de avaliação, nem garantimos hardware/solver idênticos ao de futuras publicações. A revisão matemática independente da AS01/AS02/AS04 e aprovação científica ainda estão pendentes.

## Interface

- `run_as06_mip.py --check-plan` — validar plano congelado.
- `run_as06_mip.py --preflight` — estimar tamanhos sem solve.
- `run_as06_mip.py --execute` / `--resume` — executar/resumir o estágio 1.
- `run_as06_mip.py --verify --audit-physical` — conferir integridade e instalações finais.
- `run_as06_mip.py --analyze` / `--verify-analysis` — relatório e gate.
- `run_as06_mip.py --init-replication-plan --plan ... --replication-parent ...` — somente após GO.

A integração detalhada está em `AS06-INTEGRACAO.md` no pacote de entrega.
