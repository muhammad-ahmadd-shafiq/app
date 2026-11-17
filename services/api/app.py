import logging
import os

from flask import Flask, jsonify, request

import db

MAX_TITLE_LENGTH = 200


def create_app(repo=None):
    app = Flask(__name__)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

    if repo is None:
        repo = db.TaskRepository(
            os.environ.get(
                "DATABASE_URL", "postgresql://app:app@localhost:5432/appdb"
            )
        )
    app.config["REPO"] = repo

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/ready")
    def ready():
        try:
            repo.ping()
        except Exception:
            app.logger.exception("database not reachable")
            return jsonify(status="unavailable"), 503
        return jsonify(status="ready")

    @app.get("/api/tasks")
    def list_tasks():
        return jsonify(repo.list_tasks())

    @app.post("/api/tasks")
    def create_task():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="JSON body required"), 400
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            return jsonify(error="title is required"), 400
        title = title.strip()
        if len(title) > MAX_TITLE_LENGTH:
            return (
                jsonify(error=f"title must be at most {MAX_TITLE_LENGTH} characters"),
                400,
            )
        return jsonify(repo.add_task(title)), 201

    @app.patch("/api/tasks/<int:task_id>")
    def update_task(task_id):
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not isinstance(data.get("done"), bool):
            return jsonify(error="done (boolean) is required"), 400
        task = repo.set_done(task_id, data["done"])
        if task is None:
            return jsonify(error="task not found"), 404
        return jsonify(task)

    @app.delete("/api/tasks/<int:task_id>")
    def delete_task(task_id):
        if not repo.delete_task(task_id):
            return jsonify(error="task not found"), 404
        return "", 204

    return app


app = create_app()
