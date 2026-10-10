# MIN-STATION — N2-T6: Gate científico de limites inferiores certificados

**Decisão científica segundo critérios pré-registrados:** **`N2 FAIL`**  
**Situação documental:** **`FECHADO — N2 FAIL — AUDITORIA LOCAL CONCLUÍDA E INFORMADA PELO PESQUISADOR`**  
**Data:** 2026-10-10 (`America/Sao_Paulo`)  
**Escopo:** seleção **B / F-CC+K root-only**, com corte K pré-existente, para quatro instâncias congeladas na N2-T1.  
**Autoridade:** aplicação reprodutível dos critérios do freeze N2-T1 aos valores apresentados; este documento **não representa assinatura digital, decisão de banca, revisão independente adicional ou reexecução do solver**.

## 1. Base normativa e cadeia de gates

A decisão usa, sem alteração posterior:

1. `specs/proxima-fase-n2-limite-compatibilidade-certificado/spec.md`, Story 6 / **N2-T6**;
2. `docs/technical/plans/execucao/n2-t1-pre-registro.md`;
3. `experiments/alternative-formulations/n2-t1-freeze.json`, SHA-256 `b036e9d0fe8f446dfcaca2716df85054c73dbb8702484aacce3c807e6574de71`;
4. Gate N2-T3: aceite técnico da certificação racional N1, ENUM e N2, validade de K, primal e G2;
5. Gate N2-T4: `ACEITA_COM_EXCECAO_FORMAL` (22 regressões CG + prova independente `Direct0`; exclusão `SC-GF2-k3`);
6. `n2-t5-medicoes.csv`, `n2-t5-lb-versus-work.csv`, `n2-t5-custos.md` e `n2-t5-manifest.json` da execução prospectiva, conforme conteúdos informados pelo pesquisador.

**Integridade (atualização de fechamento, 2026-10-10):** o pesquisador executou localmente `verify_n2_t6_gate.py` no checkout de origem e compartilhou o JSON emitido com `audit_status=VERIFIED_ARTIFACT_BYTES_AND_TABULAR_INVARIANTS` e `decision=N2 FAIL`. O verificador informou os quatro SHA-256 abaixo, em acordo com o manifesto N2-T5. Essa é **evidência reportada de auditoria local**, não uma nova leitura independente dos bytes pelo redator deste registro. O próprio verificador declara que verificar arquivos e invariantes não substitui reauditoria das provas E5.

## 2. Regra decisória imutável

`N2 PASS` exige **simultaneamente**:

- certificados válidos e regressões/controles aceitos;
- melhoria do LB físico certificado sobre a referência B0 nas **duas famílias** estruturais;
- persistência da melhoria nos **dois níveis** de tamanho;
- recuperação **≥50%** do incremento positivo do LP completo sobre B0, nos casos de nível 1 com LP conhecido;
- custo computacional compatível, dentro de **164 Work** por instância e limites operacionais.

Se **qualquer condição necessária falhar**, a classificação pré-registrada é **`N2 FAIL`**. Essa classificação não depende de esgotar Work nem de encontrar bugs no solver.

## 3. Evidências quantificáveis do Gate

| Família e nível | B0 de referência | LB físico certificado | Ganho exato (LB−B0) | Work total | RMP final (somente diagnóstico) |
|---|---:|---:|---:|---:|---:|
| HB — nível 1 | `1` | `1/2` | `−1/2` | 0,417963 | 2 |
| BP-não — nível 1 | `6` | `1` | `−5` | 0,083058 | 7 |
| HB — nível 2 | `11500000000000001/10000000000000000` | `2/3` | `−14500000000000003/30000000000000000` | 1,364441 | 3 |
| BP-não — nível 2 | `8` | `18/13` | `−86/13` | 0,670544 | 9 |

Os quatro LBs físicos têm status `CERTIFIED`. Todos foram reportados com `lp_source=N1` e `g2_status=NOT_CONVERGED_CERTIFIED`. **Nenhum foi maior do que B0.**

No nível 1:

- HB: `LP_histórico=2`, `B0=1`, recuperação `(1/2−1)/(2−1)=−1/2`, inferior a `+1/2`;
- BP: `LP_histórico=7`, `B0=6`, recuperação `(1−6)/(7−6)=−5`, inferior a `+1/2`.

No nível 2, não existe LP completo histórico congelado. O gate não imputa LP nem taxa de recuperação nesse nível; a condição de **ganho sobre B0** também falhou nos dois casos maiores.

### 3.1. Matriz de critérios

