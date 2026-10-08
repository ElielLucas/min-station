# Plano: auditoria da rodada E5 e próxima rodada (E7)

## Contexto

A rodada E5 terminou: E2, E3, E4 e E6 rodaram, e o relatório
`docs/technical/reference/experimentos/resultados-e2-e4-pli.md` foi reescrito. Uma auditoria contra os CSVs,
os logs e o plano E5 encontrou três tipos de problema, que precisam ser resolvidos antes de
qualquer experimento novo:

1. **Conclusões erradas no relatório e em `direcoes-pli-min-station.md`.** A mais grave: o
   texto afirma que "OPT(hc9u) > 32 está provado". O que `verify_structure.py` testa é **uma**
   solução ótima do núcleo (a primeira que o Gurobi devolve). O núcleo pode ter muitas soluções
   ótimas de 32 estações — e cobertura de código de raio 1 costuma ter muitas. Ver uma delas
   inviável não prova que todas são. O status correto é **aberto: OPT(hc9u) ∈ [32, 38]**.
2. **Contaminação de resultados antigos pelo defeito do C2 assimétrico.** A correção
   (`dijkstra_to`) mudou números nas instâncias TNTP: Barcelona st25 E2-S1 12→11, Barcelona st50
   E2-S1 e E3 10→9, Philadelphia E2-S2 36,31→36,23. Os valores do E1 para Philadelphia
   (33,595 nas configs C/D e 35,3425 na E) foram medidos com o C2 defeituoso e não foram
   remedidos.
3. **Itens do plano E5 incompletos.** Alguns scripts de verificação existem só em `/tmp`,
   uma verificação não foi executada, os metadados de Q6 estão ausentes e o C.8 ficou sem
   decisão.

Depois disso vem o **E7**: comparar o branch-and-cut em y, completo, com o compacto em uma
instância de cada regime, para decidir se A2 vira a linha principal da pesquisa.

**Passo 0, ao aprovar:** copiar este plano para `docs/technical/plans/execucao/plano-experimentos-e7.md`.

---

## Bloco 1 — Correções de documentação (sem experimento)

Arquivos: `resultados-e2-e4-pli.md`, `direcoes-pli-min-station.md` (linhas 92 e 646) e a mensagem
de `verify_structure.py:265`.

| # | Erro | Correção |
|---|---|---|
| 1 | "OPT(hc9u) > 32 provado" (§1, §5.3, §7.3, §8.1, §8.2; direcoes:646) | "a solução ótima do núcleo **testada** é inviável; OPT(hc9u) ∈ [32, 38] continua aberto". Continua valendo: o núcleo não passa de 32, então ir além exige informação de fluxo (𝒵). Mensagem do script: "a solução testada é inviável", sem o "OPT > núcleo" |
| 2 | "hc*: 1 classe de assinatura", "bip42p: 995, logo não transitivo" | CSV: hc* têm 256 classes de tamanho 1 (**sem gêmeos**). bip42p tem 995 classes, a maior de tamanho 2, ou seja, **tem gêmeos em C1**. Assinatura mede gêmeos, não transitividade |
| 3 | E6 bip42p: "C2/C4 não são redundantes com C1, incluir estáticos" | CSV: `C2_subset_C1 = C4_subset_C1 = True` também em bip42p. Remover a recomendação. Hipótese honesta para bound 33 < 36: `LazyConstraints=1` restringe o presolve (**conferir na documentação do Gurobi 12**, não afirmar de memória), e a busca rodou sem incumbente |
| 4 | "hc11p é o único caso com contribuição do B&B" | hc10p também tem contribuição: 56 > ⌈51,2⌉ = 52. Só em hc12p ela é zero (171 = ⌈170,67⌉) |
| 5 | E4 Barcelona st15: "CORTES melhora o bound" | Piora: 14 contra 15 do BASE-C. E o "padrão de cortes piorando o UB" vem de **uma única seed**, então é observação, não padrão |
| 6 | hc9u UB e frase truncada em §6.3 | O E4-CORTES achou obj = 38 no **compacto**, o que torna esse UB verificado diretamente (antes era só inferido). Intervalo [32, 38] |
| 7 | §2.3 "4 gabaritos com S∩T, no smoke do E6" | Direct0 e TermRelay não têm S∩T. StayPut rodou em `/tmp/verify_e5*.py`, não no E6 |
| 8 | Tabela C: "corte C4/C2 de 42 elementos" | Era C2 |
| 9 | Encerramento de B2 (direcoes:92, relatório §1) | Fixar 1 variável na raiz é o esperado sob grupo transitivo e não mede nada; `Symmetry=2` é sonda binária. Redação: "sonda sem efeito; orbital branching não testado". B2 continua fechada, mas com a justificativa correta |
| 10 | §9 (histórico) omite Barcelona st50 LB 10 | Registrar que o LB 10 antigo vinha de um corte C2 inválido; valor correto 9 |

