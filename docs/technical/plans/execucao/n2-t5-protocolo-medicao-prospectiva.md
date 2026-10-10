# MIN-STATION — N2-T5: protocolo operacional de medição prospectiva

**Estado:** `IMPLEMENTADA — MEDIÇÃO COM GUROBI PENDENTE`  
**Ramo exigido:** `novos_testes`  
**Pré-registro:** `experiments/alternative-formulations/n2-t1-freeze.json` (`FROZEN`)  
**Gate anterior:** `docs/technical/plans/execucao/n2-t4-gate-aceite-regressao.md` (`ACEITA_COM_EXCECAO_FORMAL`)

> Este documento acompanha o executor; **não** cria um novo pré-registro, não altera
> metas ou escolhas da N2-T1 e **não** emite `N2 PASS/FAIL`. O gate científico é N2-T6.

## 1. Objetivo e corpus imutável

Determinar se o limite inferior certificado de F-CC+K (CG na raiz) gera melhoria
útil sobre a referência B0, em duas famílias e dois níveis, levando em conta
**todo o esforço computacional**. A seleção foi congelada **antes** das medições N2.

| Ordem | Instância | Família | Nível | n | m | B0 histórico | LP completo histórico |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | `HB-q4-ndir2-p1` | HB | 1 | 16 | 6 | 1 | 2 |
| 2 | `BP-nao-[3,1]-q2` | BP | 1 | 16 | 4 | 6 | 7 |
| 3 | `HB-q6-ndir2-p1` | HB | 2 | 26 | 10 | `NOT MEASURED` | `NOT MEASURED` |
| 4 | `BP-nao-[2,2,2]-q2` | BP | 2 | 23 | 6 | `NOT MEASURED` | `NOT MEASURED` |

No nível 1, B0 é a **referência histórica N1-T5** e não consome novo Work.
Seus componentes `lp_comp`/`core_ip` são confrontados novamente com o freeze.
No nível 2, B0 é medido **dentro do orçamento compartilhado** resolvendo:

1. LP da formulação COMP (modelo `baseline.construir_modelo_baseline` relaxado,
   adicionando exatamente K=C1/C2/C4-DM válido);
2. IP em espaço `y` (`yspace._build_ymodel`, integridade binária) com os mesmos K;
3. `B0 = max(z_COMP^LP, z_core^IP)` **somente quando ambos os solves forem OPTIMAL**.

Se algum componente não estiver disponível, **B0 fica vazio**, nunca `0`.
Esses objetivos são **referências numéricas**; não constituem, por si, prova
racional física da E5. A distinção aparece em `b0_reference_status` e
`b0_certificate_status`. Isso é deliberado: não certificamos B0 grande usando
uma busca exaustiva não executada nem usamos `ObjBoundC` como prova.

## 2. Configuração imutável

| Parâmetro | Valor |
|---|---|
| Representação | `B / F-CC+K`, raiz apenas |
| Orçamento de solver **por instância** | `WorkLimit_total = 164` |
| Guarda de parede **por instância** | `1800 s` |
| `Threads` | `4` |
| `Seed` | `42` |
| `PYTHONHASHSEED` | `0` |
| Tolerância científica | `1e-6` |
| Ganho mínimo em casos conhecidos | `>= 50%` do incremento positivo `LP_FCC+K − B0` |
| Branching | **Proibido** |

O número de iterações técnicas no executor é limitado a `300`, com o mesmo
controlador N2-T2B; **não redefine** o orçamento científico. A auditoria N2
usa N1 analítico e N2 racional (multiplicadores zero na E4), e não faz ENUM
para `n >= 16`, evitando enumeração exponencial. A E5 verifica K/instância,
recalcula o Teorema L e publica limites físicos somente após reauditoria.

**Alerta de força do bound:** multiplicadores zero para N2-box podem produzir
limites fracos. Essa implementação não efetua um solve auxiliar para melhorá-los;
qualquer mudança posterior exige o diagnóstico e o rito previstos na N2-T1.

## 3. Integridade antes dos experimentos

O `check` **não soluciona nenhum modelo e não cria saída**. Ele valida:

- freeze N2-T1 (parâmetros, composição, hashes de fontes);
- gate N1-T7 e `run_n2_t1.py check`;
- manifesto e CSV **reais** da N2-T4 (hash byte a byte, 22 replays CG, exceção
  `Direct0` aprovada, `SC-GF2-k3` excluída);
- documentação do aceite humano, mantendo intacto o status
  `SCOPE_EXCEPTION_REVIEW_BLOCK_N2_T5` original do manifesto.

Na conferência da cópia enviada em 2026-10-10, foram encontrados:

- SHA-256 do freeze N2-T1: `b036e9d0fe8f446dfcaca2716df85054c73dbb8702484aacce3c807e6574de71`;
- SHA-256 do CSV corrigido N2-T4: `62032d439ce86b62673b50e1cb3936e56fcea8cfef59c5a2376baf4b077c4153`;
- gate N2-T4 aceito com exceção formal.

