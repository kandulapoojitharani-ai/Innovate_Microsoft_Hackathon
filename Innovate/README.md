# PulseOps — Memory-driven DevOps Pipeline Agent

PulseOps is a full-stack hackathon prototype that demonstrates a DevOps agent concept: record deployments, assess changes with an explainable risk heuristic, retain incident memory, and surface safeguards before a release.

## Features
- Flask REST API with SQLite persistence and seeded demo records.
- Dashboard metrics, deployment timeline, incident memory, and agent activity.
- Explainable risk assessment API, including factors and recommendations.
- Create deployment simulations and complete running deployments.
- Add/search incidents; each new incident emits a learning event.
- Generic CI/CD webhook receiver example (`POST /webhooks/deployment`).
- Responsive UI built with HTML, CSS, and modular JavaScript.

## Requirements
- Python 3.10+
- macOS, Windows, or Linux

## Run on macOS
```bash
cd pulseops_fullstack
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```
Open http://127.0.0.1:5000

If port 5000 is busy, stop the other server or edit the `app.run` port in `app.py`.

## API quick reference
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/overview` | Metrics, recent deployments and events |
| GET | `/api/deployments` | Deployment list; optional `?environment=Production` |
| POST | `/api/deployments` | Assess and create a simulation |
| POST | `/api/deployments/<id>/complete` | Complete a running deployment |
| GET | `/api/incidents?q=timeout` | Search incident memory |
| POST | `/api/incidents` | Add an incident and create a learning event |
| POST | `/api/risk` | Assess a proposed change |
| GET | `/api/events` | Agent event stream |
| GET | `/api/memory/stats` | Incident counts by service |
| POST | `/webhooks/deployment` | Example generic webhook receiver |

### Example risk request
```bash
curl -X POST http://127.0.0.1:5000/api/risk \
  -H 'Content-Type: application/json' \
  -d '{"service":"checkout-api","change_type":"database migration","environment":"Production","change_size":"large"}'
```

### Example deployment simulation
```bash
curl -X POST http://127.0.0.1:5000/api/deployments \
  -H 'Content-Type: application/json' \
  -d '{"service":"checkout-api","commit_sha":"d7c3b10","environment":"Staging","change_type":"routine patch","change_size":"small"}'
```

## Architecture
- `app.py`: application factory and route registration.
- `database.py`: SQLite connection, schema and demo seed data.
- `routes/api.py`: REST endpoints.
- `routes/webhooks.py`: generic signed-webhook example.
- `services/risk_engine.py`: transparent baseline risk scoring.
- `services/agent.py`: assessment logging and incident-learning events.
- `templates/index.html`: application shell.
- `static/css/app.css`: responsive design system.
- `static/js/api.js`: API client.
- `static/js/ui.js`: rendering helpers.
- `static/js/app.js`: page behavior and interactions.

## Important prototype limitations
The seeded records and risk values are demo data. The risk engine is an explainable heuristic, **not a trained model and not a calibrated probability of failure**. The webhook endpoint only logs generic events; provider-specific signature validation and payload mapping need to be implemented. The app does not deploy, roll back, or modify infrastructure.

For a production-oriented extension, integrate Azure DevOps/GitHub Actions, collect telemetry from Azure Monitor/OpenTelemetry, add authentication and role-based authorization, use migrations and managed storage, build a labeled dataset, evaluate model quality, and require approval for remediation. Store secrets in environment variables or a secret manager.
