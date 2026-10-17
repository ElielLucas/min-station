# Parecer pós-AS28 — próxima direção científica do MIN-STATION

> **Data:** 2026-10-17. **Branch:** `novos_testes` (commit de partida `f935abb`).
> **Tipo:** parecer de pesquisa elaborado por assistente de IA a pedido do pesquisador. É **proposta sob revisão**, não spec, não prova independente e não autorização de implementação.
> **Escopo:** problema original de Das (baseline U/COMP+K, estações em todo `V`, `S∩T` permitido). Nada aqui introduz custos, capacidades, rótulos ou autonomias heterogêneas.
> **Rotulagem:** [FATO] verificado em arquivo/JSON; [EXP] medição pontual feita para este parecer; [PROVA] argumento matemático (esboço, precisa de auditoria); [HIP] hipótese; [ESP] especulação.
> **Limite das sondas [EXP]:** uma seed, Gurobi 12.0.3, 4 threads, máquina com carga concorrente, sem réplica e sem pré-registro. São indícios, não resultados. Os scripts ficaram fora do repositório (scratchpad da sessão): `ls_primal.py`, `ld_bound.py`, `dominance.py`, `dom_mip.py`.

## 1. Resumo executivo

**Recomendação:** método exato no espaço de instalação `y`, em três camadas (nome provisório **Y-RBC**):

1. reduções seguras por dominância de vizinhança em `H = G^r`;
2. mestre inteiro de cobertura (núcleo K) com cortes de projeção do fluxo de COMP, separados por max-flow em nós fracionários e inteiros;
3. oráculo exato de viabilidade (componentes de `H[C]` + matching) como lazy constraint e heurística primal.

**Justificativa:** o gap das instâncias difíceis é inteiro, não LP. Toda família fracionária avaliada esbarra num patamar próximo do LP de COMP+K. Os melhores limites conhecidos vêm de dois mecanismos inteiros distintos (IP do núcleo e B&B de COMP+K) e nenhum método atual obtém os dois. Y-RBC visa `max(núcleo, COMP)` por construção e ataca o gargalo de tamanho medido em Vienna e MAPF.

**Confiança moderada-baixa.** A direção reabre parcialmente BC-y/CBI (E7/E8/E12) e só prossegue se os gates G2a/G2b (§10) passarem. Se falharem, o achado é "patamar LP + limite da cobertura inteira em PUC r=1", também defensável.

## 2. Estado atual

[FATO] (`linha_base.csv`, agregação de agente): 39/75 instâncias principais fechadas; 36 abertas com gap mediano 21,8%. Nas 29 D/A: gap 3,2–55,6%, mediana 18,6%. O regime difícil é `r` pequeno frente a λ\*, UB/m ≈ 0,5 (mediana 0,50 nas abertas, 0,25 nas fechadas), onde `(m−b_v)y_v` dilui a ativação por até `m`. K (C1+C2+C4-DM) recupera a maior parte: CC9 1,25 → 27,03; BIP42 1,0 → 31,7.

**Nomenclatura (divergência):** nas fases E7–E14 e na linha de base, COMP = U + C1+C2+C4-DM. Do AS04 em diante, COMP = U sem cortes e COMP+K = antigo COMP. Este parecer usa a convenção AS.

**LB\* — procedência** [FATO]: `resultados-linha-de-base.md` (Spec A R4). LB\* = ⌈maior `mip_bound` − 1e-6⌉ entre os braços base, comp e núcleo, `WorkLimit=164`, 3 sementes. São bounds numéricos do Gurobi, não certificados e não ótimos.

| Instância | COMP+K LP | Núcleo IP | COMP MIP | LB\* (fonte) | UB\* |
|---|---:|---:|---:|---|---:|
| CC9 | 27,03 | 27 (ótimo) | **31 ótimo** (AS06/AS09) | 30 (**desatualizado**) | 31 |
| BIP42 | 31,71 | bound 35, incumbente 37 | 33 | 35 (núcleo) | 43 |
| CC3 | 16,93 | **18 (ótimo)** | 17 | 18 (núcleo) | 26 |
| MAPF Room m10 | 13,2 | 13 | 16 | 16 (comp) | 18 |
| Vienna I056 | 8,5 | 9 | 9 | 9 | 11 |
| W3C571 | 432,9 | 571 | 669–678 | 669 | 1064 |

