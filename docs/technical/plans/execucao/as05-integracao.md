# AS-05 — Como integrar e executar no MIN-STATION

Este pacote contém **somente arquivos novos/revistos**; não contém o repositório todo nem modifica evidências históricas. A organização segue os diretórios existentes `experiments/formulation-comparison/`, `specs/as-05-piloto-lp-gate/` e `docs/technical/plans/execucao/`.

## 1. Aplicação do ZIP

Estando na raiz da branch `novos_testes`, extraia o ZIP **diretamente nessa raiz**. Antes de executar, use `git status --short` e `git diff -- experiments/formulation-comparison/as04_runner.py` para conferir a extensão do ajuste ao AS-04. O único arquivo AS-04 modificado é o runner, com `grouping_seed` opcional para preservar a mesma partição quando variar a seed do Gurobi. Seu comportamento padrão permanece inalterado.

## 2. Gates rápidos sem solver

```bash
python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-05-piloto-lp-gate/spec.md --strict
python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-05-piloto-lp-gate/tasks.md --strict
PYTHONHASHSEED=0 PYTHONPATH=. python3 -m unittest discover -s experiments/formulation-comparison -p 'test_as05*.py' -v
PYTHONHASHSEED=0 PYTHONPATH=. python3 -m unittest discover -s experiments/formulation-comparison -p 'test_as04*.py' -v
PYTHONPATH=. python3 experiments/formulation-comparison/run_as05_smoke.py
python3 -m ruff check experiments/formulation-comparison/as05*.py experiments/formulation-comparison/run_as05*.py experiments/formulation-comparison/as04_runner.py
```

O smoke AS-05 contém **resultados inteiramente sintéticos**. `GO` nele não é conclusão experimental. O Ruff está pendente no ambiente de preparação.

## 3. Criar o adendo prospectivo ANTES dos solves

```bash
PYTHONPATH=. python3 experiments/formulation-comparison/run_as05_pilot.py \
  --init-plan results/benchmark/as05-prospective-plan-v1.json

PYTHONPATH=. python3 experiments/formulation-comparison/run_as05_pilot.py \
  --check-plan results/benchmark/as05-prospective-plan-v1.json
```

**Importante:** o programa não sobrescreve arquivo existente. Se já houve LP, não edite silenciosamente o plano; registre um novo adendo/desvio com outro nome. Os números **1% e 3× são proposta AS-05**, não valores congelados na AS-00. Revise-os **antes do primeiro solve**. O plano padrão mantém A4 desligada.

## 4. Revisões independentes e arquivo de autorização

Examine `docs/technical/plans/execucao/as05-gate-evidence-template.json`. Ele vem com tudo **PENDING/FALSE** e é intencionalmente não autorizador. Após verificação independente real dos documentos matemáticos e testes, crie um arquivo separado (não versionar como prova se não for auditável) preenchendo as evidências e os caminhos de pareceres. **Não altere os estados apenas para destravar o script.**

O executor valida a estrutura de autores e revisores distintos e os indicadores de PASS. Isso **não substitui** verificar assinatura/autenticidade e o conteúdo dos pareceres. Esta parte depende de homologação humana externa.

## 5. Rodar piloto real — somente depois dos gates

```bash
PYTHONPATH=. python3 experiments/formulation-comparison/run_as05_pilot.py \
  --execute \
  --plan results/benchmark/as05-prospective-plan-v1.json \
  --gate-file docs/technical/plans/execucao/as05-gate-evidence-REVISADO.json \
  --output-dir results/benchmark/as05-20261011-pilot-001
```

Estimativa de máximo de orçamento de supervisor: **18 execuções obrigatórias × 90 s = até 27 min**, mais até **12 repetições candidatas × 90 s = até 18 min**, além de A4 opcional. Não é previsão de duração nem promessa de execução. O programa só pode ser executado no seu ambiente com Gurobi e gate externo, não foi executado aqui.

Os casos obrigatórios são U sem K, U+K e A2+K em cada uma das seis instâncias de desenvolvimento. Duas seeds complementares (43 e 44) são executadas **somente para pares com ganho material candidato**. Em todas, a partição AS-03 conserva seed 42. As evidências e os manifestos recebem hashes sem sobrescrever resultados anteriores.

## 6. Fechamento e limites

A AS-05 ainda exige: (i) revisão matemática independente AS-01/AS-02 e revisão AS-04; (ii) Ruff no seu ambiente; (iii) Gurobi em casos reais; (iv) revisão independente da decisão e (v) controle pequeno F-CC ou justificativa documentada da não aplicabilidade. Sem esses gates, status **IMPLEMENTADA PARA TESTES / NÃO HOMOLOGADA**. Uma decisão simulada `GO` dos testes não constitui decisão do piloto.
