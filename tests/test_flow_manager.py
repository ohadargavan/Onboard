import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flow_manager import FlowManager


FLOW_JSON = os.path.join(os.path.dirname(__file__), '..', 'flow.json')
FLOW_CREATIVE_JSON = os.path.join(os.path.dirname(__file__), '..', 'flow_creative_PM.json')


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def fm():
    return FlowManager(FLOW_JSON)

@pytest.fixture
def fm_creative():
    return FlowManager(FLOW_CREATIVE_JSON)


# ── __init__ / loading ────────────────────────────────────────────────────────

class TestInit:
    def test_initial_step(self, fm):
        assert fm.initial_step == "PERSONAL_DETAILS"

    def test_all_steps_loaded(self, fm):
        expected = {"PERSONAL_DETAILS", "IQ_TEST", "INTERVIEW", "SIGN_CONTRACT", "PAYMENT", "JOIN_SLACK"}
        assert set(fm.steps.keys()) == expected

    def test_unknown_condition_type_raises(self, tmp_path):
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("""{
            "version": "1.0",
            "initial_step": "STEP_A",
            "transitions": {"STEP_A": {"completed": "DONE"}},
            "steps": {
                "STEP_A": {
                    "display_name": "Step A",
                    "tasks": [{"id": "t1", "condition": {"type": "UNKNOWN", "field": "x"}}]
                }
            }
        }""")
        with pytest.raises(ValueError, match="Unknown condition type"):
            FlowManager(str(bad_json))


# ── get_initial_step ──────────────────────────────────────────────────────────

class TestGetInitialStep:
    def test_returns_correct_initial_step(self, fm):
        assert fm.get_initial_step() == "PERSONAL_DETAILS"


# ── get_step ──────────────────────────────────────────────────────────────────

class TestGetStep:
    def test_existing_step(self, fm):
        step = fm.get_step("IQ_TEST")
        assert step is not None
        assert step.id == "IQ_TEST"
        assert step.display_name == "IQ Test"

    def test_nonexistent_step_returns_none(self, fm):
        assert fm.get_step("DOES_NOT_EXIST") is None


# ── get_tasks_for_step ────────────────────────────────────────────────────────

class TestGetTasksForStep:
    def test_single_task_step(self, fm):
        tasks = fm.get_tasks_for_step("PERSONAL_DETAILS")
        assert len(tasks) == 1
        assert tasks[0].id == "submit_details"

    def test_multi_task_step(self, fm):
        tasks = fm.get_tasks_for_step("INTERVIEW")
        task_ids = [t.id for t in tasks]
        assert task_ids == ["schedule_interview", "perform_interview"]

    def test_task_with_threshold_condition(self, fm):
        tasks = fm.get_tasks_for_step("IQ_TEST")
        assert tasks[0].condition is not None

    def test_task_without_condition(self, fm):
        tasks = fm.get_tasks_for_step("PERSONAL_DETAILS")
        assert tasks[0].condition is None

    def test_task_with_match_condition(self, fm):
        tasks = fm.get_tasks_for_step("INTERVIEW")
        perform = next(t for t in tasks if t.id == "perform_interview")
        assert perform.condition is not None

    def test_task_with_range_condition(self, fm_creative):
        tasks = fm_creative.get_tasks_for_step("IQ_TEST")
        assert tasks[0].condition is not None


# ── get_next_step_id ──────────────────────────────────────────────────────────

class TestGetNextStepId:
    def test_passed_iq_goes_to_interview(self, fm):
        assert fm.get_next_step_id("IQ_TEST", "passed") == "INTERVIEW"

    def test_failed_iq_goes_to_rejected(self, fm):
        assert fm.get_next_step_id("IQ_TEST", "failed") == "REJECTED"

    def test_completion_based_transition(self, fm):
        assert fm.get_next_step_id("PERSONAL_DETAILS", "completed") == "IQ_TEST"

    def test_nonexistent_outcome_returns_none(self, fm):
        assert fm.get_next_step_id("IQ_TEST", "nonexistent_outcome") is None

    def test_nonexistent_step_returns_none(self, fm):
        assert fm.get_next_step_id("GHOST_STEP", "passed") is None

    def test_creative_medium_score_goes_to_second_chance(self, fm_creative):
        assert fm_creative.get_next_step_id("IQ_TEST", "medium_score") == "IQ_SECOND_CHANCE"


# ── get_default_flow_from_step ────────────────────────────────────────────────

class TestGetDefaultFlowFromStep:
    def test_full_flow_from_start(self, fm):
        flow = fm.get_default_flow_from_step("PERSONAL_DETAILS")
        assert flow == ["IQ_TEST", "INTERVIEW", "SIGN_CONTRACT", "PAYMENT", "JOIN_SLACK"]

    def test_flow_from_middle(self, fm):
        flow = fm.get_default_flow_from_step("SIGN_CONTRACT")
        assert flow == ["PAYMENT", "JOIN_SLACK"]

    def test_flow_from_last_step_is_empty(self, fm):
        flow = fm.get_default_flow_from_step("JOIN_SLACK")
        assert flow == []

    def test_creative_flow_follows_default_outcome(self, fm_creative):
        # medium_score branch should NOT appear in default flow
        flow = fm_creative.get_default_flow_from_step("PERSONAL_DETAILS")
        assert "IQ_SECOND_CHANCE" not in flow
        assert "INTERVIEW" in flow