import unittest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)

class TestCreateUser(unittest.TestCase):

    def test_create_user_returns_200(self):
        response = client.post("/users", json={"email": "a@example.com"})
        self.assertEqual(response.status_code, 200)

    def test_create_user_returns_user_id(self):
        response = client.post("/users", json={"email": "a@example.com"})
        self.assertIn("user_id", response.json())

    def test_create_user_id_is_string(self):
        response = client.post("/users", json={"email": "a@example.com"})
        self.assertIsInstance(response.json()["user_id"], str)

    def test_create_user_ids_are_unique(self):
        id1 = client.post("/users", json={"email": "a@example.com"}).json()["user_id"]
        id2 = client.post("/users", json={"email": "a@example.com"}).json()["user_id"]
        self.assertNotEqual(id1, id2)

    def test_create_user_missing_email_returns_422(self):
        response = client.post("/users", json={})
        self.assertEqual(response.status_code, 422)


class TestGetUserFlow(unittest.TestCase):

    def setUp(self):
        self.user_id = client.post("/users", json={"email": "a@example.com"}).json()["user_id"]

    def test_get_flow_returns_200(self):
        response = client.get(f"/users/{self.user_id}/flow")
        self.assertEqual(response.status_code, 200)

    def test_get_flow_returns_list(self):
        response = client.get(f"/users/{self.user_id}/flow")
        self.assertIsInstance(response.json()["flow"], list)

    def test_get_flow_contains_steps(self):
        response = client.get(f"/users/{self.user_id}/flow")
        flow = response.json()["flow"]
        self.assertGreater(len(flow), 0)

    def test_get_flow_step_has_required_fields(self):
        response = client.get(f"/users/{self.user_id}/flow")
        step = response.json()["flow"][0]
        self.assertIn("step_id", step)
        self.assertIn("is_completed", step)
        self.assertIn("tasks", step)

    def test_get_flow_nonexistent_user_returns_404(self):
        response = client.get("/users/nonexistent/flow")
        self.assertEqual(response.status_code, 404)


class TestGetUserState(unittest.TestCase):

    def setUp(self):
        self.user_id = client.post("/users", json={"email": "a@example.com"}).json()["user_id"]

    def test_get_state_returns_200(self):
        response = client.get(f"/users/{self.user_id}/state")
        self.assertEqual(response.status_code, 200)

    def test_get_state_returns_current_step_and_task(self):
        response = client.get(f"/users/{self.user_id}/state")
        body = response.json()
        self.assertIn("current_step", body)
        self.assertIn("current_task", body)

    def test_get_state_initial_step_is_personal_details(self):
        response = client.get(f"/users/{self.user_id}/state")
        self.assertEqual(response.json()["current_step"], "PERSONAL_DETAILS")

    def test_get_state_nonexistent_user_returns_404(self):
        response = client.get("/users/nonexistent/state")
        self.assertEqual(response.status_code, 404)

    def test_get_state_after_process_ends_returns_404(self):
        client.put("/users/tasks", json={
            "user_id": self.user_id,
            "step_name": "PERSONAL_DETAILS",
            "task_name": "submit_details",
            "task_payload": {}
        })
        client.put("/users/tasks", json={
            "user_id": self.user_id,
            "step_name": "IQ_TEST",
            "task_name": "complete_iq_test",
            "task_payload": {"score": 10}
        })
        response = client.get(f"/users/{self.user_id}/state")
        self.assertEqual(response.status_code, 404)


class TestSubmitTask(unittest.TestCase):

    def setUp(self):
        self.user_id = client.post("/users", json={"email": "a@example.com"}).json()["user_id"]

    def _submit(self, step, task, payload=None):
        return client.put("/users/tasks", json={
            "user_id": self.user_id,
            "step_name": step,
            "task_name": task,
            "task_payload": payload or {}
        })

    def test_submit_task_returns_200(self):
        response = self._submit("PERSONAL_DETAILS", "submit_details")
        self.assertEqual(response.status_code, 200)

    def test_submit_task_advances_step(self):
        self._submit("PERSONAL_DETAILS", "submit_details")
        state = client.get(f"/users/{self.user_id}/state").json()
        self.assertEqual(state["current_step"], "IQ_TEST")

    def test_submit_task_wrong_step_returns_404(self):
        response = self._submit("IQ_TEST", "complete_iq_test", {"score": 80})
        self.assertEqual(response.status_code, 404)

    def test_submit_task_wrong_task_returns_404(self):
        response = self._submit("PERSONAL_DETAILS", "nonexistent_task")
        self.assertEqual(response.status_code, 404)

    def test_submit_task_nonexistent_user_returns_404(self):
        response = client.put("/users/tasks", json={
            "user_id": "nonexistent",
            "step_name": "PERSONAL_DETAILS",
            "task_name": "submit_details",
            "task_payload": {}
        })
        self.assertEqual(response.status_code, 404)

    def test_submit_task_missing_fields_returns_422(self):
        response = client.put("/users/tasks", json={"user_id": self.user_id})
        self.assertEqual(response.status_code, 422)

    def test_submit_task_after_rejection_returns_404(self):
        self._submit("PERSONAL_DETAILS", "submit_details")
        self._submit("IQ_TEST", "complete_iq_test", {"score": 10})
        response = self._submit("PERSONAL_DETAILS", "submit_details")
        self.assertEqual(response.status_code, 404)


class TestGetUserStatus(unittest.TestCase):

    def setUp(self):
        self.user_id = client.post("/users", json={"email": "a@example.com"}).json()["user_id"]

    def test_get_status_returns_200(self):
        response = client.get(f"/users/{self.user_id}/status")
        self.assertEqual(response.status_code, 200)

    def test_get_status_initial_is_in_progress(self):
        response = client.get(f"/users/{self.user_id}/status")
        self.assertEqual(response.json()["user_status"], "IN_PROGRESS")

    def test_get_status_after_rejection(self):
        client.put("/users/tasks", json={
            "user_id": self.user_id,
            "step_name": "PERSONAL_DETAILS",
            "task_name": "submit_details",
            "task_payload": {}
        })
        client.put("/users/tasks", json={
            "user_id": self.user_id,
            "step_name": "IQ_TEST",
            "task_name": "complete_iq_test",
            "task_payload": {"score": 10}
        })
        response = client.get(f"/users/{self.user_id}/status")
        self.assertEqual(response.json()["user_status"], "failed")

    def test_get_status_nonexistent_user_returns_404(self):
        response = client.get("/users/nonexistent/status")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
