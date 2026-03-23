import unittest
import os
from service import Service


def get_flow_path(filename="flow.json"):
    return os.path.join(os.path.dirname(__file__), f"../{filename}")


class TestCreateUser(unittest.TestCase):

    def setUp(self):
        self.service = Service(get_flow_path())

    def test_create_user_returns_string_id(self):
        user_id = self.service.create_user("a@example.com")
        self.assertIsInstance(user_id, str)

    def test_create_user_ids_are_unique(self):
        id1 = self.service.create_user("a@example.com")
        id2 = self.service.create_user("b@example.com")
        self.assertNotEqual(id1, id2)

    def test_created_user_exists_in_store(self):
        user_id = self.service.create_user("a@example.com")
        user = self.service.store.get_user(user_id)
        self.assertIsNotNone(user)

    def test_created_user_starts_at_initial_step(self):
        user_id = self.service.create_user("a@example.com")
        user = self.service.store.get_user(user_id)
        self.assertEqual(user.current_step, "PERSONAL_DETAILS")

    def test_created_user_status_is_in_progress(self):
        user_id = self.service.create_user("a@example.com")
        self.assertEqual(self.service.get_user_status(user_id), "IN_PROGRESS")

    def test_same_email_creates_multiple_users(self):
        id1 = self.service.create_user("same@example.com")
        id2 = self.service.create_user("same@example.com")
        self.assertNotEqual(id1, id2)


class TestGetUserStatus(unittest.TestCase):

    def setUp(self):
        self.service = Service(get_flow_path())
        self.user_id = self.service.create_user("a@example.com")

    def test_initial_status_in_progress(self):
        self.assertEqual(self.service.get_user_status(self.user_id), "IN_PROGRESS")

    def test_status_after_rejection(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 60})
        self.assertEqual(self.service.get_user_status(self.user_id), "failed")

    def test_status_nonexistent_user_raises(self):
        with self.assertRaises(ValueError):
            self.service.get_user_status("nonexistent")


class TestGetUserCurrentState(unittest.TestCase):

    def setUp(self):
        self.service = Service(get_flow_path())
        self.user_id = self.service.create_user("a@example.com")

    def test_initial_state(self):
        state = self.service.get_user_current_state(self.user_id)
        self.assertEqual(state["current_step"], "PERSONAL_DETAILS")
        self.assertEqual(state["current_task"], "submit_details")

    def test_state_after_first_step(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        state = self.service.get_user_current_state(self.user_id)
        self.assertEqual(state["current_step"], "IQ_TEST")
        self.assertEqual(state["current_task"], "complete_iq_test")

    def test_state_after_passing_iq(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 80})
        state = self.service.get_user_current_state(self.user_id)
        self.assertEqual(state["current_step"], "INTERVIEW")
        self.assertEqual(state["current_task"], "schedule_interview")

    def test_state_mid_step_multi_task(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 80})
        self.service.submit_task("INTERVIEW", "schedule_interview", self.user_id, {})
        state = self.service.get_user_current_state(self.user_id)
        self.assertEqual(state["current_step"], "INTERVIEW")
        self.assertEqual(state["current_task"], "perform_interview")

    def test_state_returns_none_after_process_ends(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 60})
        state = self.service.get_user_current_state(self.user_id)
        self.assertIsNone(state)

    def test_state_nonexistent_user_raises(self):
        with self.assertRaises(ValueError):
            self.service.get_user_current_state("nonexistent")


