import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def sep(title=""):
    if title:
        print(f"\n{'='*20} {title} {'='*20}")
    else:
        print("─" * 50)


def print_flow(flow: list):
    for step in flow:
        status = "✅" if step["is_completed"] else "⬜"
        print(f"  {status} {step['step_id']}")
        for task in step["tasks"]:
            task_status = "✓" if task["is_completed"] else "·"
            print(f"       {task_status} {task['task_id']}")


def print_state(user_id: str):
    response = client.get(f"/users/{user_id}/state")
    if response.status_code == 404:
        print("  📍 State: process ended")
    else:
        state = response.json()
        print(f"  📍 Current step: {state['current_step']}  |  Current task: {state['current_task']}")


def print_status(user_id: str):
    status = client.get(f"/users/{user_id}/status").json()["user_status"]
    icon = "🟢" if status == "IN_PROGRESS" else "🔴" if status == "failed" else "🏁"
    print(f"  {icon} Status: {status}")


def submit(user_id, step, task, payload=None):
    print(f"\n  ➤  Submit  [{step}] → [{task}]  payload={payload or {}}")
    r = client.put("/users/tasks", json={
        "user_id": user_id,
        "step_name": step,
        "task_name": task,
        "task_payload": payload or {}
    })
    if r.status_code != 200:
        print(f"  ⚠️  Error: {r.json()['detail']}")


# ─────────────────────────────────────────────
sep("SCENARIO 1: Happy Path — Full Acceptance")
# ─────────────────────────────────────────────

user_id = client.post("/users", json={"email": "ohad@example.com"}).json()["user_id"]
print(f"\n  Created user: {user_id}")

sep()
print("  Flow at start:")
print_flow(client.get(f"/users/{user_id}/flow").json()["flow"])
print_state(user_id)
print_status(user_id)

submit(user_id, "PERSONAL_DETAILS", "submit_details", {"email": "ohad@example.com"})
print_state(user_id)

submit(user_id, "IQ_TEST", "complete_iq_test", {"score": 90})
print_state(user_id)

submit(user_id, "INTERVIEW", "schedule_interview", {"interview_date": "2025-06-01"})
print_state(user_id)

submit(user_id, "INTERVIEW", "perform_interview", {"decision": "passed_interview"})
print_state(user_id)

submit(user_id, "SIGN_CONTRACT", "upload_id", {"passport_number": "AB123456"})
print_state(user_id)

submit(user_id, "SIGN_CONTRACT", "sign_contract", {})
print_state(user_id)

submit(user_id, "PAYMENT", "make_payment", {"payment_id": "pay-001"})
print_state(user_id)

submit(user_id, "JOIN_SLACK", "join_slack_channel", {"email": "ohad@example.com"})

sep()
print("  Flow at end:")
print_flow(client.get(f"/users/{user_id}/flow").json()["flow"])
print_state(user_id)
print_status(user_id)


# ─────────────────────────────────────────────
sep("SCENARIO 2: Rejected — Low IQ Score")
# ─────────────────────────────────────────────

user_id = client.post("/users", json={"email": "rejected@example.com"}).json()["user_id"]
print(f"\n  Created user: {user_id}")

submit(user_id, "PERSONAL_DETAILS", "submit_details", {})
submit(user_id, "IQ_TEST", "complete_iq_test", {"score": 50})

sep()
print("  Flow at end:")
print_flow(client.get(f"/users/{user_id}/flow").json()["flow"])
print_state(user_id)
print_status(user_id)


# ─────────────────────────────────────────────
sep("SCENARIO 3: Rejected — Failed Interview")
# ─────────────────────────────────────────────

user_id = client.post("/users", json={"email": "interview_fail@example.com"}).json()["user_id"]
print(f"\n  Created user: {user_id}")

submit(user_id, "PERSONAL_DETAILS", "submit_details", {})
submit(user_id, "IQ_TEST", "complete_iq_test", {"score": 80})
submit(user_id, "INTERVIEW", "schedule_interview", {})
submit(user_id, "INTERVIEW", "perform_interview", {"decision": "failed_interview"})

sep()
print("  Flow at end:")
print_flow(client.get(f"/users/{user_id}/flow").json()["flow"])
print_state(user_id)
print_status(user_id)


# ─────────────────────────────────────────────
sep("SCENARIO 4: Error Handling")
# ─────────────────────────────────────────────

user_id = client.post("/users", json={"email": "errors@example.com"}).json()["user_id"]
print(f"\n  Created user: {user_id}")

print("\n  Trying wrong step:")
submit(user_id, "IQ_TEST", "complete_iq_test", {"score": 80})

print("\n  Trying nonexistent user:")
client_resp = client.put("/users/tasks", json={
    "user_id": "fake-id",
    "step_name": "PERSONAL_DETAILS",
    "task_name": "submit_details",
    "task_payload": {}
})
print(f"  ⚠️  Error: {client_resp.json()['detail']}")

print("\n  Submitting task after rejection:")
submit(user_id, "PERSONAL_DETAILS", "submit_details", {})
submit(user_id, "IQ_TEST", "complete_iq_test", {"score": 10})
submit(user_id, "PERSONAL_DETAILS", "submit_details", {})

sep()
print("\n  Done.\n")
