#!/usr/bin/env python3
"""N2-T4: regressão prospectiva nos 23 controles N1 com LP F-CC+K conhecido.

Não implementa medição N2-T5. Nunca reescreve resultados da N1, freeze ou
artefatos existentes da própria T4. Modos:

    PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t4.py check
    PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t4.py run

Um resultado numérico do RMP não é um LB; a comparação de regressão usa
somente o limite LP revalidado pela E5 e, se aplicável, G2 certificado.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import subprocess
import sys
from dataclasses import dataclass
from collections import deque
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
from time import monotonic

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RESULTS = ROOT / 'results' / 'alternative-formulations'
FREEZE_T5 = HERE / 'n1-t5-freeze.json'
FREEZE_T6 = HERE / 'n1-t6-freeze.json'
N1_T5 = RESULTS / 'n1-t5-diagnostico.csv'
N1_T6 = RESULTS / 'n1-t6-diagnostico.csv'
N1_PAIRS = RESULTS / 'n1-t6-pares.json'
EPS = Fraction(1, 1_000_000)
EXPECTED_T5 = 18
EXPECTED_T6 = 6
EXPECTED_ELIGIBLE = 23
EXPECTED_EXCLUDED = 1
STATUS_REFERENCE = 'COMPUTATIONALLY VERIFIED'
EXCLUDED = 'EXCLUDED_NO_FULL_LP_REFERENCE'
PASS_G2 = 'PASS_G2_FULL_LP'
PASS_LB = 'PASS_CERTIFIED_LB_LE_FULL_LP'
PASS_NUMERIC = 'PASS_NUMERIC_STATIONARY_WITH_CERTIFIED_LB'
PASS_DIRECT_ZERO = 'PASS_DIRECT_ZERO_EXACT_OUTSIDE_CONNECTED_DOMAIN'
PASS_CLASSES = frozenset({PASS_G2, PASS_LB, PASS_NUMERIC, PASS_DIRECT_ZERO})
FAIL = 'FAIL'
G2_PASSED = 'CONVERGED_CERTIFIED'
CERTIFIED = 'CERTIFIED'
FIELDS = (
    'id', 'n1_source', 'name', 'n', 'm', 'r', 'reference_lp_fcc_k',
    'reference_status', 'reference_k_hash', 'instance_sha256',
    'lp_certification_status', 'lp_lb_exact', 'lp_lb_floor_12dp',
    'proof_method', 'direct_matching',
    'physical_status', 'g2_status', 'u_exact', 'stop_reason',
    'rmp_objective_diagnostic', 'objective_reflects_all_columns',
    'iterations', 'pricing_calls', 'columns_added', 'total_work',
    'wall_seconds', 'comparison', 'justification',
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def _reference_fraction(raw: str) -> Fraction:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError('referência de LP ausente')
    try:
        decimal = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError('referência LP malformada') from exc
    if not decimal.is_finite():
        raise ValueError('referência LP não finita')
    return Fraction(decimal)


def _ratio(value: Fraction | None) -> str:
    return '' if value is None else f'{value.numerator}/{value.denominator}'


@dataclass(frozen=True)
class Control:
    id: str
    source: str
    name: str
    n: int
    m: int
    r: int
    reference_raw: str
    reference_status: str
    k_hash: str
    instance_hash: str
    excluded: bool = False

    @property
    def reference(self) -> Fraction | None:
        return None if self.excluded else _reference_fraction(self.reference_raw)


def _verify_archive_hashes(frozen_t5: dict, frozen_t6: dict) -> None:
    """Verificações puras: não carregam bibliotecas do solver nem executam N1."""
    if _sha(N1_T5) != frozen_t6['gate_t5']['source_hashes'][
            'results/alternative-formulations/n1-t5-diagnostico.csv']:
        raise ValueError('CSV histórico T5 não coincide com freeze T6')
    for relative, expected in frozen_t6['source_hashes'].items():
        if _sha(ROOT / relative) != expected:
            raise ValueError(f'freeze T6: hash divergente {relative}')
    for relative, expected in frozen_t6['gate_t5']['source_hashes'].items():
        if _sha(ROOT / relative) != expected:
            raise ValueError(f'gate T5: hash divergente {relative}')
    if _read_json(N1_PAIRS).get('freeze_hash') != _sha(FREEZE_T6):
        raise ValueError('pares T6 não referenciam o freeze da N1-T6')
    if tuple(item['nome'] for item in frozen_t5['instances']) != tuple(
            row['instancia'] for row in _read_csv(N1_T5)):
        raise ValueError('ordem histórica T5 divergente do freeze')


def build_manifest(*, verify_hashes: bool = True) -> tuple[Control, ...]:
    """18 T5 + 6 T6; 23 LP medidos, 1 sem referência (não é zero)."""
    frozen_t5, frozen_t6 = _read_json(FREEZE_T5), _read_json(FREEZE_T6)
    if verify_hashes:
        _verify_archive_hashes(frozen_t5, frozen_t6)
    rows_t5, rows_t6 = _read_csv(N1_T5), _read_csv(N1_T6)
    if len(rows_t5) != EXPECTED_T5 or len(rows_t6) != EXPECTED_T6:
        raise ValueError('corpus N1 precisa manter 18 T5 e 6 T6')
    if len(frozen_t5['instances']) != EXPECTED_T5:
        raise ValueError('freeze T5 tem cardinalidade inválida')
    cases = []
    for row, pre in zip(rows_t5, frozen_t5['instances']):
        if row['instancia'] != pre['nome'] or row['k_hash'] != pre['k_hash']:
            raise ValueError('T5: identidade/K divergente do freeze')
        measured = (row['status_lp_fcc_k'] == STATUS_REFERENCE and
                    bool(row['lp_fcc_k'].strip()))
        if measured:
            _reference_fraction(row['lp_fcc_k'])
        elif row['instancia'] != 'SC-GF2-k3' or row['lp_fcc_k'] != '' or not pre['fcc_cap_reason']:
            raise ValueError('T5: exclusão não prevista ou LP histórico inconsistente')
        cases.append(Control(
            f"T5:{row['instancia']}", 'T5', row['instancia'],
            int(row['n']), int(row['m']), int(row['r']),
            row['lp_fcc_k'] if measured else '', row['status_lp_fcc_k'],
            row['k_hash'], pre['data_sha256'], excluded=not measured,
        ))
    generated = _read_json(N1_PAIRS)
    graph_map = {
        g['name']: g for pair in generated['pairs'] for g in pair['graphs']
    }
    if len(graph_map) != EXPECTED_T6 or len(generated['pairs']) != 3:
        raise ValueError('pares N1-T6 inconsistentes')
    for row in rows_t6:
        name = row['name']
        if name not in graph_map or graph_map[name]['graph_hash'] != row['graph_hash']:
            raise ValueError('grafo N1-T6 divergente da evidência congelada')
        if row['pair_status'] != CERTIFIED or row['status_lp_fcc_k'] != STATUS_REFERENCE:
            raise ValueError('T6: controle sem certificação histórica ou sem LP')
        _reference_fraction(row['lp_fcc_k'])
        cases.append(Control(f'T6:{name}', 'T6', name, int(row['n']),
                             int(row['m']), int(row['r']), row['lp_fcc_k'],
                             row['status_lp_fcc_k'], row['k_hash'], row['graph_hash']))
    if len(cases) != EXPECTED_T5 + EXPECTED_T6 or len({x.id for x in cases}) != len(cases):
        raise ValueError('controles duplicados ou faltando')
    if sum(not case.excluded for case in cases) != EXPECTED_ELIGIBLE or sum(
            case.excluded for case in cases) != EXPECTED_EXCLUDED:
        raise ValueError('N2-T4 exige exatamente 23 controles elegíveis e 1 exclusão')
    return tuple(cases)


def classify(reference: Fraction, *, status: str, lb: Fraction | None,
             g2_status: str, upper: Fraction | None,
             stop_reason: str = '', rmp_objective: float | None = None,
             reflects_all_columns: bool = False) -> tuple[str, str]:
    """Regra T4: LB rigoroso sempre; CG estacionário recebe teste numérico adicional."""
    if status != CERTIFIED or not isinstance(lb, Fraction):
        return FAIL, 'ausência de LB global do LP com prova E5 revalidada'
    if lb > reference + EPS:
        return FAIL, 'LB certificado ultrapassou o LP completo histórico'
    if g2_status == G2_PASSED:
        if not isinstance(upper, Fraction) or upper < lb:
            return FAIL, 'G2 anunciado sem U primal racional consistente'
        if abs(lb - reference) > EPS or abs(upper - reference) > EPS:
            return FAIL, 'G2 certificado diverge do LP completo N1 além de 1e-6'
        return PASS_G2, 'G2 validado e intervalo [LB,U] coincide com LP N1 em 1e-6'
    if stop_reason == 'NUMERICAL_STATIONARY':
        if not reflects_all_columns or rmp_objective is None or not math.isfinite(rmp_objective):
            return FAIL, 'estacionariedade numérica sem objetivo completo do RMP'
        numeric = Fraction(Decimal(str(rmp_objective)))
        if abs(numeric - reference) > EPS:
            return FAIL, 'master numericamente estacionário diverge do LP N1 em >1e-6'
        return PASS_NUMERIC, ('RMP numericamente estacionário coincide com LP N1; '
                              'LB separado permanece rigoroso; G2 não demonstrado')
    return PASS_LB, 'sem G2: LB rigoroso <= LP completo N1 (+1e-6)'


def _preflight_runtime() -> None:
    if os.environ.get('PYTHONHASHSEED') != '0':
        raise RuntimeError('PYTHONHASHSEED=0 é obrigatório para replay N1')
    from run_n1_t5 import check_freeze
    from run_n1_t6 import checked_freeze, read_pairs
    check_freeze()
    checked_freeze()
    read_pairs()
    proc = subprocess.run(
        [sys.executable, str(HERE / 'run_n2_t1.py'), 'check'],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError('freeze N2-T1 inválido: ' + proc.stdout + proc.stderr)
    proc = subprocess.run(
        [sys.executable, str(HERE / 'verify_n1_t7_gate.py')],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0 or 'PROMOTE FCC + EXISTING CUTS' not in proc.stdout:
        raise RuntimeError('gate N1-T7 não confirma caminho B: ' + proc.stdout + proc.stderr)


def _rebuild_case(case: Control, t5_corpus, t6_graphs):
    """Reconstrói por fábricas originais; reconfere grafo e K sem usar CSV como instância."""
    from run_n1_t5 import instance_hash
    from fcc_k import prepare_k
    if case.source == 'T5':
        inst = t5_corpus[case.name]
        if instance_hash(inst) != case.instance_hash:
            raise ValueError(f'{case.id}: instância mudou após N1-T5')
    else:
        inst = t6_graphs[case.name]
        if inst['graph_hash'] != case.instance_hash:
            raise ValueError(f'{case.id}: variante N1-T6 diferente')
    S, T, V = [tuple(inst[key]) for key in ('S', 'T', 'V')]
    adj = {v: tuple((u, length) for u, length in inst['adj'][v]) for v in V}
    A_r = tuple(tuple(edge) for edge in inst['A_r'])
    r = inst['r']
    if (len(V), len(S), r) != (case.n, case.m, case.r):
        raise ValueError(f'{case.id}: dimensões divergentes')
    K, k_hash, _ = prepare_k(S, T, V, adj, A_r, r)
    if k_hash != case.k_hash:
        raise ValueError(f'{case.id}: K não coincide com referência N1')
    return S, T, V, adj, A_r, r, K, k_hash


def _exact_direct_zero_exception(case: Control, data) -> dict | None:
    """Prova especial para o controle N1 Direct0, que viola G conexo da N2.

    Não executa nem simula a CG/E5. Demonstra z_Q=OPT=0 pela solução primal
    y=lambda=0, d matching direto perfeito; custo não negativo e K vazio.
    Recusa qualquer variação do caso, do grafo, de A_r, de K ou da referência.
    """
    if case.id != 'T5:Direct0':
        return None
    S, T, V, adj, A_r, r, K, k_hash = data
    if (case.source != 'T5' or case.name != 'Direct0' or case.excluded or
            case.reference != Fraction(0) or len(S) != len(T) or
            not S or len(set(S)) != len(S) or len(set(T)) != len(T) or
            len(set(V)) != len(V) or not set(S + T) <= set(V) or
            type(r) is not int or r < 1 or not isinstance(adj, dict)):
        raise ValueError('Direct0: identidade/domínio/referência incompatível com prova exata')
    # Mesma canonização histórica de run_n1_t5.instance_hash, sem importar
    # módulos com Gurobi. Vincula a prova à instância N1-T5 congelada.
    serialized = {
        'V': [str(v) for v in V], 'S': [str(v) for v in S],
        'T': [str(v) for v in T], 'r': r,
        'adj': sorted((str(u), str(v), str(w)) for u, links in adj.items()
                      for v, w in links),
        'A_r': sorted((str(u), str(v)) for u, v in A_r),
    }
    blob = (json.dumps(serialized, indent=2, sort_keys=True,
                       ensure_ascii=False) + '\n').encode('utf8')
    if hashlib.sha256(blob).hexdigest() != case.instance_hash:
        raise ValueError('Direct0: dados não coincidem com hash da N1-T5')
    # K deve ser comprovadamente vazio, não apenas possuir um hash fornecido.
    empty_k_hash = hashlib.sha256(b'[]').hexdigest()
    if K or k_hash != empty_k_hash or case.k_hash != empty_k_hash:
        raise ValueError('Direct0: K não vazio ou hash incompatível com ótimo zero')
    neighbors = {v: set() for v in V}
    for v in V:
        local = adj.get(v, ())
        if len(local) != len(set(u for u, _ in local)):
            raise ValueError('Direct0: adj contém duplicatas')
        for u, length in local:
            if u not in neighbors or u == v or length != 1:
                raise ValueError('Direct0: aresta inválida')
            neighbors[v].add(u)
    if set(adj) != set(V) or any(v not in neighbors[u] for u in V for v in neighbors[u]):
        raise ValueError('Direct0: adj assimétrica/incompleta')
    comps = []
    unseen = set(V)
    while unseen:
        root = next(v for v in V if v in unseen)
        group, work = {root}, deque([root])
        while work:
            v = work.popleft()
            for u in neighbors[v] - group:
                group.add(u)
                work.append(u)
        comps.append(frozenset(group))
        unseen.difference_update(group)
    if len(comps) != 2:
        raise ValueError('Direct0: número inesperado de componentes; não é a exceção autorizada')
    # Recalcular TODOS os arcos em H (não confiar em A_r vindo da N1).
    reach = set()
    for root in V:
        seen, queue = {root}, deque([(root, 0)])
        while queue:
            v, depth = queue.popleft()
            if depth == r:
                continue
            for u in neighbors[v]:
                if u not in seen:
                    seen.add(u)
                    reach.add((root, u))
                    queue.append((u, depth + 1))
    arcs = tuple(A_r)
    if len(arcs) != len(set(arcs)) or set(arcs) != reach:
        raise ValueError('Direct0: A_r difere do alcance exato de G')
    options = {origin: tuple(dest for dest in T if origin == dest or
                             (origin, dest) in reach) for origin in S}
    assigned = {}

    def augment(origin, tried):
        for dest in options[origin]:
            if dest in tried:
                continue
            tried.add(dest)
            if dest not in assigned or augment(assigned[dest], tried):
                assigned[dest] = origin
                return True
        return False
    if not all(augment(origin, set()) for origin in S):
        raise ValueError('Direct0: inexistente matching direto perfeito')
    matching = tuple((assigned[dest], dest) for dest in T)
    # Todas as equações R1/R2 são satisfeitas por d=1 nos pares do matching;
    # R3/K por lambda=y=0. Assim 0 <= z_Q <= 0, logo z_Q=0 exatamente.
    return {
        'lp_certification_status': CERTIFIED, 'lp_lb_exact': '0/1',
        'lp_lb_floor_12dp': '0.000000000000',
        'proof_method': 'EXACT_DIRECT_MATCHING_ZERO_NO_CG',
        'direct_matching': json.dumps([[str(s), str(t)] for s, t in matching],
                                      separators=(',', ':'), ensure_ascii=False),
        'physical_status': CERTIFIED,
        'g2_status': 'NOT_EVALUATED_NO_CG', 'u_exact': '0/1',
        'stop_reason': 'OUTSIDE_CONNECTED_DOMAIN_EXACT_DIRECT_PROOF',
        'rmp_objective_diagnostic': '', 'objective_reflects_all_columns': False,
        'iterations': 0, 'pricing_calls': 0, 'columns_added': 0,
        'total_work': '', 'wall_seconds': '', 'comparison': PASS_DIRECT_ZERO,
        'justification': ('EXCEÇÃO FORMAL N1 Direct0: G desconexo (2 componentes), '
            'fora do domínio autorizado do master N2; NÃO houve CG/E5. '
            'K vazio e hash histórico conferidos; A_r recalculado por BFS; '
            f'matching direto perfeito certificado {matching!r}; '
            'y=0, lambda=0, d do matching e K vazio satisfazem o LP completo; '
            'objetivo não negativo prova z_LP=OPT=0 exatamente. '
            'Uma comparação excepcional não comprova execução da CG no Direct0.'),
    }


def _evaluate_case(case: Control, data, *, time_limit: float,
                   work_limit: float | None, max_iterations: int,
                   enum_cap: int) -> dict:
    S, T, V, adj, A_r, r, K, k_hash = data
    direct_proof = _exact_direct_zero_exception(case, data)
    if direct_proof is not None:
        return direct_proof
    from n2_t3_cert_integration import CertificationOptions
    from n2_t3_cert_validation import FinalCertificate, run_verified_column_generation
    options = CertificationOptions(
        use_n1=True, use_n2=True, max_n2_vertices=24,
        enum_cap=enum_cap if len(V) <= 10 else None,
        max_enum_vertices=10,
    )
    started = monotonic()
    result = run_verified_column_generation(
        S, T, V, adj, A_r, r, K=K, k_hash=k_hash, options=options,
        max_iterations=max_iterations, work_limit=work_limit,
        time_limit=time_limit, master_params={'Seed': 42, 'Threads': 1},
        pricing_params={'Seed': 42, 'Threads': 1},
    )
    if not isinstance(result, FinalCertificate):
        raise TypeError('E5 não retornou FinalCertificate real')
    if result.k_evidence is None or result.k_evidence.k_hash != case.k_hash:
        raise ValueError('E5 não comprovou identidade dos cortes K')
    if result.physical_status != CERTIFIED:
        raise ValueError('E5 não concluiu promoção física: K/prova/tempo insuficientes')
    if result.audit_warnings:
        # A falha de alguma tentativa não é necessariamente erro se houver
        # outra prova revalidada, mas deve constar da justificativa.
        audit = '; '.join(str(x) for x in result.audit_warnings)
    else:
        audit = ''
    upper = result.primal_upper.u_exact if result.primal_upper else None
    base = result.numerical_result
    comparison, why = classify(
        case.reference, status=result.lp_status, lb=result.lp_lb_exact,
        g2_status=result.convergence_status, upper=upper,
        stop_reason=getattr(base, 'stop_reason', ''),
        rmp_objective=getattr(base, 'rmp_objective', None),
        reflects_all_columns=getattr(base, 'objective_reflects_all_columns', False),
    )
    row = {
        'lp_certification_status': result.lp_status,
        'proof_method': 'N2_T3_E5_REAUDITED_CG',
        'direct_matching': '',
        'lp_lb_exact': _ratio(result.lp_lb_exact),
        'lp_lb_floor_12dp': result.as_dict()['lp_lb_floor_12dp'],
        'physical_status': result.physical_status,
        'g2_status': result.convergence_status,
        'u_exact': _ratio(upper),
        'stop_reason': getattr(base, 'stop_reason', ''),
        'rmp_objective_diagnostic': getattr(base, 'rmp_objective', None),
        'objective_reflects_all_columns': getattr(base, 'objective_reflects_all_columns', None),
        'iterations': getattr(base, 'iterations', ''),
        'pricing_calls': getattr(base, 'pricing_calls', ''),
        'columns_added': getattr(base, 'columns_added', ''),
        'total_work': getattr(base, 'total_work', None),
        'wall_seconds': monotonic() - started,
        'comparison': comparison,
        'justification': why + '; ' + result.justification +
                         ('; avisos de reauditoria: ' + audit if audit else ''),
    }
    return row


def _initial_row(case: Control) -> dict:
    return {
        'id': case.id, 'n1_source': case.source, 'name': case.name,
        'n': case.n, 'm': case.m, 'r': case.r,
        'reference_lp_fcc_k': case.reference_raw,
        'reference_status': case.reference_status,
        'reference_k_hash': case.k_hash,
        'instance_sha256': case.instance_hash,
    }


def _csv_bytes(rows: list[dict]) -> bytes:
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=FIELDS, extrasaction='ignore',
                            lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, '') for field in FIELDS})
    return output.getvalue().encode('utf-8')


def _output(run_dir: Path, rows: list[dict], manifest: tuple[Control, ...],
            *, config: dict, result: str) -> tuple[Path, Path]:
    csv_path = run_dir / 'n2-t4-regressao.csv'
    json_path = run_dir / 'n2-t4-regressao-manifest.json'
    if csv_path.exists() or json_path.exists():
        raise FileExistsError('arquivos N2-T4 já existem: não sobrescrever evidências')
    run_dir.mkdir(parents=True, exist_ok=True)
    payload = _csv_bytes(rows)
    metadata = {
        'task': 'N2-T4', 'status': result, 'expected_eligible': EXPECTED_ELIGIBLE,
        'eligible_checked': sum(r['comparison'] not in (EXCLUDED, '') for r in rows),
        'excluded': [x.id for x in manifest if x.excluded],
        'passed': sum(r['comparison'] in PASS_CLASSES for r in rows),
        'exact_domain_exceptions': [r['id'] for r in rows if r['comparison'] == PASS_DIRECT_ZERO],
        'cg_evaluated': sum(r['comparison'] in (PASS_G2, PASS_LB, PASS_NUMERIC) for r in rows),
        'failures': [r['id'] for r in rows if r['comparison'] == FAIL],
        'n1_sources_sha256': {str(path.relative_to(ROOT)): _sha(path)
                              for path in (FREEZE_T5, FREEZE_T6, N1_T5, N1_T6, N1_PAIRS)},
        'n2_t1_sha256': _sha(HERE / 'n2-t1-freeze.json'),
        'config': config, 'csv_sha256': hashlib.sha256(payload).hexdigest(),
        'scope': 'prospective N1 regression only; NOT N2-T5 measurements or N2 PASS',
        'exception_policy': ('Direct0 fora do domínio G conexo: prova independente '
                             'de LP=0; requer decisão explícita antes de N2-T5'),
    }
    json_blob = (json.dumps(metadata, indent=2, sort_keys=True, ensure_ascii=False)
                 + '\n').encode('utf-8')
    # Reservar ambos os destinos antes de iniciar; falha não pisa em resultado antigo.
    try:
        with csv_path.open('xb') as file:
            file.write(payload)
        with json_path.open('xb') as file:
            file.write(json_blob)
    except BaseException:
        # Nunca eliminar um arquivo que já existia antes do início.
        if not json_path.exists() and csv_path.exists():
            csv_path.unlink()
        raise
    return csv_path, json_path


def _run(manifest: tuple[Control, ...], *, run_dir: Path,
         time_limit: float, work_limit: float | None,
         max_iterations: int, enum_cap: int) -> bool:
    if any((run_dir / name).exists() for name in
           ('n2-t4-regressao.csv', 'n2-t4-regressao-manifest.json')):
        raise FileExistsError('resultados N2-T4 existentes; use outro --output-dir')
    from run_n1_t5 import corpus
    from run_n1_t6 import read_pairs
    t5_corpus = {x['nome']: x for x in corpus()}
    t6_graphs = {graph['name']: graph for pair in read_pairs()['pairs']
                 for graph in pair['graphs']}
    rows, failure = [], False
    for case in manifest:
        row = _initial_row(case)
        if case.excluded:
            row.update(comparison=EXCLUDED,
                       justification='N1-T5 sem LP F-CC+K medido por cap; não tratar como zero')
        else:
            try:
                data = _rebuild_case(case, t5_corpus, t6_graphs)
                row.update(_evaluate_case(case, data, time_limit=time_limit,
                                          work_limit=work_limit,
                                          max_iterations=max_iterations,
                                          enum_cap=enum_cap))
            except Exception as exc:
                row.update(comparison=FAIL,
                           justification=f'{type(exc).__name__}: {exc}')
        rows.append(row)
        print(case.id, row['comparison'], flush=True)
        if row['comparison'] == FAIL:
            failure = True
            break  # requisito de stop imediato perante falha de regressão
    passed = (not failure and len(rows) == EXPECTED_T5 + EXPECTED_T6 and
              sum(r['comparison'] in PASS_CLASSES for r in rows) == EXPECTED_ELIGIBLE)
    exceptions = [r['id'] for r in rows if r['comparison'] == PASS_DIRECT_ZERO]
    # O usuário deve avaliar a exceção ao domínio matemático G conexo antes de
    # liberar N2-T5; não declarar PASS puro com apenas 22 chamadas reais da CG.
    accepted = passed and not exceptions
    config = {
        'time_limit_per_case_s': time_limit, 'work_limit_per_case': work_limit,
        'max_iterations': max_iterations, 'enum_cap': enum_cap,
        'seed': 42, 'threads': 1, 'tolerance': str(EPS),
        'note': 'Limites por controle são somente da regressão, não alteram pré-registro N2-T1',
    }
    run_status = ('PASS' if accepted else
                  'SCOPE_EXCEPTION_REVIEW_BLOCK_N2_T5' if passed else
                  'FAIL_BLOCK_N2_T5')
    csv_path, manifest_path = _output(run_dir, rows, manifest, config=config,
                                      result=run_status)
    print('EVIDÊNCIA', csv_path, manifest_path, flush=True)
    return accepted


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['check', 'run'])
    parser.add_argument('--output-dir', type=Path, default=RESULTS)
    parser.add_argument('--time-limit', type=float, default=600.0,
                        help='segundos por controle; não é Work N2-T5')
    parser.add_argument('--work-limit', type=float, default=None)
    parser.add_argument('--max-iterations', type=int, default=300)
    parser.add_argument('--enum-cap', type=int, default=2048)
    args = parser.parse_args(argv)
    if os.environ.get('PYTHONHASHSEED') != '0':
        parser.error('execute com PYTHONHASHSEED=0')
    if not math.isfinite(args.time_limit) or args.time_limit <= 0:
        parser.error('--time-limit deve ser finito e positivo')
    if args.work_limit is not None and (not math.isfinite(args.work_limit)
                                        or args.work_limit <= 0):
        parser.error('--work-limit deve ser finito e positivo')
    if args.max_iterations <= 0 or args.enum_cap <= 0:
        parser.error('--max-iterations e --enum-cap precisam ser positivos')
    try:
        manifest = build_manifest()
        print('CONTROLES N1:', len(manifest), 'TOTAL;', EXPECTED_ELIGIBLE,
              'ELEGÍVEIS;', EXPECTED_EXCLUDED, 'EXCLUÍDO', flush=True)
        _preflight_runtime()
        if args.mode == 'check':
            for c in manifest:
                print(c.id, EXCLUDED if c.excluded else c.reference_raw)
            print('N2-T4 CHECK PASS: sem execuções e sem arquivos gerados')
            return 0
        passed = _run(manifest, run_dir=args.output_dir,
                      time_limit=args.time_limit, work_limit=args.work_limit,
                      max_iterations=args.max_iterations, enum_cap=args.enum_cap)
        return 0 if passed else 2
    except (OSError, ValueError, RuntimeError, KeyError, AssertionError) as exc:
        print('N2-T4 BLOCKED:', type(exc).__name__, str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
