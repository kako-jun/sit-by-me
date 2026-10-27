"""Typed cells must retain JSON meanings and reject ambiguous paths."""
import unittest

from tests.ledger_test_support import TOOLS
import ledger_flat as F


class TypedLedgerTests(unittest.TestCase):
    def test_json_semantics_round_trip(self):
        expected = {"日本語": {"flag": True, "other": False, "nothing": None},
                    "numbers": [0, -4, 1.25], "empty": [[], {}, ""],
                    "dot.key": {"bracket[key]": "pipes | and\nnewlines"}}
        self.assertEqual(F.unflatten(F.flatten(expected)), expected)

    def test_unknown_type_is_rejected(self):
        with self.assertRaises(ValueError):
            F.unflatten([("x", "7", "NMBR")])

    def test_numbers_must_be_finite_json_numbers(self):
        for value in ("{}", "[]", "true", "false", "null", "NaN", "Infinity", "-Infinity", '"1"'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                F.unflatten([("x", value, "数")])

    def test_boolean_spelling_is_exact(self):
        for value in ("TRUE", "False", "1", "", "yes"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                F.unflatten([("x", value, "真偽")])

    def test_empty_types_cannot_hide_values(self):
        for kind in ("空", "空配列", "空辞書"):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                F.unflatten([("x", "discarded", kind)])

    def test_duplicate_and_alias_paths_are_rejected(self):
        for other in ("x", '["x"]'):
            with self.subTest(other=other), self.assertRaises(ValueError):
                F.unflatten([("x", "one", "文"), (other, "two", "文")])

    def test_parent_child_paths_are_rejected_in_both_orders(self):
        values = [("x", "", "空辞書"), ("x.y", "1", "数")]
        for order in (values, list(reversed(values))):
            with self.subTest(order=order), self.assertRaises(ValueError):
                F.unflatten(order)

    def test_sparse_negative_or_malformed_indices_are_rejected(self):
        for path in ("x[2]", "x[-1]", "x[]", "x[1.5]", "x[", "x..y", "x]", ".x"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                F.unflatten([(path, "1", "数")])

    def test_dict_and_list_paths_cannot_share_a_container(self):
        for values in ([('x.a', 'one', '文'), ('x[0]', 'two', '文')],
                       [('x[0]', 'one', '文'), ('x.a', 'two', '文')]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                F.unflatten(values)
