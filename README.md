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