import unittest

from novacore.kernel.activity import ActivityStatus


class ActivityStatusTests(unittest.TestCase):
    def test_expected_status_values(self):
        self.assertEqual(ActivityStatus.DRAFT.value, "draft")
        self.assertEqual(ActivityStatus.ACTIVE.value, "active")
        self.assertEqual(ActivityStatus.COMPLETED.value, "completed")
        self.assertEqual(ActivityStatus.CANCELLED.value, "cancelled")

    def test_status_is_string_compatible(self):
        self.assertEqual(ActivityStatus.ACTIVE, "active")

    def test_statuses_are_distinct(self):
        self.assertEqual(len(ActivityStatus), 4)


if __name__ == "__main__":
    unittest.main()

