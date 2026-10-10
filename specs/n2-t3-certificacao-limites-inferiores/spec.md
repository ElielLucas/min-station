# MIN-STATION — N2-T3: Certificação rigorosa dos limites inferiores

**Estado:** `IMPLEMENTADA — ACEITE OPERACIONAL REGISTRADO` (2026-10-10). O registro formal e o manifesto SHA-256 estão em `docs/technical/plans/execucao/n2-t3-gate-aceite-certificacao.md`; este documento preserva o contrato normativo e atualiza apenas a rastreabilidade.  
**Caminho:** B — `PROMOTE FCC + EXISTING CUTS`, `F-CC+K`, somente raiz.  
**Pré-requisito:** N2-T2B / Gate O aprovado; Gate M e N2-T1 congelados.  
**Escopo:** N2-T3, anterior à regressão prospectiva N2-T4 e às medições N2-T5.  
**Implementação planejada:** `experiments/alternative-formulations/`.

## Problem Statement

O controlador N2-T2B resolve numericamente o master restrito `P_R`, gera colunas admissíveis com pricing MIP e devolve resultados `UNCERTIFIED`. Seu objetivo `z_R` **não é** um limite inferior do master completo `P_Q` nem do MIN-STATION. É necessário construir provas rastreáveis de limites inferiores para `P_Q`, mesmo sob pricing incompleto, sem confundir `ObjBoundC` do Gurobi, estacionariedade numérica e certificação.

A revisão matemática v2.1 demonstrou o Teorema L e três caminhos para fornecer um limite global `ℓ` do pricing: enumeração completa exata (`ENUM`), bound analítico (`N1`) e relaxação racional com caixa (`N2`). Esta tarefa implementará **o contrato já aprovado**, não outra formulação científica.

## Goals

- [x] Obter `LB_CG` racional, correto e auditável a partir de **um único vetor** e de `ℓ≤min_{q∈Q} rc(q)` comprovado.
- [x] Implementar e validar `N1`, `ENUM` completo e `N2` racional; manter `UNCERTIFIED` quando faltar prova.
- [x] Preservar o melhor certificado anterior quando o procedimento é interrompido.
- [x] Atestar `K`/hash e a validade necessária para promover `LB_CG≤z_Q` a `LB_CG≤OPT`.
- [x] Manter `B0`, `z_R`, limite certificado, prova de `U` e estado de convergência em campos independentes.
- [x] Integrar o certificado ao CG exclusivamente na raiz, sem modificar os resultados desabilitados da N2-T2B.
- [x] Testar casos exatos e adversariais, sem campanha N2-T4/N2-T5.

## Out of Scope

| Excluído | Razão |
|---|---|
| Mudar a formulação de `P_Q`, os cortes `K`, o caminho B ou o pré-registro N2-T1 | Material congelado e gates anteriores |
| Usar `ObjBound`, `ObjBoundC`, `GRB.OPTIMAL`, `MIPGap` ou margem fixa como prova global | R-01 / D-2 rejeitada |
| Branch-and-price, branching, trio, caminho A ou novos cortes | Fora da N2-T3 |
| Certificar LP por arredondamento tolerante sem prova dos resíduos | Não satisfaz H-ARIT/G2 |
| Medir ganhos, escalabilidade ou alterar níveis e orçamento | N2-T5; orçamento N2-T1 é imutável |
| Regressão prospectiva nos 23 controles N1 | N2-T4 |
| Emissão de decisão `N2 PASS/FAIL` ou implementação da N3 | N2-T6 / N3 |
| Reabrir Gate M/Gate O, alterar `fcc.py`, `fcc_k.py`, baseline ou revisão v2.1 | Evidências históricas preservadas |

## Normative References and Source of Truth

