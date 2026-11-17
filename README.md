# SecureGitOps target app

A small three-service app used as the deployment target for the SecureGitOps pipeline.

| Service    | Tech                    | Port |
|------------|-------------------------|------|
| frontend   | Flask, server-rendered  | 8080 |
| api        | Flask, PostgreSQL       | 5000 |
| database   | PostgreSQL 16           | 5432 |

## Run everything

    docker compose up --build

Open http://localhost:8080. API health: http://localhost:5000/health, readiness: http://localhost:5000/ready.

## Run the tests (no database needed)

    cd services/api
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements-dev.txt
    pytest

    cd ../frontend
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements-dev.txt
    pytest

## API

| Method | Path              | Body              | Result             |
|--------|-------------------|-------------------|--------------------|
| GET    | /health           |                   | 200                |
| GET    | /ready            |                   | 200, or 503 if DB down |
| GET    | /api/tasks        |                   | 200, list of tasks |
| POST   | /api/tasks        | {"title": "..."}  | 201, created task  |
| PATCH  | /api/tasks/<id>   | {"done": true}    | 200, or 404        |
| DELETE | /api/tasks/<id>   |                   | 204, or 404        |
