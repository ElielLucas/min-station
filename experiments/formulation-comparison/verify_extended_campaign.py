#!/usr/bin/env python3
"""FC-06: verificador independente, somente leitura, do pré-registro e CSV final.

Não importa o reporter da campanha nem roda Gurobi. Todos os casos censurados
ficam no denominador. SHA-256 é controle de integridade, não assinatura digital.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
from verify_comparison_artifacts import verify as verify_fc04  # noqa: E402
from verify_comparison_pilot import evaluate as evaluate_fc05  # noqa: E402

EXPECTED_SEEDS = (42, 43, 44)
MIP_ARMS = frozenset({'comp_mip', 'fcc_k'})
LP_ARMS = frozenset({'lp_base', 'lp_comp', 'lp_fcc_k'})


def _sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as file:
        for piece in iter(lambda: file.read(1024 * 1024), b''):
            h.update(piece)
    return h.hexdigest()


def _float(value):
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _load_csv(path):
    with open(path, encoding='utf-8', newline='') as file:
        return list(csv.DictReader(file))


def _source_integrity(prereg, root, issues):
    """Verifica novamente fontes anteriores. Declaração de READY não basta."""
    for kind in ('pilot', 'screening'):
        raw = prereg.get(f'{kind}_run')
        if not isinstance(raw, str) or not raw:
            issues.append(f'MISSING_{kind.upper()}_SOURCE')
            continue
        rel = Path(raw)
        if rel.is_absolute() or '..' in rel.parts or '.' in rel.parts:
            issues.append(f'UNSAFE_{kind.upper()}_SOURCE_PATH')
            continue
        try:
            folder = (root / rel).resolve(strict=True)
            folder.relative_to(root.resolve(strict=True))
            digest = _sha(folder / 'manifest.json')
            if digest != prereg.get(f'{kind}_manifest_sha256'):
                issues.append(f'{kind.upper()}_MANIFEST_CHANGED')
            if kind == 'pilot':
                gate = evaluate_fc05(folder, root=root)
                if gate['status'] != 'READY_FOR_EXTENDED':
                    issues.append('PILOT_NO_LONGER_AUDITED_READY')
            else:
                ok, findings = verify_fc04(folder, root=root)
                if not ok:
                    issues.append(f'SCREENING_NO_LONGER_AUDITABLE:{findings}')
                if _sha(folder / 'results.csv') != prereg.get('screening_results_sha256'):
                    issues.append('SCREENING_RESULTS_CHANGED')
        except (OSError, ValueError, KeyError) as exc:
            issues.append(f'{kind.upper()}_SOURCE_UNAVAILABLE:{exc}')


def _fail(issues):
    return {'status': 'INTEGRITY_FAIL', 'problems': issues,
            'scientific_conclusion': 'INCONCLUSIVE', 'campaign_triggered': False}


def verify(run_dir: Path, *, root: Path = ROOT):
    root = Path(root).resolve()
    run_dir = Path(run_dir).resolve()
    issues = []
    ok, artifact_problems = verify_fc04(run_dir, root=root)
    if not ok:
        issues.extend(f'ARTIFACT_AUDIT:{problem}' for problem in artifact_problems)
    try:
        prereg_file = run_dir / 'preregistration.json'
        prereg_bytes = prereg_file.read_bytes()
        prereg = json.loads(prereg_bytes)
        checksum = (run_dir / 'preregistration.sha256').read_text(encoding='ascii').strip()
        if checksum != hashlib.sha256(prereg_bytes).hexdigest() + '  preregistration.json':
            issues.append('PREREGISTRATION_SHA256_MISMATCH')
        manifest = json.loads((run_dir / 'manifest.json').read_text(encoding='utf-8'))
        results = _load_csv(run_dir / 'results.csv')
        report = json.loads((run_dir / 'campaign_report.json').read_text(encoding='utf-8'))
        plan = _load_csv(run_dir / 'plan.csv')
        with (run_dir / 'events.jsonl').open(encoding='utf-8') as stream:
            events = [json.loads(x) for x in stream if x.strip()]
    except (OSError, ValueError, UnicodeError, KeyError, json.JSONDecodeError, csv.Error) as exc:
        return _fail(issues + [f'MISSING_OR_CORRUPT_CAMPAIGN:{exc}'])
    if (prereg.get('schema') != 'FC06-prereg-v1' or
            prereg.get('pilot_gate') != 'READY_FOR_EXTENDED' or
            prereg.get('mip_wall_cap_s') != 3600.0 or
            prereg.get('lp_wall_cap_s') != 600.0 or
            prereg.get('seeds') != list(EXPECTED_SEEDS) or
            not prereg.get('selected')):
        issues.append('INVALID_PREREGISTRATION_CONTRACT')
    if (manifest.get('fc06_schema') != 'FC06-run-v1' or
            manifest.get('tier') != 'extended' or
            manifest.get('preregistration_sha256') != hashlib.sha256(prereg_bytes).hexdigest()):
        issues.append('MANIFEST_DOES_NOT_BIND_PREREGISTRATION')
    if manifest.get('code_files_sha256') != prereg.get('code_files_sha256'):
        issues.append('CODE_SNAPSHOT_DIFFERS_FROM_PREREGISTRATION')
    _source_integrity(prereg, root, issues)
    selected = prereg.get('selected', [])
    selected_by_name = {x.get('instance'): x for x in selected if isinstance(x, dict)}
    if len(selected_by_name) != len(selected):
        issues.append('DUPLICATE_OR_INVALID_SELECTION')
    for entry in selected:
        if not isinstance(entry, dict):
            issues.append('INVALID_SELECTED_ENTRY')
            continue
        if manifest.get('input_files_sha256', {}).get(entry.get('input_path')) != entry.get('instance_sha256'):
            issues.append('SELECTED_INSTANCE_INPUT_HASH_MISMATCH:' + str(entry.get('instance')))
    if (manifest.get('planned_arm_count') != len(plan) or
            manifest.get('reported_arm_count') != len(results)):
        issues.append('MANIFEST_ROW_COUNTS_MISMATCH')
    prepared_plan = prereg.get('plan', [])
    if len(plan) != len(prepared_plan):
        issues.append('PLAN_COUNT_DIFFERS_FROM_PREREGISTRATION')
    expected = {}
    for ordinal, entry in enumerate(prepared_plan):
        try:
            key = (entry['instance'], str(entry['seed']), entry['modality'], entry['formulation'])
            if (entry['order'] != ordinal or
                    (entry['modality'] == 'B' and entry['formulation'] not in MIP_ARMS) or
                    (entry['modality'] == 'A' and entry['formulation'] not in LP_ARMS) or
                    entry['instance'] not in selected_by_name or key in expected):
                issues.append('INVALID_OR_DUPLICATED_PREREGISTERED_PLAN')
            expected[key] = entry
            if ordinal >= len(plan) or any(str(plan[ordinal].get(k)) != str(v)
                                          for k, v in entry.items()):
                issues.append('PLAN_CSV_DIFFERS_FROM_PREREGISTRATION')
        except (KeyError, TypeError, AttributeError):
            issues.append('MALFORMED_PLAN_ENTRY')
    seen = Counter()
    by_mip = defaultdict(dict)
    groups = defaultdict(lambda: {'planned_arms': 0, 'completed_numeric_optimal': 0,
                                  'censored_arms': 0, 'pair_valid_repetitions': 0,
                                  'pair_not_valid_repetitions': 0})
    for entry in prepared_plan:
        if isinstance(entry, dict) and entry.get('origin_graph'):
            groups[entry['origin_graph']]['planned_arms'] += 1
    for row in results:
        key = (row.get('instance'), str(row.get('seed')), row.get('modality'),
               row.get('formulation'))
        seen[key] += 1
        if key not in expected:
            issues.append(f'UNEXPECTED_ARM:{key}')
            continue
        p = expected[key]
        origin = p['origin_graph']
        if (row.get('instance_name') != p['instance'] or
                row.get('origin_graph') != origin or
                row.get('plan_order') != str(p['order']) or
                _float(row.get('wall_budget_s')) != p['wall_budget_s']):
            issues.append(f'ARM_METADATA_MISMATCH:{key}')
        if row.get('instance_sha256') not in ('', None, selected_by_name[p['instance']]['instance_sha256']):
            issues.append(f'ARM_INPUT_MISMATCH:{key}')
        wall = _float(row.get('wall_total_s'))
        solver = _float(row.get('solver_runtime_s'))
        work = _float(row.get('work'))
        if wall is not None and (wall < 0 or wall > p['wall_budget_s'] + min(.75, max(.25, .005 * p['wall_budget_s']))):
            issues.append(f'BUDGET_VIOLATION:{key}')
        if solver is not None and (solver < 0 or (wall is not None and solver > wall + .05)):
            issues.append(f'SOLVER_WALL_INCONSISTENCY:{key}')
        if work is not None and work < 0:
            issues.append(f'NEGATIVE_WORK:{key}')
        if (row.get('rational_verification') != 'NOT_CERTIFIED' or
                row.get('rational_verified_lb_exact') or
                row.get('certified_gap_abs_exact') or
                row.get('certified_gap_rel_exact') or
                row.get('certified_gap_status') != 'INCONCLUSIVE'):
            issues.append(f'RATIONAL_CERTIFICATION_UNSUPPORTED:{key}')
        if row.get('modality') == 'B':
            if row.get('status') in ('CAP_EXCEEDED', 'TIMEOUT_PREPARATION',
                                     'TIMEOUT_SOLVER', 'TIMEOUT_VALIDATION',
                                     'WORKER_ERROR', 'SOLVER_UNAVAILABLE'):
                if (row.get('solver_numeric_mip_lb') not in ('', None) or
                        row.get('solver_numeric_mip_incumbent') not in ('', None) or
                        row.get('physical_feasible_ub') not in ('', None)):
                    issues.append(f'FABRICATED_CENSORED_EVIDENCE:{key}')
            if row.get('physical_feasible_ub') not in ('', None) and (
                    row.get('physically_validated', '').lower() != 'true'):
                issues.append(f'UNVALIDATED_PHYSICAL_UB:{key}')
        if (row.get('modality') == 'A' and row.get('status') != 'OPTIMAL' and
                row.get('solver_numeric_lp_objective') not in ('', None)):
            issues.append(f'FABRICATED_INCOMPLETE_LP:{key}')
        if row.get('status') == 'OPTIMAL' and row.get('solver_evidence') == 'SOLVER_NUMERIC_OPTIMAL':
            groups[origin]['completed_numeric_optimal'] += 1
        else:
            groups[origin]['censored_arms'] += 1
        if p['modality'] == 'B':
            by_mip[(origin, p['instance'], str(p['seed']))][p['formulation']] = row
            if row.get('pair_status') == 'PAIR_VALID':
                s = selected_by_name[p['instance']]
                if (row.get('k_sha256') != s['k_sha256'] or
                        row.get('model_complete', '').lower() != 'true' or
                        row.get('k_validated', '').lower() != 'true' or
                        row.get('instance_sha256') != s['instance_sha256']):
                    issues.append(f'FALSE_VALID_PAIR:{key}')
                if row.get('solver_numeric_mip_incumbent') not in ('', None):
                    if (row.get('physically_validated', '').lower() != 'true' or
                            _float(row.get('physical_feasible_ub')) is None):
                        issues.append(f'INVALID_PHYSICAL_WITNESS:{key}')
    for key, count in seen.items():
        if count != 1:
            issues.append(f'DUPLICATED_RESULT:{key}:{count}')
    for key in expected:
        if seen[key] == 0:
            issues.append(f'PLANNED_ARM_NOT_RECORDED:{key}')
            groups[expected[key]['origin_graph']]['censored_arms'] += 1
    for (origin, _, _), pair in by_mip.items():
        pair_valid = (len(pair) == 2 and all(pair.get(x, {}).get('pair_status') == 'PAIR_VALID'
                                                for x in MIP_ARMS))
        if pair_valid and (pair['comp_mip'].get('k_sha256') != pair['fcc_k'].get('k_sha256') or
                           pair['comp_mip'].get('instance_sha256') !=
                           pair['fcc_k'].get('instance_sha256')):
            issues.append('PAIR_IDENTITIES_DIVERGED:' + str((origin, _, _)))
        groups[origin]['pair_valid_repetitions' if pair_valid else 'pair_not_valid_repetitions'] += 1
    for entry in selected:
        if not isinstance(entry, dict):
            continue
        for seed in EXPECTED_SEEDS:
            key = (entry['origin_graph'], entry['instance'], str(seed))
            if key not in by_mip:
                groups[entry['origin_graph']]['pair_not_valid_repetitions'] += 1
    expected_groups = dict(sorted(groups.items()))
    if report.get('origin_graph_groups') != expected_groups:
        issues.append('REPORT_GROUP_COUNTS_DO_NOT_MATCH_RESULTS_AND_PLAN')
    if report.get('planned_arms_total') != len(expected) or report.get('recorded_arms_total') != len(results):
        issues.append('REPORT_DENOMINATORS_MISMATCH')
    if (report.get('censored_or_missing_arms_total') != sum(x['censored_arms'] for x in groups.values()) or
            report.get('numeric_optimal_arms_total') != sum(
                x['completed_numeric_optimal'] for x in groups.values())):
        issues.append('REPORT_CENSORED_COUNTS_MISMATCH')
    planned_pairs = len(selected) * len(EXPECTED_SEEDS)
    comparable_pairs = sum(x['pair_valid_repetitions'] for x in groups.values())
    if (report.get('planned_mip_pairs_total') != planned_pairs or
            report.get('comparable_mip_pairs_total') != comparable_pairs):
        issues.append('REPORT_PAIR_COUNTS_MISMATCH')
    if (report.get('any_rational_certification_claimed') is not False or
            report.get('universal_superiority_claimed') is not False or
            manifest.get('rational_verifier_executed') is not False or
            manifest.get('superiority_claimed') is not False):
        issues.append('UNSUPPORTED_SCIENTIFIC_CLAIM')
    # Independently recompute numerical LP and per-seed MIP tabulations.
    # A hash is not scientific verification of claims in a report.
    lp_by_instance = defaultdict(dict)
    mip_by_pair = defaultdict(dict)
    for row in results:
        if row.get('modality') == 'A':
            lp_by_instance[row.get('instance')][row.get('formulation')] = row
        elif row.get('modality') == 'B':
            mip_by_pair[(row.get('instance'), str(row.get('seed')))][row.get('formulation')] = row
    observations = report.get('lp_strength_observations', [])
    if len(observations) != len(selected):
        issues.append('LP_REPORT_COUNT_MISMATCH')
    for e in selected:
        if not isinstance(e, dict):
            continue
        original = e['instance']
        listed = [x for x in observations if x.get('instance') == original]
        if len(listed) != 1:
            issues.append('LP_REPORT_MISSING_OR_DUPLICATED:' + original)
            continue
        a, b = (lp_by_instance[original].get(x, {}) for x in ('lp_comp', 'lp_fcc_k'))
        measured = (a.get('status') == b.get('status') == 'OPTIMAL' and
                    a.get('solver_evidence') == b.get('solver_evidence') ==
                    'SOLVER_NUMERIC_OPTIMAL')
        reported = listed[0]
        if (reported.get('comparison_available') is not measured or
                reported.get('origin_graph') != e['origin_graph'] or
                reported.get('rational_verification') != 'NOT_CERTIFIED'):
            issues.append('LP_REPORT_EVIDENCE_MISMATCH:' + original)
        for key, raw in (('solver_numeric_comp_lp', a.get('solver_numeric_lp_objective')),
                         ('solver_numeric_fcc_lp', b.get('solver_numeric_lp_objective'))):
            expected_value = _float(raw) if measured else None
            if reported.get(key) != expected_value:
                issues.append('LP_REPORT_NUMERIC_MISMATCH:' + original + ':' + key)
    pair_observations = report.get('mip_pair_outcomes', [])
    if len(pair_observations) != planned_pairs:
        issues.append('MIP_REPORT_COUNT_MISMATCH')
    for e in selected:
        if not isinstance(e, dict):
            continue
        for seed in EXPECTED_SEEDS:
            pair_key = (e['instance'], str(seed))
            recorded = [x for x in pair_observations if
                        (x.get('instance'), str(x.get('seed'))) == pair_key]
            if len(recorded) != 1:
                issues.append('MIP_REPORT_MISSING_OR_DUPLICATED:' + str(pair_key))
                continue
            report_pair = recorded[0]
            a = mip_by_pair[pair_key].get('comp_mip', {})
            b = mip_by_pair[pair_key].get('fcc_k', {})
            valid = (a.get('pair_status') == b.get('pair_status') == 'PAIR_VALID')
            both_optimal = valid and a.get('status') == b.get('status') == 'OPTIMAL'
            if (report_pair.get('pair_status') != ('PAIR_VALID' if valid else
                                                  'PAIR_CENSORED_OR_INVALID') or
                    report_pair.get('both_solver_optimal') is not both_optimal or
                    report_pair.get('comparison_of_runtime_allowed') is not both_optimal or
                    report_pair.get('origin_graph') != e['origin_graph'] or
                    report_pair.get('rational_verification') != 'NOT_CERTIFIED'):
                issues.append('MIP_REPORT_EVIDENCE_MISMATCH:' + str(pair_key))
            if (report_pair.get('comp_wall_s') != _float(a.get('wall_total_s')) or
                    report_pair.get('fcc_wall_s') != _float(b.get('wall_total_s'))):
                issues.append('MIP_REPORT_TIMES_MISMATCH:' + str(pair_key))
    if report.get('both_numeric_optimal_pairs_total') != sum(
            x.get('both_solver_optimal') is True for x in pair_observations):
        issues.append('MIP_REPORT_OPTIMAL_PAIR_COUNT_MISMATCH')
    if (not events or events[0].get('event') != 'START' or
            events[0].get('preregistration_sha256') != hashlib.sha256(prereg_bytes).hexdigest() or
            len([e for e in events if e.get('event') == 'ARM_FINISHED']) != len(expected)):
        issues.append('EXECUTION_EVENT_LEDGER_INCONSISTENT')
    return {'status': 'PASS' if not issues else 'INTEGRITY_FAIL',
            'problems': issues, 'planned_arms': len(expected),
            'recorded_arms': len(results), 'comparable_pairs': comparable_pairs,
            'scientific_conclusion': 'DESCRIPTIVE_ONLY_NOT_RATIONALLY_CERTIFIED',
            'campaign_triggered': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path)
    args = parser.parse_args(argv)
    r = verify(args.run_dir)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0 if r['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
