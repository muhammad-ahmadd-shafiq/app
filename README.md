# SecureGitOps Target Application

![python](https://img.shields.io/badge/python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![framework](https://img.shields.io/badge/framework-Flask-000000?style=flat-square&logo=flask&logoColor=white)
![database](https://img.shields.io/badge/database-PostgreSQL_16-336791?style=flat-square&logo=postgresql&logoColor=white)
![container](https://img.shields.io/badge/container-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![tests](https://img.shields.io/badge/tests-pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![platform](https://img.shields.io/badge/platform-Linux-E67E22?style=flat-square&logo=linux&logoColor=white)
![deploy](https://img.shields.io/badge/deploy-GitOps_%2F_k3s-6D28D9?style=flat-square&logo=argo&logoColor=white)
![status](https://img.shields.io/badge/status-active-2EA44F?style=flat-square)
![security](https://img.shields.io/badge/security-DevSecOps-C0392B?style=flat-square)
![category](https://img.shields.io/badge/category-Supply_Chain_Security-8E24AA?style=flat-square)
![type](https://img.shields.io/badge/type-Final_Year_Project-F39C12?style=flat-square)

A small three-service application (frontend, API, database) that serves as the deployment target for the **SecureGitOps** pipeline, a continuously verified CI/CD and GitOps pipeline with integrated attack simulation and a real-time security dashboard.

This repository contains the application only. The pipeline that scans, signs and deploys it, the deployment configuration, the dashboard and the attack scripts are separate parts of the wider SecureGitOps project (see [Role in the SecureGitOps project](#role-in-the-securegitops-project)).

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Repository Structure](#repository-structure)
4. [Technology Stack](#technology-stack)
5. [Prerequisites](#prerequisites)
6. [Getting Started](#getting-started)
7. [Running the Tests](#running-the-tests)
8. [API Reference](#api-reference)
9. [Docker Notes](#docker-notes)
10. [Role in the SecureGitOps project](#role-in-the-securegitops-project)
11. [Troubleshooting](#troubleshooting)
12. [Project Information](#project-information)
13. [References](#references)

---

## Overview

The application is a simple task manager. Users view, add, complete and delete tasks through a server-rendered web page. The page talks to a REST API, which stores tasks in PostgreSQL.

The application is intentionally small, but it has a real dependency tree, real container images and real inter-service communication. That gives the SecureGitOps pipeline something genuine to scan, sign, deploy and attack.

| Service    | Tech                    | Port |
|------------|-------------------------|------|
| frontend   | Flask, server-rendered  | 8080 |
| api        | Flask, PostgreSQL       | 5000 |
| database   | PostgreSQL 16           | 5432 |

## Architecture

```
  Browser
     |
     |  HTTP :8080
     v
+------------+   HTTP :5000   +------------+   SQL :5432   +---------------+
|  frontend  | -------------> |    api     | ------------> |   database    |
|  (Flask)   |  api_client.py |  (Flask)   |     db.py     | (PostgreSQL16)|
+------------+                +------------+               +---------------+
```

- **frontend** renders `templates/index.html` and calls the API through `api_client.py`. It holds no data of its own.
- **api** exposes the REST endpoints and health probes, and talks to PostgreSQL through `db.py`.
- **database** is a PostgreSQL 16 image whose schema is created by `init.sql` on first start.

The API exposes two probes with different meanings:

- `/health` (liveness): the process is running. Always returns 200 while the service is up.
- `/ready` (readiness): the service can reach its database. Returns 200, or 503 if the database is down.

These map directly onto Kubernetes liveness and readiness probes when the app runs on the k3s cluster.

## Repository Structure

```
.
├── docker-compose.yml          Runs all three services locally
├── .gitignore
├── README.md
└── services/
    ├── api/
    │   ├── app.py              Flask application, routes and health probes
    │   ├── db.py               PostgreSQL access layer
    │   ├── Dockerfile
    │   ├── .dockerignore
    │   ├── pytest.ini
    │   ├── requirements.txt        Runtime dependencies
    │   ├── requirements-dev.txt    Test dependencies
    │   └── tests/
    │       ├── conftest.py
    │       └── test_api.py
    ├── database/
    │   ├── Dockerfile
    │   └── init.sql            Schema created on first start
    └── frontend/
        ├── app.py              Flask application, server-rendered pages
        ├── api_client.py       HTTP client for the API service
        ├── templates/
        │   └── index.html
        ├── Dockerfile
        ├── .dockerignore
        ├── pytest.ini
        ├── requirements.txt        Runtime dependencies
        ├── requirements-dev.txt    Test dependencies
        └── tests/
            ├── conftest.py
            └── test_frontend.py
```

## Technology Stack

| Layer            | Technology                                  |
|------------------|---------------------------------------------|
| Frontend         | Python, Flask, Jinja2 templates             |
| API              | Python, Flask                               |
| Database         | PostgreSQL 16                               |
| Testing          | pytest                                      |
| Containerisation | Docker, Docker Compose (one image per service) |

## Prerequisites

To run the full application:

- Docker Engine and Docker Compose v2 (the `docker compose` command)
- Free local ports 8080, 5000 and 5432

To run the tests without containers:

- Python 3 with `venv` and `pip`
- Git

## Getting Started

### Run everything

From the repository root:

```bash
docker compose up --build
```

Then open:

| What             | URL                              |
|------------------|----------------------------------|
| Web application  | http://localhost:8080            |
| API health       | http://localhost:5000/health     |
| API readiness    | http://localhost:5000/ready      |
| API tasks        | http://localhost:5000/api/tasks  |

### Stop the application

```bash
docker compose down
```

### Reset to a clean database

`init.sql` runs only when the database starts with an empty data directory. To discard stored data and start over, remove the volumes as well:

```bash
docker compose down -v
docker compose up --build
```

### Configuration

Service settings such as ports, database connection details and service URLs are defined in `docker-compose.yml`. Review that file before changing ports or deploying anywhere other than a local machine. Do not commit real credentials; the repository is scanned for secrets by the pipeline and a leaked secret fails the build.

## Running the Tests

The unit tests do not need a database or any running service. Each service has its own virtual environment and test suite.

**API service**

```bash
cd services/api
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

**Frontend service**

```bash
cd services/frontend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

Each service has a `pytest.ini` and a `tests/conftest.py` with shared fixtures. In the SecureGitOps pipeline these tests must pass before an image is built.

## API Reference

Base URL: `http://localhost:5000`

| Method | Path              | Body              | Result                 |
|--------|-------------------|-------------------|------------------------|
| GET    | /health           |                   | 200                    |
| GET    | /ready            |                   | 200, or 503 if DB down |
| GET    | /api/tasks        |                   | 200, list of tasks     |
| POST   | /api/tasks        | {"title": "..."}  | 201, created task      |
| PATCH  | /api/tasks/<id>   | {"done": true}    | 200, or 404            |
| DELETE | /api/tasks/<id>   |                   | 204, or 404            |

### Examples

List tasks:

```bash
curl http://localhost:5000/api/tasks
```

Create a task:

```bash
curl -X POST http://localhost:5000/api/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Write the report"}'
```

Mark a task as done (replace `1` with a real task id):

```bash
curl -X PATCH http://localhost:5000/api/tasks/1 \
     -H "Content-Type: application/json" \
     -d '{"done": true}'
```

Delete a task:

```bash
curl -X DELETE http://localhost:5000/api/tasks/1
```

Check health and readiness:

```bash
curl http://localhost:5000/health
curl http://localhost:5000/ready
```

## Docker Notes

- Each service has its own `Dockerfile` and builds into its own image, so each can be scanned, signed and deployed independently.
- The `api` and `frontend` services each have a `.dockerignore` to keep tests, virtual environments and local files out of the image.
- Runtime and development dependencies are kept in separate files (`requirements.txt` and `requirements-dev.txt`), so test tooling is not shipped in the images.
- The `database` service has its own `Dockerfile` that adds `init.sql` to the PostgreSQL 16 image.

## Role in the SecureGitOps project

SecureGitOps is a final year project built on one idea: **one commit, one build ID, one place to see everything.** Every change is verified before it reaches the cluster, the pipeline is then attacked on purpose to prove the controls work, and every result is shown per commit on a dashboard.

This repository is the application under test. The following describes the wider design.

### Build flow

```
Commit -> Source gates -> Build image -> Image gates -> Registry
       -> gitops-config -> ArgoCD -> Kyverno -> k3s cluster
```

Every stage reports to the dashboard API, keyed by the git commit SHA.

### Pipeline gates

| Stage         | Tool       | Purpose                                      |
|---------------|------------|----------------------------------------------|
| Source gate   | Gitleaks   | Finds leaked secrets                         |
| Source gate   | Semgrep    | Finds insecure code                          |
| Source gate   | Trivy      | Checks dependencies                          |
| Build         | Docker     | Builds one image per service (unit tests must pass first) |
| Image gate    | Trivy      | Scans the image                              |
| Image gate    | Syft       | Generates the SBOM                           |
| Image gate    | Cosign     | Signs the image (keyless, Sigstore)          |
| Registry      | GHCR       | Stores signed images                         |
| Deployment    | ArgoCD     | Syncs the cluster from `gitops-config`, detects drift |
| Admission     | Kyverno    | Rejects unsigned images, privileged or root pods and untrusted registries |

The scanners run as parallel GitHub Actions jobs. Each posts a JSON report to the dashboard API as soon as it finishes. Application code and deployment configuration live in separate repositories, so a change to the application cannot silently change what the cluster runs. A bad deployment is rolled back with `git revert`.

### Security score

Every build receives a score from 0 to 100, starting at 100 and losing points by finding severity, with fixed penalties for a missing signature or missing SBOM. The proposal defines the gates as pass or fail and the score as a dashboard trend indicator. A hybrid gate (hard blockers for leaked secrets, invalid signatures and critical CVEs; scored thresholds for everything else) has been proposed and is subject to supervisor approval, with thresholds to be tuned by testing.

### Attack scenarios

This application is the target for six scripted, repeatable attack scenarios. Each is run 5 to 10 times against a baseline pipeline (gates off) and a protected pipeline (gates on).

| Scenario                     | Expected control                                      | Caught at   |
|------------------------------|-------------------------------------------------------|-------------|
| Leaked secret                | Gitleaks                                              | Commit or CI |
| Vulnerable dependency        | Trivy                                                 | CI          |
| Typosquatted dependency      | Dependency scan and SBOM review                       | CI          |
| Unsigned or tampered image   | Kyverno signature check                               | Admission   |
| Insecure workload            | Kyverno policy                                        | Admission   |
| Pipeline or config tampering | Branch protection, review, ArgoCD drift detection     | Repo or sync |

The `requirements.txt` files, the Dockerfiles and the deployment manifests are the surfaces these scenarios act on.

### Evaluation

Results are compared across a baseline pipeline, a strict pipeline and the hybrid score-based pipeline, using six measures: block rate, detection stage, time to detect, false positives, pipeline overhead and rollback time.

### Scope and limitations

All attacks target only the team's own lab infrastructure and repositories. The evaluation covers one application and scenarios chosen by the team, so the results describe this configuration and should not be read as a general claim about other environments.

## Troubleshooting

| Problem | Likely cause and fix |
|---------|----------------------|
| `port is already allocated` on startup | Another process uses 8080, 5000 or 5432. Stop it, or change the host port in `docker-compose.yml`. |
| `/ready` returns 503 | The API cannot reach the database. Check `docker compose ps` and `docker compose logs database`. The database may still be starting. |
| Frontend page loads but shows no tasks or an error | The API is down or unreachable. Check `http://localhost:5000/health` and `docker compose logs api`. |
| Schema changes in `init.sql` have no effect | `init.sql` runs only on first start. Run `docker compose down -v` to recreate the data volume. |
| `pytest` cannot find modules | Activate the service's virtual environment and install `requirements-dev.txt` from inside that service folder. |
| Changes do not appear after editing code | Rebuild the images with `docker compose up --build`. |

## Project Information

| Item        | Detail |
|-------------|--------|
| Project     | SecureGitOps, Final Year Project (Session 2023-2027) |
| Degree      | BS in Information Technology |
| Institution | School of Information Technology, Minhaj University Lahore |
| Domain      | DevSecOps, Cloud and Software Supply Chain Security |
| Type        | Research and Development |
| Duration    | 12 weeks, 6 phases |
| Supervisor  | Ms. Najam Us Sahar |
| Co-supervisor | Mr. Zeeshan Hassan |

### Team

| Member           | Responsibilities |
|------------------|------------------|
| Muhammad Ahmad   | Pipeline, GitOps, admission policies, dashboard |
| Hassan Khan      | Threat model, attack scenarios, attack simulation, vulnerability analysis |

Scope, evaluation metrics, the final report and the defense are shared.

## References

1. NIST, "Secure Software Development Framework (SSDF) Version 1.1," NIST SP 800-218, 2022.
2. OWASP Foundation, "OWASP Top 10 CI/CD Security Risks."
3. OpenSSF, "Supply-chain Levels for Software Artifacts (SLSA) Specification," slsa.dev.
4. Z. Newman, J. S. Meyers and S. Torres-Arias, "Sigstore: Software Signing for Everybody," ACM CCS, 2022.
5. OpenGitOps, "GitOps Principles v1.0.0," opengitops.dev.
6. Official documentation: GitHub Actions, ArgoCD, k3s, Kyverno, Trivy, Semgrep, Gitleaks, Syft, Cosign.
