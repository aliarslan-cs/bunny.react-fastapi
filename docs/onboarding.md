# Developer onboarding

1. Create and activate a Python 3.12 virtual environment.
2. Install `backend/requirements.txt`, then run `cd backend` followed by `python -m scripts.seed`.
3. Start the API with `uvicorn app.main:app --app-dir backend --reload`.
4. Run `npm install` and `npm run dev` from `frontend`.
5. Use `manager / reganam` for dashboard access or `worker / rekrow` for the limited view.

For containers, use `podman compose up --build` or `docker compose up --build`. SQLite data is stored in the named `bunny-data` volume. `COLD_START=true` makes startup create the schema and insert demo data once.

Run backend checks with `pytest backend/tests`. Add schema changes as an Alembic migration before production use; the current code-first `create_all` is intentionally only a simple bootstrap.

## Backend concepts

`config.py` creates a typed `Settings` object. `DATABASE_URL` selects the database, while `COLD_START` controls whether startup invokes the idempotent seed function. In containers, Compose sets the database URL to `/app/data/bunny.db`, which is backed by the named `bunny-data` volume.

`db.py` creates the SQLAlchemy engine, `SessionLocal`, and declarative `Base`. Routes receive sessions, repositories, and authenticated users through `Depends`; they do not need to know how SQLite connections are created.

`repositories.py` contains the database adapter boundary. Protocols describe operations such as `ProductRepository.list()`, and SQLite classes implement them. Factory functions such as `get_user_repository()` receive a session through `Depends(get_db)` and return the appropriate implementation.

FastAPI automatically generates `/docs`, `/redoc`, and `/openapi.json` from route declarations and Pydantic schemas. `/health` checks the database. Workers can access products and support requests; managers can also access sales and metrics.

The login request sends a password to the backend over HTTPS in production. The backend verifies it with bcrypt, creates a short-lived JWT, and uses the token on later requests. The current demo stores the frontend token in browser storage for simplicity; a production application should prefer an httpOnly cookie and add refresh-token rotation.