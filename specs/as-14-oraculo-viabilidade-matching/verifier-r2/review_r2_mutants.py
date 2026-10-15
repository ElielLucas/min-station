"""AS14 R2 review: mutants against the R1 corrections themselves, in isolated temp copies.

Killed = the author's AS14 unit suite (or the R2 adversarial script) fails on the mutant.
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

CACHE_PROBE = ('                # Check again before returning a certified cached result.\n'
               '                probe()\n')
M = [
    ('N01_CACHE_HIT_RETURN_PROBE_REMOVED', 'h2_oracle.py', [(CACHE_PROBE, '')]),
    ('N02_DEADLINE_STRICT_GT', 'h2_oracle.py',
     [('if budget is not None and elapsed() >= budget:', 'if budget is not None and elapsed() > budget:')]),
    ('N03_CACHE_HIT_BOTH_PROBES_REMOVED', 'h2_oracle.py',
     [('            if hit is not None:\n                probe()\n', '            if hit is not None:\n'),
      (CACHE_PROBE, '')]),
    ('N04_CACHE_GET_IGNORES_INSTANCE', 'h2_oracle_cache.py',
     [('        item = self._items.get(key)\n',
       '        item = next((e for (h, a), e in self._items.items() if a == key[1]), None)\n')]),
    ('N05_MONO_ACROSS_INSTANCES', 'h2_oracle_cache.py',
     [('            if other_hash != result.instance_sha256:\n                continue\n', '')]),
    ('N06_CACHE_HIT_STATUS_FLIPPED_TO_INFEASIBLE_ONLY_IF_VIABLE', 'h2_oracle.py',
     [('answer = result(hit.status, hit.matching_size, hit.witness,',
       'answer = result(hit.status, hit.matching_size, hit.witness[:-1] if hit.witness else (),')]),
    ('N07_ELAPSED_FROM_ZERO_NOT_BEGIN', 'h2_oracle.py',
     [('            return max(0., self.clock() - begin)', '            return max(0., self.clock() - 0.0)')]),
    ('N08_FINGERPRINT_TERMINALS_MERGED', 'h2_oracle.py',
     [("'T': [row(x) for x in order_vertices(self.T)],", "'T': [],")]),
    ('N09_FRESH_FINAL_PROBE_MOVED_AFTER_PUT', 'h2_oracle.py',
     [('            probe()\n            self.cache.put(answer)', '            self.cache.put(answer)\n            probe()')]),
]


def apply(dest, filename, pairs, name):
    p = dest / filename
    text = p.read_text(encoding='utf8')
    for o, r in pairs:
        if text.count(o) != 1:
            raise SystemExit(f'{name}: mutation text found {text.count(o)} times')
        text = text.replace(o, r)
    p.write_text(text, encoding='utf8')


def run(cmd, cwd, env=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=600, env=env)
    return p.returncode, p.stdout + p.stderr


def main():
    rows = []
    for name, filename, pairs in M:
        with tempfile.TemporaryDirectory(prefix='as14-r2-') as tmp:
            dest = Path(tmp)
            for f in FILES:
                shutil.copy2(CUTS / f, dest / f)
            apply(dest, filename, pairs, name)
            rc_i, log_i = run([sys.executable, '-c', 'import h2_oracle'], dest)
            if rc_i:
                rows.append({'mutant': name, 'invalid': log_i[-200:]})
                continue
            rc_a, log_a = run([sys.executable, '-m', 'unittest', 'test_h2_oracle'], dest)
            fails = [ln for ln in log_a.splitlines() if ln.startswith(('FAIL:', 'ERROR:'))]
            env = dict(os.environ, AS14_CUTS=str(dest))
            rc_x, log_x = run([sys.executable, str(HERE / 'review_r2_adversarial.py')], str(HERE), env)
            rows.append({'mutant': name, 'author_suite_killed': rc_a != 0,
                         'author_failing_tests': [f.split(' ')[1] for f in fails][:5],
                         'r2_adversarial_killed': rc_x != 0,
                         'r2_first_failure': next((ln for ln in log_x.splitlines() if ln.startswith('(')), '')[:160]})
    print(json.dumps(rows, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
