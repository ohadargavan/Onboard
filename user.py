from datetime import datetime

#Note: for simplicity, the only unique field is user_id (so, same email can be used for multiple users)
class User:
    # The constructor is called when a user enters for the first time ("POST")
    def __init__(self, user_id: str, email: str, initial_step: str):
        self.user_id = user_id
        self.email = email
        self.status = "IN_PROGRESS"
        self.current_step = initial_step
        self.completed_steps = []
        #dict[str, dict[str, str]]
        self.completed_tasks_by_step = {}


    # A helper method to easily record a new completed task
    def record_task_result(self, step_id: str, task_id: str, outcome: str):
        #step_id mentioned for the 1st time
        if step_id not in self.completed_tasks_by_step:
            self.completed_tasks_by_step[step_id] = {}

        #save or update the task outcome
        self.completed_tasks_by_step[step_id][task_id] = outcome


    # To be used when user finished a step, to move it to the next step
    def move_to_step(self, next_step_id: str):
        self.completed_steps.append(self.current_step)
        self.current_step = next_step_id

    # A helper method to finalize the user's journey
    def finish_process(self, final_status: str):
        self.current_step = None
        self.status = final_status


