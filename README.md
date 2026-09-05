# Bunny full-stack boilerplate

A deliberately small starting point for a React and FastAPI application with authentication, role-based access, SQLite, seed data, and a manager dashboard. It is a foundation, not a finished business system: replace the repository implementations, add migrations, and grow the API around your domain.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
python -m scripts.seed
cd ..
uvicorn app.main:app --app-dir backend --reload

cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Demo accounts: `manager / reganam` and `worker / rekrow`.

## Podman or Docker

```bash
podman compose up --build
# or: docker compose up --build
```

The API is at `http://localhost:8000` and the frontend at `http://localhost:5173`. Set `CORS_ORIGINS` and `JWT_SECRET` in `.env` for non-local use. The development cold start seeds data when `COLD_START=true`.

## Observability (LGTM & OpenTelemetry)

The repository includes a complete observability stack powered by **OpenTelemetry** and the **LGTM** stack (Loki, Grafana, Tempo, Prometheus) with persistent named volumes and bidirectional cross-navigation.

### Start the observability stack

```bash
make obs-up
# Or directly:
podman compose -f deploy/observability/docker-compose.observability.yml up -d
# (or: docker compose -f deploy/observability/docker-compose.observability.yml up -d)
```

To run both the application and the observability stack together:
```bash
make dev-all
```

### Stop or inspect the observability stack

* **Follow container logs**: `make obs-logs`
* **Stop containers** (preserves volume data): `make obs-down`
* **Clean up containers and volumes**: `make obs-clean`

### Explore in Grafana

Open `http://localhost:3000` (Default credentials: `admin` / `admin`).

* **Dashboards**: Navigate to **Dashboards → Bunny → Bunny API Overview** for real-time Request Rate (RPS), Latency P50/P95, 5xx server errors, and live logs.
* **Explore Logs & Traces (Correlation)**:
  1. Open **Explore → Loki** and query `{service_name="bunny-api"} | json`.
  2. Click any highlighted `trace_id` in a log line to immediately open the full distributed trace waterfall in **Tempo**.
  3. In **Tempo**, use the `tracesToLogs` button to jump back into the exact log stream for that span.
* **Prometheus Metrics**: Available directly in Grafana or at `http://localhost:9090`.

For full architecture and design details, see [`docs/observability.md`](docs/observability.md).


## API

FastAPI publishes OpenAPI at `/docs` and `/redoc`.

| Method | Path | Access |
| --- | --- | --- |
| POST | `/auth/login` | Public |
| GET | `/auth/me` | Authenticated |
| GET | `/products` | Authenticated |
| GET | `/support-requests` | Authenticated |
| POST | `/support-requests` | Authenticated |
| GET | `/sales` | Manager |
| GET | `/metrics/summary` | Manager |
| POST | `/dev/seed` | Manager, development only |

Managers can see sales and metrics; workers can see products and support requests. Passwords are hashed with bcrypt. Access tokens are short-lived JWTs; refresh-token rotation is intentionally left as a next step.

## Project shape

`backend/app` contains API routes, models, schemas, security, database setup, and repository contracts. `backend/scripts/seed.py` owns repeatable cold-start data. `frontend/src` contains pages, API access, auth state, and styles. SQLite is code-first today; replace `app/repositories.py` and its provider to move to another database.

## Checks

```bash
pytest backend/tests
cd frontend && npm test
```