Divergências registradas: o `manifest.csv` traz `lb` 33/17/666 (COMP, 600 s), não 35/18/669; `resultados-linha-de-base.md` e AS28 §4.1 tratam CC9 como aberta, mas AS06/AS09 provam numericamente OPT = 31. A comparação LB\* × LP da AS28 §4.1 mistura bound MIP de outras configurações com LP pareado de 90 s e serve apenas como régua de relevância.

## 3. Síntese dos resultados anteriores

| Linha | Alvo | Válida | Ganho LP sobre COMP+K | Custo | Conclusão | Reabrir? |
|---|---|---|---|---|---|---|
| A (grupos de origens) | desagregar ativação | sim (revisão pendente) | ≤ 0,70% (A4); interação negativa com K em 6/6 | ~4× variáveis | K absorve o ganho | não |
| B caminhos + CG (AS08) | DW de A_unit | sim; proj = A_unit | CG nunca convergiu; certificados 25–62% abaixo do LP COMP+K | 0/6 convergências | inconclusivo | não |
| C cumulativa (AS09) | tamanho | proj = COMP | LP igual em 30/30 | 3,7× menos variáveis; MIP não melhor; sem K colapsa; `VALIDATION_FAIL` em w3c571 C+K nunca investigado | suspensa | só como representação |
| Desagregação por origem (T18) | multicommodity | sim; errata: não domina U | só gadgets, contra base sem K | O(m·\|A_r\|) | pausada | não (parte individual = C3) |
| F-CC(+K) | configurações conectadas | sim (GF1 PASS) | sem dominância (SharedTerminal 0,5 < 1) | explosão de W; N2 FAIL | teórica/diagnóstica | não sem pricing novo |
| F-C3 | trios | sim | só Tri (núcleo já ótimo) | explosivo | não promovida | não |
| CBI / BC-y (E7/E8/E12) | Benders combinatório em y | sim (Teorema 6) | raiz ≈ núcleo | callback 70–99,9% do tempo; start com 767–915 estações | 0 vitórias contra o núcleo; encerrada para Das | **condicional (§6)** |
| Lagrangeana L1 | bound | — | ≤ LP em 8/8 | — | teto teórico = LP | só com outro subproblema |
| H2 (AS16) | insuficiência local | parcial | **0 cortes emitidos** nos 4 braços U_K_H2 | orçamento esgotado em BIP42/CC3 | STOP | não |
| HL (AS20–22) | casco local | sim | 0 | — | se V∖R viável ⇒ cubo | não |
| FC-R (AS25/25.1) | cobertura de fluxo regional | sim (AS23 PASS) | +0,109% / +0,025% / 0 / +0,606%; fecho BIP42 +1,17% (5203 linhas, ~400 s) | — | classe B; encerrada | não |
| C3-cut (AS28) | conectividade individual | sim | +0,011% / +0,928% / 0 / 0 | separação 0,2–1,2 s | `NO_SIGNAL_BOUNDED_POLICY` | não |

**Disjunções globais.** O parecer versionado (`parecer-astra-pos-as251-disjuncoes-globais.md`) recomenda diagnóstico limitado, não parada. O parecer "independente" contrário citado no pedido **não está no repositório** (a AS28 cita um parecer Opus não versionado). Os argumentos do texto do Astra (teto de uma disjunção isolada = mínimo de 4 LPs; certificado = CGLP de Balas; testemunha K4 derivável por arredondamento de K) não revelam falha na decisão de não priorizar. Direção mantida fechada.