| Critério pré-registrado | Evidência | Julgamento |
|---|---|---|
| Identidade: 2 famílias × 2 níveis | Quatro nomes e hashes congelados | **Atendido, segundo manifesto/check local** |
| Validade da certificação física K/E5 | 4× `CERTIFIED_PHYSICAL_LB` | **Atendido, segundo pipeline E5 aceito** |
| Regressão histórica N1 | Gate N2-T4 aceito com exceção formal `Direct0` | **Atendido no escopo aprovado** |
| Limite de 164 Work e guarda 1800 s | Work máximo 1,364442; Wall máximo 7,001145 s | **Atendido** |
| Ganho certificado sobre B0 em HB e BP | Quatro ganhos estritamente negativos | **NÃO ATENDIDO** |
| Ganho reproduzido nos dois níveis | Negativo nos níveis 1 e 2 | **NÃO ATENDIDO** |
| Recuperação ≥50% do incremento LP conhecido | HB = −50%; BP = −500% | **NÃO ATENDIDO** |
| Custo útil por ganho obtido | Custo baixo, mas nenhum ganho certificado | **Sem vantagem comprovada** |
| G2 / convergência certificada | `NOT_CONVERGED_CERTIFIED` em todas as linhas | **Não demonstrada** (não usada como substituto do critério principal) |
| Integridade dos artefatos finais | Auditoria local concluída: `VERIFIED_ARTIFACT_BYTES_AND_TABULAR_INVARIANTS`; digests publicados coincidentes | **Atendido segundo log local apresentado** |

A falha das condições de ganho e recuperação é **suficiente** para o veredicto, mesmo que os custos sejam muito baixos. O critério é sobre LB físico certificado; não é satisfeito pelo objetivo do master restrito nem pelo último `ObjBoundC` numérico.

## 4. Interpretação técnica restrita

O resultado é **um insucesso experimental pré-registrado**, **não** uma refutação da validade matemática de F-CC+K.

- O master apresentou estacionariedade numérica, mas não houve prova G2. `z_R=2,7,3,9` é **diagnóstico**, não LB comprovado.
- O bound publicado se originou exclusivamente de **N1 analítico**. ENUM não foi utilizado em instâncias `n≥16` e N2-box iniciou com multiplicadores racionais zero. A implementação experimental não demonstrou conversão eficaz dos duais numéricos em um LB global forte.
- Não se pode deduzir, desses números, que **um N2-box fortalecido ou outro pricing nunca daria resultado melhor**. Essa questão exige investigação científica **posterior e distinta**, sem substituir a campanha congelada.
- A referência B0 (histórica no nível 1, numérica no nível 2) possui `b0_certificate_status=UNCERTIFIED`: tratá-la como **referência de comparação**, não como LB físico E5 independente. A ausência dessa prova não cria um sucesso retrospectivo.
- As quatro instâncias eram pequenas em Wall/Work, mas o protocolo exige utilidade do **limite certificado**, não apenas rapidez ou estação numérica.

## 5. Consequências previstas na Story 6

1. **Emitir `N2 FAIL` para o caminho B medido**. **Não promover à N3** com base nesta campanha.
2. Manter a F-CC+K como contribuição **teórica e de diagnóstico**, com código, provas e dados preservados.
3. Registrar a limitação observada de escalabilidade **da certificação de LB**: em instâncias dos dois níveis selecionados, o certificado alcançou apenas `1/2`, `1`, `2/3`, `18/13`, apesar de RMP numericamente estacionário e sem esgotar orçamento. Isso **não comprova** um limite intrínseco de escalabilidade computacional da formulação.
4. **Não** abrir branch-and-price, N3, trocar família/instância, alterar B0, relaxar a tolerância ou repetir seletivamente a medição para fabricar PASS.
5. Se houver continuidade, abrir **nova investigação explicitamente pós-gate** sobre certificadores globais/pricing, com hipóteses, orçamento e protocolo próprios. Nunca mesclar seus resultados aos quatro pré-registrados.

## 6. Evidência de auditoria local e rastreabilidade pendente

Em 2026-10-10, o pesquisador executou os seguintes comandos no checkout que realizou a N2-T5 e apresentou os resultados completos:

- `PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p 'test_n2_t6_gate.py' -v` → **13/13 PASS**, sem falhas nem skips;
- `python -m ruff check experiments/alternative-formulations/verify_n2_t6_gate.py experiments/alternative-formulations/test_n2_t6_gate.py` → **All checks passed!**;
- `python experiments/alternative-formulations/verify_n2_t6_gate.py` → JSON com `decision=N2 FAIL`, `audit_status=VERIFIED_ARTIFACT_BYTES_AND_TABULAR_INVARIANTS`, 4 medições e 6 razões explícitas de bloqueio.

Para repetir a auditoria futuramente:

```bash
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/alternative-formulations -p 'test_n2_t6_gate.py' -v

python -m ruff check \
  experiments/alternative-formulations/verify_n2_t6_gate.py \
  experiments/alternative-formulations/test_n2_t6_gate.py

python experiments/alternative-formulations/verify_n2_t6_gate.py
```

