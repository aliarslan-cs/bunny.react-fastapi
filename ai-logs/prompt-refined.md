# Assessment and Recommended Additions

Your spec is a solid starting point and covers the major pieces. It’s clear about tech choices, goals (boilerplate, simple, extensible), and key features (authz/authn, seed data, containerization, tests). To make the repo immediately useful to other developers and to reduce ambiguity when someone implements it, add a few more concrete details and constraints. Below I list concise suggestions grouped by purpose: structure, backend, frontend, infra, testing, developer experience, and security/ops. After that I propose a clear folder structure you can confirm or tweak.

## Key Things to Add

- **Goals and scope:** Add a short paragraph to `README.md` explaining what this boilerplate is for, what it intentionally does not include, and how to extend it.

- **API contract:** Define a minimal OpenAPI/Swagger surface, including endpoints and request/response shapes, so the frontend and backend can be developed in parallel.

- **Auth model:** Define an explicit roles and permissions matrix for managers and workers, including which endpoints and fields each role can access.

- **Data model:** Add a concise ER diagram or list of entities and relationships for products, support requests, sales, users, and roles.

- **Seed data rules:** Document the format and location of seed data, how to run it, and the password policy for seeded users.

- **DB adapter interface:** Define the adapter contract, including methods and return types, so swapping SQLite for Postgres is straightforward.

- **CI hooks:** Add a basic lint and test workflow, such as GitHub Actions, to run unit tests and linters on pull requests.

- **Dev scripts:** Add npm, pnpm, or yarn scripts and Makefile or `package.json` scripts for common tasks such as start, build, test, seed, lint, and format.

- **Docs:** Add short developer onboarding steps covering local development, Docker/Podman, tests, and adding migrations or seed data.

## Backend (FastAPI)

- **Project layout:** Use explicit modules for `api`, `core`, `models`, `schemas`, `services`, `repositories`, `db`, `tests`, `migrations`, and `utils`.

- **Authentication:** Use JWT-based access and refresh tokens with defined expiry defaults and password hashing via bcrypt or Argon2.

- **Authorization:** Use role-based decorators or middleware, with example permission checks for each endpoint.

### Database

- **Code-first:** Use SQLModel or SQLAlchemy with Pydantic schemas. Include Alembic for migrations, even with SQLite.

- **Adapter:** Define repository interfaces such as `IProductRepo`, `ISupportRequestRepo`, and `ISalesRepo`, then provide a SQLite implementation. Keep adapter registration in the dependency-injection container.

### Seed and Cold Start

- Seed two users, `manager` and `worker`, with the reversed passwords specified in the original requirements.

- Seed sample products, support requests linked to products, and sales.

- Provide a CLI command or `make seed`, plus a protected REST endpoint for re-seeding in development.

### Testing

- Write unit tests for services and repositories using in-memory SQLite or a test database.

- Write integration tests for key endpoints such as auth, product listing, and support requests using `TestClient`.

- Add test-data fixtures and factory helpers.

> Note: Although you said “add them after I test the functionality,” still include test scaffolding and examples so adding tests is straightforward.

- **OpenAPI:** Enable documentation at `/docs` and `/redoc`.

## Frontend (React)

- **Project layout:** Use `src/components`, `src/pages`, `src/services/api`, `src/hooks`, `src/state` (or React Query), `src/utils`, and `src/styles`.

### Auth Flow

- Provide a login page with client-side validation for email or username and password, error handling, and a token-storage strategy. Prefer an `httpOnly` cookie over `localStorage` when supported by the backend.

- Add role-aware routing with protected routes and role-based UI for managers and workers.

### Data Fetching

- Use React Query or SWR for caching, background refresh, and optimistic updates.

- Use a centralized API client that reads tokens and handles the `401` refresh flow.

### UI

- Keep it minimal with a simple component library such as Tailwind CSS or plain CSS with a small component set.

- Provide a manager dashboard with charts and searchable tables. Limit worker pages to allowed views.

### Charts and Tables

- Use a lightweight charting library such as Chart.js, Recharts, or ApexCharts. Keep charts simple and mock-driven.

- Provide searchable tables with client-side filtering and server-side pagination endpoints.

- Use a form library such as React Hook Form with Zod or Yup for consistent validation.

## Data and Visualizations

### Sales Metrics

- Sales count and revenue aggregated by day, month, quarter, and year.

- Top N products by revenue.

- Time-series line charts and bar charts for comparisons.

### Support Metrics

- Requests by status: open, in progress, and resolved.

- Average resolution time and the 95th percentile for resolved requests.

- Requests per time bucket: month, quarter, and year.

- Optional heatmap or histogram for resolution times.

### Optional Visualizations

- Conversion funnel from product views to support requests to sales, if analytics are added later.

- Optional cohort or retention chart for repeat purchases.

- Simple KPI cards for total revenue, open requests, and average resolution time.

## Containerization and Infrastructure

### Dockerfiles

- Use separate Dockerfiles for the frontend (multi-stage build) and backend (Uvicorn/Gunicorn).

- Keep images small and reproducible.

### `docker-compose.yml`

- Define services for the frontend, backend, and optionally `db` for a non-SQLite database and Adminer.

