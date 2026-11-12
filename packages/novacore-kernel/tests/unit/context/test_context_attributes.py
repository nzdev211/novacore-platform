import unittest
from dataclasses import FrozenInstanceError

from novacore.kernel.context import ContextAttributes


class ContextAttributesTests(unittest.TestCase):
    def test_accepts_empty_mapping(self):
        self.assertEqual(dict(ContextAttributes(values={}).values), {})

    def test_recursively_freezes_mappings_and_sequences(self):
        source = {"title": "Studio", "nested": {"tone": "professional"}, "tags": ["a", "b"]}
        attributes = ContextAttributes(values=source)
        source["title"] = "changed"
        source["nested"]["tone"] = "changed"
        source["tags"].append("c")
        self.assertEqual(attributes.values["title"], "Studio")
        self.assertEqual(attributes.values["nested"]["tone"], "professional")
        self.assertEqual(attributes.values["tags"], ("a", "b"))
        with self.assertRaises(TypeError):
            attributes.values["new"] = "value"
        with self.assertRaises(TypeError):
            attributes.values["nested"]["tone"] = "changed"

    def test_freezes_sets(self):
        self.assertEqual(
            ContextAttributes(values={"labels": {"a", "b"}}).values["labels"],
            frozenset({"a", "b"}),
        )

    def test_rejects_non_mapping_root(self):
        with self.assertRaises(TypeError):
            ContextAttributes(values=["not", "mapping"])

    def test_rejects_invalid_keys(self):
        for key in ("", " ", 1, None):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    ContextAttributes(values={key: "value"})

    def test_rejects_unsupported_values(self):
        with self.assertRaises(TypeError):
            ContextAttributes(values={"object": object()})

    def test_rejects_cycles(self):
        cyclic = []
        cyclic.append(cyclic)
        with self.assertRaises(ValueError):
            ContextAttributes(values={"cycle": cyclic})

    def test_equal_values_have_equal_hashes(self):
        first = ContextAttributes(values={"a": 1, "b": {"c": [2, 3]}})
        second = ContextAttributes(values={"b": {"c": [2, 3]}, "a": 1})
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))

    def test_inequality_for_different_values(self):
        self.assertNotEqual(ContextAttributes(values={"a": 1}), ContextAttributes(values={"a": 2}))

    def test_dataclass_is_frozen(self):
        attributes = ContextAttributes(values={})
        with self.assertRaises(FrozenInstanceError):
            attributes.values = {"changed": True}


if __name__ == "__main__":
    unittest.main()