A execução é **somente leitura**, não chama Gurobi e não modifica congelamentos. Resultado **observado pelo pesquisador** com os arquivos originais: JSON com `audit_status=VERIFIED_ARTIFACT_BYTES_AND_TABULAR_INVARIANTS`, `decision=N2 FAIL`, código de saída `0`.

Se houver arquivo ausente, hash diferente ou inconsistência tabular: `audit_status=AUDIT_FAILED`, código `2`. Não relatar auditoria final como aprovada nesse caso. O código de saída `0` significa que o **verificador concluiu corretamente um resultado científico negativo**, não que a N2 passou.

Registrar adicionalmente:

```bash
sha256sum results/alternative-formulations/n2-t5-prospectivo/n2-t5-manifest.json
sha256sum experiments/alternative-formulations/verify_n2_t6_gate.py
sha256sum experiments/alternative-formulations/run_n2_t5.py
git branch --show-current
git rev-parse HEAD
git status --short
```

Campos restantes para rastreabilidade documental, sem inventar valores:

| Campo de evidência | Estado atual |
|---|---|
| Hash do manifesto N2-T5 | **PENDENTE DE REGISTRO** |
| Auditoria byte a byte dos quatro artefatos | **EXECUTADA LOCALMENTE — VERIFICADA PELO SCRIPT (conforme saída enviada)** |
| HEAD do commit com runner efetivamente executado | **PENDENTE DE REGISTRO** |
| Resultado Ruff específico dos arquivos N2-T6 | **PASS — All checks passed!** |
| Testes de auditoria N2-T6 | **13/13 PASS** |
| Revisão independente do código/relatório do gate | **NÃO DECLARADA** |

A verificação de artefatos não refaz do zero a prova formal de cada dual E5: depende do aceite separado da N2-T3 e da rastreabilidade dos certificados originais. Essa limitação deve ser preservada.

## 7. Registro final de decisão

| Campo | Valor |
|---|---|
| Gate | **N2-T6** |
| Decisão científica indicada pelos dados e pelo freeze | **`N2 FAIL`** |
| Causas suficientes | **Sem ganho B0 em 4/4**; recuperação **<50% nos 2/2 controles conhecidos** |
| Estado de evidência nesta conversa | **Log de auditoria local aprovado e apresentado**; hashes comparados pelo verificador; arquivos binários não anexados a esta conversa |
| Aceite técnico N2-T5 | Execução concluída, 30/30 testes, Ruff PASS, quatro LBs físicos certificados segundo executor |
| N3 | **NÃO LIBERADA** |
| Branch-and-price para compensar resultado | **VEDADO neste escopo** |
| Preservação | Fontes, freeze, registros de regressão e resultados prospectivos **inalterados** |
| Formalização final | **Gate fechado com auditoria local; adicionar HEAD/manifest SHA para rastreabilidade máxima** |

**Síntese:** sob o protocolo congelado e os valores prospectivos fornecidos, **N2 FAIL**. A constatação é reproduzível por aplicação direta das condições quantitativas e deve ser preservada como resultado científico negativo. O fecho **documental** registra a auditoria local já executada e comunicada; o SHA do manifesto e o HEAD permanecem pendentes de identificação, **sem impedir a decisão científica já estabelecida**. Isso não autoriza recalibrar critérios nem repetir seletivamente os experimentos.


## 8. Adendo de fechamento — auditoria executada

**Registro de aceite nesta interação:** diante da saída de auditoria local com `N2 FAIL`, o responsável pelo projeto solicitou expressamente **"vamos fechar"**. Este registro documenta o encerramento da **N2** com **resultado científico negativo**, não uma revisão independente ou assinatura criptográfica.

**SHA-256 recalculados pelo verificador no ambiente local e informados no JSON:**

| Artefato | SHA-256 |
|---|---|
| `n2-t5-medicoes.csv` | `2e1215e135561d4af962318f15eeaa96be0d04aed09a8e801765ae577958bac5` |
| `n2-t5-lb-versus-work.csv` | `c0be65a1fe79f7da59be50bc3b184e0143f6c97a7f0153e66464c26a43563d5d` |
| `n2-t5-custos.md` | `0b6700ed47b257e1fb5aa368d5bd1b5ec17bbf832d691b89625c912601258d0a` |
| `n2-t5-lb-versus-work.svg` | `520f82c4e0e64dec45c3d4d11ce5c61abfe150aaaedc76c5bd9cecd0f55f9920` |

**Limites da evidência:** a saída do verificador foi recebida como transcrição do terminal; os cinco arquivos prospectivos originais não estão incluídos neste pacote, e não se recalculou aqui o hash do manifesto. A prova dual E5 continua sujeita ao Gate N2-T3, não à auditoria tabular.

**Decisão final:** `N2 FAIL`; **N2-T6 concluída**; **N3 não liberada**; conservar F-CC+K como contribuição matemática e ferramenta diagnóstica.
