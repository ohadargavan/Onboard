from task import Task

class Step:
    # The constructor initializes the step with its properties
    def __init__(self, step_id: str, display_name: str, visible: bool, tasks: list[Task]):
        self.id = step_id
        self.display_name = display_name
        self.visible = visible
        self.tasks = tasks

    # Checks if all the tasks in this step are completed
    def is_complete(self, completed_tasks: dict) -> bool:
        for task in self.tasks:
            if task.id not in completed_tasks:
                return False
        return True

    def get_task(self, task_id: str) -> Task | None:
        return next((task for task in self.tasks if task.id == task_id), None)
