import unittest
from task import Task
from conditions import MatchCondition, ThresholdCondition, RangeCondition


class TestTask(unittest.TestCase):

    # --- evaluate: no condition ---

    def test_no_condition_returns_completed(self):
        task = Task("upload_id", "Upload ID")
        self.assertEqual(task.evaluate({}), "completed")

    def test_no_condition_ignores_payload(self):
        task = Task("sign_contract", "Sign Contract")
        self.assertEqual(task.evaluate({"score": 99, "decision": "failed"}), "completed")

    # --- evaluate: ThresholdCondition ---

    def test_threshold_above_passes(self):
        task = Task("iq_test", "IQ Test", ThresholdCondition("score", 75))
        self.assertEqual(task.evaluate({"score": 80}), "passed")

    def test_threshold_exactly_at_threshold_fails(self):
        task = Task("iq_test", "IQ Test", ThresholdCondition("score", 75))
        self.assertEqual(task.evaluate({"score": 75}), "failed")

    def test_threshold_below_fails(self):
        task = Task("iq_test", "IQ Test", ThresholdCondition("score", 75))
        self.assertEqual(task.evaluate({"score": 60}), "failed")

    def test_threshold_missing_field_fails(self):
        task = Task("iq_test", "IQ Test", ThresholdCondition("score", 75))
        self.assertEqual(task.evaluate({}), "failed")

    # --- evaluate: MatchCondition ---

    def test_match_correct_value_passes(self):
        task = Task("perform_interview", "Perform Interview", MatchCondition("decision", "passed_interview"))
        self.assertEqual(task.evaluate({"decision": "passed_interview"}), "passed")

    def test_match_wrong_value_fails(self):
        task = Task("perform_interview", "Perform Interview", MatchCondition("decision", "passed_interview"))
        self.assertEqual(task.evaluate({"decision": "failed_interview"}), "failed")

    def test_match_missing_field_fails(self):
        task = Task("perform_interview", "Perform Interview", MatchCondition("decision", "passed_interview"))
        self.assertEqual(task.evaluate({}), "failed")

    # --- evaluate: RangeCondition ---

    def test_range_returns_correct_outcome(self):
        rules = [
            {"min": 76, "max": 100, "outcome": "passed"},
            {"min": 60, "max": 75, "outcome": "medium_score"},
            {"min": 0, "max": 59, "outcome": "failed"},
        ]
        task = Task("iq_test", "IQ Test", RangeCondition("score", rules))
        self.assertEqual(task.evaluate({"score": 90}), "passed")
        self.assertEqual(task.evaluate({"score": 65}), "medium_score")
        self.assertEqual(task.evaluate({"score": 30}), "failed")

    def test_range_boundary_values(self):
        rules = [
            {"min": 76, "max": 100, "outcome": "passed"},
            {"min": 60, "max": 75, "outcome": "medium_score"},
        ]
        task = Task("iq_test", "IQ Test", RangeCondition("score", rules))
        self.assertEqual(task.evaluate({"score": 76}), "passed")
        self.assertEqual(task.evaluate({"score": 75}), "medium_score")
        self.assertEqual(task.evaluate({"score": 60}), "medium_score")

    def test_range_out_of_all_ranges_returns_failed(self):
        rules = [
            {"min": 76, "max": 100, "outcome": "passed"},
        ]
        task = Task("iq_test", "IQ Test", RangeCondition("score", rules))
        self.assertEqual(task.evaluate({"score": 50}), "failed")

    # --- task attributes ---

    def test_task_id_and_display_name(self):
        task = Task("submit_details", "Submit Details")
        self.assertEqual(task.id, "submit_details")
        self.assertEqual(task.display_name, "Submit Details")

    def test_task_condition_stored(self):
        condition = ThresholdCondition("score", 75)
        task = Task("iq_test", "IQ Test", condition)
        self.assertIs(task.condition, condition)

    def test_task_no_condition_is_none(self):
        task = Task("submit_details", "Submit Details")
        self.assertIsNone(task.condition)


if __name__ == "__main__":
    unittest.main()
