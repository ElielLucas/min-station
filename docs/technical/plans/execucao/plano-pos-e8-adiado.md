# Plano pós-E8 adiado

> **Documento histórico.** Agenda adiada depois do E8, retomada no
> benchmark-v1 e nos experimentos E9–E14. O programa de pesquisa corrente
> está em `docs/technical/plans/plano-proxima-fase.md`. Números e vereditos
> abaixo não foram reescritos.

Preservado para retomada depois do lote 1 do benchmark-v1 (`plano-benchmark-v1.md`).

Itens originais (de `resultados-e8-pli.md` §7–8):
1. ~~E8 com 3 seeds~~ — substituído pelo desenho estratificado abaixo (E12): 3 seeds só nas
   instâncias em que o veredito depender de poucas unidades de LB, não em toda a bateria.
2. CBI com mestre sem pool até o ótimo e enumeração só depois (não termina em hc10p/bip42p) —
   **pré-requisito de E12** abaixo.
3. Heurística primal partindo de C pequeno em vez de C = V — **E10** abaixo.
4. Decidir o recorte de escopo de A2 (proposta: fora de R-a) — **suspenso**, ver a ressalva em
   `direcoes-pli-min-station.md` §13 (resultado E8) e **E12** abaixo.
5. ~~Commit do trabalho E7–E8~~ — feito em 2026-09-26 (c9f5322, 702a1dc, a647555).

A revisão pré-E8 já foi executada; registro em
`plano-experimentos-e8.md`, seção "Revisão pré-execução".

## Repriorização (2026-09-26, após o lote 1 do benchmark-v1)

O benchmark-v1 (70 instâncias fiéis a Das, `benchmark-v1.md`) mostrou que a dificuldade acompanha
UB/m (estações por robô), não o tamanho do dígrafo de alcance nem a densidade de cortes estáticos:
instâncias fáceis compartilham estação entre ~4 robôs (UB/m mediano 0,16–0,25); as 30 difíceis
(classes D/A) se aproximam de uma estação por robô (UB/m mediano 0,67–0,85). Isso também mostrou
que o regime R-c, onde o CBI venceu o compacto em `cc12-2p` (E8), não produz nenhuma instância
difícil quando fiel a Das — o resultado de `cc12-2p` não se generaliza. Os itens acima são
retomados nesta ordem, condicionados uns aos outros:

- **E9 — diagnóstico de raiz nas 30 instâncias D/A** (novo, entra antes de tudo). Mede `z_LP` e o
  efeito de C1/C2/C4/C3/cotas R6/IP do núcleo, família a família — nenhuma delas (MAPF, `pucn`,
  `vienna`, `pace`) teve isso medido antes. Decide se o item 2 e o item 4 (E11/E12 abaixo) devem
  vir primeiro.
- **E10 — primal construtivo** (era item 3). Substitui o `reverse-delete` de `primal.py`, que
  parte de C=V e devolve C=V inteiro nas instâncias grandes. Custo de máquina baixo, independente
  do resultado de E9.
- **E11 — cortes de multiplicidade (C6)**, condicionado a E9 mostrar que C3/R6 não fecham o gap
  nas famílias sem compartilhamento (UB/m ≥ 1).
- **E12 — veredito de A2 sobre instâncias de Das** (era item 4). Requer o item 2 (mestre do CBI
  sem pool) como pré-requisito, e roda só onde E9 mostrar que o núcleo tem chance de igualar o LB
  do compacto. Critério pré-registrado: A2 segue se o CBI vencer em LB final ou tempo até o ótimo
  em ≥ 3 instâncias e ≥ 2 famílias; caso contrário, A2 é encerrada para Das.

Desenho experimental completo (instâncias, configurações, critérios de sucesso, o que cortar) no
plano de execução desta sessão.

## Situação após E9 e E10 (2026-09-26)

Resultados em `docs/technical/reference/resultados-e9-e10-pli.md`. Mudanças nesta lista:

