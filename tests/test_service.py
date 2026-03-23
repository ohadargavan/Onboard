import unittest
import os
from service import Service


class TestService(unittest.TestCase):
    def setUp(self):
        # וודא ש-flow.json נמצא בתיקיית הפרויקט הראשית
        json_path = os.path.join(os.path.dirname(__file__), '../flow.json')
        self.service = Service(json_path)

    def test_happy_path_to_interview(self):
        # 1. יצירת משתמש
        user_id = self.service.create_user("ohad@example.com")

        # 2. השלמת שלב PERSONAL_DETAILS
        # ב-flow.json: ID השלב הוא ב-Uppercase, המשימה ב-lowercase
        self.service.submit_task(
            "PERSONAL_DETAILS",
            "submit_details",
            user_id,
            {"email": "ohad@example.com"}
        )

        # בדיקה שהגענו ל-IQ_TEST
        state = self.service.get_user_current_state(user_id)
        self.assertEqual(state["current_step"], "IQ_TEST")
        self.assertEqual(state["current_task"], "complete_iq_test")

        # 3. מעבר IQ_TEST עם ציון 80 (מעל 75)
        self.service.submit_task(
            "IQ_TEST",
            "complete_iq_test",
            user_id,
            {"score": 80}
        )

        # בדיקה שהגענו ל-INTERVIEW
        state = self.service.get_user_current_state(user_id)
        self.assertEqual(state["current_step"], "INTERVIEW")
        self.assertEqual(state["current_task"], "schedule_interview")

    def test_rejection_on_low_iq(self):
        user_id = self.service.create_user("rejected@example.com")

        # מעבר שלב ראשון
        self.service.submit_task("PERSONAL_DETAILS", "submit_details", user_id, {})

        # ציון נמוך (60) אמור להחזיר 'failed' ולשלוח ל-REJECTED
        self.service.submit_task("IQ_TEST", "complete_iq_test", user_id, {"score": 60})

        # בדיקה שהמשתמש נדחה (status הופך לתוצאה של המשימה - 'failed')
        status = self.service.get_user_status(user_id)
        self.assertEqual(status, "failed")

        # בדיקה שהתהליך הסתיים (current_step הוא None)
        state = self.service.get_user_current_state(user_id)
        self.assertIsNone(state)


if __name__ == '__main__':
    unittest.main()