class TestSubmitTask(unittest.TestCase):

    def setUp(self):
        self.service = Service(get_flow_path())
        self.user_id = self.service.create_user("a@example.com")

    def test_submit_task_nonexistent_user_raises(self):
        with self.assertRaises(ValueError):
            self.service.submit_task("PERSONAL_DETAILS", "submit_details", "nonexistent", {})

    def test_submit_task_wrong_step_raises(self):
        with self.assertRaises(ValueError):
            self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {})

    def test_submit_task_wrong_task_raises(self):
        with self.assertRaises(ValueError):
            self.service.submit_task("PERSONAL_DETAILS", "nonexistent_task", self.user_id, {})

    def test_submit_task_after_process_ended_raises(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 10})
        with self.assertRaises(ValueError):
            self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})

    def test_submit_task_advances_step_on_completion(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        user = self.service.store.get_user(self.user_id)
        self.assertEqual(user.current_step, "IQ_TEST")

    def test_submit_task_does_not_advance_mid_step(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 80})
        self.service.submit_task("INTERVIEW", "schedule_interview", self.user_id, {})
        user = self.service.store.get_user(self.user_id)
        self.assertEqual(user.current_step, "INTERVIEW")

    def test_submit_task_records_outcome(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        user = self.service.store.get_user(self.user_id)
        self.assertIn("submit_details", user.completed_tasks_by_step["PERSONAL_DETAILS"])

    def test_failed_iq_ends_process(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 50})
        user = self.service.store.get_user(self.user_id)
        self.assertIsNone(user.current_step)
        self.assertEqual(user.status, "failed")

    def test_passed_iq_moves_to_interview(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 76})
        user = self.service.store.get_user(self.user_id)
        self.assertEqual(user.current_step, "INTERVIEW")

    def test_failed_interview_ends_process(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 80})
        self.service.submit_task("INTERVIEW", "schedule_interview", self.user_id, {})
        self.service.submit_task("INTERVIEW", "perform_interview", self.user_id, {"decision": "failed_interview"})
        user = self.service.store.get_user(self.user_id)
        self.assertIsNone(user.current_step)
        self.assertEqual(user.status, "failed")


class TestGetEntireFlow(unittest.TestCase):

    def setUp(self):
        self.service = Service(get_flow_path())
        self.user_id = self.service.create_user("a@example.com")

    def test_flow_contains_current_step(self):
        flow = self.service.get_entire_flow(self.user_id)
        step_ids = [s["step_id"] for s in flow]
        self.assertIn("PERSONAL_DETAILS", step_ids)

    def test_flow_contains_future_steps(self):
        flow = self.service.get_entire_flow(self.user_id)
        step_ids = [s["step_id"] for s in flow]
        self.assertIn("IQ_TEST", step_ids)
        self.assertIn("INTERVIEW", step_ids)

    def test_completed_step_marked_correctly(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        flow = self.service.get_entire_flow(self.user_id)
        personal_details = next(s for s in flow if s["step_id"] == "PERSONAL_DETAILS")
        self.assertTrue(personal_details["is_completed"])

    def test_current_step_not_marked_completed(self):
        flow = self.service.get_entire_flow(self.user_id)
        personal_details = next(s for s in flow if s["step_id"] == "PERSONAL_DETAILS")
        self.assertFalse(personal_details["is_completed"])

    def test_future_steps_not_marked_completed(self):
        flow = self.service.get_entire_flow(self.user_id)
        iq_test = next(s for s in flow if s["step_id"] == "IQ_TEST")
        self.assertFalse(iq_test["is_completed"])

    def test_tasks_in_current_step_not_completed(self):
        flow = self.service.get_entire_flow(self.user_id)
        personal_details = next(s for s in flow if s["step_id"] == "PERSONAL_DETAILS")
        task = personal_details["tasks"][0]
        self.assertFalse(task["is_completed"])

    def test_completed_task_marked_in_flow(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 80})
        self.service.submit_task("INTERVIEW", "schedule_interview", self.user_id, {})
        flow = self.service.get_entire_flow(self.user_id)
        interview = next(s for s in flow if s["step_id"] == "INTERVIEW")
        schedule_task = next(t for t in interview["tasks"] if t["task_id"] == "schedule_interview")
        self.assertTrue(schedule_task["is_completed"])

    def test_flow_nonexistent_user_raises(self):
        with self.assertRaises(ValueError):
            self.service.get_entire_flow("nonexistent")

    def test_flow_after_rejection_no_future_steps(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 10})
        flow = self.service.get_entire_flow(self.user_id)
        step_ids = [s["step_id"] for s in flow]
        self.assertNotIn("INTERVIEW", step_ids)
        self.assertNotIn("SIGN_CONTRACT", step_ids)


