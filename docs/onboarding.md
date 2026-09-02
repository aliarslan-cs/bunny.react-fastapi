# Developer onboarding

1. Create and activate a Python 3.12 virtual environment.
2. Install `backend/requirements.txt` and run `python backend/scripts/seed.py`.
3. Start the API with `uvicorn app.main:app --app-dir backend --reload`.
4. Run `npm install` and `npm run dev` from `frontend`.
5. Use `manager / reganam` for dashboard access or `worker / rekrow` for the limited view.

For containers, use `podman compose up --build` or `docker compose up --build`. SQLite data is stored in the named `bunny-data` volume. `COLD_START=true` makes startup create the schema and insert demo data once.

Run backend checks with `pytest backend/tests`. Add schema changes as an Alembic migration before production use; the current code-first `create_all` is intentionally only a simple bootstrap.