- SQLite may not need a database container. Include a placeholder or comment explaining how to switch to Postgres.

### Podman Instructions

- Add a README section with `podman compose` or `podman play kube` instructions and example build and run commands.

### Development and Production

- Add `docker-compose.override.yml` for development mounts and hot reload.

### Entrypoints

- Configure the backend entrypoint to run migrations and seeds on the first cold start via an environment variable.

## Security and Operations

- **Secrets:** Use `.env` with `.env.example` and do not commit secrets.

- **Password hashing:** Use bcrypt or Argon2; never store plaintext passwords.

- **CORS:** Configure explicit allowed origins for development and production.

- **Rate limiting:** Add simple middleware or document it as a future addition.

- **Logging:** Use structured logs and request IDs in the backend.

- **Health checks:** Add a `/health` endpoint for readiness and liveness checks.

## Developer Experience

- **Scripts:** Add `make dev` to run `podman compose up --build`, along with `make build`, `make test`, `make seed`, and `make lint`, plus equivalent npm scripts where appropriate.

- **Linting and formatting:** Use ESLint and Prettier for the frontend; Black, isort, and flake8 (or equivalent tools) for the backend.

- **Editor config:** Add `.editorconfig` and recommended VS Code settings to the README.

- **Contribution guide:** Add a short `CONTRIBUTING.md` with branch and pull-request rules and local test instructions.

## Minimal API Surface

Example endpoints:

```text
POST /auth/login              # Returns access and refresh tokens
POST /auth/refresh
GET  /products                 # Paginated
GET  /products/{id}
GET  /support-requests         # Filterable; role-aware results
POST /support-requests
GET  /sales                    # Manager only; supports chart aggregation
GET  /metrics/support/summary  # Average/95th percentile resolution time and counts
```

## Proposed Folder Structure

Below is a concrete folder layout you can confirm or adjust. I split frontend/backend clearly and include dev infra and docs.

```text
/ (repo root)
├─ README.md
├─ .env.example
├─ docker-compose.yml
├─ docker-compose.override.yml
├─ Makefile
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ infra/
│  └─ podman.md
├─ backend/
│  ├─ Dockerfile
│  ├─ pyproject.toml / requirements.txt
│  ├─ alembic/ (migrations)
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ core/
│  │  │  ├─ config.py
│  │  │  └─ security.py
│  │  ├─ api/
│  │  │  ├─ v1/
│  │  │  │  ├─ deps.py
│  │  │  │  ├─ auth.py
│  │  │  │  ├─ products.py
│  │  │  │  ├─ support_requests.py
│  │  │  │  └─ sales.py
│  │  ├─ models/        # SQLAlchemy/SQLModel models
│  │  ├─ schemas/       # Pydantic schemas
│  │  ├─ services/      # business logic
│  │  ├─ repositories/  # DB adapter interfaces + sqlite impl
│  │  ├─ db/
│  │  │  ├─ base.py
│  │  │  └─ session.py
│  │  ├─ tests/
│  │  │  ├─ unit/
│  │  │  └─ integration/
│  │  └─ utils/
│  └─ scripts/
│     ├─ seed.py
│     └─ run_migrations.sh
├─ frontend/
│  ├─ Dockerfile
│  ├─ package.json
│  ├─ public/
│  └─ src/
│     ├─ main.tsx / index.tsx
│     ├─ App.tsx
│     ├─ pages/
│     │  ├─ Login/
│     │  ├─ Dashboard/
│     │  ├─ Products/
│     │  └─ SupportRequests/
│     ├─ components/
│     │  ├─ auth/
│     │  ├─ charts/
│     │  └─ tables/
│     ├─ services/
│     │  └─ apiClient.ts
│     ├─ hooks/
│     ├─ styles/
│     └─ tests/
└─ docs/
   ├─ architecture.md
   └─ onboarding.md
```

## README Clarifications

- **Run locally:** `make dev` or `podman compose -f docker-compose.yml up --build`

- **Run with Podman:** Include short commands and a note about `podman compose` versus `podman play kube`.

- **Seed data:** `python backend/scripts/seed.py` or `make seed`

- **Switch databases:** Document the environment variables and point to `backend/app/repositories` for new adapters.

- **Run tests:** `pytest backend/app/tests` and `npm test` for the frontend.

## Final Notes and Trade-offs

- Keep the boilerplate minimal: prefer clear examples over full production features. For example, include a simple JWT refresh flow but skip complex token revocation lists.

- Keep the database adapter contract explicit and small, with a few CRUD methods per aggregate, so swapping databases remains low friction.

- Provide seed data and a cold-start script that runs only in development mode or when `COLD_START=true` is set.

- Keep charts and tables client-side simple and rely on backend aggregation endpoints for heavier queries.

## Next Step: Confirm the Folder Structure

I included a proposed folder structure above. Choose one of the following:

1. Use that structure exactly and produce a `README.md`, `docker-compose.yml` skeleton, and a short backend/frontend scaffold with a file list and minimal content.

2. Tweak the structure by specifying what to change.

3. Keep the structure and also generate the API contract (OpenAPI specification) and database schema.

Select 1, 2, or 3, and I’ll produce the next artifact.