1. `docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md`, **v2.1**, SHA-256 `db1fb71b6e4afba421ccc9f8d4f244aee6700edb886dc1c0219ed7e812aa9237`, especialmente §§3–6.6 e 11.2.
2. `docs/technical/reference/formulacoes/parecer-independente-N2-T2B.md`, SHA-256 `32a62d416e994de1d58f31e1d3b3aa61bf8d365e223025273728d52b9559a888`, D-1–D-4, D.3 e R-01–R-10.
3. `docs/technical/plans/execucao/n2-t2b-decisao-aprovacao-matematica.md` e `n2-t2b-gate-o-aceite-operacional.md`: autorização matemática e aceite operacional distintos.
4. `docs/technical/plans/execucao/n2-t1-pre-registro.md`: parâmetros, famílias, níveis, tolerância e orçamento congelados.
5. `specs/proxima-fase-n2-limite-compatibilidade-certificado/spec.md`, Story 3, requisitos `COMPAT-BOUND-15` a `COMPAT-BOUND-20`.
6. Código real: `n2_t2b_master.py`, `n2_t2b_pricing.py`, `n2_t2b_column_generation.py` e respectivos testes, sob `experiments/alternative-formulations/`.

**Regra de precedência:** divergências são registradas; não alterar artefatos congelados nem inferir que a presente especificação já executou seus testes.

## Mathematical Contract (normative)

**Domínio.** Grafo `G` simples, não dirigido, conexo, unitário, `r≥1`, `H=G^r`, `|S|=|T|=m≥1`, com `S∩T` permitido. Os pares diretos `D={(s,t):d_G(s,t)≤r}` incluem `(s,s)` para papéis compartilhados. Cada coluna `q=(W,I,J)` exige `∅≠W⊆V`, `H[W]` conexo, `I⊆S∩B(W)`, `J⊆T∩B(W)`, `1≤|I|=|J|`. Não há matching fixo.

**Vetor exato.** Converter cada `float` finito do snapshot em seu racional binário **exato** (`as_integer_ratio`/`Fraction.from_float`), rejeitar `NaN`/infinito, projetar `μ_v=max(0,μ_v)` e `κ_Z=max(0,κ_Z)` **antes de qualquer cálculo**. `π,τ` continuam livres. Criar identidade imutável/canônica do vetor pós-projeção, vinculada a `revision`, `solve_id`, `k_hash` e à instância. Todos os termos usam o mesmo vetor.

**Teorema L.** Dados `ℓ` finito com prova global `ℓ≤c*=min_{q∈Q} rc(q)` para esse vetor, em aritmética racional:

\[
\eta_v=\max\left\{0,\mu_v+\sum_{Z\in K:v\in Z}\kappa_Z-1\right\},\quad
L=\sum_{s\in S}\pi_s+\sum_{t\in T}\tau_t+\sum_{Z\in K}\kappa_Z-\sum_{v\in V}\eta_v.
\]

\[
a=\min(0,\ell),\qquad
\delta=\min\left(\{0\}\cup\{-\pi_s-\tau_t:(s,t)\in D\}\right).
\]

