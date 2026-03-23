import unittest
from step import Step
from task import Task


def make_task(task_id: str) -> Task:
    return Task(task_id, task_id.replace("_", " "))


class TestStepIsComplete(unittest.TestCase):

    def test_single_task_complete(self):
        step = Step("S1", "Step 1", [make_task("task_a")])
        self.assertTrue(step.is_complete({"task_a": "completed"}))

    def test_single_task_not_complete(self):
        step = Step("S1", "Step 1", [make_task("task_a")])
        self.assertFalse(step.is_complete({}))

    def test_multiple_tasks_all_complete(self):
        step = Step("S1", "Step 1", [make_task("task_a"), make_task("task_b")])
        self.assertTrue(step.is_complete({"task_a": "completed", "task_b": "passed"}))

    def test_multiple_tasks_partial_complete(self):
        step = Step("S1", "Step 1", [make_task("task_a"), make_task("task_b")])
        self.assertFalse(step.is_complete({"task_a": "completed"}))

    def test_multiple_tasks_none_complete(self):
        step = Step("S1", "Step 1", [make_task("task_a"), make_task("task_b")])
        self.assertFalse(step.is_complete({}))

    def test_extra_tasks_in_completed_dict_ignored(self):
        step = Step("S1", "Step 1", [make_task("task_a")])
        self.assertTrue(step.is_complete({"task_a": "completed", "task_b": "completed"}))

    def test_no_tasks_is_complete(self):
        step = Step("S1", "Step 1", [])
        self.assertTrue(step.is_complete({}))


class TestStepGetTask(unittest.TestCase):

    def setUp(self):
        self.task_a = make_task("task_a")
        self.task_b = make_task("task_b")
        self.step = Step("S1", "Step 1", [self.task_a, self.task_b])

    def test_get_existing_task(self):
        result = self.step.get_task("task_a")
        self.assertIs(result, self.task_a)

    def test_get_second_task(self):
        result = self.step.get_task("task_b")
        self.assertIs(result, self.task_b)

    def test_get_nonexistent_task_returns_none(self):
        result = self.step.get_task("nonexistent")
        self.assertIsNone(result)

    def test_get_task_empty_step_returns_none(self):
        step = Step("S2", "Step 2", [])
        self.assertIsNone(step.get_task("task_a"))


class TestStepAttributes(unittest.TestCase):

    def test_step_id_and_display_name(self):
        step = Step("INTERVIEW", "Interview Step", [])
        self.assertEqual(step.id, "INTERVIEW")
        self.assertEqual(step.display_name, "Interview Step")

    def test_step_stores_tasks(self):
        tasks = [make_task("task_a"), make_task("task_b")]
        step = Step("S1", "Step 1", tasks)
        self.assertEqual(len(step.tasks), 2)
        self.assertIs(step.tasks[0], tasks[0])
        self.assertIs(step.tasks[1], tasks[1])


if __name__ == "__main__":
    unittest.main()
