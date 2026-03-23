import unittest
from conditions import MatchCondition, ThresholdCondition, RangeCondition


class TestMatchCondition(unittest.TestCase):

    def setUp(self):
        self.condition = MatchCondition("decision", "passed_interview")

    def test_exact_match_passes(self):
        self.assertEqual(self.condition.check({"decision": "passed_interview"}), "passed")

    def test_wrong_value_fails(self):
        self.assertEqual(self.condition.check({"decision": "failed_interview"}), "failed")

    def test_missing_field_fails(self):
        self.assertEqual(self.condition.check({}), "failed")

    def test_case_sensitive(self):
        self.assertEqual(self.condition.check({"decision": "Passed_Interview"}), "failed")

    def test_empty_string_fails(self):
        self.assertEqual(self.condition.check({"decision": ""}), "failed")


class TestThresholdCondition(unittest.TestCase):

    def setUp(self):
        self.condition = ThresholdCondition("score", 75)

    def test_above_threshold_passes(self):
        self.assertEqual(self.condition.check({"score": 76}), "passed")

    def test_exactly_at_threshold_fails(self):
        self.assertEqual(self.condition.check({"score": 75}), "failed")

    def test_below_threshold_fails(self):
        self.assertEqual(self.condition.check({"score": 50}), "failed")

    def test_missing_field_defaults_to_zero_and_fails(self):
        self.assertEqual(self.condition.check({}), "failed")

    def test_zero_threshold(self):
        condition = ThresholdCondition("score", 0)
        self.assertEqual(condition.check({"score": 1}), "passed")
        self.assertEqual(condition.check({"score": 0}), "failed")

    def test_high_score_passes(self):
        self.assertEqual(self.condition.check({"score": 100}), "passed")


class TestRangeCondition(unittest.TestCase):

    def setUp(self):
        self.rules = [
            {"min": 76, "max": 100, "outcome": "passed"},
            {"min": 60, "max": 75, "outcome": "medium_score"},
            {"min": 0,  "max": 59, "outcome": "failed"},
        ]
        self.condition = RangeCondition("score", self.rules)

    def test_high_range_returns_passed(self):
        self.assertEqual(self.condition.check({"score": 90}), "passed")

    def test_medium_range_returns_medium_score(self):
        self.assertEqual(self.condition.check({"score": 65}), "medium_score")

    def test_low_range_returns_failed(self):
        self.assertEqual(self.condition.check({"score": 30}), "failed")

    def test_lower_boundary_of_range(self):
        self.assertEqual(self.condition.check({"score": 76}), "passed")
        self.assertEqual(self.condition.check({"score": 60}), "medium_score")
        self.assertEqual(self.condition.check({"score": 0}), "failed")

    def test_upper_boundary_of_range(self):
        self.assertEqual(self.condition.check({"score": 100}), "passed")
        self.assertEqual(self.condition.check({"score": 75}), "medium_score")
        self.assertEqual(self.condition.check({"score": 59}), "failed")

    def test_value_outside_all_ranges_returns_failed(self):
        self.assertEqual(self.condition.check({"score": 150}), "failed")

    def test_missing_field_defaults_to_zero(self):
        self.assertEqual(self.condition.check({}), "failed")

    def test_single_rule(self):
        condition = RangeCondition("score", [{"min": 50, "max": 100, "outcome": "passed"}])
        self.assertEqual(condition.check({"score": 75}), "passed")
        self.assertEqual(condition.check({"score": 49}), "failed")


if __name__ == "__main__":
    unittest.main()
