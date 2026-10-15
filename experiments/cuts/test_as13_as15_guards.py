"""AS15 entry prerequisites: make AS13's physical-validity guards observable.

These tests intentionally inject incorrect certificates into the existing
verifier, and require the exact assertion from each independent safety gate.
In particular, the corrupted HL projection keeps beta unchanged; checking
only beta must NOT be sufficient to pass the projection identity contract.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

import verify_as13_foundations as as13


class AS13AS15EntryGuards(unittest.TestCase):
    def test_as15_entry_invalid_full_h2_must_be_rejected(self):
        original = as13.h2_for_support
        injected = []

        def bad_full_h2(*args, **kwargs):
            row = original(*args, **kwargs)
            if (row is not None and tuple(args[0]) == ('a',)
                    and frozenset(args[5]) == {'b'}
                    and kwargs.get('partial_insufficient') is None):
                coefs, rhs, B = row
                injected.append(True)
                return coefs, rhs + 1, B  # excludes the feasible installation {b}
            return row

        with patch.object(as13, 'h2_for_support', side_effect=bad_full_h2):
            with self.assertRaisesRegex(AssertionError, 'H2 excludes physical'):
                as13.check_exhaustive_small_cuts(as13.small_controls())
        self.assertEqual(len(injected), 1, 'the invalid full H2 must be injected')

    def test_as15_entry_invalid_partial_h2_must_be_rejected(self):
        original = as13.h2_for_support
        injected = []

        def bad_partial_h2(*args, **kwargs):
            row = original(*args, **kwargs)
            if (row is not None and tuple(args[0]) == ('a',)
                    and frozenset(args[5]) == {'b'}
                    and kwargs.get('partial_insufficient') == {'b'}):
                coefs, rhs, B = row
                injected.append(True)
                return coefs, rhs + 1, B  # excludes the feasible installation {b}
            return row

        with patch.object(as13, 'h2_for_support', side_effect=bad_partial_h2):
            with self.assertRaisesRegex(AssertionError, 'H2 partial excludes'):
                as13.check_exhaustive_small_cuts(as13.small_controls())
        self.assertEqual(len(injected), 1, 'the invalid partial H2 must be injected')

    def test_as15_entry_hl_projection_identity_not_redundant_with_beta(self):
        original = as13.hl_beta_from_patterns
        injected = []

        def drop_nonminimal_feasible_pattern(patterns, alpha):
            # Control a-b-c with R=V: {b}, {a,b}, {b,c}, {a,b,c}
            # are all feasible. Drop the full set while retaining {b},
            # so beta remains 2. Only the projection identity detects it.
            if set(alpha) == {'a', 'b', 'c'}:
                full = {'a', 'b', 'c'}
                if full in patterns and {'b'} in patterns:
                    patterns.remove(full)
                    injected.append(True)
            return original(patterns, alpha)

        with patch.object(as13, 'hl_beta_from_patterns',
                          side_effect=drop_nonminimal_feasible_pattern):
            with self.assertRaisesRegex(AssertionError,
                                        'HL projection identity fails'):
                as13.check_exhaustive_small_cuts(as13.small_controls())
        self.assertEqual(len(injected), 1, 'the projection omission must be injected')


if __name__ == '__main__':
    unittest.main()
