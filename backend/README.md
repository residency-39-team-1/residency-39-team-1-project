Loopy Backend API · Tasks and Archive (Firestore + Flask)
Minimal REST API over Firestore to unblock the mobile app. Provides CRUD for tasks and a simple archive for snapshots to support restart/history flows.

Quick Start
Activate venv
source venv/bin/activate
Install deps
pip install --upgrade pip && pip install flask firebase-admin python-dotenv
Set Firebase Admin key (path to your local Admin SDK JSON)
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/backend/firebase/serviceAccountKey.json"
Run the server from repo root
python -m backend.app
Health check (expect {"ok": true})
http://127.0.0.1:5000/health
Simulators

Android emulator base URL: http://10.0.2.2:5000
iOS simulator base URL: http://127.0.0.1:5000
Endpoints
Tasks
POST /tasks — Create a task (requires user_id, title; optional status, details)
GET /tasks?user_id=UID — List tasks for a user
Optional status filter: backlog | in_progress | complete
GET /tasks/{id} — Get one task
PATCH /tasks/{id} — Update only: title, status, or details
DELETE /tasks/{id} — Delete a task
Task fields: user_id, title, status, details, created_at, updated_at
Status values: backlog, in_progress, complete
Timestamps: server-generated, ISO-8601 strings

Archive
POST /archive — Create a snapshot (requires user_id, ref_type, ref_id, data_snapshot)
GET /archive?user_id=UID[&ref_type=task] — List snapshots for a user
GET /archive/{archive_id} — Get a snapshot
DELETE /archive/{archive_id} — Delete a snapshot
Archive fields: user_id, type (e.g., task), ref_id, data_snapshot, timestamp

Health
GET /health — Server heartbeat
GET / — Friendly message
Request / Response Examples
Create Task
Request

POST /tasks
Content-Type: application/json

{
  "user_id": "demo_user",
  "title": "Try Loopy",
  "status": "backlog",
  "details": "optional notes"
}
201 Response

{
  "id": "TASK_ID",
  "user_id": "demo_user",
  "title": "Try Loopy",
  "status": "backlog",
  "details": "optional notes",
  "created_at": "2025-08-13T19:42:01.708000+00:00",
  "updated_at": "2025-08-13T19:42:01.708000+00:00"
}
Update Task
Request

PATCH /tasks/TASK_ID
Content-Type: application/json

{ "status": "in_progress", "details": "WIP" }
200 — returns the full updated task

Create Archive Snapshot
Request

POST /archive
Content-Type: application/json

{
  "user_id": "demo_user",
  "ref_type": "task",
  "ref_id": "TASK_ID",
  "data_snapshot": { "title": "Try Loopy", "status": "in_progress" }
}
201 Response

{
  "id": "ARCHIVE_ID",
  "user_id": "demo_user",
  "type": "task",
  "ref_id": "TASK_ID",
  "data_snapshot": { "title": "Try Loopy", "status": "in_progress" },
  "timestamp": "2025-08-13T19:44:26.677000+00:00"
}
Quick Tests (curl)
# health
curl -s http://127.0.0.1:5000/health

# create
curl -s -X POST http://127.0.0.1:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo_user","title":"Try Loopy","status":"backlog"}'

# list
curl -s "http://127.0.0.1:5000/tasks?user_id=demo_user"

# update
curl -s -X PATCH http://127.0.0.1:5000/tasks/TASK_ID \
  -H "Content-Type: application/json" \
  -d '{"status":"in_progress"}'

# archive snapshot
curl -s -X POST http://127.0.0.1:5000/archive \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo_user","ref_type":"task","ref_id":"TASK_ID","data_snapshot":{"title":"Try Loopy","status":"in_progress"}}'

# list archive
curl -s "http://127.0.0.1:5000/archive?user_id=demo_user&ref_type=task"
Validation & Errors
status must be one of: backlog, in_progress, complete
PATCH /tasks/{id} accepts only: title, status, details
Missing required fields → 400 { "error": "..." }
Unknown IDs → 404 { "error": "..." }
Files
backend/app.py — Creates the Flask app and registers route groups
backend/crudServices/tasks.py — Tasks CRUD + route registration
backend/crudServices/archived.py — Archive CRUD + route registration
backend/client.py — Firestore init, exports db and SERVER_TS
Next Steps (optional)
Add Firebase ID token verification to protect routes
Add Firestore composite index for user_id + status if you want server-side filtering
Add CORS for web callers if needed
Add tests against Firebase Emulator and CI workflow