# Plano: commit do E13 e próximos passos

## Contexto

O E13 fechou com **veredito de gap primal** (7/13 com Δ_UB ≥ 5% sob `MIPFocus=1`, TL 1800 s — no
limiar). Pelo §7 de `resultados-e9-e10-pli.md`, isso deixa o E11 sem o gatilho que o condicionava.

A decomposição do gap, calculada agora a partir dos CSVs do E13, mostra que o veredito binário
esconde algo importante. Mesmo com o melhor UB encontrado, **o gap residual continua entre 10% e 44%**
e é maior que a queda primal em 11 das 12 instâncias não resolvidas (exemplos: `warehouse-m50`
81/117, 30,8% residual contra 7,1% de queda; `random-64` 41/63, 34,9% contra 7,4%). Sem OPT não dá
para dizer se esse residual está no LB ou no UB. O E13 provou que o UB não estava saturado. **Não
provou que o LB está bom.** Portanto "gap primal" não quer dizer "o lado dual está resolvido", e a
agenda não deve tratar assim.

Três pendências concretas saíram da leitura do código:

- `run_dificuldade.py` pula instâncias já presentes em `dificuldade_v1_fatiaK.csv`. Regerar exige
  tirar os CSVs antigos do caminho.
- `build_manifest.py` lê a dificuldade de `results/benchmark/dificuldade_v1*.csv` e **não** lê
  `reavaliacao_c4dm.csv`. Um rebuild hoje reverteria as 3 correções do C4-DM (b-b09 4→2 etc.) para os
  valores errados. A regeneração resolve isso de forma estrutural.
- O manifesto já tem as colunas `lb_melhor`/`ub_melhor`/`fonte_melhor`, alimentadas pelo dicionário
  `MELHORES` em `src/converters/build_manifest.py:91`. É o lugar certo para os melhores limites do E13,
  sem mexer na semântica de `lb`/`ub`, que valem só para o protocolo.

## Passo 0 — Commit do E13 (imediato)

Arquivos: `experiments/cuts/harness.py` (parâmetro `params` em `measure_mip`),
`experiments/benchmark/run_e13.py`, `experiments/benchmark/tabela_e13.py`,
`results/benchmark/e13_{base,longo}_fatia{1,2}.csv`, `docs/technical/reference/resultados-e13-pli.md`,
`docs/technical/reference/resultados-e9-e10-pli.md`.

Mensagem: `feat(e13): primal × dual via MIPFocus=1 em MAPF/Vienna — veredito gap primal (7/13, limiar)`,
com corpo curto (critério, inversão em relação à fase base, divergência de 9/13 com o manifesto) e a
linha `Co-Authored-By` vigente.

## Passo 1 — Adendo ao relatório do E13: gap residual

- Acrescentar a `tabela_e13.py` uma função `residual(base, longo)` que imprime, por instância,
  LB_melhor = max(LB dos três braços), UB_melhor = min(UB dos três braços), a queda primal e o gap
  residual `(UB_melhor − LB_melhor)/UB_melhor`, com as contagens "residual > queda primal".
- Colar a saída como §3.1 de `resultados-e13-pli.md`, com a leitura do Contexto acima: o veredito
  prioriza, mas não atribui o residual. Commit separado.

## Passo 2 — Frente B: regerar o benchmark-v1 (~6 h de máquina, 2 fatias)

1. `git mv results/benchmark/dificuldade_v1_fatia{1,2}.csv results/benchmark/historico/dificuldade_v1_pre_c4fix_fatia{1,2}.csv`.
   Isso preserva o "antes" e tira os arquivos do glob de `build_manifest.py`.
2. Rodar `run_dificuldade.py --fatia k/2`, sem alterar o script. Condições do original: TL 600 s,
   seed 42, 4 threads.
3. Adicionar a `MELHORES` as 13 do E13 que melhoraram LB ou UB em relação ao novo protocolo, com
   fonte "E13, COMP C1+C2+C4, MIPFocus=1, TL 1800 s — resultados-e13-pli.md".
4. Reconstruir o manifesto com `build_manifest.py` **completo** (sem `--sem-atributos`: esse caminho
   só copia `CAMPOS_RES` do manifesto antigo e pode deixar os atributos vazios).
5. Script de comparação (no molde de `reavaliar_c4dm.py`), gravando
   `results/benchmark/regeneracao_c4fix.csv` com antes/depois de `lb`, `ub` e `dificuldade`, mais a
   lista de instâncias que entraram ou saíram de D/A.