**BIP42 na AS28** [FATO, reexecução de agente]: os 5 cortes têm a mesma estrutura, `Z = (N(raiz) ∖ {w}) ∪ (N(w) ∖ N[raiz])`: a cobertura C1 com um vizinho não terminal `w` empurrado um salto. O mecanismo é real mas marginal: o LP fica apenas 3,5·10⁻⁴ acima de 32 e a raiz do Gurobi sobre COMP+K já dá 33 (AS09). Pode virar família estática barata ("C1 levantado"); não justifica linha de pesquisa. Os suportes C3 não são persistidos pelo runner da AS28.

## 4. Diagnóstico dos gargalos

Resposta à pergunta 3.4: combinação, com peso desigual.

1. **Régua desalinhada e patamar LP (dominante).** Os gates mediram ganho LP ≥ 1% sobre COMP+K, mas o limite competitivo é inteiro e bem acima desse LP (BIP42 +10%, CC3 +6%, CC9 +15% até o ótimo, Room +21%). A, B, C e a desagregação projetam em `y` ao redor de COMP+K.
2. **Estrutura.** 4 dos 6 grafos de desenvolvimento são PUC/PUCN com r=1, onde a dominância fixa 0% [EXP].
3. **Tamanho.** Vienna, warehouse e random-64: LP raiz de 16–320 s, `node_count = 1` sob `WorkLimit`, RSS de GiB [FATO]; censuras de Vienna e W3C571 em todas as campanhas LP de 90 s.
4. **Custo de separadores: secundário.**

**Sonda DW [EXP]:** bound `L* = min{1ᵀy : y ∈ proj LP(COMP+K) ∩ conv(Y_núcleo)}` (domina `max(núcleo, LP)` por construção). O valor do mestre restrito é **cota superior** de `L*`: CC9 ≤ 27,40 (OPT 31, 43 iterações); Room ≤ 15,11 (LB\* 16); CC3 ≤ 18,64 (núcleo 18); BIP42 inconclusivo. Convexificar cobertura junto com o fluxo não fecha o gap, o que descarta a Lagrangeana por decomposição como direção principal. Os limites Lagrangeanos ficaram muito negativos por degenerescência dual.

**Sonda primal [EXP]:** ILS ingênuo com oráculo de matching reproduziu UB 18 (Room) e 26 (CC3); não bateu BIP42 (55 contra 43) nem CC9 (32 contra 31). O OPT de BIP42 e CC3 segue desconhecido.

## 5. Alternativas investigadas

- **A. F-CC com branch-and-price estabilizado.** Ataca compatibilidade (Γ>0); força real só em gadgets. Contra: N2 FAIL (o projeto atribui a falha ao certificador, mas a enumeração de W permanece), LP sem dominância sobre COMP. Risco alto.
- **B/C. Lagrangeana núcleo × COMP.** Única Lagrangeana que cumpria a condição de reabertura; refutada pela sonda.
- **D. Y-RBC (escolhida).**
- **E. Novos cortes.** Só "C1 levantado", com teto na raiz do Gurobi.
- **Descartadas:** Benders clássico isolado e Lagrangeana da ativação (teto = LP); simetria genérica; decomposição por separadores (matching acopla regiões, `direcoes` R9).
- **Multicommodity B1 (variante all-V, nunca testada):** parte individual projetada em `y` é o C3 (ganho ≈ 0 na AS28); o acoplamento por destinos só dá cortes `(|X|−k)/|X|`, mais fracos que o C4-DM arredondado já em K; custo O(m·|A_r|). Fica como controle opcional no G2b.

## 6. Comparação crítica

| Critério | A: F-CC B&P | C: Lagrangeana núcleo×COMP | **D: Y-RBC** |
|---|---|---|---|
| Fraqueza atacada | compatibilidade Γ | integralidade da cobertura com fluxo | envelope inteiro + tamanho |
| Limite potencial | alto em gadgets; desconhecido em reais | ≤ 27,4 (CC9), ≤ 15,1 (Room) [EXP] | meta ≥ max(núcleo, COMP); LP não sobe |
| Desempenho potencial | baixo (pricing) | baixo | médio, plausível em MAPF/Vienna |
| Escalabilidade | ruim | média | boa |
| Implementação | alta | média | média (oráculo e cortes existem) |
| Validação | difícil | fácil | fácil (oráculo exato, bateria T2) |
| Reuso | `fcc.py`, N2 | núcleo, COMP | `integer_oracle`, `separate_classical_fracs`, `bc_yspace.py`, K |
| Risco de repetir negativo | alto | já materializado | médio (E8/E12) |
| Contribuição | formulação | baixa | algoritmo exato + reduções + caracterização do patamar |
| Experimento mínimo | caro | feito | barato (G2a/G2b) |

