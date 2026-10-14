# AS13 — Testemunhas, controles e gate de fundamentação H2/HL

**Data da auditoria:** 13/10/2026.  
**Branch de referência:** `novos_testes`, commit `ed1a04740e59f2c8ae4f13e9a62b69624032fa62`.  
**Gate científico após revisão independente R3 (Opus): `PASS` — **GO PARA AS14**. Os critérios AS13-01 a AS13-07 foram aprovados. Este fechamento atualiza o status das rodadas anteriores sem apagar R1/R2; o registro primário da R3 permanece em `specs/as-13-fundamentacao-h2-hl/validation.md`. **Quatro mutantes residuais não bloqueiam a AS14, mas devem ser tratados antes da AS15.**

## 1. Resultados reproduzidos

| Construção | `n` | `m` | `r` | K materializado | `zLP(COMP+K)` | `+H2` | `+HL` | `OPT` físico |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| HB `q4-ndir2-p1-k1` | 16 | 6 | 1 | 4 | 1 | 2 | Não aplicado | 2 |
| Quatro relés / `K4` | 16 | 6 | 1 | 6 | 2 | 8/3 | 3 | 3 |

**Método de cálculo LP:** resolver por `scipy.optimize.linprog(method="highs")` as equações geradas pelo compilador `compile_u(..., relax=True)` do repositório, incluindo K extraído de `generate_C1`, `generate_C2` e `generate_C4_DM`. H2/HL foram incluídos apenas como restrições **locais ao script de validação**, sem modificar o modelo salvo. **Não é uma execução Gurobi**. Tolerância utilizada para asserção `1e-8` (salvo comparações com `8/3`, também `1e-8`).

**Ótimos físicos:** a versão corrigida do script **calcula** `ip_phys_opt` pelo oráculo físico, em vez de inserir os literais 2 e 3 no JSON. HB com zero e uma estação inviável, duas `x0_0,x0_1` viáveis. No `K4`, a necessidade de três relés tem prova estrutural: com dois ausentes alguma origem `s_ij` não alcança destino; com três presentes existe pareamento direto `s_ij→t_ij` por relé instalado. O script conferiu exaustivamente as `2^16=65.536` instalações do K4 usando o verificador por estado de bateria. Há agora testes **adversariais** que alteram uma classificação física de um único subconjunto e exigem que o laço exaustivo detecte a divergência; contar até 65.536 não basta.

**Natureza da evidência:** resultados computacionais numéricos e provas analíticas em instâncias explícitas. Não representam ganho MIP em benchmark nem prova de originalidade bibliográfica. A relaxação LP foi resolvida numericamente, não por certificado racional independente.

## 2. Testemunhas e falsificações

| Afirmação / controle | Evidência |
|---|---|
| HB: instalação `{x0_0}` satisfaz K inteiro, mas é fisicamente inviável | K canônico com quatro suportes em JSON; matching independente rejeita a instalação |
| HB: H2 com `R=V` exige pelo menos duas estações | Todas as 16 instalações singulares rejeitadas; `{x0_0,x0_1}` viável |
| K4: `y_w=2/3` satisfaz **todos os H2 de todos os suportes**, não somente os quatro trios | Varredura de 65.536 suportes; 45.056 com H2 aplicável; 16.384 suportes têm H2 justo no ponto |
| K4: `|C∩W|≥3` é condição exata de viabilidade | 65.536/65.536 conjuntos de estações classificados conforme o verificador físico por bateria |
| Concordância entre os dois oráculos de viabilidade | 674 comparações HB/K4 e 64 comparações em quatro microcontroles; nenhuma divergência |
| H2 exato, H2 parcial e HL não eliminam instalações físicas em controles pequenos | 32 suportes H2 não triviais e 32 suportes HL não triviais, com verificação sobre todas as instalações físicas dos respectivos controles |
| Deficiência de Hall não é número de estações | Dois robôs podem compartilhar uma estação em relé central |
| Ganho de matching não é submodular | Caminho `s-a-b-t`, com `r=1` e necessidade simultânea de `{a,b}` |
| Permanência, `S∩T`, uso de terminais | Testes diretos de estados de bateria, incluindo origem=destino |

