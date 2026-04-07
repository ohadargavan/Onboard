
# Onboard Admissions API

A REST API that manages a multi-step admissions process for new applicants.
Each user goes through a series of steps (IQ test, interview, contract, etc.) and ends up either accepted or rejected.

Built with **Python** and **FastAPI**.

<br clear="left"/>



## Requirements

- Python 3.11+
- pip

---

## Installation

1. Clone the repo and go into the project folder:
   ```
   git clone <your-repo-url>
   cd Onboard
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv .venv
   ```
   On Windows:
   ```
   .venv\Scripts\activate
   ```
   On Mac/Linux:
   ```
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

---

## Run the server

```
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

To see all the endpoints in your browser: `http://localhost:8000/docs`

---

## Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/users` | Create a new user (returns user_id) |
| GET | `/users/{user_id}/flow` | Get the entire step flow for a user |
| GET | `/users/{user_id}/state` | Get the current step and task for a user |
| PUT | `/users/tasks` | Submit a completed task |
| GET | `/users/{user_id}/status` | Check if user is accepted, rejected, or in progress |

---

## Modifying the Flow

The flow is fully defined in `flow.json` — no code changes needed.

**To add a step:**
1. Add it as a step in the JSON under `"steps"`.
2. Edit the `"transitions"` map:
   - **Regular step:** make sure the path of default outcomes goes through the new step.
   - **Hidden step** (only visible to certain users): make sure the path of default outcomes does *not* go through it. Instead, route to it via a specific condition/outcome in the previous step's transition. See `flow_creative_PM.json` for an example.

**To add a task to a step:**
- Regular task: just add it in the right order under the step in the JSON.
- Hidden task: treat it like a hidden step — see above.

---

## Run the tests

Make sure you are in the project root folder, then:

```
pytest
```

To run a specific test file:
```
pytest tests/test_service.py
```

To see a visual walkthrough of the flow in the console:
```
cd tests
python frontend_test.py
```


---

## Development Process

The core logic and flow engine were initially implemented as a standalone Python structure, focusing on functional requirements without immediate integration or running the program.

Once the logic seemed complete, the project was migrated to GitHub for version control, then integrated with FastAPI, and finally went through unit and integration tests.

---

## Notes

- There is no real database. All data is stored in memory, so it resets every time you restart the server.
