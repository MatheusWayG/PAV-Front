# Plan: frontend/backend integration repair

## Goal
Align the PyQt frontend and the FastAPI backend so login, registration, and dashboard data fetching use the same contract, ports, and payloads.

## Current findings
- Backend is FastAPI, not Flask. The app is created in [Python-PAV/PAV-Project/app.py](Python-PAV/PAV-Project/app.py).
- Frontend is mixing database port 5432 with API ports 5000/8000 and using Flask comments.
- There is no real authentication route in the backend. The API only exposes client CRUD in [Python-PAV/PAV-Project/routes/client_routes.py](Python-PAV/PAV-Project/routes/client_routes.py).
- The backend client schema in [Python-PAV/PAV-Project/schemas/client_schema.py](Python-PAV/PAV-Project/schemas/client_schema.py) and entity in [Python-PAV/PAV-Project/entities/client.py](Python-PAV/PAV-Project/entities/client.py) do not include email/password fields.
- The frontend login code in [PAV-Front/Screens_Project/login_screen.py](PAV-Front/Screens_Project/login_screen.py) is trying to check email by listing all clients, which does not match the backend contract.
- The login button in [PAV-Front/Screens_Project/main.py](PAV-Front/Screens_Project/main.py) is currently only switching screens, not calling the backend.

## Required fixes

### 1) Backend API contract
Add a true authentication endpoint, ideally:
- POST /login
- Request body: { "email": "...", "password": "..." }
- Response: success/error JSON with status and optional token

If the app requires user persistence, create a dedicated user model or extend client model intentionally with email/password fields. Do not pretend that /clients can serve as login.

### 2) Frontend login flow
In [PAV-Front/Screens_Project/login_screen.py](PAV-Front/Screens_Project/login_screen.py):
- fix indentation of `realizar_login`
- import `requests` and `QMessageBox`
- connect the button to the method instead of only navigation
- send the correct POST request to the backend auth endpoint
- validate response status and show auth errors

### 3) Frontend registration flow
In [PAV-Front/Screens_Project/cadastro_screen.py](PAV-Front/Screens_Project/cadastro_screen.py):
- ensure the payload matches the real backend schema
- confirm whether the backend expects a client creation or a user signup model
- if using `/clients`, ensure fields match the schema exactly
- ensure the request goes to the correct API base URL

### 4) Dashboard data calls
In [PAV-Front/Screens_Project/main_dashboard.py](PAV-Front/Screens_Project/main_dashboard.py):
- standardize a single API base URL constant
- make sure it targets the FastAPI app, not the Postgres DB port
- verify the dashboard GET /clients response matches the UI’s expected fields

### 5) Port and configuration cleanup
- Remove the mixed use of 5432, 5000, and any inconsistent backend URLs.
- Define a single backend base URL, for example: http://localhost:8000
- Keep database and API ports separate.

### 6) Validation checklist
- backend app starts successfully
- database connection works
- login endpoint responds with expected JSON
- frontend can call login successfully
- registration creates client data correctly
- dashboard loads client data without schema mismatch

## Suggested implementation order
1. Add login endpoint to backend.
2. Update login screen to call backend auth.
3. Standardize frontend URLs.
4. Validate registration payload against real backend schema.
5. Validate dashboard GET data contract.
6. Run the app end-to-end and fix any remaining mismatches.

## Notes
This is not a random bug fix; it is a contract mismatch between two systems. The backend and frontend currently assume different models and ports. The cleanest fix is to define one explicit API contract and wire the UI to it consistently.