- **E9 feito**, sem C3 e sem R6 além de L_bot (motivos no relatório). L_bot é dominado pela raiz
  com cortes em todas as instâncias: **R6 além de L_bot sai da agenda**.
- **E10 feito, inconclusivo quanto ao gap primal.** Os dois construtores falharam por escala e
  por um desempate ruim no H3, não por falta de gap primal. O critério pré-registrado ("se H3
  perder, o gargalo é dual") tinha uma inferência inválida e **não** se aplica.
- **E10b feito, também inconclusivo.** O reparo da solução do núcleo venceu o UB do COMP em 1/30
  (0/13 em MAPF/Vienna) e não ficou viável no prazo em 9/30. Nenhum dos dois desfechos
  pré-registrados ocorreu — ambos os ramos valiam sobre MAPF/Vienna, e a única vitória
  (`w23c23-seed`) está fora desse conjunto. Na fase `comp` dessa instância o start baixou o UB de
  158 para 156 e deixou o LB em 141, o que **não** decide primal × dual: um MIP start age sobre o
  incumbente, não sobre o dual. A pergunta passa para um instrumento baseado no solver
  (COMP com `MIPFocus=1`, TL maior) — proposta, não executada; ver o relatório §7.
- **E12 — filtro corrigido.** O núcleo é o LB da *primeira* iteração do CBI, não o teto: o CBI
  acrescenta cortes 𝒵 e o LB sobe. "Rodar só onde OPT(núcleo) ≥ LB do COMP" vira ordem de
  prioridade, não exclusão. Subconjunto prioritário: PUC/PUCN, onde o núcleo já supera o LB do
  COMP de 600 s em 6 instâncias.
- **E11 redefinido:** C4 na versão mochila (provada em `direcoes-pli-min-station.md` §5.4) com
  δ ≥ 2; o C6 do §5.6 é só esboço e não entra. Condicionado a evidência de gap dual em MAPF/Vienna (instrumento do relatório §7, passo 1).
- **C3 exato** (oráculo fracionário restrito) sai da agenda até o E11 falhar.
- **`generate_C4_DM` corrigida (2026-09-26) — pré-requisito cumprido.** A função tinha dois
  defeitos: gerava cortes **inválidos** quando `S∩T ≠ ∅` (media a deficiência de Hall contra `T∖S`
  em vez de `T` inteiro, divergindo do §5.4 de `direcoes-pli-min-station.md`) e não era
  determinística entre processos. Ambos corrigidos, com regressão nova
  (`experiments/cuts/verify_c4_dm.py`) que comprovadamente reprova o código anterior. Reavaliação
  das 5 instâncias com `S∩T ≠ ∅` corrigiu 3 linhas do manifesto — inclusive um "ótimo provado" que
  estava errado (`b-b09-intercalado-f2-rho`: 4 → 2). Nenhuma classe de dificuldade mudou, então a
  seleção das 30 D/A e as análises do benchmark seguem válidas. Ver `correcao-c4-dm.md`.
  **O E12 está desbloqueado**: o gerador agora é determinístico, e seu critério decide por margens
  de 1 estação. As instâncias PUC/PUCN do subconjunto prioritário têm `S∩T = ∅`, logo não foram
  afetadas pelos cortes inválidos; os LBs do E9 nelas podem variar em ±1 numa reexecução.

## Situação após E12 (2026-10-02)

Resultado em `docs/technical/reference/resultados-e12-pli.md`. **A2 encerrada para Das.** Uma
vitória contra o COMP (`hc11p`) e nenhuma contra o núcleo. Onde o núcleo fecha, os cortes 𝒵 não
sobem o LB*. Os controles MAPF se comportaram como esperado: o CBI ficou no núcleo e abaixo do
COMP. O recorte "A2 só fora de R-a", suspenso até este veredito, não se sustenta no benchmark-v1.


