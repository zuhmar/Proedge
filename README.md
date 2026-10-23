# PRO EDGE

An NFL and NBA research platform. Phase 1 provides a working, offline-first foundation: Next.js App Router, strict TypeScript, Tailwind, a shadcn-compatible Radix button, Lucide icons, FastAPI, SQLAlchemy, Alembic and PostgreSQL. Recharts is installed for later data-backed visualizations; no chart invents statistics.

**All bundled teams, athletes and schedules are fictional demonstration records.** There are no live sports feeds, betting odds, projections, or accuracy claims in this phase. No paid services or API keys are needed.

## Run with Docker

Requires Docker Engine and the Compose plugin. From the repository root:

```bash
cp .env.example .env  # only if you do not already have a local .env
# Local development defaults only; never reuse them for production.
docker compose up --build -d --wait
```

The web service uses port 3000, API 8000, PostgreSQL 5432, SMTP 1025, and the local Mailpit inbox 8025. Ports bind to loopback. Open the application locally on port 3000. API documentation is at `/docs` on the API service. A fresh database is migrated and seeded automatically. Fixture date: **2026-10-23 (UTC)**. Sport, date and team search filters operate on API records. Game times follow the selected display timezone, default America/New_York.

A cloud network that intercepts TLS requires its trusted CA bundle during image builds:

```bash
BUILDX_CONFIG=/workspace/.buildx docker compose \
  -f docker-compose.yml -f infrastructure/docker/compose.cloud.yml build
docker compose up -d --wait
```

`CLOUD_CA_BUNDLE` can override the default Linux CA bundle path. The bundle is mounted as a build secret, with certificate validation retained. It is not embedded into application configuration.

Stop services with `docker compose down`. The database volume is retained. Never use `down -v` unless you intend to delete local data. Offline operation means no external sports calls after dependencies/images are installed; initial installation requires package registries.

## Native development

Requires Node 22+, Python 3.12+, Docker and Compose. Use the existing checkout; no Git worktree is needed.

```bash
npm ci --cache /workspace/.npm-cache
python -m venv .venv
.venv/bin/pip install --require-hashes -r services/analytics-api/requirements-dev.lock
./scripts/dev.sh
```

The script starts PostgreSQL and Mailpit, applies migrations, seeds demo data idempotently, checks API readiness, and starts Next.js with an API proxy. It stops its own API process when the frontend exits; database/mail containers remain. If using a different workspace, replace the npm cache path with a writable directory. API and frontend may also run independently:

```bash
# Terminal 1, from repository root
cd services/analytics-api
../../.venv/bin/alembic upgrade head
../../.venv/bin/python -m app.seed
../../.venv/bin/uvicorn app.main:app --reload --port 8000
# Terminal 2, from repository root
npm run dev
```

Custom `.env` values are loaded by Compose and `scripts/dev.sh`. For manual commands, export them into the shell first. The seed command is for demo databases only. Set `DEMO_MODE=false` on a new clean database for an empty workspace; it does not erase existing demo records.

## Accounts and security foundation

Register with an email and a password of at least 12 characters. Passwords use Argon2. Session tokens and password-reset tokens are stored hashed; session cookies are HttpOnly and SameSite=Lax. Authenticated mutations require the session's CSRF token. Origins are validated against the API host or the configured `ALLOWED_ORIGINS` JSON list. Registration never accepts an admin role. Watchlists and preferences require authentication and enforce ownership.

Forgot password sends a real message to the local Mailpit inbox. Follow its link to set a new password. Reset tokens expire after 30 minutes, are single-use, and revoke existing sessions. Mailpit is a local development sink; it does not send external email. Never expose it publicly. Admin health is role-restricted; no default admin credential is seeded. Operational admin controls arrive in later phases.

For public deployment, Phase 7 must add HTTPS, `COOKIE_SECURE=true`, explicit `WEB_ORIGIN` and `ALLOWED_ORIGINS`, credential rotation, authenticated TLS email delivery, account verification, distributed abuse protection, monitoring, backups and deployment review. The included limiter is per process and unsuitable as the sole public-facing abuse control. This foundation is not a completed production deployment.

## Validation

Start database and mail before integration tests:

```bash
docker compose up -d --wait db mail
cd services/analytics-api
../../.venv/bin/alembic upgrade head
../../.venv/bin/python -m app.seed
../../.venv/bin/python -m pytest -q
cd ../..
.venv/bin/ruff check services/analytics-api
npm run lint
npm run typecheck
npm test
npm run build
# With web and API running; uses installed system Chromium by default.
CHROMIUM_PATH=/usr/bin/chromium npm run test:e2e
# Else install Playwright Chromium and set CHROMIUM_PATH to that executable.
npm audit --omit=dev
.venv/bin/pip-audit --cache-dir /tmp/proedge-audit -r services/analytics-api/requirements.lock
```

API integration tests require a dedicated development/test database with the demo seed and Mailpit, and create and clean up unique test accounts. Browser tests create uniquely named local test accounts. Do not run these tests against production. See [PROGRESS.md](PROGRESS.md) for observed results and limitations.

## Layout

- `apps/web`: responsive dashboard, authentication forms, watchlists, preferences and unavailable states.
- `services/analytics-api`: API, normalized models, frozen migrations, demo seeding and integration tests.
- `packages/shared-types`: shared frontend contracts.
- `infrastructure/docker`: independent service images and cloud trust override.
- `tests/browser`: desktop/mobile functional tests.
- `docs`: architecture and data-source boundaries.

Next: Phase 2, permitted real data providers and CSV imports, with source/license verification before enabling access. The later analytics, odds, evaluation and production phases remain intentionally unimplemented.
