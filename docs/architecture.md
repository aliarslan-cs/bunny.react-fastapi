# Architecture

The frontend is a Vite React single-page app. It sends bearer access tokens to the FastAPI API and keeps the current demo token in browser storage for simplicity. A production application should prefer an httpOnly cookie and add refresh-token rotation.

The backend uses SQLAlchemy's code-first models and a dependency-provided SQLAlchemy session. `Base.metadata.create_all(engine)` creates registered model tables that do not exist yet; it does not update existing schemas, so migrations will be added when schema evolution matters.

`Mapped[T]` is the typed ORM attribute, `mapped_column(...)` defines a database column, and `relationship()` defines a Python-side link. For example, a sale stores `product_id` as a foreign-key column; `sale.product` is an ORM relationship and is not an extra column.

API handlers depend on repository protocols rather than issuing SQL directly. The current `Sqlite*Repository` classes are adapters, and FastAPI dependency factories provide them with request-scoped sessions from `get_db()`. A PostgreSQL implementation can use the same contracts; basic SQLAlchemy queries usually do not need separate classes unless database-specific features differ.

FastAPI's `Depends` resolves dependencies per request. Repository dependencies chain to `get_db`, while authentication chains from the bearer token to `current_user` and then to manager authorization. `get_db()` yields one `Session` and closes it in `finally`.

SQLite uses `check_same_thread=False` because FastAPI may handle requests across threads. This does not create multiple databases: SQLite still uses one file and serializes writes. PostgreSQL is preferable when concurrent writes and scale increase.

Configuration is loaded by `pydantic-settings`: environment variables such as `DATABASE_URL` override `.env` values, which override class defaults. The health endpoint uses a database session and `SELECT 1` to report database availability. Passwords are verified against bcrypt hashes and are never stored as plaintext.

## Data model

```text
User (id, username, password_hash, role)
Product (id, name, category, price)
SupportRequest (id, product_id -> Product, title, status, created_at, resolved_at)
Sale (id, product_id -> Product, quantity, revenue, sold_at)
```

Managers can read all records and metrics. Workers can read products and support requests and create support requests. The API's OpenAPI document at `/docs` is the source of truth for request and response shapes.