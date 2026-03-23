from user import User


class Store:
    #Initialize the in-memory "database"
    def __init__(self):
        # this dictionary maps user_id (string) -> User (object)
        self.users = {}

    # Saves a new or updated user into the store
    def save_user(self, user: User):
        #We use Upsert, so the logic stays the same if we'd implement a database
        self.users[user.user_id] = user

    # Returns None if the user does not exist.
    def get_user(self, user_id: str) -> User:
        return self.users.get(user_id)

    # Check if a user exists (Redundant, might delete this function)
    def user_exists(self, user_id: str) -> bool:
        return user_id in self.users