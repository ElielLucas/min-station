# MIN-STATION — N2-T3: desenho técnico da certificação

**Status:** PROPOSTA / SEM IMPLEMENTAÇÃO.  
**Spec:** [spec.md](spec.md) · **Tarefas:** [tasks.md](tasks.md)  
**Fonte normativa:** revisão matemática `n2-t2b-master-dual-pricing-revisao.md` v2.1 §§3–6.6. Não é uma reformulação.

## Architecture Overview

```text
N2-T2B RestrictedMaster.solve()  -- DualSnapshot válido (pi,tau,mu,kappa; revisão/solve_id/K)
          |                                    |
          |                         [E1] snapshot -> RationalDual
          |                                    |  + canonical vector digest
          |                         [E1] N1 / [E2] ENUM / [E3] N2
          |                                    |  cada rota: GlobalPricingBound(ell,proof)
          |                         [E1] evaluate_theorem_l(...) com Fraction
          |                                    |
          |                         CertifiedIteration / abstenção rastreável
          |                                    |
          +---------- [E4] integra root-only CG e mantém max certificado
                                               |
                           [E5] K validado + U exato/G2 + B0 separado
                                               |
                     CertifiedCGResult (z_R diagnóstico + LB_CG racional + status)
```

**Separação de responsabilidades:** nenhum `PricingResult` numérico vira prova; certificação opera sobre cópia dos números + estruturas combinatórias validadas; a avaliação de L1 não depende da vida do objeto Gurobi. O algoritmo legado só é tocado na E4.

## Code Reuse Analysis

| Existente | Interface real | Reuso e cuidado |
|---|---|---|
| `n2_t2b_master.RestrictedMaster` | `solve(params=...) -> MasterResult`; `validate_column(q)`; `reach_graph`; `primal_values()` | Construção idêntica de `G,H,K,D`; não mudar R1/R2/R3; snapshot somente da resolução atual |
| `n2_t2b_master.DualSnapshot` | `values: DualValues`, `revision`, `solve_id`, `k_hash`, `checks` | Cópia de floats finitos para racionais exatos, depois projeção; `checks.passed` é numérico, não certifica |
| `n2_t2b_master.MasterResult` | `objective_rmp`, `dual`, `status_name`, `runtime`, `work` | `objective_rmp` diagnóstico; `dual=None` impede nova certificação |
| `n2_t2b_master.RestrictedMaster.primal_values()` | Dicionários `lambda`, `d`, `y` imutáveis com floats | Só candidato a U; exigir verificação racional de todas as restrições |
| `n2_t2b_pricing.price()` | `PricingResult`, bound numérico, status, Work, versão/params | Gera colunas; não serve como `ell` global provado |
| `n2_t2b_column_generation.run_column_generation()` | `ColumnGenerationResult`, `history: tuple[IterationRecord]` | Hoje descarta master e **não guarda pi/tau/mu/kappa** no histórico; integração mínima opt-in precisa ocorrer antes do descarte |
| `fcc.enumerar_conexos` | `enumerar_conexos(neigh,V,cap) -> (W_list,truncated)` | `truncated=True` também quando `len(out)==cap`; nunca inferir cobertura apenas do número |
| `fcc.B_de`, `fcc.grafo_H`, `fcc.pares_diretos` | Operações sobre grafo e alcance | Reusar sem alterar a semântica de terminais e `D` |
| `fcc_k.prepare_k` / `harness.add_cuts_to_model` | K canônico/hash e validação com `assert_valid_cuts` | Guardar evidência por instância; não mutar K |
| `test_n2_t2b_controles_matematicos.py` | Controles racionais já existentes | Regressão de referência; **não** substituir testes de nova implementação |

## Components and Planned Interfaces

Interfaces **propostas**, não funções existentes; confirmar nomes concretos na implementação. Todos os retornos devem ser imutáveis e sem referências a `gp.Model` ou `gp.Var`.

### E1 — `n2_t3_cert_core.py`: racional e Teorema L

```python
@dataclass(frozen=True)
class RationalDual:
    pi: Mapping
    tau: Mapping
    mu: Mapping          # projetado ≥ 0
    kappa: Mapping       # projetado ≥ 0
    revision: int
    solve_id: int
    k_hash: str
    vector_digest: str   # digest determinístico do payload canônico

@dataclass(frozen=True)
class GlobalPricingBound:
    ell: Fraction
    source: Literal['N1', 'ENUM', 'N2']
    vector_digest: str
    evidence: Mapping    # conteúdo específico validado por construção do oráculo

@dataclass(frozen=True)
class CertifiedIteration:
    status: Literal['CERTIFIED', 'UNCERTIFIED']
    lb_exact: Fraction | None
    source: str | None
    justification: str
    revision: int
    solve_id: int
    vector_digest: str
    k_hash: str
    l_exact: Fraction | None
    delta_exact: Fraction | None
    ell_exact: Fraction | None
    winning_branch: str | None
```

