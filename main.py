from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from service import Service

app = FastAPI(title="Onboard Admissions API")

admissions_service = Service("flow.json")

# ---Pydantic Models for incoming info---

class CreateUserRequest(BaseModel):
    # Endpoint 1: POST request

    email: str

class SubmitTaskRequest(BaseModel):
    # Endpoint 4: PUT

    user_id: str
    step_id: str
    task_id: str
    task_payload: Dict[str, Any]


# Endpoint 1 (POST)
@app.post("/users")
def create_user_endpoint(request: CreateUserRequest):

    new_user_id = admissions_service.create_user(request.email)
    return {"user_id": new_user_id}

# EndPoint 5 (GET)
@app.get("/users/{user_id}/status")
def get_user_status_endpoint (user_id: str):
    user_status = admissions_service.get_user_status(user_id)
    return {"user_status" : user_status}