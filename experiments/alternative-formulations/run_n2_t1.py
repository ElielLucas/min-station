#!/usr/bin/env python3
"""N2-T1: ativação e pré-registro NÃO destrutivo do caminho B (F-CC+K).

Executar na raiz: PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t1.py freeze
                      PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t1.py check

Não otimiza, não mede e não modifica resultados N1. Congelamento único, sem sobrescrita.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESULTS = ROOT / 'results' / 'alternative-formulations'
DOCS = ROOT / 'docs' / 'technical' / 'plans' / 'execucao'
FREEZE = HERE / 'n2-t1-freeze.json'
PREREG = DOCS / 'n2-t1-pre-registro.md'
EPS = 1e-6
EXPECTED_DECISION = 'PROMOTE FCC + EXISTING CUTS'
REFERENCE_WORK = 164.0  # Spec A: 4 threads, 1800s guarda; total de subsolves.
LEVEL_ONE = (
    ('HB-q4-ndir2-p1', 'hb'),
    ('BP-nao-[3,1]-q2', 'bp-nao'),
)
# Segundo nível: geradores estruturais preexistentes, parâmetros escolhidos antes de N2.
LEVEL_TWO = (
    ('HB-q6-ndir2-p1', 'hb', 'hb.construir', {'q': 6, 'ndir': 2, 'p': 1, 'k': 1, 'L': 2}),
    ('BP-nao-[2,2,2]-q2', 'bp-nao', 'bp.construir', {'items': [2, 2, 2], 'q': 2, 'B': 3}),
)
SOURCES = (
    'specs/proxima-fase-n2-limite-compatibilidade-certificado/spec.md',
    'specs/proxima-fase-n1-informacao-compatibilidade/spec.md',
    'docs/technical/plans/execucao/n1-t7-decisao-cientifica.md',
    'docs/technical/reference/formulacoes/revisao-mr-f3-n1.md',
    'docs/technical/reference/baseline-e-metodo/linha-de-base-pre-registro.md',
    'experiments/alternative-formulations/verify_n1_t7_gate.py',
    'experiments/alternative-formulations/n1-t5-freeze.json',
    'results/alternative-formulations/n1-t5-diagnostico.csv',
    'results/alternative-formulations/n1-t6-diagnostico.csv',
    'experiments/structural/hb.py',
    'experiments/structural/bp.py',
    'experiments/structural/io_instancia.py',
    'experiments/alternative-formulations/fcc.py',
    'experiments/alternative-formulations/fcc_k.py',
    'experiments/cuts/cuts.py',
    'experiments/cuts/harness.py',
)


def require(cond, msg):
    if not cond:
        raise RuntimeError(msg)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def load_csv(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def activation():
    """Recalcula o gate N1, sem confiar apenas em uma string da documentação."""
    require(os.environ.get('PYTHONHASHSEED') == '0', 'Exige PYTHONHASHSEED=0')
    path = HERE / 'verify_n1_t7_gate.py'
    require(path.exists(), 'Verificador N1-T7 ausente')
    spec = importlib.util.spec_from_file_location('n1_t7_gate_for_n2', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    stream = io.StringIO()
    with redirect_stdout(stream):
        module.main()  # falha se evidências/hash/decisão divergem
    output = stream.getvalue()
    require(f'DECISÃO N1-T7: {EXPECTED_DECISION}' in output, 'Caminho B não foi promovido pela N1')
    decision = (DOCS / 'n1-t7-decisao-cientifica.md').read_text(encoding='utf8')
    require(f'**Decisão:** `{EXPECTED_DECISION}`' in decision, 'Registro da N1 incompatível')
    return output


def ensure_no_n2_results():
    """Evita congelamento retrospectivo depois de resultado N2."""
    if RESULTS.exists():
        prior = sorted(p.name for p in RESULTS.iterdir()
                       if p.is_file() and p.name.startswith('n2-')
                       and p.suffix in ('.csv', '.json', '.md'))
        require(not prior, f'Já há evidência N2 antes do freeze: {prior}')


def prior_rows():
    t5 = {row['instancia']: row for row in load_csv(RESULTS / 'n1-t5-diagnostico.csv')}
    require(len(t5) == 18, 'N1-T5: esperado 18 instâncias únicas')
    n1freeze = json.loads((HERE / 'n1-t5-freeze.json').read_text(encoding='utf8'))
    info = {row['nome']: row for row in n1freeze['instances']}
    require(len(info) == 18, 'N1-T5 freeze incompleto')
    return t5, info


def level_two_instance(source, params):
    sys.path.insert(0, str(ROOT / 'experiments' / 'structural'))
    if source == 'hb.construir':
        import hb
        S, T, V, adj, _edges, r, _delta = hb.construir(**params)
    elif source == 'bp.construir':
        import bp
        S, T, V, adj, _edges, r = bp.construir(**params)
    else:
        raise ValueError('Gerador não permitido')
    require(len(V) > 21, f'{source}: nível 2 exige n > 21; n={len(V)}')
    require(len(S) == len(T) and set(S).issubset(V) and set(T).issubset(V), 'Instância inválida')
    require(r == 1, 'Alteração inesperada de autonomia')
    # Neste corpus r=1 e todas as arestas são unitárias. A_r contém os pares não reflexivos.
    arcs = sorted({(str(u), str(v)) for u in V for v, w in adj.get(u, []) if w <= 1})
    edge_data = sorted((str(u), str(v), str(w)) for u in adj for v, w in adj[u])
    payload = {'V': [str(v) for v in V], 'S': [str(s) for s in S],
               'T': [str(t) for t in T], 'r': r,
               'adj': edge_data, 'A_r': arcs}
    data_hash = hashlib.sha256(encoded(payload)).hexdigest()
    return {'S': S, 'T': T, 'V': V, 'adj': adj, 'A_r': arcs,
            'r': r, 'data_sha256_n2': data_hash}


def assemble():
    t5, prior = prior_rows()
    rows = []
    for name, family in LEVEL_ONE:
        row, src = t5[name], prior[name]
        require(row['tipo'] == family and src['tipo'] == family, f'Família divergente: {name}')
        require(row['status_lp_fcc_k'] == 'COMPUTATIONALLY VERIFIED', 'F-CC+K não medido no N1')
        require(abs(float(row['lp_fcc_k']) - float(src.get('lp_fcc_k', row['lp_fcc_k']))) < EPS,
                'Valores congelados divergentes')
        require(float(row['lp_fcc_k']) > float(row['B0']) + EPS, 'Controle sem ganho N1')
        rows.append({'name': name, 'family': family, 'level': 1,
                     'source': 'N1-T5', 'instance_sha256': src['data_sha256'],
                     'k_sha256': src['k_hash'], 'n': int(row['n']), 'm': int(row['m']),
                     'r': int(row['r']), 'B0_source': 'N1-T5 lp_comp/core_ip',
                     'B0_reference': float(row['B0']),
                     'full_lp_source': 'N1-T5 lp_fcc_k',
                     'full_lp_reference': float(row['lp_fcc_k']),
                     'expected_positive_increment': float(row['lp_fcc_k']) - float(row['B0'])})
    for name, family, generator, params in LEVEL_TWO:
        inst = level_two_instance(generator, params)
        rows.append({'name': name, 'family': family, 'level': 2,
                     'source': generator, 'parameters': params,
                     'instance_sha256': inst['data_sha256_n2'],
                     'n': len(inst['V']), 'm': len(inst['S']), 'r': inst['r'],
                     'B0_source': 'recompute COMP LP and core IP at N2 under same budget',
                     'B0_reference': None,
                     'full_lp_source': 'NOT MEASURED: above N1 enumeration cap',
                     'full_lp_reference': None,
                     'expected_positive_increment': None})
    require(len(rows) == 4 and {r['family'] for r in rows} == {'hb', 'bp-nao'}
            and {r['level'] for r in rows} == {1, 2}, 'Plano não cobre dois tipos e dois níveis')
    return rows


def regressions():
    t5, _ = prior_rows()
    t6 = load_csv(RESULTS / 'n1-t6-diagnostico.csv')
    require(len(t6) == 6, 'N1-T6 incompleta')
    r = []
    for name, row in t5.items():
        if row['status_lp_fcc_k'] == 'COMPUTATIONALLY VERIFIED':
            r.append({'name': name, 'phase': 'N1-T5',
                      'full_lp': float(row['lp_fcc_k']), 'k_hash': row['k_hash']})
        else:
            require(row['status_lp_fcc_k'] == 'NOT MEASURED', f'Status inválido: {name}')
    for row in t6:
        if row['status_lp_fcc_k'] == 'COMPUTATIONALLY VERIFIED':
            r.append({'name': row['name'], 'phase': 'N1-T6',
                      'full_lp': float(row['lp_fcc_k'])})
        else:
            require(row['status_lp_fcc_k'] == 'NOT MEASURED', 'Status T6 inesperado')
    return r


def generate_data():
    trace = activation()
    ensure_no_n2_results()
    for name in SOURCES:
        require((ROOT / name).is_file(), f'Pré-requisito ausente: {name}')
    rows = assemble()
    reg = regressions()
    return {
        'task': 'N2-T1', 'state': 'FROZEN', 'frozen_at_utc': datetime.now(timezone.utc).isoformat(),
        'decision': EXPECTED_DECISION, 'path': 'B', 'representation': 'F-CC + K',
        'root_only': True, 'pricing': 'EXACT REQUIRED FOR CERTIFICATION',
        'restricted_master_is_lower_bound': False,
        'read_only_gate_signature_sha256': hashlib.sha256(trace.encode()).hexdigest(),
        'source_hashes': {name: sha(ROOT / name) for name in SOURCES},
        'runner_sha256': sha(Path(__file__)),
        'protocol': {
            'family_types': ['hb', 'bp-nao'], 'size_levels': [1, 2],
            'seed': 42, 'threads': 4, 'PYTHONHASHSEED': '0',
            'WorkLimit_total': REFERENCE_WORK, 'wall_guard_seconds': 1800,
            'work_includes': ['instance preparation', 'reachability', 'K', 'master', 'all pricing calls',
                              'separation', 'validation', 'reference computation'],
            'work_accounting': 'sum of solver Work for every solve, plus recorded non-solver wall time; never equate work to wall seconds',
            'solver_params_source': 'Spec A / linha-de-base-pre-registro.md; WorkLimit=164, Threads=4',
            'tolerance': EPS, 'min_recovery_fraction': 0.5,
            'reference': 'B0=max(LP COMP, core IP) on the same instance',
            'certification': 'CERTIFIED only with full exact pricing dual feasibility or an independently reviewed globally valid derived bound; else B0 if separately certified, otherwise UNCERTIFIED',
            'integer_round': 'ceil(LB - 1e-6), only when LB certified',
            'change_limit': 1, 'branching': False,
            'stop': ['uncertified bound', 'pricing exhausts total budget without gain',
                     'gain disappears at both size levels', 'total cost eliminates advantage',
                     'no minimal scaling beyond enumeration cap'],
            'gate': 'PASS only with certified controls, gain over B0 in both families and both levels, >=50% of positive known LP increment at level 1 within total budget and viable cost; otherwise FAIL',
        },
        'instances': rows, 'small_regressions': reg,
        'note': 'Level 2 is structural development-only; not the benchmark-v1 evaluation partition. No full-LP result is imputed.'
    }


def render(data):
    rows = data['instances']; prot = data['protocol']
    text = [
        '# N2-T1 — Pré-registro imutável do caminho B', '',
        f"**Congelado UTC:** `{data['frozen_at_utc']}`. **Caminho único:** `B / F-CC + K` (raiz apenas).",
        '**Estado:** `FROZEN`; nenhum resultado N2 foi medido por este comando.', '',
        '## Corpus prospectivo', '',
        '| Instância | Família | Nível | n | m | B0 | LP completo F-CC+K |',
        '|---|---|---:|---:|---:|---:|---:|',
    ]
    for r in rows:
        b = 'NOT MEASURED' if r['B0_reference'] is None else f"{r['B0_reference']:.9g}"
        lp = 'NOT MEASURED' if r['full_lp_reference'] is None else f"{r['full_lp_reference']:.9g}"
        text.append(f"| `{r['name']}` | `{r['family']}` | {r['level']} | {r['n']} | {r['m']} | {b} | {lp} |")
    text.extend([
        '', 'Nível 1: instâncias N1-T5 e seus hashes/LPs históricos; nível 2: geradores estruturais já existentes, acima do cap N1 `n_max=21`. ',
        'Instâncias de nível 2 são **desenvolvimento estrutural**, não avaliação da partição benchmark-v1. ',
        'Os códigos, parâmetros e hashes de dados por instância estão congelados em `experiments/alternative-formulations/n2-t1-freeze.json`.',
        '', '## Orçamento e certificação', '',
        f"- **Orçamento total por instância:** `WorkLimit={prot['WorkLimit_total']}` unidades de trabalho do solver, com `Threads={prot['threads']}`, `Seed={prot['seed']}` e guarda de parede de `{prot['wall_guard_seconds']}` segundos.",
        '- Todos os subsolves consomem o mesmo orçamento total: não reiniciar um WorkLimit cheio para cada pricing.',
        '- Registrar Wall time, pico de memória, custos de preparação, master, pricing, separação e verificação, número de colunas/cortes/chamadas e gap de pricing.',
        '- `B0=max(LP COMP, core IP)` em instâncias comparáveis; nos casos grandes, calcular B0 sob o protocolo, jamais preenchê-lo com zero.',
        '- Objetivo de master restrito de minimização é apenas valor de master restrito, **não** LB certificado.',
        '- Certificação de um novo LB somente com pricing global exato demonstrando dual completo viável, ou bound incompleto demonstrado e revisado especificamente para F-CC+K.',
        '- Com pricing interrompido: usar somente último limite válido previamente certificado (B0, quando validado) ou `UNCERTIFIED`.',
        '- Arredondamento: `ceil(LB - 1e-6)` exclusivamente após certificação.',
        '', '## Regressão N1', '',
        f"Há `{len(data['small_regressions'])}` controles de LP completo historicamente medidos (N1-T5/N1-T6). ",
        'Antes do nível 2, pricing exato deve coincidir com enumeração do custo reduzido e o master convergido deve reproduzir cada LP conhecido até `1e-6`. ',
        'Qualquer falha interrompe o nível 2.', '',
        '## Gate e parada', '',
        '- N2 PASS exige, conjuntamente: certificados válidos nos controles; ganho sobre B0 em HB e BP; reprodução em níveis 1 e 2; recuperação ≥50% do incremento positivo do LP completo nos casos conhecidos, dentro do orçamento total; custo compatível com a utilidade.',
        '- Caso contrário N2 FAIL, incluindo ausência de certificado, custo excessivo ou falta de escala.',
        '- No máximo uma mudança de representação, **somente** após diagnóstico escrito, sem novo pré-registro retrospectivo.',
        '- Sem branch-and-price, N3, novos sintéticos ou alterações de baseline.', '',
        '## Pré-condição pendente antes do código N2-T2B', '',
        'Primal, dual, custo reduzido, pricing exato e eventual fórmula de limite com pricing incompleto devem ser revistos formalmente **antes da implementação**. A minuta está em `docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md`.',
        '', '## Proveniência', '',
        f"- SHA-256 do runner: `{data['runner_sha256']}`.",
        '- Hashes e parâmetros completos: `n2-t1-freeze.json`.',
        '- Não sobrescrever este documento após os primeiros resultados N2.', '',
    ])
    return '\n'.join(text).encode('utf8')


def freeze():
    require(not FREEZE.exists() and not PREREG.exists(), 'N2-T1 já congelada ou estado parcial; não sobrescrever')
    data = generate_data()
    document = render(data)
    data['prereg_sha256'] = hashlib.sha256(document).hexdigest()
    FREEZE.parent.mkdir(parents=True, exist_ok=True)
    PREREG.parent.mkdir(parents=True, exist_ok=True)
    # Criar uma única vez; rollback somente quando *esta mesma chamada* falha antes da conclusão.
    created = []
    try:
        with PREREG.open('xb') as f:
            f.write(document)
        created.append(PREREG)
        with FREEZE.open('xb') as f:
            f.write(encoded(data))
        created.append(FREEZE)
    except Exception:
        for path in created:
            path.unlink()
        raise
    print('N2-T1 FROZEN: caminho B / F-CC + K; 2 famílias x 2 níveis; zero solves')
    print('Pré-registro:', PREREG)
    print('Freeze:', FREEZE)
    print('Regressões LP N1:', len(data['small_regressions']))


def check():
    require(FREEZE.is_file() and PREREG.is_file(), 'Pré-registro N2 ainda não existe: execute freeze')
    data = json.loads(FREEZE.read_text(encoding='utf8'))
    require(data['task'] == 'N2-T1' and data['state'] == 'FROZEN'
            and data['path'] == 'B' and data['representation'] == 'F-CC + K', 'Seleção alterada')
    require(sha(PREREG) == data['prereg_sha256'], 'Pré-registro Markdown modificado')
    require(sha(Path(__file__)) == data['runner_sha256'], 'Runner alterado depois do freeze')
    for relative, expected in data['source_hashes'].items():
        require(sha(ROOT / relative) == expected, f'Fonte alterada depois do freeze: {relative}')
    require(len(data['instances']) == 4 and len(data['small_regressions']) >= 17, 'Corpus incompleto')
    require({r['family'] for r in data['instances']} == {'hb', 'bp-nao'}, 'Famílias divergentes')
    require({r['level'] for r in data['instances']} == {1, 2}, 'Níveis divergentes')
    print('PASS: N2-T1 freeze íntegro; caminho B; 2 famílias x 2 níveis; orçamento total 164 Work')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['freeze', 'check'])
    args = parser.parse_args()
    if args.phase == 'freeze':
        freeze()
    else:
        check()


if __name__ == '__main__':
    main()