6. `benchmark-v1.md`: nova seção com a mudança de partição D/A e a ressalva de que E9/E10/E10b/E13
   usaram a partição anterior (não são refeitos).

## Passo 3 — E14: certificar OPT nas D/A de gap pequeno (atribui o residual)

Instrumento sem heurística e sem instância nova: em quatro instâncias com UB_melhor − LB_melhor = 2
estações (`room-32-32-4-m10-f8` 16/18, `room-32-32-4-m25-f4-rho` 17/19, `vienna-I056-regiao-f4`
9/11, `vienna-I065-intercalado-f2` 17/19), rodar o COMP com `Cutoff = UB_melhor − 0,5` e ênfase no
bound, TL 4 h, 2 fatias. Confirmar na documentação do Gurobi 12.0.3 a semântica de `Cutoff`, o status
retornado quando nenhuma solução melhor existe e o valor de `MIPFocus` para bound. Não preencher de
memória.

Critério pré-registrado, por instância:
- provado que não existe solução < UB_melhor → **OPT = UB_melhor**, e o residual era todo LB (dual);
- achou solução < UB_melhor → o UB ainda não estava saturado nem em 1800 s (primal);
- TL sem nenhum dos dois → inconclusivo; registrar o LB final.

Regra para o E11: se ≥ 3 das 4 certificarem OPT = UB_melhor, o E11 volta à fila com essa
justificativa. Ressalva a registrar: são as instâncias de gap *menor*, e o resultado não se estende
automaticamente às de 30–44% de residual.

Mudança de código mínima: `run_e14.py` usando `measure_mip(..., params={'Cutoff': ..., 'MIPFocus': ...})`,
que já existe em `harness.py:213`. UB_melhor e LB_melhor são lidos dos CSVs do E13.

## Passo 4 — Frente D: E12, CBI × COMP em PUC/PUCN

Sem mudança em relação ao plano anterior. A correção de código pode ser feita enquanto a Frente B
roda (verificação leve, 1 thread); a bateria roda depois da B.
- Em `bc_yspace.solve_cbi` (`experiments/cuts/bc_yspace.py:~271`), o `PoolSearchMode=2` fica ligado
  antes do único `optimize()` do mestre. A correção mínima resolve o mestre sem pool até o ótimo, testa
  a incumbente no oráculo e acrescenta o corte 𝒵 se ela for inviável. Não mexer na reconstrução do
  mestre por iteração.
- Verificação: `verify_e8_cc12_opt.py` mantém OPT(cc12-2p)=6; mais de uma iteração e cortes 𝒵 gerados
  em hc10p e bip42p.
- Critério pré-registrado de `plano-pos-e8-adiado.md`: A2 segue se o CBI vencer em LB final ou em
  tempo até o ótimo em ≥ 3 instâncias de avaliação, nas duas famílias.

## Fora desta rodada

- **E11 (C4 mochila δ≥2):** depende do E14. A ordem obrigatória (derivação escrita, depois validador
  próprio para RHS δ≥2, depois medição) continua valendo.
- **Frente primal dedicada:** não abrir. O E10b mostrou que um start melhor não move o LB, e o foco do
  projeto são os limites. Registrar os melhores UBs em `ub_melhor` (passo 2.3) basta.
- **Frente E (instâncias sintéticas):** segue planejada. É o único instrumento para atribuir o residual
  nas instâncias de gap grande, e fica para quando for pedida.

## Ordem e CPU

0 → 1 (sem CPU) → 2 (8 threads, ~6 h; a correção do passo 4 é feita em paralelo) → 3 (~8 h) → 4
(bateria). Nunca 3 fatias. O E14 não roda junto com a Frente B.

## Verificação

- Passo 0: `git status` limpo depois do commit, sem arquivos fora da lista.
- Passo 1: a tabela residual vem de `tabela_e13.py`, e nenhum número é digitado à mão.
- Passo 2: `verify_regeneracao.py` sai com código 0. O diff do manifesto toca **só** `dificuldade`,
  `lb`, `ub`, `fonte_lb_ub`, `lb_melhor`, `ub_melhor` e `fonte_melhor`. Qualquer outra coluna
  alterada aborta a aplicação. As 3 correções do C4-DM (b-b09, den312d-m50, room-m25) aparecem com os
  valores corrigidos, agora vindos do CSV regerado.
- Passo 3: nenhuma instância é declarada "OPT certificado" sem o status que a documentação do Gurobi
  define para "nenhuma solução melhor que o Cutoff".
- Passo 4: `verify_e8_cc12_opt.py`, `verify_c4_dm.py` e `verify_e8_oracle.py` saem com código 0.
