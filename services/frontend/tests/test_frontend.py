def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_index_empty(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"No tasks yet." in resp.data


def test_index_lists_tasks(client, fake):
    fake.tasks = [{"id": 1, "title": "Set up k3s", "done": False}]
    resp = client.get("/")
    assert b"Set up k3s" in resp.data


def test_index_escapes_html(client, fake):
    fake.tasks = [{"id": 1, "title": "<script>alert(1)</script>", "done": False}]
    resp = client.get("/")
    assert b"<script>alert(1)</script>" not in resp.data
    assert b"&lt;script&gt;" in resp.data


def test_index_when_api_down(client, fake):
    fake.fail = True
    resp = client.get("/")
    assert resp.status_code == 502
    assert b"unreachable" in resp.data


def test_add_task_redirects(client, fake):
    resp = client.post("/tasks", data={"title": "  new task "})
    assert resp.status_code == 302
    assert ("add", "new task") in fake.calls


def test_add_blank_title_rejected(client, fake):
    resp = client.post("/tasks", data={"title": "   "})
    assert resp.status_code == 400
    assert fake.calls == []


def test_add_when_api_down(client, fake):
    fake.fail = True
    assert client.post("/tasks", data={"title": "x"}).status_code == 502


def test_toggle(client, fake):
    resp = client.post("/tasks/3/toggle", data={"done": "true"})
    assert resp.status_code == 302
    assert ("set_done", 3, True) in fake.calls


def test_delete(client, fake):
    resp = client.post("/tasks/3/delete")
    assert resp.status_code == 302
    assert ("delete", 3) in fake.calls
