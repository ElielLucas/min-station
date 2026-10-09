# N2-T2B — Entrega 1: implementação do master restrito e dual (Astra)

**Estado:** `AUTORIZADO PARA DESENVOLVIMENTO` pelo Gate M de 2026-10-09; **implementação não iniciada neste registro**.  
**Relação de dependência:** esta é a primeira entrega incremental da N2-T2B. **Não** é o Gate O, N2-T3 ou N2-T4.  
**Fonte matemática normativa:** `docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md`, **v2.1**, SHA-256 `db1fb71b6e4afba421ccc9f8d4f244aee6700edb886dc1c0219ed7e812aa9237`.  
**Autorização:** `docs/technical/plans/execucao/n2-t2b-decisao-aprovacao-matematica.md`.

## 1. Objetivo e limite desta entrega

Implementar, em **módulo novo** de `experiments/alternative-formulations/`, um master LP restrito de colunas
`q=(W,I,J)` F-CC+K, com extração de `π,τ,μ,κ` do Gurobi, reconstrução explícita de `η`, custo reduzido
reproduzível e API para **inserir colunas validadas**. Construir testes determinísticos sobre instâncias
minúsculas. Não implementar ainda **oráculo de pricing**, busca de colunas, laço de geração de colunas,
certificação ENUM/N1/N2, experimento ou relatório de desempenho. Não usar o RMP como limite inferior.

A arquitetura deve permitir a próxima entrega (pricing) **sem antecipá-la**. Usar `/tlc-spec-driven` e
`/karpathy-guidelines` quando disponíveis, mas as equações/documento aprovado prevalecem.

## 2. Arquivos de referência obrigatórios

1. `CLAUDE.md`, `docs/project-overview.md`, `RESEARCH.md` e `docs/context-ai/code-guidelines.md`.
2. `specs/proxima-fase-n2-limite-compatibilidade-certificado/spec.md` (Story 2B).
3. `docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md` (seções 0–4, 6 e 11).
4. `docs/technical/reference/formulacoes/parecer-independente-N2-T2B.md` (sobretudo C.1–C.3, D-1/D-2).
5. `experiments/alternative-formulations/fcc.py` (sem modificar: `grafo_H`, `pares_diretos`, `B_de`).
6. `experiments/alternative-formulations/fcc_k.py` (sem modificar: `prepare_k` e hash K).
7. `experiments/cuts/cuts.py` e `experiments/cuts/harness.py` (somente para compreender e reutilizar cortes).
8. `experiments/alternative-formulations/test_n2_t2b_controles_matematicos.py` (referência de casos dirigidos).
9. `experiments/alternative-formulations/n2-t1-freeze.json`, pré-registro e decisão N1-T7 (somente leitura).

## 3. Contrato matemático obrigatório

Domínio: `G` simples, conexo, não dirigido e unitário; `r≥1`, `|S|=|T|=m≥1`, `S∩T` permitido;
`H=G^r`; `D={(s,t):s=t ou d_G(s,t)≤r}`, inclusive `d_ss`.

Para uma lista explícita inicial `Q_R⊂Q` **sem vazio**, construir:

- `λ_q≥0` para `q=(W,I,J)` conexo em H, `W≠∅`, `I⊆S∩B(W)`, `J⊆T∩B(W)`, `1≤|I|=|J|`;
- `d_st≥0` para **todos** os pares diretos D;
- `0≤y_v≤1` para todo vértice v;
- objetivo `min Σ_v y_v` (**nunca** `Σ|W_q|λ_q`);
- R1: `Σ_{q:s∈I_q}λ_q+Σ_{t:(s,t)∈D}d_st=1` para cada s;
- R2: `Σ_{q:t∈J_q}λ_q+Σ_{s:(s,t)∈D}d_st=1` para cada t;
- R3: `Σ_{q:v∈W_q}λ_q−y_v≤0` para cada v;
- K: `Σ_{v∈Z} y_v≥1` para cada `Z` da lista congelada `prepare_k`;
- **não** impor ub explícito em `λ` e `d` (já implícitos por R1/R2);
- manter `y` contínuo; nenhuma variável inteira, branching, MIP ou corte adicional.

O RMP deve iniciar viável com a coluna `(V,S,T)`; cortes K e pares D são todos incluídos.
`K` deve ser **exatamente** o da fonte N1 (`C1/C2/C4`), em ordem canônica; registrar
`k_hash`, número de cortes e conferir o hash informado. Reutilizar `prepare_k` sem recriar sua semântica.
Se algum parâmetro já oferece K exato, conferir o digest, não regenerar silenciosamente outro conjunto.

**API mínima recomendada**, ajustável à arquitetura real apenas mediante justificativa explícita:

