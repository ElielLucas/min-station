"""Testes derivados de AS03-01/02/05; sem necessidade de solver."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import os
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from as02_model_a import Instance, compile_a
from as03_grouping import (
    NotApplicable, instance_fingerprint, is_nested, partition_two, refine_four,
)


def case(m=6):
    vertices = tuple(f'v{i}' for i in range(9))
    arcs = tuple((vertices[i], vertices[j]) for i in range(9)
                 for j in range(9) if i != j and (i + j) % 3 != 0)
    return Instance(vertices, vertices[:m], vertices[3:3+m], arcs, 2)


class TestAS03Grouping(unittest.TestCase):
    def test_as03_01_two_groups_stable_when_shuffling_all_inputs(self):
        instance = case(6)
        shuffled = Instance(tuple(reversed(instance.V)), tuple(reversed(instance.S)),
                            tuple(reversed(instance.T)), tuple(reversed(instance.A_r)), 2)
        for policy in ('balanced', 'reachability_degree'):
            with self.subTest(policy=policy):
                a = partition_two(instance, policy=policy, seed=123)
                b = partition_two(shuffled, policy=policy, seed=123)
                self.assertEqual(a.blocks, b.blocks)
                self.assertEqual(a.partition_hash, b.partition_hash)
                self.assertEqual(a.instance_hash, b.instance_hash)

    def test_as03_01_two_groups_are_complete_and_balanced(self):
        for m in (2, 3, 4, 5, 6):
            for policy in ('balanced', 'reachability_degree'):
                a = partition_two(case(m), policy=policy)
                self.assertEqual(len(a.blocks), 2)
                self.assertEqual(set().union(*map(set, a.blocks)), set(case(m).S))
                self.assertLessEqual(abs(len(a.blocks[0])-len(a.blocks[1])), 1)
                self.assertFalse(set(a.blocks[0]) & set(a.blocks[1]))

    def test_as03_01_fingerprint_sensitive_to_ar_and_r(self):
        instance = case()
        different_ar = replace(instance, A_r=instance.A_r[:-1])
        different_r = replace(instance, r=3)
        self.assertNotEqual(instance_fingerprint(instance), instance_fingerprint(different_ar))
        self.assertNotEqual(instance_fingerprint(instance), instance_fingerprint(different_r))

    def test_as03_01_no_python_hash_dependency_in_public_hash(self):
        self.assertEqual(len(partition_two(case()).partition_hash), 64)

    def test_as03_02_four_is_nested_and_parent_provenance_is_retained(self):
        instance = case()
        for policy in ('balanced', 'reachability_degree'):
            with self.subTest(policy=policy):
                a2 = partition_two(instance, policy=policy, seed=42)
                a4 = refine_four(instance, a2, authorized=True)
                self.assertEqual(len(a4.blocks), 4)
                self.assertTrue(is_nested(a2.blocks, a4.blocks))
                self.assertEqual(a4.parent_hash, a2.partition_hash)
                self.assertEqual(set().union(*map(set, a4.blocks)), set(instance.S))

    def test_as03_02_reordering_parents_does_not_change_children(self):
        instance = case(6)
        a2 = partition_two(instance)
        reordered = replace(a2, blocks=tuple(reversed(a2.blocks)))
        a4 = refine_four(instance, a2, authorized=True)
        b4 = refine_four(instance, reordered, authorized=True)
        self.assertEqual(a4.blocks, b4.blocks)
        self.assertEqual(a4.partition_hash, b4.partition_hash)

    def test_as03_02_no_four_groups_when_m_below_four(self):
        for m in (2, 3):
            instance = case(m)
            with self.assertRaises(NotApplicable):
                refine_four(instance, partition_two(instance), authorized=True)

    def test_as03_02_four_requires_explicit_authorization(self):
        instance = case()
        with self.assertRaises(PermissionError):
            refine_four(instance, partition_two(instance))

    def test_as03_02_rejects_foreign_parent(self):
        parent = partition_two(case())
        with self.assertRaises(ValueError):
            refine_four(replace(case(), r=3), parent, authorized=True)

    def test_as03_02_rejects_tampered_parent_hash(self):
        inst = case()
        parent = partition_two(inst)
        with self.assertRaises(ValueError):
            refine_four(inst, replace(parent, partition_hash='0' * 64), authorized=True)

    def test_as03_01_different_python_hash_seeds(self):
        root = Path(__file__).resolve().parent
        code = (
            "from as02_model_a import Instance; "
            "from as03_grouping import partition_two; "
            "i=Instance(('a','b','c','d'),('a','b','c','d'),"
            "('a','b','c','d'),(('a','b'),('b','c'),('c','d')),1); "
            "print(partition_two(i,seed=20).partition_hash)"
        )
        outputs = []
        for value in ('1', '213'):
            env = dict(os.environ, PYTHONHASHSEED=value,
                       PYTHONPATH=str(root))
            outputs.append(subprocess.check_output([sys.executable, '-c', code],
                                                   env=env, text=True).strip())
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(len(outputs[0]), 64)

    def test_as03_02_nonnested_candidate_detected(self):
        self.assertFalse(is_nested((('a', 'b'), ('c', 'd')),
                                   (('a', 'c'), ('b',), ('d',), ('x',))))

    def test_as03_05_only_structural_arguments_accepted(self):
        instance = case()
        with self.assertRaises(TypeError):
            partition_two(instance, objective=8)
        with self.assertRaises(ValueError):
            partition_two(instance, policy='optimized_on_evaluation')
        with self.assertRaises(ValueError):
            partition_two(instance, seed=-1)

    def test_as03_05_model_accepts_generated_two_and_four(self):
        instance = case(6)
        a2 = partition_two(instance)
        a4 = refine_four(instance, a2, authorized=True)
        for groups in (a2.blocks, a4.blocks):
            compiled = compile_a(instance, groups, relax=True)
            self.assertEqual(compiled.families['A1'], len(groups)*len(instance.V))
            self.assertEqual(sum(1 for x in compiled.variables if x.name.startswith('y[')), len(instance.V))


if __name__ == '__main__':
    unittest.main()