Se esses artefatos mudarem, o programa deve recusar a medição.

## 4. Comandos

Descompacte o pacote N2-T5 na raiz `min-station/` (não substitui E1–E5).

```bash
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/alternative-formulations \
  -p 'test_n2_t5_prospective.py' -v

python -m ruff check \
  experiments/alternative-formulations/run_n2_t5.py \
  experiments/alternative-formulations/test_n2_t5_prospective.py

PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t5.py check

PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t5.py run
```

Para preservar tentativas anteriores, informe diretório novo:

```bash
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t5.py run \
  --output-dir results/alternative-formulations/n2-t5-execucao-02
```

**Nunca sobrescrever** um diretório com resultados existentes. O runner escreve
os arquivos somente após completar o loop das quatro instâncias (uma falha
por instância é registrada como `ABSTAINED_INCOMPLETE`, sem inventar B0/LB).
`run` termina com código `2` se nem todas obtiverem novo LB físico certificado;
isso **não é** um veredito automático `N2 FAIL`.

## 5. Entregáveis gerados

Os arquivos criados no diretório de saída:

| Arquivo | Conteúdo |
|---|---|
| `n2-t5-medicoes.csv` | 4 linhas, referência B0, LB LP, LB físico, arredondamento, U/G2, esforço, memória, justificativa |
| `n2-t5-lb-versus-work.csv` | Evolução do melhor LB **reauditado** e do Work acumulado por iteração |
| `n2-t5-lb-versus-work.svg` | Visualização estática por instância; não transforma diagnóstico numérico em certificado |
| `n2-t5-custos.md` | Protocolo, medições, composição Work e limitações |
| `n2-t5-manifest.json` | Hash SHA-256 dos quatro arquivos, congelamento e proveniência da N2-T4 |

Todos são **novos**; nenhum resultado de N1/N2-T4 ou freeze é alterado.

## 6. Contabilidade de custos — sem dupla contagem

`work_total = work_comp_lp + work_core_ip + work_master + work_pricing`.

- `COMP LP` e `core IP` consomem Work apenas no nível 2.
- `work_master` soma todos os solves do RMP, incluindo resolução final sem pricing.
- `work_pricing` soma *todas* as chamadas numéricas P0–P5.
- A CG recebe **exatamente o saldo** de Work e wall após a baseline.
- A E5 usa Python e não faz novos solves Gurobi. A geração de K e a
  verificação de alcance são contabilizadas em wall, não convertidas falsamente
  em Work do solver.
- `wall_cg_s` inclui master, pricing, construção e certificação E4/E5; os
  campos de runtime master/pricing e validação E5 são **subcomponentes informativos**,
  não somados duas vezes ao wall total.
- `wall_other_s` reconcilia o período sem solver entre fases; verificação
  automática impõe soma exata das fases exclusivas dentro da precisão numérica.
- `peak_rss_mb` usa `ru_maxrss` no Linux: pico do processo como um todo, não
  memória isolada do solve, sujeito ao carregamento de bibliotecas anteriores.
- Gap numérico do pricing usa diferença `|incumbente_rc − ObjBoundC|`, apenas
  como diagnóstico, **não** prova global exata de custo reduzido.

Se Work for ausente, negativo, NaN, ou se o Work/tempo global ultrapassar o
teto, o runner **não publica novo LB desse solve**; mantém o registro do
consumo parcial conhecido para análise, com justificativa explícita.

## 7. Critérios de aceite e limitações

A N2-T5 implementa a medição da Story 5 (`COMPAT-BOUND-25/26/27`).
A aprovação experimental depende da execução **com Gurobi do pesquisador**,
das quatro linhas preenchidas e da conferência do orçamento e curvas.

- `CERTIFIED` LP, `CERTIFIED` físico, `CONVERGED_CERTIFIED` (G2) e B0
  são campos **diferentes**; nenhum pode substituir outro.
- Uma execução `NUMERICAL_STATIONARY` não recebe selo G2.
- Uma referência B0 numérica (inclusive OPTIMAL do Gurobi) não é
  automaticamente uma prova de B0 racional independente.
- Ausência de B0 ou ausência de certificado não deve ser convertida em ganho
  de zero nem em recuperação de 50%.
- Os casos do nível 2 são **desenvolvimento estrutural**, jamais instâncias
  da partição benchmark-v1.
- Os resultados da N2-T5 alimentam a **N2-T6**. A regra de PASS/FAIL (dois
  tipos e níveis, ganho e recuperação >=50%, certificação e custo viável)
  continua aquela da N2-T1, sem alteração retrospectiva.

**Não abrangido:** resultados das quatro otimizações, parecer independente do
novo runner, certificação exata da baseline numérica de nível 2, N2 PASS/FAIL,
N3, branch-and-price ou revisão do freeze.
