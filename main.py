from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from service import Service
import os


app = FastAPI(title="Onboard Admissions API")

admissions_service = Service(os.path.join(os.path.dirname(__file__), "flow.json"))


# ---Pydantic Models for incoming info---

class CreateUserRequest(BaseModel):
    # (Endpoint 1: POST request)

    email: str

class SubmitTaskRequest(BaseModel):
    # (Endpoint 4: PUT)

    user_id: str
    step_name: str
    task_name: str
    task_payload: Dict[str, Any]


# Endpoint 1 (POST)
@app.post("/users")
def create_user_endpoint(request: CreateUserRequest):
    try:
        new_user_id = admissions_service.create_user(request.email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"user_id": new_user_id}

# Endpoint 2 (GET)
@app.get("/users/{user_id}/flow")
def get_user_entire_flow (user_id: str):
    try:
        flow = admissions_service.get_entire_flow(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"flow": flow}

# Endpoint 3 (GET)
@app.get("/users/{user_id}/state")
def get_user_state_endpoint (user_id: str):
    try:
        user_state = admissions_service.get_user_current_state(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if user_state is None:
        raise HTTPException(status_code=404, detail="State not found. User might have finished the process.")
    return user_state

# Endpoint 4 (PUT)
@app.put("/users/tasks")
def submit_task_endpoint (request: SubmitTaskRequest):
    try:
        admissions_service.submit_task(request.step_name, request.task_name, request.user_id, request.task_payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# EndPoint 5 (GET)
@app.get("/users/{user_id}/status")
def get_user_status_endpoint (user_id: str):
    try:
        user_status = admissions_service.get_user_status(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"user_status" : user_status}