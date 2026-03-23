import unittest
from store import Store
from user import User


class TestStore(unittest.TestCase):

    def setUp(self):
        self.store = Store()
        self.user = User("user-1", "test@example.com", "PERSONAL_DETAILS")

    # --- save_user / get_user ---

    def test_save_and_get_user(self):
        self.store.save_user(self.user)
        result = self.store.get_user("user-1")
        self.assertEqual(result, self.user)

    def test_get_nonexistent_user_returns_none(self):
        result = self.store.get_user("nonexistent-id")
        self.assertIsNone(result)

    def test_save_user_upsert(self):
        self.store.save_user(self.user)
        self.user.status = "accepted"
        self.store.save_user(self.user)
        result = self.store.get_user("user-1")
        self.assertEqual(result.status, "accepted")

    def test_save_multiple_users(self):
        user2 = User("user-2", "other@example.com", "PERSONAL_DETAILS")
        self.store.save_user(self.user)
        self.store.save_user(user2)
        self.assertEqual(self.store.get_user("user-1"), self.user)
        self.assertEqual(self.store.get_user("user-2"), user2)

    # --- user_exists ---

    def test_user_exists_after_save(self):
        self.store.save_user(self.user)
        self.assertTrue(self.store.user_exists("user-1"))

    def test_user_not_exists_before_save(self):
        self.assertFalse(self.store.user_exists("user-1"))

    def test_user_exists_only_for_saved_user(self):
        self.store.save_user(self.user)
        self.assertFalse(self.store.user_exists("user-2"))

    # --- isolation between users ---

    def test_users_are_independent(self):
        user2 = User("user-2", "other@example.com", "PERSONAL_DETAILS")
        self.store.save_user(self.user)
        self.store.save_user(user2)
        self.user.status = "rejected"
        self.store.save_user(self.user)
        self.assertEqual(self.store.get_user("user-2").status, "IN_PROGRESS")


if __name__ == "__main__":
    unittest.main()
