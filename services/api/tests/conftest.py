from datetime import datetime, timezone

import pytest

from app import create_app


class FakeRepo:
    """In-memory stand-in for db.TaskRepository."""

    def __init__(self):
        self.tasks = {}
        self.next_id = 1
        self.healthy = True

    def ping(self):
        if not self.healthy:
            raise RuntimeError("db down")
        return True

    def list_tasks(self):
        return [self.tasks[k] for k in sorted(self.tasks)]

    def add_task(self, title):
        task = {
            "id": self.next_id,
            "title": title,
            "done": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.tasks[self.next_id] = task
        self.next_id += 1
        return task

    def set_done(self, task_id, done):
        task = self.tasks.get(task_id)
        if task is None:
            return None
        task["done"] = done
        return task

    def delete_task(self, task_id):
        return self.tasks.pop(task_id, None) is not None


@pytest.fixture
def repo():
    return FakeRepo()


@pytest.fixture
def client(repo):
    return create_app(repo).test_client()