## 3. Proveniência e comandos de reprodução

**Entradas:** `experiments/structural/hb.py` (gerador HB), construção determinística K4 dentro de `verify_as13_foundations.py`, `experiments/cuts/cuts.py` (K), `experiments/alternative-formulations/as02_model_a.py` (COMP), `experiments/cuts/independent_validator.py` (viabilidade física).

Identidade dos blobs de código consultados na branch de referência:

| Fonte | Git blob SHA |
|---|---|
| `experiments/cuts/cuts.py` | `d305457f3b60a7f263106e624e3a0b821d99f935` |
| `experiments/cuts/independent_validator.py` | `73c99798b2afcfbdfa57b53d1d368446f573c0bc` |
| `experiments/structural/hb.py` | `855d93c6b1b306cc27c51cbd90702a58a8132f95` |
| `experiments/alternative-formulations/as02_model_a.py` | `b1d9b5a6387e89966665c40026156068bc6c3dbb` |

Hashes de grafos na representação canônica do script: HB `7f18b7d6f531a33618597dc59968a6e263a5b02f42650c5ac7c9c27da2397ef9`; K4 `36838a00cb39d9ababc24e495c7ba70aaaa00df97eca4088b6e01f1a0201f49a`.

Executar na **raiz do repo**, com dependências do projeto instaladas:

```bash
poetry run python -m unittest discover -s experiments/cuts -p 'test_as13_foundations.py' -v
poetry run python experiments/cuts/verify_as13_foundations.py --output /tmp/as13-math-evidence.json
```

A opção `--output` cria arquivo novo e **falha se já existir** (`open('x')`), preservando a evidência preexistente; use outro nome ao repetir. Também é permitido rodar o script sem `--output`, exibindo JSON na saída padrão.

Artefatos desta entrega:

- `docs/technical/reference/formulacoes/as13-cortes-h2-hl-fundamentos.md`;
- `docs/technical/reference/formulacoes/as13-prova-h2.md`;
- `docs/technical/reference/formulacoes/as13-prova-hl.md`;
- `docs/technical/reference/experimentos/as13-testemunhas-e-gate.md`;
- `docs/technical/reference/experimentos/as13-math-evidence.json`;
- `experiments/cuts/verify_as13_foundations.py`;
- `experiments/cuts/test_as13_foundations.py`;
- `experiments/cuts/verify_as13_discrimination.py`;
- `specs/as-13-fundamentacao-h2-hl/validation.md` (parecer independente R3: **PASS**; preservar R1, R2 e relatório do autor).

## 4. Relação com histórico e limites da contribuição

**K:** distinguir três níveis: o LP com as linhas K **efetivamente materializadas**, o fecho inteiro desse núcleo e a projeção do MIP completo COMP+K. No HB, H2 elimina o ponto **inteiro** `{x0_0}` admitido por K, logo H2 não decorre de nenhum corte CG válido apenas para o fecho inteiro de K; isso não afirma viabilidade em COMP+K. No K4, o LP+H2 e LP+HL melhoram o LP inicial, mas o fecho inteiro de K já exige três relés. A contribuição científica potencial está nos suportes físicos não gerados em K e no custo de separação, não numa propriedade supostamente inédita dos coeficientes.

**C6:** os cortes antigos de Hall de primeiro salto não são o mesmo objeto que testar matching global sob `V\R`; porém alguns suportes poderão coincidir, exigindo controle de duplicação.

**CBI/C5:** não reabrir geração repetitiva de cortes de inviabilidade como se H2 fosse apenas uma nova nomenclatura. AS15 precisa demonstrar diferença e custo competitivo.

**CG/zero-half sobre K:** no **K4**, as três coberturas de cada trio de relés dão `2y(trio)≥3`; arredondar produz **exatamente** H2-card `y(trio)≥2`. Somar os quatro H2-card dá `3y(W)≥8`; outro arredondamento recupera HL `y(W)≥3`. Logo a testemunha K4 **não** constitui ganho além do fecho inteiro de K nem prova novidade contra CG. No **HB**, `{x0_0}` satisfaz K inteiro e viola H2, impedindo derivar o H2 global exclusivamente de cortes válidos ao fecho inteiro de K. Não chamar H2 de zero-half novo nem afirmar posto CG universal.

