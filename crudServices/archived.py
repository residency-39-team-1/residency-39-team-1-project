# archived.py
from typing import Optional, Dict, Any, List
from datetime import datetime
from google.cloud.firestore_v1 import DocumentReference

from backend.client import db, SERVER_TS

def _serialize(value):
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value

def create_archived_entry(user_id: str, data_snapshot: Dict[str, Any], ref_type: str, ref_id: str) -> str:
    doc_ref: DocumentReference = db.collection("archived_entries").document()
    doc_ref.set({
        "user_id": user_id,
        "type": ref_type,
        "ref_id": ref_id,
        "data_snapshot": data_snapshot,
        "timestamp": SERVER_TS,
    })
    return doc_ref.id

def get_archived_entry(archive_id: str) -> Optional[dict]:
    doc = db.collection("archived_entries").document(archive_id).get()
    if doc.exists:
        return {"id": doc.id, **doc.to_dict()}
    return None

def delete_archived_entry(archive_id: str) -> bool:
    doc_ref = db.collection("archived_entries").document(archive_id)
    if doc_ref.get().exists:
        doc_ref.delete()
        return True
    return False

def list_archived_for_user(user_id: str, ref_type: Optional[str] = None) -> List[Dict[str, Any]]:
    q = db.collection("archived_entries").where("user_id", "==", user_id)
    if ref_type:
        q = q.where("type", "==", ref_type)
    return [{"id": d.id, **d.to_dict()} for d in q.stream()]

def register_archived_routes(app):
    from flask import request, jsonify

    def _bad_request(msg: str, **extra):
        payload = {"error": msg}
        if extra:
            payload.update(extra)
        return jsonify(payload), 400

    @app.post("/archive")
    def create_archive_http():
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        ref_type = data.get("ref_type")
        ref_id = data.get("ref_id")
        data_snapshot = data.get("data_snapshot") or {}
        if not user_id or not ref_type or not ref_id:
            return _bad_request("user_id, ref_type, and ref_id are required")
        archive_id = create_archived_entry(user_id, data_snapshot, ref_type, ref_id)
        entry = get_archived_entry(archive_id)
        return jsonify(_serialize(entry)), 201

    @app.get("/archive/<archive_id>")
    def get_archive_http(archive_id: str):
        entry = get_archived_entry(archive_id)
        if not entry:
            return jsonify({"error": "archive entry not found"}), 404
        return jsonify(_serialize(entry)), 200

    @app.delete("/archive/<archive_id>")
    def delete_archive_http(archive_id: str):
        ok = delete_archived_entry(archive_id)
        if not ok:
            return jsonify({"error": "archive entry not found"}), 404
        return jsonify({"deleted": True, "id": archive_id}), 200

    @app.get("/archive")
    def list_archive_http():
        uid = request.args.get("user_id")
        ref_type = request.args.get("ref_type")
        if not uid:
            return _bad_request("user_id query param is required")
        entries = list_archived_for_user(uid, ref_type=ref_type)
        return jsonify(_serialize(entries)), 200