Funções esperadas: `rationalize_snapshot(snapshot, instance_key, S, T, V, K) -> RationalDual` (finitude/índices/projeção, sem aproximação), `analytical_bound_n1(dual,S,T,V) -> GlobalPricingBound`, `evaluate_theorem_l(dual,bound,D,m) -> CertifiedIteration`, `floor_export(lb, precision) -> Decimal/string ou float limitado inferiormente`, `conservative_integer_bound(lb) -> int`, `vector_digest(...) -> sha256`.

**Invariante:** a camada não deve aceitar `GlobalPricingBound` arbitrariamente forjado por chamador como prova. Cada bound deve ser emitido por oráculo verificador (`N1`, `ENUM`, `N2`) e identificado com tipo/origem verificáveis; a função de L1, em modo não confiável, deve revalidar a evidência ou retornar `UNCERTIFIED`. Para testes matemáticos puros pode haver helper privado `theorem_l_formula` sem rótulo de certificação; `ell` manual não ganha selo por passar no helper. Identidade do vetor sozinha não prova `ell≤c*`.

**N1:** TopK por `sorted` de valores `Fraction` e somas exatas; preservar valores negativos; `k` começa em 1. Bound pode ser fraco/negativo.

### E2 — `n2_t3_cert_enum.py`: cobertura exata

`enumerate_global_bound(dual, H, S, T, V, cap, ...) -> GlobalPricingBound | Abstention`.

- Calcular `S_W/T_W` por vizinhança fechada, não por inclusão em `W`.
- Avaliar TopK exato por todo `W` elegível e `k≥1`; ordenação pode afetar apenas empate, não valor.
- Conferir `truncated=False`, `visited_connected_W` e `eligible_W` como contagens; cap conservador, `cap=total` é truncado na API atual.
- Verificação independente em grafos minúsculos por inspeção dos `2^n−1` subconjuntos, com verificação exata de conectividade; não contar com a mesma implementação para ser seu próprio oráculo.
- Se cap/tempo interromper, retornar abstenção; nunca retornar menor custo visitado como `GlobalPricingBound`.

### E3 — `n2_t3_cert_box.py`: P0–P5 racional e N2

`build_rational_pricing_lp(instance, dual) -> RationalLP` e `certify_box_bound(lp, theta, nu, vector_digest) -> GlobalPricingBound | Abstention`.

- Construir racionalmente coeficientes de **todas** as linhas de P0–P5, incluindo os dois sentidos das arestas de H, sinais de `g,f`, bounds `u` de `x,a,b,ρ,g,f`, `n=1` e zero em `f`.
- Normalizar cada linha desigualdade como `Bw≥h` antes de usar `ν≥0`; igualdade `Aw=b` tem `θ` livre. Testar sinais/índices e reconferir objetivo.
- Somente a montagem numérica auxiliar (para sugerir `θ,ν`) pode usar Gurobi; a prova reavalia a matriz **original racional**; se multiplicadores indisponíveis, usar vetores racionais simples (p. ex. zeros) ou abster-se, sem supor utilidade.
- Validar com enumeração em instâncias minúsculas: `ell_N2≤c*`, mesmo com `θ,ν` não ótimos e parciais.

### E4 — `n2_t2b_column_generation.py` (extensão opt-in)

Acrescentar **parâmetro opt-in** de certificação, mantendo a chamada legada e os campos atuais estáveis. Não alterar o conteúdo de `IterationRecord` vigente por padrão; preferir resultado envoltório `CertifiedCGResult(base_result, certification_history, best_certificate, ...)`, ou campos **opcionais** retrocompatíveis se o desenho final provar equivalência dos testes. Evitar uma segunda execução do RMP para reconstruir snapshot.

Ponto de inserção: **depois de `MasterResult.dual` válido e checagem de orçamento, antes de `price(...)`/`add_column(...)` ou descarte do master**. Copiar para objeto independente os dados necessários (vetor pós-projeção, topologia de H, S/T/V/D, K/hash, identidade de iteração). Permitir certificar N1 imediatamente; ENUM/N2 quando disponíveis e no orçamento. Não reutilizar `DualSnapshot` após adicionar coluna. Se o budget não permitir oráculo caro, conservar `N1` ou certificado anterior.

**Custos:** solve adicional de N2 deve gastar `WorkLimit`/`TimeLimit` restantes; tempo de CPU de certificação sem solver entra no wall time; contabilidade de Work dos solves continua explícita; ausência/invalidez de `Work` não soma zero. Não exigir que custo da certificação produza certificado antes de parar. Resultados de CG numérico continuam diagnósticos após interrupção.

