import unittest
from user import User


class TestUser(unittest.TestCase):

    def setUp(self):
        self.user = User("user-123", "test@example.com", "PERSONAL_DETAILS")

    # --- __init__ ---

    def test_initial_status_is_in_progress(self):
        self.assertEqual(self.user.status, "IN_PROGRESS")

    def test_initial_current_step(self):
        self.assertEqual(self.user.current_step, "PERSONAL_DETAILS")

    def test_initial_completed_steps_empty(self):
        self.assertEqual(self.user.completed_steps, [])

    def test_initial_completed_tasks_empty(self):
        self.assertEqual(self.user.completed_tasks_by_step, {})

    # --- record_task_result ---

    def test_record_task_result_new_step(self):
        self.user.record_task_result("PERSONAL_DETAILS", "submit_details", "completed")
        self.assertIn("PERSONAL_DETAILS", self.user.completed_tasks_by_step)
        self.assertEqual(
            self.user.completed_tasks_by_step["PERSONAL_DETAILS"]["submit_details"],
            "completed"
        )

    def test_record_task_result_multiple_tasks_same_step(self):
        self.user.record_task_result("INTERVIEW", "schedule_interview", "completed")
        self.user.record_task_result("INTERVIEW", "perform_interview", "passed")
        self.assertEqual(len(self.user.completed_tasks_by_step["INTERVIEW"]), 2)

    def test_record_task_result_overwrite(self):
        self.user.record_task_result("IQ_TEST", "complete_iq_test", "failed")
        self.user.record_task_result("IQ_TEST", "complete_iq_test", "passed")
        self.assertEqual(
            self.user.completed_tasks_by_step["IQ_TEST"]["complete_iq_test"],
            "passed"
        )

    # --- move_to_step ---

    def test_move_to_step_updates_current_step(self):
        self.user.move_to_step("IQ_TEST")
        self.assertEqual(self.user.current_step, "IQ_TEST")

    def test_move_to_step_adds_to_completed(self):
        self.user.move_to_step("IQ_TEST")
        self.assertIn("PERSONAL_DETAILS", self.user.completed_steps)

    def test_move_to_step_multiple_times(self):
        self.user.move_to_step("IQ_TEST")
        self.user.move_to_step("INTERVIEW")
        self.assertEqual(self.user.completed_steps, ["PERSONAL_DETAILS", "IQ_TEST"])
        self.assertEqual(self.user.current_step, "INTERVIEW")

    # --- finish_process ---

    def test_finish_process_accepted(self):
        self.user.finish_process("accepted")
        self.assertEqual(self.user.status, "accepted")
        self.assertIsNone(self.user.current_step)

    def test_finish_process_rejected(self):
        self.user.finish_process("rejected")
        self.assertEqual(self.user.status, "rejected")
        self.assertIsNone(self.user.current_step)

    def test_finish_process_clears_current_step(self):
        self.user.finish_process("accepted")
        self.assertIsNone(self.user.current_step)

    # --- combined flow scenario ---

    def test_full_happy_path_state(self):
        self.user.record_task_result("PERSONAL_DETAILS", "submit_details", "completed")
        self.user.move_to_step("IQ_TEST")
        self.user.record_task_result("IQ_TEST", "complete_iq_test", "passed")
        self.user.move_to_step("INTERVIEW")

        self.assertEqual(self.user.current_step, "INTERVIEW")
        self.assertEqual(self.user.completed_steps, ["PERSONAL_DETAILS", "IQ_TEST"])
        self.assertEqual(self.user.status, "IN_PROGRESS")

    def test_rejection_path_state(self):
        self.user.record_task_result("PERSONAL_DETAILS", "submit_details", "completed")
        self.user.move_to_step("IQ_TEST")
        self.user.record_task_result("IQ_TEST", "complete_iq_test", "failed")
        self.user.finish_process("failed")

        self.assertIsNone(self.user.current_step)
        self.assertEqual(self.user.status, "failed")


if __name__ == "__main__":
    unittest.main()