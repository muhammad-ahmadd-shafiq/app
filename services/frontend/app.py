from flask import Flask, redirect, render_template, request, url_for

import api_client


def create_app(client=api_client):
    app = Flask(__name__)

    def render_index(error=None, status=200):
        try:
            tasks = client.list_tasks()
        except client.ApiError:
            tasks = []
            error = error or "The API is unreachable right now."
            status = 502
        return render_template("index.html", tasks=tasks, error=error), status

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/")
    def index():
        return render_index()

    @app.post("/tasks")
    def add():
        title = request.form.get("title", "").strip()
        if not title:
            return render_index(error="Please enter a task title.", status=400)
        try:
            client.add_task(title)
        except client.ApiError:
            return render_index(error="Could not save the task.", status=502)
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/toggle")
    def toggle(task_id):
        done = request.form.get("done") == "true"
        try:
            client.set_done(task_id, done)
        except client.ApiError:
            return render_index(error="Could not update the task.", status=502)
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/delete")
    def delete(task_id):
        try:
            client.delete_task(task_id)
        except client.ApiError:
            return render_index(error="Could not delete the task.", status=502)
        return redirect(url_for("index"))

    return app


app = create_app()
