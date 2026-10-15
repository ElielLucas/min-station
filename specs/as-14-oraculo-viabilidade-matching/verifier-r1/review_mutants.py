"""AS14 review: verifier-designed mutants, run in isolated temp copies.

For each mutant record whether it is killed by (a) the author's full AS14 suite,
(b) the author's verify_as14_oracle.py, (c) the reviewer's micro/audit/budget scripts.
A mutant whose mutation text is not found exactly once aborts the harness.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CUTS = ROOT / 'experiments/cuts'
HERE = Path(__file__).resolve().parent
FILES = ('h2_oracle.py', 'h2_oracle_schema.py', 'h2_oracle_cache.py',
         'independent_validator.py', 'test_h2_oracle.py')

M = [
    # --- matching / nu ---
    ('R01_KUHN_NO_AUGMENT', 'h2_oracle.py',
     'if t not in right_owner or augment(right_owner[t], seen):', 'if t not in right_owner:'),
    ('R02_KUHN_SHARED_SEEN', 'h2_oracle.py',
     '    for s in order_vertices(S):\n        probe()\n        augment(s, set())',
     '    _shared = set()\n    for s in order_vertices(S):\n        probe()\n        augment(s, _shared)'),
    ('R03_NU_OFF_BY_ONE_INFEASIBLE', 'h2_oracle.py',
     'return len(right_owner), (), order_vertices(left_seen), order_vertices(neighbors)',
     'return max(0, len(right_owner) - 1), (), order_vertices(left_seen), order_vertices(neighbors)'),
    ('R04_VIABLE_THRESHOLD_M_MINUS_1', 'h2_oracle.py',
     'status = Status.VIABLE if size == len(instance.S) else Status.INFEASIBLE',
     'status = Status.VIABLE if size >= len(instance.S) - 1 else Status.INFEASIBLE'),
    # --- Hall certificate ---
    ('R05_HALL_NO_ALTERNATING_EXPANSION', 'h2_oracle.py',
     'if other is not None and other not in left_seen:', 'if False:'),
    ('R06_HALL_REPORTS_UNMATCHED_ONLY', 'h2_oracle.py',
     'return len(right_owner), (), order_vertices(left_seen), order_vertices(neighbors)',
     'return len(right_owner), (), order_vertices(set(S) - set(left_partner)), order_vertices(neighbors)'),
    ('R07_HALL_EMPTY_NEIGHBORS_NO_CHECKS', 'h2_oracle.py',
     "    neighbors = {t for s in left_seen for t in reach[s]}\n    if len(neighbors) >= len(left_seen):\n        raise AssertionError('matching deficiency did not produce a Hall witness')",
     '    neighbors = set()'),
    # --- viability loops / physical semantics ---
    ('R08_REACH_SKIPS_LAST_ORIGIN', 'h2_oracle.py',
     'for s in order_vertices(instance.S):\n                probe()\n                reach[s]',
     'for s in order_vertices(instance.S)[:-1]:\n                probe()\n                reach[s]'),
    ('R09_TERMINALS_AS_STATIONS_IN_ORACLE', 'h2_oracle.py',
     'reach[s] = destinos_alcancaveis(s, instance.T, stations, graph, instance.r)',
     'reach[s] = destinos_alcancaveis(s, instance.T, stations + tuple(instance.S), graph, instance.r)'),
    ('R10_SHARED_REACH_TERMINALS_RECHARGE', 'independent_validator.py',
     'nb = r if w in Cset else b - 1', 'nb = r if (w in Cset or w in Tset) else b - 1'),
    ('R11_SHARED_REACH_NO_STAY', 'independent_validator.py',
     '    if origem in Tset:\n        alcance.add(origem)\n', ''),
    ('R12_SHARED_REACH_OFF_BY_ONE_BATTERY', 'independent_validator.py',
     '        if b < 1:\n            continue', '        if b < 2:\n            continue'),
    ('R13_STATION_CAPACITY_ONE', 'h2_oracle.py',
     '                reach[s] = destinos_alcancaveis(s, instance.T, stations, graph, instance.r)\n',
     '                reach[s] = destinos_alcancaveis(s, instance.T, stations, graph, instance.r)\n'
     '                stations = stations[1:]\n'),
    # --- F = V \\ R and Bhat ---
    ('R14_F_OVER_TERMINALS_ONLY', 'h2_oracle.py',
     'F = frozenset(instance.V) - R', 'F = (frozenset(instance.S) | frozenset(instance.T)) - R'),
    ('R15_F_IGNORES_R', 'h2_oracle.py',
     'F = frozenset(instance.V) - R', 'F = frozenset(instance.V)'),
    ('R16_BHAT_WITHOUT_ADDING_V', 'h2_oracle.py',
     'outcome = oracle.check(instance, F | {v}, budget_s=remaining())',
     'outcome = oracle.check(instance, F, budget_s=remaining())'),
    ('R17_COEF_ONE_FOR_EXAMINED', 'h2_oracle.py',
     'coeffs = tuple((v, 1 if v in Bhat else 2) for v in R_sorted)',
     'coeffs = tuple((v, 1 if v in examined else 2) for v in R_sorted)'),
    ('R18_COEF_ONE_FOR_NON_CANDIDATES', 'h2_oracle.py',
     'coeffs = tuple((v, 1 if v in Bhat else 2) for v in R_sorted)',
     'coeffs = tuple((v, 1 if (v in Bhat or v not in examine) else 2) for v in R_sorted)'),
    ('R19_UNKNOWN_COMPLEMENT_PROCEEDS', 'h2_oracle.py',
     'if complement.status is Status.UNKNOWN:', 'if False:'),
    ('R20_REMAINING_DROPS_BUDGET', 'h2_oracle.py',
     '        return max(0., budget_s - max(0., oracle.clock() - start))', '        return None'),
    # --- UNKNOWN returns ---
    ('R21_TIMEOUT_PROMOTED_TO_INFEASIBLE', 'h2_oracle.py',
     "answer = result(Status.UNKNOWN, reason='TIME_BUDGET_EXCEEDED')",
     "answer = result(Status.INFEASIBLE, 0, hall_origins=tuple(instance.S), reason='TIME_BUDGET_EXCEEDED') if instance.S else result(Status.UNKNOWN, reason='T')"),
    ('R22_ERROR_PROMOTED_TO_INFEASIBLE', 'h2_oracle.py',
     "answer = result(Status.UNKNOWN, reason=f'ORACLE_ERROR:{type(exc).__name__}')",
     "answer = result(Status.INFEASIBLE, 0, hall_origins=tuple(instance.S), reason='E') if instance.S else result(Status.UNKNOWN, reason='E')"),
    ('R23_FINAL_PROBE_REMOVED', 'h2_oracle.py',
     '            probe()\n            self.cache.put(answer)', '            self.cache.put(answer)'),
    ('R24_UNKNOWN_CACHED', 'h2_oracle_cache.py',
     '        if result.status is Status.UNKNOWN:\n            return\n', ''),
    # --- cache key / fingerprint ---
    ('R25_KEY_DROPS_STATIONS', 'h2_oracle_cache.py',
     'return (instance_sha256, frozenset(allowed))', 'return (instance_sha256, frozenset())'),
    ('R26_FINGERPRINT_DROPS_R', 'h2_oracle.py', "'r': self.r})", "'r': 0})"),
    ('R27_FINGERPRINT_DROPS_EDGES', 'h2_oracle.py',
     "'edges': [[row(u), row(v)] for u, v in edge_rows]", "'edges': []"),
    ('R28_FINGERPRINT_DROPS_S', 'h2_oracle.py',
     "'S': [row(x) for x in order_vertices(self.S)],", "'S': [],"),
    ('R29_FINGERPRINT_DROPS_TYPES', 'h2_oracle.py',
     '            return list(vertex_key(x))', '            return [str(x)]'),
    # --- monotonicity ---
    ('R30_MONO_BRANCH_VIABLE_DISABLED', 'h2_oracle_cache.py',
     'and allowed <= other_allowed) or', 'and False) or'),
    ('R31_MONO_BRANCH_INFEASIBLE_FLIPPED', 'h2_oracle_cache.py',
     'and other_allowed <= allowed))', 'and allowed <= other_allowed))'),
    ('R32_SAME_KEY_CONFLICT_IGNORED', 'h2_oracle_cache.py',
     "        if key in self._items and self._items[key].result.status != result.status:\n            raise AssertionError('conflicting matching certificates for identical cache key')\n", ''),
    # --- schema guard (defence in depth) ---
    ('R33_SCHEMA_INFEASIBLE_GUARD_REMOVED_PLUS_SHARED_SEEN', 'h2_oracle_schema.py',
     "            raise ValueError('INFEASIBLE requires a matching deficiency and Hall witness')",
     '            pass'),
]

# Order-2 mutant: schema guard removed AND Kuhn shared-seen AND internal Hall raise removed.
SECOND_ORDER = {
    'R33_SCHEMA_INFEASIBLE_GUARD_REMOVED_PLUS_SHARED_SEEN': [
        ('h2_oracle.py',
         '    for s in order_vertices(S):\n        probe()\n        augment(s, set())',
         '    _shared = set()\n    for s in order_vertices(S):\n        probe()\n        augment(s, _shared)'),
        ('h2_oracle.py',
         "    if len(neighbors) >= len(left_seen):\n        raise AssertionError('matching deficiency did not produce a Hall witness')",
         '    pass'),
        ('h2_oracle.py', '                assert len(hall_t) < len(hall_s)\n', ''),
    ],
}

WRAP_VERIFY = r'''
import sys, runpy
sys.path.insert(0, sys.argv[1])
import independent_validator, h2_oracle_schema, h2_oracle_cache, h2_oracle  # mutated copies
sys.argv = ['verify_as14_oracle.py']
runpy.run_path(sys.argv[0] if False else %r, run_name='__main__')
''' % str(CUTS / 'verify_as14_oracle.py')


def apply(dest, filename, original, replacement, name):
    p = dest / filename
    text = p.read_text(encoding='utf8')
    if text.count(original) != 1:
        raise SystemExit(f'{name}: mutation text found {text.count(original)} times in {filename}')
    p.write_text(text.replace(original, replacement), encoding='utf8')


def run(cmd, cwd, env=None, timeout=300):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return 'TIMEOUT', ''


def main():
    py = sys.executable
    rows = []
    for name, filename, original, replacement in M:
        with tempfile.TemporaryDirectory(prefix='as14-review-') as tmp:
            dest = Path(tmp)
            for f in FILES:
                shutil.copy2(CUTS / f, dest / f)
            apply(dest, filename, original, replacement, name)
            for f2, o2, r2 in SECOND_ORDER.get(name, []):
                apply(dest, f2, o2, r2, name)
            # syntax / import sanity: a mutant that does not import is not a valid mutant
            rc_imp, log_imp = run([py, '-c', 'import h2_oracle, independent_validator'], dest)
            if rc_imp != 0:
                rows.append({'mutant': name, 'invalid': log_imp[-200:]})
                continue
            rc_a, log_a = run([py, '-m', 'unittest', 'test_h2_oracle'], dest)
            fails_a = [ln.split(' ')[1] for ln in log_a.splitlines()
                       if ln.startswith('FAIL:') or ln.startswith('ERROR:')]
            rc_v, log_v = run([py, '-c', WRAP_VERIFY, str(dest)], str(CUTS))
            env = dict(os.environ, AS14_CUTS=str(dest))
            rc_m, _ = run([py, str(HERE / 'review_micro.py')], str(HERE), env)
            rc_b, _ = run([py, str(HERE / 'review_budget.py'),
                           'Budget.test_indivisible_reach_overshoot_is_unknown',
                           'Budget.test_indivisible_graph_build_overshoot_is_unknown',
                           'Budget.test_every_clock_crossing_point_yields_unknown_or_in_budget',
                           'Budget.test_classify_h2_exhausted_budget_never_enters_bhat'], str(HERE), env)
            rc_x, log_x = run([py, str(HERE / 'review_audit.py')], str(HERE), env)
            audit_killed = rc_x != 0 or 'failures 0' not in log_x
            rows.append({'mutant': name,
                         'author_suite_killed': rc_a != 0, 'author_failing_tests': fails_a[:6],
                         'author_verify_killed': rc_v != 0,
                         'review_micro_killed': rc_m != 0, 'review_budget_killed': rc_b != 0,
                         'review_audit_killed': audit_killed})
    print(json.dumps(rows, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
