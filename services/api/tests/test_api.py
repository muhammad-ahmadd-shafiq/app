def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_ready_ok(client):
    assert client.get("/ready").status_code == 200


def test_ready_when_db_down(client, repo):
    repo.healthy = False
    assert client.get("/ready").status_code == 503


def test_list_starts_empty(client):
    assert client.get("/api/tasks").get_json() == []


def test_create_and_list(client):
    resp = client.post("/api/tasks", json={"title": "  write threat model  "})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["title"] == "write threat model"
    assert body["done"] is False

    tasks = client.get("/api/tasks").get_json()
    assert [t["title"] for t in tasks] == ["write threat model"]


def test_create_rejects_missing_title(client):
    assert client.post("/api/tasks", json={}).status_code == 400


def test_create_rejects_blank_title(client):
    assert client.post("/api/tasks", json={"title": "   "}).status_code == 400


def test_create_rejects_non_string_title(client):
    assert client.post("/api/tasks", json={"title": 123}).status_code == 400


def test_create_rejects_long_title(client):
    resp = client.post("/api/tasks", json={"title": "x" * 201})
    assert resp.status_code == 400


def test_create_rejects_non_json(client):
    resp = client.post("/api/tasks", data="title=hello")
    assert resp.status_code == 400


def test_mark_done(client):
    task_id = client.post("/api/tasks", json={"title": "a"}).get_json()["id"]
    resp = client.patch(f"/api/tasks/{task_id}", json={"done": True})
    assert resp.status_code == 200
    assert resp.get_json()["done"] is True


def test_patch_requires_boolean(client):
    task_id = client.post("/api/tasks", json={"title": "a"}).get_json()["id"]
    resp = client.patch(f"/api/tasks/{task_id}", json={"done": "yes"})
    assert resp.status_code == 400


def test_patch_unknown_task(client):
    resp = client.patch("/api/tasks/999", json={"done": True})
    assert resp.status_code == 404


def test_delete(client):
    task_id = client.post("/api/tasks", json={"title": "a"}).get_json()["id"]
    assert client.delete(f"/api/tasks/{task_id}").status_code == 204
    assert client.get("/api/tasks").get_json() == []


def test_delete_unknown_task(client):
    assert client.delete("/api/tasks/999").status_code == 404
