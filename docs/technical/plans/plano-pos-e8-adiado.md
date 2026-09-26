# Plano pós-E8 adiado

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
plano de execução desta sessão. Nenhuma dessas quatro baterias foi executada ainda — ficam para
aprovação em separado.


