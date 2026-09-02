# Architecture

The frontend is a Vite React single-page app. It sends bearer access tokens to the FastAPI API and keeps the current demo token in browser storage for simplicity. A production application should prefer an httpOnly cookie and add refresh-token rotation.

The backend uses SQLAlchemy's code-first models and a dependency-provided SQLAlchemy session. API handlers call small repository contracts; the `Sqlite*Repository` classes are the current adapters. A future Postgres adapter can implement the same contracts without changing route schemas.

## Data model

```text
User (id, username, password_hash, role)
Product (id, name, category, price)
SupportRequest (id, product_id -> Product, title, status, created_at, resolved_at)
Sale (id, product_id -> Product, quantity, revenue, sold_at)
```

Managers can read all records and metrics. Workers can read products and support requests and create support requests. The API's OpenAPI document at `/docs` is the source of truth for request and response shapes.