**Por que D não é "reorganizar callbacks"** (condição de reabertura da Análise Consolidada §6). Evidência nova desde E8/E12: (1) envelope medido sob o mesmo orçamento (núcleo vence COMP MIP em BIP42, CC3, hc10p, hc11p; o inverso em CC9, MAPF, W3C571); (2) patamar LP em 9 linhas + sonda DW; (3) gargalo de tamanho (`node_count = 1`); (4) reduções medidas [EXP]:

| Instância | Fixados | Arcos | LP | Tempo LP | MIP base → dom (300 s) |
|---|---:|---|---:|---|---|
| Vienna I056 | 1360/1991 | 381.600 → 66.042 | 8,5 = 8,5 | 21 s → 3,1 s | UB 12 → 11; LB 9 = 9; nós 1 → 272 |
| MAPF Room m10 | 330/682 | 11.622 → 4.224 | 13,2 = 13,2 | 0,5 s → 0,1 s | LB 15 → 16; UB 18 = 18; nós 1319 → 15204 |
| CC9, CC3, W3C571, hc9u | 0% | — | — | — | — |
| BIP42 | 4% | — | — | — | — |
| warehouse m25 | 2,5% | — | — | — | — |

Leitura: tamanho cai e throughput sobe muito; o bound não melhora de forma comprovada em 300 s. Uma seed, sem réplica.

**Pré-processamento já testado (ressalva):** `experiments/preprocessing/` (folhas, RS/RT, arcos zerados, dominância Pred/Succ, separadores obrigatórios) em ~12 instâncias legadas/extensões: LB igual, UB de bip42p piorou (46 → 49), Barcelona st25 de 624 s para 799 s ("sem ganho robusto", H18). Não foi no benchmark-v1 de Das e a sonda aqui usa dominância de vizinhança fechada em `G^r`, mas G2a deve comparar explicitamente com esse resultado e ser pré-registrado.

Mecanismos ausentes no BC-Y' do E8: (i) separação de projeção em todos os nós (E8 só em nós rasos e desligava com |A_r| > 500 mil); (ii) rede restrita compilada; (iii) heurística primal pelo oráculo; (iv) múltiplos cortes de Hall por ponto inviável (CBI gerava um por incumbente); (v) reduções antes de tudo.

## 7. Recomendação

Investir em D (Y-RBC) em estágios que abortam cedo. Os estágios 1 e 2 isolados já seriam avanço computacional publicável. Se Y-RBC não atingir o envelope em ≥ 2 grafos brutos, parar.

## 8. Proposta matemática

**Dados.** `G` não dirigido conexo; `S, T ⊆ V`, `|S| = |T| = m`; `r` em passos; `a_v = [v∈S]`, `b_v = [v∈T]`; `H = G^r`; `N_H[v] = {u : d(u,v) ≤ r}`.

**Reduções.**
- **R-dom:** `F = {u : ∃ v≠u, N_H[u] ⊆ N_H[v], e (|N_H[v]| > |N_H[u]| ou ord(v) < ord(u))}`; fixar `y_u = 0` para `u ∈ F`.
- **Teorema D [PROVA, esboço; auditar]:** existe ótimo `C*` com `C* ∩ F = ∅`. Substitua `u ∈ C` pelo dominador maximal `w` (relação acíclica e transitiva). Toda componente `K` de `H[C]` vira `K − u + w`, ainda conexa porque `N_H(u) ⊆ N_H[w]`. Todo terminal `x` com `N_H[x] ∩ K ∋ u` satisfaz `x ∈ N_H[u] ⊆ N_H[w]`. Arestas diretas e permanência em `S∩T` não mudam; logo `B_{C'} ⊇ B_C` e, por monotonicidade, `C'` é viável. O desempate por ordem em gêmeos evita remover ambos (corrige a ressalva do R3 de `direcoes` §10).
- **Remoção de arcos (R4):** `(x,u)` com `u ∈ F∖T` e `(u,x)` com `u ∈ F∖S`.
- Também: R8 (componentes pendentes) e regra de módulos (IJCAI Lema 4, r=1).