**Limites globais (`L_bot`, E9):** a desigualdade global `y(V)≥2` da construção HB não demonstra melhoria geral sobre limites inferiores já estudados. A contribuição útil em AS15/AS16 deverá ser cortes **não triviais e não redundantes na raiz** em instâncias de desenvolvimento.

**Literatura:** há antecedentes de cortes de cobertura com coeficientes 0/1/2 e de *local cuts*. Uma alegação de novidade requer revisão bibliográfica especializada. Esta entrega não faz tal alegação.

## 5. Estado por critério após revisão independente R3

**Parecer informado pelo revisor independente (Opus), R3: `AS13 PASS`.** AS13-01 a AS13-07 foram aprovados. As rodadas R1/R2 permanecem integralmente documentadas em `specs/as-13-fundamentacao-h2-hl/validation.md` e não são reescritas neste fechamento.

| Requisito | Parecer independente R3 | Evidência/escopo |
|---|---|---|
| AS13-01 | PASS | Caracterização da viabilidade física anônima e seus controles |
| AS13-02 | PASS | Validade da desigualdade H2 |
| AS13-03 | PASS | Validade da classificação parcial de H2 |
| AS13-04 | PASS | Projeção HL e suficiência da separação com coeficientes não negativos |
| AS13-05 | PASS | Testemunhas HB/K4 e distinção entre LP e ótimo físico |
| AS13-06 | PASS | Tratamento explícito de falhas e revisão independente |
| AS13-07 | PASS | Relação com K, CG, cortes antigos e limites de originalidade |

**Discriminação na R3 (informada pelo Opus):** 27/27 testes aprovados; 19 mutantes próprios, dos quais 15 foram detectados e **4 sobreviveram**. Os quatro residuais **não reabrem o gate matemático da AS13 e não bloqueiam AS14** segundo o parecer, mas precisam ser corrigidos **antes de autorizar AS15**, com testes que injetem erros nas checagens de validade H2, H2-parcial e identidade de projeção. Não interpretar 15/19 como ausência de lacunas.

**Fechamento documental:** a prova H2 passou a indicar que falta **um** pareamento, e a afirmação sobre suficiência de `α ≥ 0` na separação HL recebeu demonstração explícita. A implementação continua sendo uma investigação de cortes para COMP+K; não há experimento que prove ganho MIP geral.

## 6. Correções de teste e verificação de instalação

- `verify_as13_foundations.py` calcula os ótimos inteiros físicos por consulta real ao oráculo; a enumeração integral de K4 deriva `OPT` das instalações viáveis observadas.
- `test_as13_foundations.py` contém testes que tornam detectáveis uma alteração única na classificação de viabilidade e a ausência da enumeração de K4; distingue instâncias com ótimo 0 e 2 para barrar ótimo literal.
- As verificações locais anteriores incluíram 27/27 testes, 9/9 mutantes em memória e 5/5 mutantes de fonte detectados. A revisão R3 do Opus ampliou a avaliação para 19 mutantes próprios: 15 mortos, 4 residuais. O resultado independente prevalece sobre o sensor próprio; remediar os sobreviventes antes da AS15.
- `verify_as13_delivery.py` falha se qualquer um dos três documentos de prova ou os scripts e relatório necessários estiverem ausentes ou truncados **no checkout real**.
- `validation.md` do Opus **não é incluído no patch**, de propósito; preservar o histórico R1/R2, o relatório do autor e a seção R3 `PASS` já adicionada pelo verificador.

## 7. Gate e regra de progressão

**Gate científico AS13: `PASS`; autorização AS14: `GO`.** A liberação decorre do parecer independente R3 do Opus, não exclusivamente dos testes locais. **AS15 permanece condicionada à correção dos quatro mutantes residuais e a um gate de discriminação correspondente**, além das dependências próprias das specs AS14/AS15. Não sobrescrever as seções R1/R2/R3 de `validation.md`; manter íntegra a rastreabilidade do parecer independente.

Não afirmar novidade poliédrica sem revisão especializada de literatura nem benefício sobre MIP em instâncias grandes.
