from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from service import Service

app = FastAPI(title="Onboard Admissions API")

admissions_service = Service("flow.json")

# Pydantic Models for incoming info

class CreateUserRequest(BaseModel):
    # Endpoint 1: POST request

    email: str

class SubmitTaskRequest(BaseModel):
    # Endpoint 4: PUT

    user_id: str
    step_id: str
    task_id: str
    task_payload: Dict[str, Any]