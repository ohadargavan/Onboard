from flow_manager import FlowManager
from step import Step
from store import Store
from task import Task
from user import User
import uuid

class Service:
    def __init__(self, json_filepath: str):
        #Load flow from json file
        self.flow_manager = FlowManager(json_filepath)
        #New store (singleton)
        self.store = Store()

    def create_user (self, email: str) -> str:
        user_id = str(uuid.uuid4())
        initial_step = self.flow_manager.get_initial_step() #need to implement
        user = User(user_id, email, initial_step)
        self.store.save_user(user)
        return user_id

    def get_entire_flow (self, user_id: str) -> list[dict]:
        user = self.validate_and_get_user(user_id)
        current_step = user.current_step
        flow = []
        # ---1. Add previous and current steps---
        # copy (to avoid changing the actual user's list)
        prev_and_cur_steps = user.completed_steps.copy()

        # If the user is still in process, add current step
        if current_step:
            prev_and_cur_steps.append(user.current_step)

        for step_id in prev_and_cur_steps:
            ordered_tasks_from_json = self.flow_manager.get_tasks_for_step(step_id)
            user_completed_tasks = user.completed_tasks_by_step.get(step_id, {})

            formatted_tasks = []
            for task in ordered_tasks_from_json:
                task_id = task["id"]
                formatted_tasks.append({
                    "task_id": task_id,
                    "is_completed": task_id in user_completed_tasks
                })

            # We included current step as well, so this check is a must
            is_step_completed = (step_id in user.completed_steps)

            flow.append({
                "step_id": step_id,
                "is_completed": is_step_completed,
                "tasks": formatted_tasks
            })


        if user.current_step is None:
            return flow
        # ---2. Add future steps (and tasks)---
        future_steps = self.flow_manager.get_default_flow_from_step(current_step)
        for future_step_id in future_steps:
            ordered_tasks_from_json = self.flow_manager.get_tasks_for_step(future_step_id)
            formatted_tasks = []
            for task in ordered_tasks_from_json:
                task_id = task["id"]
                formatted_tasks.append({
                    "task_id": task_id,
                    "is_completed": False
                })
            flow.append({
                "step_id": future_step_id,
                "is_completed": False,
                "tasks": formatted_tasks
            })
        return flow

    def get_user_current_state (self, user_id: str):

        user = self.validate_and_get_user(user_id)
        step_id = user.current_step
        if step_id is None: #user not in process
            return None
        cur_step_completed_tasks = user.completed_tasks_by_step.get(step_id, {})
        cur_step_tasks = self.flow_manager.get_tasks_for_step(step_id)
        next_task = None
        for task in cur_step_tasks:
            task_id = task["id"]
            if task_id not in cur_step_completed_tasks:
                next_task = task_id
                break
        return {"current_step":step_id, "current_task": next_task}

    def get_user_status (self, user_id: str) -> str:

        user = self.validate_and_get_user(user_id)
        return user.status

    def submit_task (self, step_id: str, task_id, user_id, task_payload: dict)->None:
        user = self.validate_and_get_user(user_id)
        if user.current_step is None:
            raise ValueError ("User not in the process, "+
                              "status: "+ self.get_user_status(user_id) +". Can't submit task")
        if user.current_step != step_id:
            raise ValueError("Step_id "+step_id +" does not match user "+user_id)

        step = self.validate_and_get_step(step_id)
        task = Service.validate_and_get_task(step,task_id)
        outcome = task.evaluate(task_payload)
        user.record_task_result(step_id, task_id, outcome)

        if step.is_complete(user.completed_tasks_by_step[step_id]):
            next_step_id = self.flow_manager.get_next_step_id(step_id, outcome)
            if next_step_id is None:
                raise ValueError("Next step undefined")
            next_step = self.flow_manager.get_step(next_step_id)
            if next_step is None: #ACCAPTED / REJECTED
                user.finish_process(outcome)
            else:
                user.move_to_step(next_step_id)

        #Important for future database implementation. Now it's not needed because "user" is a referance
        self.store.save_user(user)

    def validate_and_get_user (self, user_id: str) -> User:
        user = self.store.get_user(user_id)
        if user is None:
            raise ValueError("User not found")
        return user

    def validate_and_get_step (self, step_id) -> Step:
        step = self.flow_manager.get_step(step_id)
        if step is None:
            raise ValueError("Step was not found for step_id "+step_id)
        return step

    @staticmethod
    def validate_and_get_task(step, task_id):
        task = step.get_task(task_id)
        if task is None:
            raise ValueError("Task "+task_id +" was not found for step "+step.id)
        return task


