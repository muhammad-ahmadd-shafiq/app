"""Thin HTTP client for the tasks API."""
import os

import requests

API_URL = os.environ.get("API_URL", "http://api:5000").rstrip("/")
TIMEOUT = float(os.environ.get("API_TIMEOUT", "3"))


class ApiError(Exception):
    """Raised when the API is unreachable or returns an error."""


def _request(method, path, **kwargs):
    try:
        resp = requests.request(
            method, f"{API_URL}{path}", timeout=TIMEOUT, **kwargs
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise ApiError(str(exc)) from exc
    return resp


def list_tasks():
    return _request("GET", "/api/tasks").json()


def add_task(title):
    return _request("POST", "/api/tasks", json={"title": title}).json()


def set_done(task_id, done):
    return _request("PATCH", f"/api/tasks/{task_id}", json={"done": done}).json()


def delete_task(task_id):
    _request("DELETE", f"/api/tasks/{task_id}")