class TestHappyPath(unittest.TestCase):
    """End-to-end full acceptance flow"""

    def setUp(self):
        self.service = Service(get_flow_path())
        self.user_id = self.service.create_user("accepted@example.com")

    def test_full_acceptance_flow(self):
        svc = self.service
        uid = self.user_id

        svc.submit_task("PERSONAL_DETAILS", "submit_details", uid, {"email": "accepted@example.com"})
        self.assertEqual(svc.get_user_current_state(uid)["current_step"], "IQ_TEST")

        svc.submit_task("IQ_TEST", "complete_iq_test", uid, {"score": 90})
        self.assertEqual(svc.get_user_current_state(uid)["current_step"], "INTERVIEW")

        svc.submit_task("INTERVIEW", "schedule_interview", uid, {"interview_date": "2025-01-01"})
        self.assertEqual(svc.get_user_current_state(uid)["current_task"], "perform_interview")

        svc.submit_task("INTERVIEW", "perform_interview", uid, {"decision": "passed_interview"})
        self.assertEqual(svc.get_user_current_state(uid)["current_step"], "SIGN_CONTRACT")

        svc.submit_task("SIGN_CONTRACT", "upload_id", uid, {"passport_number": "123"})
        self.assertEqual(svc.get_user_current_state(uid)["current_task"], "sign_contract")

        svc.submit_task("SIGN_CONTRACT", "sign_contract", uid, {})
        self.assertEqual(svc.get_user_current_state(uid)["current_step"], "PAYMENT")

        svc.submit_task("PAYMENT", "make_payment", uid, {"payment_id": "pay-1"})
        self.assertEqual(svc.get_user_current_state(uid)["current_step"], "JOIN_SLACK")

        svc.submit_task("JOIN_SLACK", "join_slack_channel", uid, {"email": "accepted@example.com"})

        self.assertIsNone(svc.get_user_current_state(uid))
        self.assertEqual(svc.get_user_status(uid), "completed")


class TestCreativePMFlow(unittest.TestCase):
    """Tests using flow_creative_PM.json (second chance IQ test)"""

    def setUp(self):
        self.service = Service(get_flow_path("flow_creative_PM.json"))
        self.user_id = self.service.create_user("creative@example.com")

    def test_medium_score_moves_to_second_chance(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 65})
        state = self.service.get_user_current_state(self.user_id)
        self.assertEqual(state["current_step"], "IQ_SECOND_CHANCE")

    def test_second_chance_pass_moves_to_interview(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 65})
        self.service.submit_task("IQ_SECOND_CHANCE", "complete_second_test", self.user_id, {"score": 80})
        state = self.service.get_user_current_state(self.user_id)
        self.assertEqual(state["current_step"], "INTERVIEW")

    def test_second_chance_fail_rejects_user(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 65})
        self.service.submit_task("IQ_SECOND_CHANCE", "complete_second_test", self.user_id, {"score": 50})
        self.assertIsNone(self.service.get_user_current_state(self.user_id))
        self.assertEqual(self.service.get_user_status(self.user_id), "failed")

    def test_high_score_skips_second_chance(self):
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", self.user_id, {})
        self.service.submit_task("IQ_TEST", "complete_iq_test", self.user_id, {"score": 90})
        state = self.service.get_user_current_state(self.user_id)
        self.assertEqual(state["current_step"], "INTERVIEW")

    def test_second_chance_not_in_flow_for_high_score_user(self):
        flow = self.service.get_entire_flow(self.user_id)
        step_ids = [s["step_id"] for s in flow]
        self.assertNotIn("IQ_SECOND_CHANCE", step_ids)


if __name__ == "__main__":
    unittest.main()
