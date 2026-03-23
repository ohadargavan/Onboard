import unittest
import os
from service import Service


class TestServiceIntegration(unittest.TestCase):
    def setUp(self):
        # הגדרת נתיב לקובץ ה-JSON שנמצא לצד תיקיית הטסטים
        # הערה: וודא שהנתיב תואם למבנה התיקיות שלך
        json_path = os.path.join(os.path.dirname(__file__), '../flow.json')
        self.service = Service(json_path)

    def test_iq_test_passing_logic(self):
        # 1. יצירת משתמש
        user_id = self.service.create_user("ohad@example.com")