- construir o RMP a partir da instância e de K (ou construir K pela função aprovada);
- adicionar coluna `(W,I,J)` após **validação combinatória completa** e rejeitar duplicatas;
- otimizar o LP e retornar status, objetivo RMP e multiplicadores com mapeamento de nomes/linhas;
- calcular custo reduzido `μ(W)−π(I)−τ(J)` independentemente de `RC` numérico e comparar com `Var.RC`;
- expor metadados de integridade (`k_hash`, quantidade K, Q_R e parâmetros usados).

Evitar API que permita associar prêmios de iterações diferentes ao mesmo custo reduzido.
O método que extrai duais **só** pode ser chamado após `GRB.OPTIMAL` para LP contínuo;
tratar explicitamente outros status e falhas, sem fabricar multiplicadores.

## 4. Convenções duais e cuidados de implementação

- `π_s = Pi(R1_s)` e `τ_t = Pi(R2_t)` (multiplicadores livres).
- `μ_v = -Pi(R3_v)≥0` porque R3 foi escrita como `Σλ−y≤0`.
- `κ_Z = Pi(K_Z)≥0` para `Σ y≥1`.
- `η_v = max(0, μ_v+Σ_{Z∋v}κ_Z−1)` (UB nativo de y não aparece como uma linha Pi normal).
- `L=Σπ+Στ+Σκ−Ση`. Não omitir `η`, nem contá-la duas vezes.
- `rc_q=μ(W)−π(I)−τ(J)`; par direto `rc_st=−π_s−τ_t`.
- Solução ótima do RMP tem `z_R≥z_Q`; `z_R` **não** é cota inferior de MIN-STATION nem `CERTIFIED`.
- Usar tolerâncias numéricas para **testes**, sem inferir certificado racional delas.
- Se precisar inspecionar reduced costs de colunas que estão básicas/no limite, comparar formulações
  coerentes com convenção de ub das variáveis (sem ub explícito para `λ,d`).

## 5. Casos de teste que devem passar nesta entrega

1. Caminho `a–b–c`, `S={a}`, `T={c}`, `r=1`, `K={{b}}`: RMP com apenas `(V,S,T)` vale 3;
   ao inserir coluna `({b},{a},{c})`, vale 1. **Objetivo RMP ≠ LB**.
2. Controle com `η>0`: testar reconstrução de `η`, `L` e custo reduzido (não presumir `η=0`).
3. `S∩T` não vazio: pares `d_ss` presentes, papéis I/J separados; caso de `S=T={a}` permite RMP de valor 0.
4. `D=∅`: construir sem pares diretos, preservando R1/R2 e a coluna inicial viável.
5. Rejeitar colunas inválidas: `W=∅`, W desconexo em H, I/J vazios ou desbalanceados,
   terminais inelegíveis, duplicatas, extremos fora dos conjuntos; não fixar matching.
6. Reproduzir o `k_hash` esperado e contagem K sem alteração; rejeitar hash divergente.
7. Conferir sinais de `Pi`, custos reduzidos contra `Var.RC` para colunas do RMP e dualidade forte
   em instâncias pequenas com `GRB.OPTIMAL` (tolerância explicitada).
8. Um RMP com nova coluna não aumenta seu ótimo (dentro de tolerância); verificar a condição com degeneração
   sem exigir melhoria estrita para toda coluna negativa.
9. Nenhuma API deste módulo devolve `CERTIFIED` ou `LB_CG` por padrão, e nenhuma execução grava resultados N2.

**Reexecutar**, além dos testes novos:

```bash
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t1.py check
PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p test_n2_t2b_controles_matematicos.py -v
```

Os 18 testes originais foram previamente relatados como `OK` no ambiente com Gurobi. Não confundir
esse resultado histórico com teste executado nesta entrega. Se `gurobipy` não estiver disponível,
registrar isso como bloqueio de validação integral e **não** afirmar que todos passaram.

## 6. Entrega ao pesquisador e limites

- Implementação nova em `experiments/alternative-formulations/`, com nomes claros e docstrings;
  exemplo: `n2_t2b_master.py`, `test_n2_t2b_master.py` (evitar arquivos duplicados sem necessidade).
- Sem editar `fcc.py`, `fcc_k.py`, `cuts.py`, `harness.py`, N1, pré-registro, freeze ou documento matemático v2.1.
- Incluir testes e breve documentação da API no próprio módulo ou em README compatível com a árvore existente.
- Nenhum experimento de nível 2, nenhum CSV N2, nenhuma comparação de ganho, nenhum tuning experimental.
- Nenhum commit automático; relatar diff, resultados reais dos testes e pendências antes da próxima entrega.

**Critério de saída desta entrega:** código e testes do master/dual passam sem alterar os congelamentos;
pronto para implementar o pricing na entrega 2. **Não** declarar Gate O concluído.