**Mestre MP.** `min Σ_v y_v`, `y ∈ {0,1}^V`, `y_F = 0`, linhas K com `Z∖F`. Cortes dinâmicos sobre a rede `N(y)` de `direcoes` §3.1 / `integer_oracle` (relés de capacidade `κ_v y_v`, arcos de permanência para `S∩T`):
- **(BF)** `Σ_{v∈Z(X)} κ_v y_v ≥ m − c₀(X)` (corte de viabilidade; a família completa é exatamente `proj_y LP(COMP)`);
- **(BR)** se `c₀(X) < m`, então `y(Z(X)) ≥ 1` (Teorema 6 do projeto).

**Separação.** Nó fracionário: max-flow em `N(y*)` restrito a `S ∪ T ∪ supp(y*)`, recuperando candidatos com `y* = 0` como no passo 2 do `integer_oracle`; exata para BF. Nó inteiro (MIPSOL): oráculo exato; se inviável, vários BR disjuntos. **Primal:** arredondar `y*`, reparar por aumento de Hall (0-1 BFS), reverse-delete, validar no oráculo.

**Correção.** (1) Toda solução viável é representável; com R-dom, um ótimo sobrevive (Teorema D). (2) Todo inteiro aceito passa no oráculo exato: fluxo `m` em `N(y)` ⇔ matching perfeito em `B_C` (IJCAI Lema 2 corrigido, Erratum 1; validação T2/E8). (3) Matching anônimo, `S∩T` e terminais ficam no subproblema; o mestre não tem fluxo nem circulação. (4) `κ_v ≥ m−1` é limite de fluxo, não capacidade física.

**Relação com COMP+K.** Equivalente no inteiro. `LP(MP com todas as BF) = proj LP(COMP+K)` com `y_F = 0`, portanto ≥ `LP(COMP+K)`. Com BR, o projeto alega `LP_cov ≥ LP` (§5.9), **a re-auditar**. **Não se reivindica LP mais forte**; o ganho esperado é computacional. Microinstâncias de teste: SharedTerminal, Tri, par de gêmeos (fixar ambos é inválido), `a–p–q` com r=1 (R8), tudo em enumeração exaustiva n ≤ 5.

**Complexidade.** Mestre: n binárias + |K| + cortes dinâmicos (pior caso exponencial). Separação: um max-flow na rede restrita. Reduções: O(Σ_u |N_H(u)|·|N_H[u]|). Parâmetros que encarecem: `m` alto (W3C571), `supp(y*)` grande, platô de Γ (R7: um corte elimina no máximo 27/200 do pool). PUC r=1: sem reduções; teto esperado = envelope. A definição não limita o tamanho do grafo.

## 9. Plano incremental (identificadores sugeridos; sem specs)

| ID | Objetivo | Entregáveis | Aceite | STOP | Esforço |
|---|---|---|---|---|---|
| AS29 | Higienizar LB\*/OPT | tabela do envelope (núcleo, COMP, CC9 = 31; corrigir E9 pré-C4-DM: hc11p, den312d-m50) com proveniência | divergências registradas | — | 0,5 d (baixa incerteza) |
| AS30 (G1) | Viabilidade matemática | prova de D (lote, terminais, `S∩T`), BF/BR, re-auditoria do §5.9; micro exaustivo | 0 divergências, 0 ótimos perdidos | algum ótimo perdido | 2–4 d (média) |
| AS31 (G2a) | Reduções em COMP+K | contagem nas 75 principais + MIP pareado no desenvolvimento, 3 sementes, comparado ao pré-processamento histórico | §10 | §10 | 2 d (baixa) |
| AS32 (G2b) | Potencial de Y-RBC | protótipo com separação completa e primal; WorkLimit = linha de base | §10 | §10 | 4–7 d (alta) |
| AS33 (G3) | Piloto | callbacks compilados, logs completos, censuras preservadas | — | — | 1–2 sem (alta) |
| AS34 (G4) | Comparação | contra COMP, COMP+K, núcleo, CBI; 600 s, 3 sementes | — | — | 1 sem |
| AS35 (G5) | Avaliação congelada | partição `avaliacao`, nunca usada antes | — | — | 1 sem |