### E5 — `n2_t3_cert_validation.py`: K, U/G2, B0 e consolidação

- `validate_k_evidence(...)` reusa hash canônico e `assert_valid_cuts` com entrada real; evidência inclui parâmetros de instância, digest e resultado, não apenas string fornecida pelo chamador.
- `verify_primal_rational(master_data, witness) -> PrimalUpperBound | Abstention` reconstrói R1/R2/R3/K, `0≤y≤1`, `λ,d≥0`, e calcula `U=Σy` racional. Falha no menor resíduo exato ⇒ recusa; **tolerância numérica não prova viabilidade**. Testemunho inicial `(V,S,T)` pode fornecer `U=|V|` para instância admissível validada.
- `check_g2(U,lb)`: verdadeiro só quando mesma instância/mesmo K e `U-lb≤Fraction(1,1_000_000)`.
- `BaselineEvidence`: B0 e componentes COMP LP/core IP com **provas específicas** de serem LB para MIN-STATION; não usar incumbente de core interrompido; se evidência não existir, deixar campo não certificado/ausente. Não produzir novo baseline ou fazer experimento.
- Serializar `CertifiedCGResult` com status e justificativa não vazia, `lb_exact`, `lb_floor`, `b0_exact` separado, `z_r` diagnóstico e `convergence_status` distinto.

## Error Handling and States

| Condição | Comportamento obrigatório |
|---|---|
| `snapshot=None`, NaN/inf ou índices incompatíveis | Não cria certificado; preserva histórico válido |
| Duas provas com o mesmo vetor | Pode escolher `max(ell_N1,ell_ENUM,ell_N2)` **se todas são verificadas**, mantendo evidência da fonte vencedora |
| Novo vetor ou nova revisão | Recalcular integralmente L1; nunca usar `ell`/L de vetor anterior |
| ENUM truncado ou cap exato | Abstenção apenas de ENUM; N1/N2 ainda elegíveis |
| N2 sem matriz racional/sem verificação de sinais | Abstenção apenas de N2 |
| Pricing MIP falha/atraso/limite global | Nenhuma inferência de ótimo; melhor LB previamente certificado fica |
| Sem validação de K | Não emitir certificado válido **para MIN-STATION**; eventual análise `LB≤z_Q` deve usar rótulo distinto e não publicável como LB físico |
| `U` não validado ou G2 falha | Pode emitir LB, mas nunca `CONVERGED_CERTIFIED` |
| B0 ausente/não demonstrado | Sem comparação de ganho certificado; `LB_CG` segue válido se hipóteses próprias atendidas |

## Non-obvious Decisions and Risks

1. **Prova por construção, não por `bool certified`:** evitar API pública que permita atribuir `CERTIFIED` a um número arbitrário; vincular emissor do bound à prova reexecutável.
2. **Exatidão de floats:** `Fraction.from_float(1e-7)` representa o binário **exatamente**, não a fração decimal `1/10^7`; a tolerância `1e-6` congelada deve ser criada como `Fraction(1,1_000_000)`.
3. **Consistência de P0–P5:** `build_pricing_model` é numérico e pode configurar presolve. Certificação N2 deve espelhar as linhas racionais originais e seus limites; comparar coeficientes/semântica em testes contra instâncias pequenas.
4. **Custo e escalabilidade:** N2 com matriz racional pode ser custoso; não mudar oráculos/estruturas a posteriori para melhorar resultados N2-T5.
5. **U exato pode ser fraco:** `U=n` é testemunho seguro, não prova de que G2 será útil; abstenção de convergência é resultado correto.
6. **Preservação do Gate O:** nova API é opt-in, regressão das 87 provas e `ruff` é obrigatória; não editar a revisão v2.1 ou o parecer.

## Formal Acceptance Gate — N2-T3

- Revisor verifica rastreabilidade de `CERT-01`…`CERT-14` a testes e provas no código, não somente nos documentos.
- Testes adversariais/contraexemplos exatos aprovados; `N1`, `ENUM` e `N2` testados contra `c*` em instâncias pequenas.
- Todos os rótulos certificados têm `ℓ`, vetor, prova global, L0/L1 e H-K; nenhuma rota MIP-numérica gera prova.
- K, `B0`, `U` e G2 possuem evidências independentes; interrupções e truncamento não fabricam certificado.
- Regressão N2-T2B (87 testes) e freeze N2-T1 passam sem alterar material congelado.
- Só depois desse aceite técnico programar a regressão N2-T4; NÃO declarar `N2 PASS/FAIL` aqui.
