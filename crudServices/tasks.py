# tasks.py
from typing import Optional, Dict, Any, List
from datetime import datetime
from google.cloud.firestore_v1 import DocumentReference

# absolute import so it works when running the app as a module
from backend.client import db, SERVER_TS

# ---------- utils ----------
def _serialize(value):
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value

ALLOWED_STATUS = {"backlog", "in_progress", "complete"}
ALLOWED_UPDATE_FIELDS = {"title", "status", "details"}

# ---------- TASKS CRUD ----------
def create_task(user_id: str, title: str, status: str = "backlog", details: str = "") -> str:
    doc_ref: DocumentReference = db.collection("tasks").document()
    doc_ref.set({
        "user_id": user_id,
        "title": title,
        "status": status,
        "details": details,
        "created_at": SERVER_TS,
        "updated_at": SERVER_TS,
    })
    return doc_ref.id

def get_task(task_id: str) -> Optional[dict]:
    doc = db.collection("tasks").document(task_id).get()
    if doc.exists:
        return {"id": doc.id, **doc.to_dict()}
    return None

def update_task(task_id: str, updates: dict) -> bool:
    doc_ref = db.collection("tasks").document(task_id)
    if doc_ref.get().exists:
        updates["updated_at"] = SERVER_TS
        doc_ref.update(updates)
        return True
    return False

def delete_task(task_id: str) -> bool:
    doc_ref = db.collection("tasks").document(task_id)
    if doc_ref.get().exists:
        doc_ref.delete()
        return True
    return False

def get_all_tasks_for_user(user_id: str) -> List[Dict[str, Any]]:
    docs = db.collection("tasks").where("user_id", "==", user_id).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

# ---------- HTTP route registration ----------
def register_task_routes(app):
    from flask import request, jsonify

    def _bad_request(msg: str, **extra):
        payload = {"error": msg}
        if extra:
            payload.update(extra)
        return jsonify(payload), 400

    @app.post("/tasks")
    def create_task_http():
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        title = data.get("title")
        status = data.get("status", "backlog")
        details = data.get("details", "")

        if not user_id or not title:
            return _bad_request("user_id and title are required")
        if status not in ALLOWED_STATUS:
            return _bad_request("invalid status", allowed=sorted(ALLOWED_STATUS))

        task_id = create_task(user_id=user_id, title=title, status=status, details=details)
        task = get_task(task_id)
        return jsonify(_serialize(task)), 201

    @app.get("/tasks/<task_id>")
    def get_task_http(task_id: str):
        task = get_task(task_id)
        if not task:
            return jsonify({"error": "task not found"}), 404
        return jsonify(_serialize(task)), 200

    @app.patch("/tasks/<task_id>")
    def update_task_http(task_id: str):
        data = request.get_json(silent=True) or {}
        if not data:
            return _bad_request("no fields provided to update")

        unknown = set(data.keys()) - ALLOWED_UPDATE_FIELDS
        if unknown:
            return _bad_request("unknown fields in update", unknown_fields=sorted(unknown))

        if "status" in data and data["status"] not in ALLOWED_STATUS:
            return _bad_request("invalid status", allowed=sorted(ALLOWED_STATUS))

        ok = update_task(task_id, data)
        if not ok:
            return jsonify({"error": "task not found"}), 404

        return jsonify(_serialize(get_task(task_id))), 200

    @app.delete("/tasks/<task_id>")
    def delete_task_http(task_id: str):
        ok = delete_task(task_id)
        if not ok:
            return jsonify({"error": "task not found"}), 404
        return jsonify({"deleted": True, "id": task_id}), 200

    @app.get("/tasks")
    def list_tasks_http():
        uid = request.args.get("user_id")
        status = request.args.get("status")
        if not uid:
            return _bad_request("user_id query param is required")

        tasks = get_all_tasks_for_user(uid)
        if status:
            if status not in ALLOWED_STATUS:
                return _bad_request("invalid status", allowed=sorted(ALLOWED_STATUS))
            tasks = [t for t in tasks if t.get("status") == status]

        try:
            tasks.sort(key=lambda t: t.get("created_at"), reverse=True)
        except Exception:
            pass
        return jsonify(_serialize(tasks)), 200