\[
\boxed{LB_{CG}=\max\left\{0,\;L+m\min(a,\delta),\;\frac{L+m\delta}{1-a}\right\}\le z_Q.
\]

A convenção `D=∅ ⇒ δ=0` é obrigatória; `1-a≥1`. Sob cortes `K` comprovadamente válidos (H-K) e a equivalência física previamente provada, `LB_CG≤OPT`.

**N1 — analítico:**

\[
\ell_{N1}=\min_{v\in V}\mu_v-
\max_{1\le k\le m}\bigl(\operatorname{Top}_k(\pi;S)+\operatorname{Top}_k(\tau;T)\bigr)\le c^*.
\]

TopK opera em racionais e inclui valores negativos quando necessário. O bound é global, mas sua força não é garantida.

**ENUM:** enumerar **todos** os `W` conexos de `H`, computar elegibilidade e, para `k=1,…,min(|S_W|,|T_W|)`, avaliar TopK exatamente e o menor `rc(W,I,J)`. A cobertura depende de `truncated=False`; `enumerar_conexos` do `fcc.py` sinaliza `truncated=True` **também se o cap for atingido exatamente**. Cap atingido ou prova de cobertura ausente ⇒ esta rota não certifica. O mínimo dos visitados é uma **cota superior** de `c*`, jamais um `ℓ` global.

**N2 — relaxação com caixa:** reescrever **a mesma formulação** P0–P5, inclusive elegibilidade, conectividade e limites originais, como `min cᵀw` com `Aw=b`, `Bw≥h`, `0≤w≤u`, `u=1` nas variáveis binárias relaxadas, `n` em `g`, `n−1` em `f`. Para `θ` livres, `ν≥0` racionais, e **matriz/objetivo/bounds racionais construídos independentemente do solver**, calcular exatamente:

\[
\ell_{N2}=\theta^Tb+\nu^Th+\sum_j u_j\min\{0,c_j-(A^T\theta)_j-(B^T\nu)_j\}\le c^*.
\]

Multiplicadores podem ser sugeridos numericamente, mas **provar o limite requer recálculo exato da expressão**, com a convenção de sinais/linhas fixada e validada. Não basta copiar uma matriz aproximada do Gurobi. `ν` projetado em não negativo deve ser usado no recálculo.

**Exportação:** manter o racional `Fraction`/par `(numerador,denominador)` canônico e qualquer representação decimal/float publicada como limite deve ser arredondada **para baixo** por procedimento comprovado (não por `float(Fraction)` isolado). A convenção inteira congelada é `ceil(LB_CG−1/1_000_000)` **apenas** se certificado; a subtração não torna uma estimativa válida.

**G2 — convergência:** exigir um testemunho primal de `P_R` cuja viabilidade seja verificada **exatamente**, com `U=Σy` racional e `U−LB_CG≤1/1_000_000`. O `ObjVal` do Gurobi não é `U` certificado. É admissível testemunho explícito `(V,S,T)` com `λ=1`, `y=1`, `d=0`, produzindo `U=|V|`, desde que exatamente verificado; é válido, embora geralmente fraco. Não declarar convergência sem tal prova.

**B0 separado:** `B0=max(z_COMP^LP,z_core^IP)` só depois de verificar a **proveniência e certificação de seus componentes**; incumbente de core IP interrompido não serve como LB. Um `B0` certificado limita `OPT`, mas pode ultrapassar `z_Q` (caso Tri, `B0=2`, `z_Q=1,5`). Não aplicar L1 nem comparações com `z_Q` ao `B0`.

## Assumptions & Open Questions

| Tema | Decisão / padrão escolhido | Justificativa | Confirmed? |
|---|---|---|---|
| Modo de integração | Certificação opt-in; chamada atual sem certificação preservada | Compatibilidade com N2-T2B | Padrão proposto; revisar na aprovação |
| Aritmética | `fractions.Fraction` e serialização numerador/denominador | Prova exata e reprodutível, sem biblioteca adicional | Padrão técnico proposto |
| Identidade do vetor | Hash canônico sobre instância, K, iteração e coeficientes racionais pós-projeção | Evitar misturas entre iterações | Padrão técnico proposto |
| Ordem dos oráculos | N1 sempre elegível; ENUM quando há cobertura/tempo; N2 quando seu verificador estiver disponível | Evitar depender de ENUM para nível 2 | Estratégia proposta; não muda pré-registro |
| Uso do melhor `ℓ` na mesma iteração | Máximo entre bounds globais certificados para **o mesmo** vetor | Continua ≤`c*`; não misturar vetores | Consequência matemática |
| Testemunho de U | Primeiro provar witness `(V,S,T)` para `U=n`; aceitar candidato mais forte **somente** se reconstruído/verificado exatamente | Não confundir `ObjVal` com upper bound | Estratégia segura proposta |
| Orçamento | Qualquer solve Gurobi de certificação usa orçamento restante compartilhado; Work ausente é registrado, nunca presumido zero | N2-T1/§11.2; não alterar 164 Work | Contrato normativo; engenharia a validar |
| B0 sem evidência | Registrar `B0` como não certificado/indisponível para ganho, sem inventar valor | Core IP parcial ou LP numérico não bastam | Contrato normativo |
| Arquivos de experimento | Nenhum CSV N2-T5 será emitido nesta tarefa; preparar apenas o contrato de linhas | Separar implementação de medição | N2-T3 vs N2-T5 |

**Open questions:** none — todas as decisões científicas estão resolvidas e as escolhas de engenharia estão explicitamente registradas acima. As estratégias de engenharia propostas serão validadas antes da implementação; se inviáveis, documentar o motivo sem reformular a matemática.

## User Stories

### P1: Story 1 — Vetor racional único e Teorema L

**User Story:** Como pesquisador, quero computar exatamente os termos de L1 para um vetor identificado, para obter um limite auditável.

**Acceptance Criteria:**

1. WHEN o snapshot contém apenas coeficientes finitos THEN o certificador SHALL convertê-los sem perda para racionais binários e projetar `μ,κ≥0` antes de recalcular `η,L,δ`.
2. IF o snapshot contém `NaN`, infinito, índices ausentes ou índices extras THEN o certificador SHALL rejeitá-lo sem produzir `CERTIFIED`.
3. WHEN existe `ℓ≤c*` global comprovado para o mesmo vetor THEN o certificador SHALL calcular os três ramos de L1 exatamente e guardar o racional máximo e a prova de sua origem.
4. IF `D=∅` THEN o certificador SHALL calcular `δ=0`.
5. IF a origem do `ℓ` não comprova cobertura global do mesmo vetor THEN o certificador SHALL emitir `UNCERTIFIED`, sem usar o menor custo de colunas vistas ou `ObjBoundC`.
6. WHEN um LB certificado é publicado em decimal, float ou forma inteira THEN o certificador SHALL manter o racional e exportar conservadoramente para baixo, aplicando `ceil(LB−10⁻⁶)` somente ao certificado.

**Independent Test:** casos do parecer com `η>0`, `D=∅`, `δ<0`, vetor zero e aritmética não representável em float; comparar com `Fraction` independente.

### P1: Story 2 — Oráculos globais N1, ENUM e N2

**User Story:** Como pesquisador, quero obter `ℓ` por procedimentos matematicamente válidos, com evidência por oráculo.

**Acceptance Criteria:**

1. WHEN existe vetor racional projetado admissível THEN N1 SHALL retornar seu bound global racional, sem depender de solver ou ENUM.
2. WHEN ENUM enumera todos os conjuntos conexos elegíveis com `truncated=False` THEN ENUM SHALL devolver `min_Q rc` exato, com metadados de cobertura.
3. IF ENUM atingir o cap, inclusive exatamente, ou interromper antes de comprovar cobertura THEN ENUM SHALL retornar ausência de bound global certificado por essa rota.
4. WHEN o verificador N2 recebe `θ,ν` e uma representação racional de P0–P5 THEN ele SHALL verificar sinais/domínios e calcular a fórmula de caixa exatamente.
5. IF a matriz racional de P0–P5 não é reconstituível/auditável ou `ν` não pode ser corrigido com segurança THEN N2 SHALL abster-se de certificar essa rota.
6. IF qualquer oráculo retorna apenas `ObjBound`, `ObjBoundC`, status de solver ou incumbente THEN o agregador SHALL classificá-lo como diagnóstico numérico, nunca como prova global.

**Independent Test:** enumeração força-bruta independente com `n≤6`; verificar `ℓ_N1≤c*`, `ℓ_N2≤c*`, ENUM=`c*`; `cap=total`, `cap>total` e cap parcial.

### P1: Story 3 — Histórico e integração na raiz

**User Story:** Como pesquisador, quero preservar certificados válidos ao iterar e parar o CG sem produzir falsos limites.

**Acceptance Criteria:**

1. WHERE certificação estiver desabilitada THEN o controlador SHALL preservar sua API, comportamento e estados operacionais da N2-T2B.
2. WHEN uma iteração possuir dual válido e houver orçamento THEN a integração SHALL capturar uma cópia imutável dos dados necessários antes de o master ser alterado ou descartado.
3. WHEN uma iteração produz novo LB certificado THEN a integração SHALL manter como corrente o máximo **exato** dos certificados anteriores, com identificação da iteração vencedora.
4. IF pricing, master, certificador, Work ou tempo interromperem a execução THEN a integração SHALL conservar somente certificados previamente comprovados e deverá informar ausência de certificado se nenhum existir.
5. IF a identidade do vetor, `revision`, `solve_id`, instância ou hash de K não corresponde à evidência THEN a integração SHALL recusar o certificado novo.
6. WHEN um registro final é produzido THEN a integração SHALL incluir `certification_status ∈ {CERTIFIED,UNCERTIFIED}` e justificativa não vazia, mantendo `rmp_objective`, `B0` e `convergence_status` em campos separados.
7. WHEN uma certificação aciona um solve adicional do Gurobi THEN a integração SHALL encaminhar os limites restantes e contabilizar o seu Work/tempo sem reajustar o orçamento congelado.

**Independent Test:** CG mockado com duas iterações, LB melhor/pior, snapshot obsoleto, interrupções antes/depois do primeiro LB, limites excedidos, comparação opt-out com 27 testes atuais.

### P1: Story 4 — K, U/G2 e B0

**User Story:** Como pesquisador, quero interpretar corretamente a validade física e a convergência, sem contaminar o LB do master com valores de referência.

**Acceptance Criteria:**

1. WHEN um LB é classificado como limite do MIN-STATION THEN a certificação SHALL exigir K validado pela instância e conferir o hash canônico da instância.
2. IF qualquer corte é inválido, a validação não ocorreu ou o hash mudou THEN a certificação SHALL recusar o selo de LB do MIN-STATION e manter sua justificativa explícita.
3. WHEN existe testemunho primal racional com restrições do RMP verificadas exatamente THEN a verificação SHALL calcular `U=Σy` racional como upper bound do LP completo.
4. IF não existe U validado ou `U−LB_CG>10⁻⁶` THEN o resultado SHALL recusar convergência certificada, ainda que `ℓ≥−10⁻⁶`.
5. WHEN `U−LB_CG≤10⁻⁶` com ambos válidos e da mesma instância THEN a verificação SHALL declarar convergência certificada do LP completo.
6. WHEN B0 é fornecido THEN a camada de resultados SHALL armazenar valor, origem e prova de B0 de forma independente, sem aplicá-lo ao Teorema L nem compará-lo à condição `LB_CG≤z_Q`.
7. IF core IP foi interrompido com apenas incumbente, ou um componente de B0 não tem LB justificado THEN o resultado SHALL rejeitar o rótulo de B0 certificado para esse componente.

**Independent Test:** witness `(V,S,T)` racional, witness não viável por `K` e R3, G2 positivo/negativo, B0=2 com `z_Q=3/2`, K inválido e hash divergente.

## Edge Cases

- IF `S∩T≠∅` THEN a implementação SHALL preservar papéis `s/t` independentes e incluir os pares diretos `(s,s)` elegíveis.
- IF `n=1` ou `W` unitário THEN ENUM e a matriz N2 SHALL tratar ausência de arcos e o limite `f≤n−1=0` corretamente.
- IF TopK receber prêmios negativos THEN o oráculo SHALL exigir pelo menos um terminal de cada lado e **não** omitir o primeiro incremento.
- IF `ℓ` é estritamente menor que `c*` mas validamente global THEN L1 SHALL aceitá-lo como bound possivelmente fraco.
- IF um teste artificial fornecer `ℓ>c*` THEN a verificação independente SHALL demonstrar que não é um certificado e bloquear a publicação como válido.
- IF `η>0` THEN o cálculo SHALL descontar esse termo em `L`, sem dupla contagem de UB.
- IF o cap de ENUM for igual ao número de conjuntos visitados THEN a implementação SHALL respeitar o indicador de truncamento, sem inferir cobertura.
- IF Work não puder ser medido em um solve adicional THEN o relatório SHALL declarar a lacuna e seguir a política de interrupção do orçamento compartilhado, sem somar zero fictício.
- IF o certificado tiver origem `N1` ou `N2` e a geração de colunas for interrompida THEN o histórico SHALL preservar o bound certificado e a instância/vetor que o sustentam.

## Cross-cutting Requirements

| Dimensão | Regra ou justificativa N/A |
|---|---|
| Entrada e limites | Coeficientes finitos e exatos; índices/domínio consistentes; cap de ENUM e orçamento restante estritos |
| Falha parcial | Nunca `CERTIFIED` sem provas completas; histórico conserva apenas certificados anteriores válidos |
| Reexecução/duplicação | Mesmo vetor e mesma prova têm identificador determinístico; reprocessar não duplica um ganho |
| Ordenação | Cada certificado aponta para instância, revisão, `solve_id`, vetor pós-projeção e K específicos |
| Observabilidade | Fonte do oráculo, valores racionais, causas de abstenção e custo de cada solve rastreáveis |
| Dependência externa | Gurobi propõe duais/colunas; nunca decide validade matemática por status/ObjBound |
| Autenticação e rate limiting | N/A: execução científica local sem serviço multiusuário |
| Persistência/expiração | N/A nesta fase: objetos e relatórios locais, sem armazenamento remoto nem TTL |
| Transições | Apenas prova global + aritmética exata permitem `CERTIFIED`; interrupções não promovem estado |

## Requirement Traceability

| Requirement ID | Story | Entrega | Status | Teste / evidência planejada | Referência N2 |
|---|---|---|---|---|---|
| CERT-01 | 1 | E1 | Validado | Frações, projeção e identificação | Story 3 / `COMPAT-BOUND-15` |
| CERT-02 | 1 | E1 | Validado | L0/L1, `η`, `δ`, contraexemplos | Story 3 / `COMPAT-BOUND-17` |
| CERT-03 | 1 | E1 | Validado | Exportação dirigida e inteiro | Story 3 / `COMPAT-BOUND-15` |
| CERT-04 | 2 | E1 | Validado | N1 global vs enumeração exata | Story 3 / `COMPAT-BOUND-16` |
| CERT-05 | 2 | E2 | Validado | ENUM, cap e TopK exato | Story 3 / `COMPAT-BOUND-16` |
| CERT-06 | 2 | E3 | Validado | P0–P5 racional, N2 ≤ c* | Story 3 / `COMPAT-BOUND-17` |
| CERT-07 | 2 | E1–E3 | Validado | Bloqueio ObjBound e prova parcial | Story 3 / `COMPAT-BOUND-15` |
| CERT-08 | 3 | E4 | Validado | Histórico e última prova sob interrupção | Story 3 / `COMPAT-BOUND-18` |
| CERT-09 | 3 | E4 | Validado | Opt-in preserva 87 testes N2-T2B | Story 3 / `COMPAT-BOUND-15` |
| CERT-10 | 3 | E4 | Validado | Work/tempo reais ou ausência explícita | Story 3 / `COMPAT-BOUND-18` |
| CERT-11 | 4 | E5 | Validado | Integridade de K e assert_valid_cuts | Story 3 / `COMPAT-BOUND-16` |
| CERT-12 | 4 | E5 | Validado | U exato e G2 | Story 3 / `COMPAT-BOUND-16` |
| CERT-13 | 4 | E5 | Validado | B0 e Tri sem comparação inválida | Story 3 / `COMPAT-BOUND-16` |
| CERT-14 | 1–4 | E5 | Validado | Estados/justificativa, edge cases e independência | Story 3 / `COMPAT-BOUND-19–20` |

**Coverage:** 14 requisitos mapeados e com implementação/testes associados em E1–E5. Aceite técnico de implementação documentado no gate N2-T3; a produção do CSV experimental pertence à N2-T5 e não foi executada.

## Success Criteria

- [x] N1/ENUM/N2 produzem provas globais auditáveis e passam testes exatos independentes.
- [x] `LB_CG` certificado decorre de L1 racional e do **mesmo** vetor, nunca de `z_R` ou `ObjBound`.
- [x] Toda linha/result tem `CERTIFIED` ou `UNCERTIFIED`, justificativa e origem, com B0 separado.
- [x] Interrupções preservam somente o melhor limite anteriormente comprovado.
- [x] G2 só vale com U primal validado exatamente; K precisa de evidência por instância.
- [x] 87 testes do Gate O continuam passando; testes novos dirigidos são aprovados sem skips de certificação silenciosos.
- [x] Validações N1/N2-T1 permanecem `PASS` e hashes permanecem intactos.
- [x] Não há alteração em arquivo congelado nem campanha N2-T4/T5/T6.

**Estado após fechamento:** N2-T3 implementada e aceita operacionalmente, nos limites das evidências e ressalvas do registro formal. Isso **não** significa `N2 PASS`, certificado universal de toda instância nem certificação automática de B0; N2-T4/T5/T6 continuam pendentes.
