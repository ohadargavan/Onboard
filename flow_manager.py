import json
from typing import Any

from step import Step
from conditions import *
from task import Task


class FlowManager:
    def __init__(self, json_filepath: str):

        with open(json_filepath, 'r') as file:
            #parse json to dictionary
            data = json.load(file)

        #Extract fields from dictionary
        self.initial_step = data["initial_step"]
        self.transitions = data["transitions"]

        self.steps = {}
        self._build_steps(data["steps"])

    def _build_steps(self, steps_data: dict):
        for step_id, step_info in steps_data.items():
            tasks_list = self._build_tasks(step_info["tasks"])
            #extract step info
            step =Step(step_id, step_info["display_name"],tasks_list)
            self.steps[step_id] = step

    def _build_tasks(self, tasks_data: list) -> list:

        real_tasks_list = []

        for task_data in tasks_data:
            condition_obj = None

            if "condition" in task_data:
                cond_data = task_data["condition"]

                match cond_data["type"]:
                    case "MATCH":
                        condition_obj = MatchCondition(cond_data["field"], cond_data["expected"])

                    case "THRESHOLD":
                        condition_obj = ThresholdCondition(cond_data["field"], cond_data["value"])

                    case "RANGE":
                        condition_obj = RangeCondition(cond_data["field"], cond_data["rules"])

                    case _:
                        raise ValueError(f"Unknown condition type: {cond_data['type']}")

            task_obj = Task(
                task_data["id"],
                task_data.get("display_name",""),
                condition_obj
            )

            real_tasks_list.append(task_obj)

        return real_tasks_list

    def get_step(self, step_id: str) -> Step | None:
        return self.steps.get(step_id)

    def get_next_step_id(self, current_step_id: str, outcome: str) -> str | None:

        step_transitions = self.transitions.get(current_step_id, {})
        return step_transitions.get(outcome)

    def get_initial_step (self) -> str:
        return self.initial_step

    def get_default_flow_from_step (self, current_step_id: str) -> list[str]:
        future_steps = []
        step_to_check = current_step_id
        reached_final = False

        while not reached_final:
            step_transitions = self.transitions.get(step_to_check, {})
            default_outcome = step_transitions.get("default_outcome", None)
            if default_outcome:
                step_to_check = step_transitions.get(default_outcome)
            else:
                #no default outcome defined => completion-based step
                step_to_check = list(step_transitions.values())[0]
            reached_final = (step_to_check not in self.steps)
            if not reached_final:
                future_steps.append(step_to_check)

        return future_steps


    def get_tasks_for_step (self, step_id: str):
        step_data = self.steps.get(step_id)

        return step_data.tasks
