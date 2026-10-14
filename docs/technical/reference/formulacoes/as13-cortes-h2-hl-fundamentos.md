# AS13 — Fundamentos físicos e matemáticos de H2 e HL

**Natureza:** revisão matemática e microvalidação, não experimento em instâncias grandes.  
**Referência de código:** branch `novos_testes`, commit `ed1a04740e59f2c8ae4f13e9a62b69624032fa62` (blobs centrais verificados).  
**Especificação:** `specs/as-13-fundamentacao-h2-hl/spec.md`.  
**Situação após parecer independente:** `FAIL / NO GO`. O Opus encontrou três documentos de prova ausentes no checkout auditado e lacunas de testes. Este arquivo compõe um patch corretivo, não constitui aceitação científica; **AS14 continua bloqueada até nova revisão independente**.

## 1. Domínio e invariantes

Considerar o problema original de Das em grafo **simples, conexo, não direcionado e unitário** `G=(V,E)`, autonomia inteira `r≥1`, origens `S⊆V`, destinos `T⊆V`, `|S|=|T|=m`, robôs anônimos. Estações podem ser instaladas em qualquer vértice de `V`, inclusive em `S∪T`, e podem atender vários robôs, sem limite de capacidade. Cada robô parte com bateria completa; alcançar o destino não exige estação. Permitir `S∩T≠∅` e a opção de permanecer no mesmo vértice.

A implementação do comparador (`experiments/alternative-formulations/as02_model_a.py`, `compile_u`) utiliza fluxo **contínuo** e instalação `y_v` binária em MIP; suas relaxações LP têm `0≤y_v≤1`. As desigualdades K construídas em `experiments/cuts/cuts.py` são suportes `y(Z)≥1` de C1, C2 e C4-DM. O conjunto K **efetivamente gerado** não equivale a todas as desigualdades de Hall possíveis.

## 2. Oráculo físico e bipartido anônimo

Construir o dígrafo de alcance `A_r={(u,v):u≠v, d_G(u,v)≤r}`. Para `C⊆V`, construir `B_C=(S^L,T^R,E_C)`, com **cópias distintas** de cada vértice no lado esquerdo e direito, mesmo quando há interseção `S∩T`. Incluir a aresta `(s,t)` quando:

1. `s=t`, permitindo permanência com deslocamento zero; **ou**
2. há um caminho de `s` a `t` em `A_r` cujos vértices **internos** pertencem a `C`.

Definir `ν(C)` como a cardinalidade de um matching máximo de `B_C`.

**Proposição P1 (caracterização exata):** uma instalação `C` é fisicamente viável se, e somente se, `ν(C)=m`.

**Prova:** Se a instalação é viável, cada um dos `m` robôs sai de uma origem diferente e termina em um destino diferente. Cada viagem pode ser subdividida em trechos de comprimento `≤r` com recarga apenas em vértices instalados; assim, determina uma aresta de `B_C`. As viagens determinam um matching de tamanho `m`. Reciprocamente, um matching perfeito escolhe um destino para cada origem e uma rota compatível para cada aresta. A ausência de capacidade das estações e de restrições de colisão permite utilizar todas essas rotas conjuntamente, inclusive compartilhando os mesmos relés. O caso `s=t` dispensa deslocamento e estação. ∎

**Proposição P2 (monotonicidade):** `C⊆C' ⇒ E_C⊆E_C' ⇒ ν(C)≤ν(C')`. Qualquer estação adicional só amplia as possibilidades de recarga, nunca remove um caminho. ∎

**Importante:** deficiência de Hall igual a `δ` **não exige** `δ` estações distintas. Um único relé compartilhado pode atender muitas origens. Tampouco o ganho de matching pela instalação é submodular em geral: no caminho `s-a-b-t`, `r=1`, somente a dupla `{a,b}` torna possível o atendimento.

## 3. Critérios de independência da auditoria

O arquivo `experiments/cuts/verify_as13_foundations.py` confronta, nos mesmos conjuntos de instalações:

- **Oráculo A:** `independent_validator.viavel`, que percorre estados `(v,bateria)` no grafo físico original e depois calcula matching;
- **Oráculo B:** `reach_matching_oracle`, implementado especificamente para a auditoria, que alcança destinos por `A_r` usando apenas estações intermediárias em `C` e depois calcula matching.

A independência aqui é **algorítmica de representações** (bateria física versus arcos de alcance), não substitui auditor externo. Ambos usam a caracterização de matching no destino; a auditoria adicional valida testemunhas manualmente demonstráveis. Para HB e quatro relés, 674 pares (configuração, instância) foram comparados; outros 64 pares cobrem controles de terminais compartilhados, permanência, caminhos com duas estações e compartilhamento de relé.

## 4. O que está e não está certificado

- As demonstrações de validade de P1/P2/H2/HL são argumentos matemáticos gerais, condicionados ao domínio acima.
- Os resultados `1→2` e `2→8/3→3` são testemunhas matemáticas reproduzidas numericamente por SciPy/HiGHS, usando **exatamente as equações COMP geradas pelo compilador existente**. Não são certificados racionais externos, embora haja argumentos simbólicos para cada valor (nos documentos seguintes).
- As pequenas enumerações e os testes negativos dão evidência de correção, não uma demonstração de completude do futuro **algoritmo de separação**.
- A AS13 **não** implementa separador, **não** modifica K/COMP e **não** mede desempenho em grafos de produção.

## 5. Referências internas

- `docs/project-overview.md`, `RESEARCH.md`, `docs/context-ai/base-formulation.md`;
- `experiments/alternative-formulations/as02_model_a.py`;
- `experiments/cuts/cuts.py`, `experiments/cuts/independent_validator.py`;
- `experiments/structural/hb.py`;
- `docs/technical/reference/tecnico/c6-hall-primeiro-salto.md`;
- `docs/technical/reference/experimentos/resultados-e9-e10-pli.md` e `resultados-e12-pli.md`;
- análise Astra de 13/10/2026 (fonte de hipótese, não comprovação autônoma).
