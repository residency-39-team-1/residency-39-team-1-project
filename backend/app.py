# backend/app.py
from flask import Flask, jsonify

# absolute imports so this works when run as a module
from backend.crudServices.tasks import register_task_routes
from backend.crudServices.archived import register_archived_routes

app = Flask(__name__)

@app.get("/")
def index():
    return jsonify({"message": "Loopy Backend API is running"}), 200

@app.get("/health")
def health():
    return jsonify({"ok": True}), 200

# attach route groups
register_task_routes(app)
register_archived_routes(app)

if __name__ == "__main__":
    # run from repo root:
    #   python -m backend.app
    app.run(debug=True)