## 10. Experimentos e gates

**Matriz (desenvolvimento).** CC9, BIP42, CC3 (cobertura dura, sem redução); Room, random-32 m25 (MAPF, reduz); Vienna I056 (grande, reduz); W3C571 (m alto, censura esperada). Indicadores: dual bound final, UB validado, tempo até OPT, nós, tempo de raiz, RSS, cortes e tempo de callback.

- **G2a GO:** em ≥ 2 grafos brutos, ganho ≥ 1 estação em LB/UB, ou tempo até OPT ≤ 0,5×, ou raiz ≤ 0,5× sem perda de bound; nenhuma regressão > 1 estação.
- **G2a STOP:** fixação < 10% em todo o desenvolvimento fora de PUC, ou nenhum efeito MIP.
- **G2b GO:** bound ≥ max(núcleo, COMP+K MIP) em ≥ 4/6 e estritamente maior em ≥ 2 grafos brutos, mesmo WorkLimit; callback < 50% do tempo.
- **G2b STOP:** abaixo do envelope em ≥ 3/6, ou o CBI empata em tudo.

**Regras.** Censura é censura, nunca zero. Política congelada antes de rodar; exploração registrada à parte. Instâncias reservadas só no G5.

## 11. Contribuição acadêmica possível

1. Caracterização do patamar LP: todas as reformulações e famílias locais avaliadas projetam até COMP+K; o gap real é inteiro.
2. Reduções seguras para o MIN-STATION com terminais e `S∩T`, por dominância fechada em `G^r` (regras análogas existem para dominating set e Steiner; a aplicação com esta semântica é do projeto).
3. Algoritmo exato: branch-and-Benders-cut combinatório (tipo Codato–Fischetti) com projeção de fluxo e oráculo de matching (IJCAI). Novidade possível: método e evidência, não a técnica.
4. Benchmark com envelope reproduzível.

Bibliografia **a conferir** antes de qualquer reivindicação de originalidade: Codato & Fischetti (2006); Fischetti, Ljubić & Sinnl (2017); Rehfeldt & Koch (SCIP-Jack).

## 12. Conclusão científica

O próximo avanço deve sair do espaço inteiro de instalação, não de mais desigualdades fracionárias. Depois de H2 (nenhum corte emitido), HL (cubo), FC-R (≤ 0,6%), C3 (≤ 0,93%), das reformulações que projetam em COMP+K e da sonda DW que limita a interseção núcleo × COMP, o que separa LP de OPT é integralidade conjunta, hoje dividida entre dois métodos. Y-RBC é o candidato mais barato e verificável para uni-los e remover o gargalo de tamanho, já indicado em Vienna e Room.

Se G2a/G2b falharem, a evidência mínima faltante é o OPT verdadeiro de BIP42 e CC3 (gaps 35–43 e 18–26): campanha longa com Cutoff e heurística primal forte.

## Limitações deste parecer

- Sondas [EXP] pontuais, uma seed, carga concorrente, sem réplica.
- O relatório de um agente de reconstrução (fases E/R/N) chegou depois do primeiro rascunho; seus pontos estão incorporados (pré-processamento histórico, B1, `VALIDATION_FAIL` da cumulativa, N2, E9).
- Provas (Teorema D, BF/BR, §5.9) são esboços sem revisão independente.
- Divergências documentais encontradas (cabeçalhos "não executado" de AS05/AS06/AS25/AS25.1, rótulo `PROMISING` do AS05 com 0/6 ganhos, LB\* de CC9, E9 pré-correção) não foram corrigidas aqui.