## Bloco 2 — Contaminação pelo C2 assimétrico

- **Remedir o E1 de Philadelphia st25**, configs B–E, com o C2 corrigido e `validate` ligado.
  Leva cerca de 20 s. Não dá para saber a resposta de antemão: o LP do compacto pode ser maior
  que o do espaço-y sem que haja corte inválido.
- Registrar em `resultados-e0-e1-pli.md` uma nota de correção com os valores antigos e novos. O
  limiar 35,34 da H3 passa a ser o valor remedido. Os planos históricos (`plano-e2-e4.md`,
  `plano-e0-e1.md`) não são editados: recebem só uma referência na nota.
- Chicago st5 (R=32, trivial) não precisa ser remedido.

## Bloco 3 — Pendências do plano E5

| Item | Estado | Ação |
|---|---|---|
| Verificações B.4, B.5.1 e C.6 (gabaritos, StayPut, validador × oráculo) | rodadas, mas só em `/tmp/verify_e5.py` e `/tmp/verify_e5_yspace.py` | mover para `experiments/cuts/verify_e5_gabaritos.py` e `verify_e5_validador.py`, reexecutar e salvar a saída em `results/cuts/e5_verificacao.txt` |
| B.5.2 regressão real por equivalência | resultado desconhecido; Philadelphia agora difere por causa do C2 | usar a config **B (só C1)**, que o C2 não afeta, para isolar U: Philadelphia 28,0444; hc9u, hc10p, cc10-2p e cc12-2p na config D (grafos simétricos, igualdade exata) |
| Verificação 5: Chicago **R=26** no laço espaço-y (zero cortes, LP=0 nos 4 estágios) | não executada; o E2 passou a rodar com R=7 | executar isoladamente (cerca de 15 s): é a regressão direta do sintoma original |
| Q6 (metadados em CSV) | ausentes: commit, versão do Gurobi, TL, formulação | colunas `gurobi`, `tl_s`, `formulacao=U` nos runners **novos** (E7). CSVs antigos não são reescritos; o cabeçalho do relatório registra o ambiente |
| Commit | **aprovado pelo usuário** | commitar tudo o que foi feito nas rodadas E0–E5 e ainda não subiu, **depois** dos Blocos 1–3: código, docs, CSVs e planos. Excluir `RKO_Cpp_v1.0/`, que já estava fora do git antes desta sessão e não foi criado por mim (confirmar com o usuário antes de incluir), e o `.pyc`. Sem push |
| C.8 (max-flow) | sem decisão | decidir com medição no E7c |
| K(n,1) bibliográfico | pendência sua | mantém |

Custo de validação observado: S1 de hc9u foi de 3,9 s para 38,9 s, e S1 de hc10p levou 350 s. O
`is_valid_cut` domina o tempo. Isso não bloqueia nada, mas fica registrado.

## Bloco 4 — E7: branch-and-cut em y contra o compacto, em vários regimes

**Por que não o teste de nível 32 em hc9u.** Fechar hc9u daria um número novo para uma única
instância, e esse número é quase uma questão de códigos de cobertura, não de método de PLI. O
objetivo da pesquisa é saber qual método escala. A pergunta que generaliza é outra: **o
branch-and-cut só em y (família 𝒵 do Teorema 6) supera o modelo compacto?**

Há motivo para achar que pode. O núcleo em y resolve cc12-2p (|A_r| = 2,8 M) em 0,1 s, enquanto o
compacto é intratável nessa instância. E o LP em y empata com o compacto (hc*, cc10-2p) ou o
supera (Philadelphia).

**Por que o E6 não responde isso.** O E6 testou um branch-and-cut incompleto:
- só um corte lazy por solução inteira;
- nenhuma separação fracionária nos nós;
- nenhuma solução inicial (bip42p terminou sem incumbente).

Resultado fraco com esse mecanismo diz pouco sobre o método.

**E7a — completar o BC-y** (`bc_yspace.py`, mudanças pequenas):
1. **MIP start** a partir de uma heurística barata. Candidata: gulosa sobre a rede agregada,
   adicionando o vértice que mais aumenta o max-flow até atingir m. A ser escrita, com cerca de
   30 linhas reusando `_build_flow_net_aggregate`.
