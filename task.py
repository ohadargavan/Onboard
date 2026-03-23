from conditions import Condition

class Task:
    # The constructor initializes the task with data from the JSON
    def __init__(self, task_id: str, display_name: str, condition: Condition = None):
        self.id = task_id
        self.display_name = display_name
        self.condition = condition

    # This method is called when a user submits data for this task
    def evaluate(self, payload: dict) -> str:
        if self.condition is None:
            return "completed"
        return self.condition.check(payload)
