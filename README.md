# Maple Syrup Online Store

Purpose: A maple syrup e-commerce storefront with catalog, cart, and checkout using Email Money Transfer (EMT) as the initial payment method.

Tech Stack: Django + PostgreSQL, GraphQL (Graphene), React (Create React App) + Apollo Client, Docker, Kubernetes

## Quick Start (Local)

### Backend

1. Create a virtual environment and install dependencies:
   - `pip install -r backend/requirements.txt`
2. Set env vars (example):
   - `DB_NAME=maple_store`
   - `DB_USER=maple_user`
   - `DB_PASSWORD=maple_pass`
   - `DB_HOST=localhost`
   - `DB_PORT=5432`
3. Run migrations and start server:
   - `python backend/manage.py migrate`
   - `python backend/manage.py runserver`

GraphQL endpoint: `http://localhost:8000/graphql/`

### Frontend

1. Install dependencies:
   - `cd frontend && npm install`
2. Start the app:
   - `npm start`

Frontend runs at `http://localhost:3000`

## Payment (EMT)

Checkout sets the order status to `PENDING_PAYMENT` and stores the EMT reference + payer email. Payment reconciliation can be completed later by an admin workflow.

## Shipping (Simple Radius)

Shipping is intentionally simple and tied to Blind River, Ontario via postal prefix:

- LOCAL_RADIUS (postal prefix `P0R`): $4.99
- ONTARIO: $7.99
- CANADA: $12.99
- INTERNATIONAL: $29.99

This keeps costs reasonable for nearby customers while still allowing supporters farther away to order.

## Kubernetes

Basic manifests live in the `k8s/` folder for backend, frontend, and postgres.

## Security

Security hardening measures are implemented including:
- Rate limiting on all API endpoints
- HTTPS/SSL support with HSTS
- Content Security Policy (CSP) headers
- Network policies for pod-to-pod communication
- Secure session and cookie settings
- Health check endpoints

**See [SECURITY.md](SECURITY.md) for comprehensive security documentation, production checklist, and best practices.**

## Testing

Comprehensive automated tests are available for both backend and frontend.

### Run All Tests

```bash
./scripts/test.sh
```

### Run Backend Tests Only

```bash
cd backend
./run_tests.sh
# Or directly: pytest -v
```

### Run Frontend Tests Only

```bash
cd frontend
./run_tests.sh
# Or directly: npm test -- --watchAll=false
```

**See [TESTING.md](TESTING.md) for detailed testing documentation, coverage reports, and best practices.**
