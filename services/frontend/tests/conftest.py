import pytest

from app import create_app
from api_client import ApiError


class FakeClient:
    """Stand-in for the api_client module."""

    ApiError = ApiError

    def __init__(self):
        self.tasks = []
        self.fail = False
        self.calls = []

    def _check(self):
        if self.fail:
            raise ApiError("boom")

    def list_tasks(self):
        self._check()
        return self.tasks

    def add_task(self, title):
        self._check()
        self.calls.append(("add", title))
        task = {"id": len(self.tasks) + 1, "title": title, "done": False}
        self.tasks.append(task)
        return task

    def set_done(self, task_id, done):
        self._check()
        self.calls.append(("set_done", task_id, done))

    def delete_task(self, task_id):
        self._check()
        self.calls.append(("delete", task_id))


@pytest.fixture
def fake():
    return FakeClient()


@pytest.fixture
def client(fake):
    return create_app(fake).test_client()