2. **Lazy no MIPSOL**, como hoje.
3. **User cuts no MIPNODE** via `separate_classical_fracs` (já corrigida no C.2/C.3). Limitar a
   separação aos nós rasos para controlar o custo.
4. **Cronometragem do callback**. Se o callback consumir mais de 50% do tempo, executar o C.8
   passo A (networkx ou esqueleto em cache) antes da bateria.

Smoke nos gabaritos (Direct0, TermRelay, SharedTerminal, StayPut, Sec59) antes das instâncias.

**E7b — bateria comparativa**, com as mesmas instâncias, R e TL do E4 (300 s), uma por regime,
todas não triviais:

| Instância | R | Regime | Referência | Compacto no E4 (melhor) |
|---|---|---|---|---|
| Chicago st15 | 7 | R-a | 17 | 17 / 16 |
| Barcelona st15 | 5 | R-a | 15 | OPT 15 (BASE-C) |
| Philadelphia st5 | 2 | R-a | 41 | 41 / 37 |
| Philadelphia st25 | 3 | R-a | [42, 46] | 47 / 40 |
| hc9u | 1 | R-b | [32, 38] | 38 / 32 |
| bip42p | 200 | R-b' | — | (sem E4) |
| cc12-2p | 500 | R-c | [6, 7] | intratável |

Configurações: **COMP** (compacto + C1+C2+C4, a melhor do E4) contra **BC-Y** (E7a). Para
bip42p e cc12-2p, que não estão no E4, a COMP roda nesta bateria. São 14 execuções de 300 s,
3 jobs em paralelo, cerca de 25 min. Métricas: UB, LB, gap, tempo até o ótimo, nº de cortes lazy
e user cuts, fração de tempo no callback. Toda solução do BC-Y é conferida no compacto
(fixando `y`).

| Resultado | Leitura |
|---|---|
| BC-Y ≥ COMP em R-c e empata em R-a/R-b | método que escala: vira a linha principal (A2) e merece o próximo investimento (separação, heurística, testes em instâncias maiores) |
| BC-Y ganha só em R-c | método para o regime denso; o compacto continua sendo a escolha em R-a |
| BC-Y perde em todos os regimes, com o callback barato | o fluxo carrega informação que 𝒵 separado sob demanda não recupera a tempo. A2 sai de pauta e o foco volta para o compacto (cortes estáticos e pré-processamento) |
| BC-Y perde, com o callback caro | resultado inconclusivo: fazer o C.8 e repetir |

**Opcional, em paralelo.** Replicar o E4 com 3 seeds em Barcelona st15 e Philadelphia st5
(BASE-C × CORTES). Testa se "cortes pioram o UB" é padrão ou ruído de seed única.

---

## Ordem e verificação

1. Blocos 1 e 3 (documentação e scripts versionados). Verificar: `grep "OPT(hc9u) > 32"` em
   `docs/` não retorna nada fora do plano E5 histórico; `verify_e5_*.py` com 0 divergências e
   todos os gabaritos PASS.
2. Bloco 2. Verificar: o E1 remedido de Philadelphia tem 0 cortes inválidos; a config B bate
   28,0444.
3. Chicago R=26 no espaço-y: LP = 0 e 0 cortes nos 4 estágios.
4. Commit (aprovado) de todo o trabalho E0–E5.
5. E7a: smoke dos gabaritos PASS e callback cronometrado. Depois o E7b. Verificar: toda solução
   do BC-Y é viável no compacto; nenhum corte lazy inválido numa amostra passada pelo
   `is_valid_cut`.
6. Criar `resultados-e7-pli.md` e atualizar `direcoes` §1.6 com a decisão sobre A2.

## Não fazer

Teste de nível 32 em hc9u (específico de uma instância); hc10p–hc12p; orbital branching;
Benders clássico e Lagrangeana; `lin23`, `lin37`, `fnl4461fst`; alterar a formulação base; push.

## Arquivos

- Corrigir: `resultados-e2-e4-pli.md`, `direcoes-pli-min-station.md`, `resultados-e0-e1-pli.md`,
  `verify_structure.py` (só a mensagem)
- Novos: `verify_e5_gabaritos.py`, `verify_e5_validador.py` (vindos de `/tmp`), `run_e7.py`
- Estender: `bc_yspace.py` (MIP start guloso, user cuts no MIPNODE, tempo do callback)
- Reusar: `baseline.construir_modelo_baseline`, `cuts._build_flow_net_aggregate`, `_extract_Z`,
  `is_valid_cut`, `harness.load_instance`/`prepare_cuts`
