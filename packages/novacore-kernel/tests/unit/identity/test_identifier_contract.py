import unittest
from dataclasses import FrozenInstanceError

from novacore.kernel.identity import (
    ActivityId,
    AssignmentId,
    CapabilityId,
    ContextId,
    ContractId,
    ExecutionId,
    Identifier,
    ObjectiveId,
    PlanningId,
    RequestId,
    TraceId,
    WorkId,
    WorkerId,
)


IDENTIFIER_TYPES = (
    ActivityId,
    ContextId,
    RequestId,
    ObjectiveId,
    PlanningId,
    CapabilityId,
    WorkId,
    WorkerId,
    AssignmentId,
    ContractId,
    ExecutionId,
    TraceId,
)


class IdentifierContractTests(unittest.TestCase):
    def test_each_concrete_identifier_accepts_a_valid_value(self):
        for identifier_type in IDENTIFIER_TYPES:
            with self.subTest(identifier_type=identifier_type.__name__):
                identifier = identifier_type("sample-001")
                self.assertEqual(identifier.value, "sample-001")
                self.assertIsInstance(identifier, Identifier)

    def test_base_identifier_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            Identifier("sample-001")

    def test_non_string_values_are_rejected(self):
        for identifier_type in IDENTIFIER_TYPES:
            for invalid_value in (None, 123, True, b"bytes"):
                with self.subTest(
                    identifier_type=identifier_type.__name__,
                    invalid_value=invalid_value,
                ):
                    with self.assertRaises(TypeError):
                        identifier_type(invalid_value)

    def test_empty_and_whitespace_values_are_rejected(self):
        for identifier_type in IDENTIFIER_TYPES:
            for invalid_value in ("", " ", "\t", "\n", "  \t  "):
                with self.subTest(
                    identifier_type=identifier_type.__name__,
                    invalid_value=repr(invalid_value),
                ):
                    with self.assertRaises(ValueError):
                        identifier_type(invalid_value)

    def test_valid_value_is_preserved_without_normalization(self):
        identifier = ActivityId("  activity-001  ")
        self.assertEqual(identifier.value, "  activity-001  ")
        self.assertEqual(str(identifier), "  activity-001  ")

    def test_identifier_is_immutable(self):
        identifier = ActivityId("activity-001")
        with self.assertRaises(FrozenInstanceError):
            identifier.value = "activity-002"

    def test_same_concrete_type_and_value_are_equal(self):
        first = ActivityId("same")
        second = ActivityId("same")
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))

    def test_different_concrete_types_are_not_equal(self):
        activity_id = ActivityId("same")
        work_id = WorkId("same")
        self.assertNotEqual(activity_id, work_id)

    def test_different_values_are_not_equal(self):
        self.assertNotEqual(ActivityId("one"), ActivityId("two"))

    def test_unrelated_objects_are_not_equal(self):
        self.assertNotEqual(ActivityId("sample"), "sample")

    def test_string_and_repr_are_stable(self):
        identifier = ActivityId("activity-001")
        self.assertEqual(str(identifier), "activity-001")
        self.assertEqual(repr(identifier), "ActivityId('activity-001')")


if __name__ == "__main__":
    unittest.main()

