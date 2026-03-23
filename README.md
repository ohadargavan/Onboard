<img src="Onboard logo.PNG" width="180" align="left" style="margin-right: 20px"/>

# Onboard Admissions API

A REST API that manages a multi-step admissions process for new applicants.
Each user goes through a series of steps (IQ test, interview, contract, etc.) and ends up either accepted or rejected.

Built with **Python** and **FastAPI**.

<br clear="left"/>

---

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

> All tests were written by AI (Claude by Anthropic).
> This was an intentional choice — the rest of the project was built with AI assistance, but the tests are where I gave it full autonomy. The difference felt worth marking.

---

## Notes

- There is no real database. All data is stored in memory, so it resets every time you restart the server.
- The flow can be changed by editing `flow.json` — no code changes needed.
- An alternative flow with a second-chance IQ test is available in `flow_creative_PM.json`. To use it, change the filename passed to `Service(...)` in `main.py`.
