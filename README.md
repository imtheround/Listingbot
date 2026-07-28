# AutoSecure

Microsoft/Minecraft account security platform with Discord bot, REST API, and web dashboard.

## Architecture

```
autosecure/          ← Python backend (FastAPI + SQLAlchemy)
  api/               REST API routes
  core/              App lifecycle, config, database, state
  dashboard/         Legacy Jinja2 templates (to be replaced)
  db/                Database repositories
  models/            SQLAlchemy models
  services/          Business logic (payments, auth, etc.)
  tasks/             Background task scheduler
  bot/               Discord bot implementation

dashboard/           ← Next.js 15 frontend (separate process)
  app/               App Router pages
  components/        React components
  lib/               Utilities and API client
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16
- Redis 7+

## Quick Start

### Backend

```bash
# Install dependencies
pip install -e .

# Copy and edit environment
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn autosecure.core.app:app --reload --host 0.0.0.0 --port 8000
```

### Dashboard

```bash
cd dashboard
npm install
npm run dev
```

Opens at `http://localhost:3000` — proxies `/api/*` to the backend.

## API Docs

FastAPI auto-generated docs:
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Features

- Discord bot for account management and role sync
- License key generation and verification
- Blockchain payment validation (BTC)
- Email verification system
- Quarantine management
- Real-time notifications
- Leaderboard tracking

## Configuration

All configuration via environment variables (prefix `AUTOSECURE_`):

| Variable | Description |
|---|---|
| `AUTOSECURE_DATABASE_URL` | PostgreSQL connection string |
| `AUTOSECURE_REDIS_URL` | Redis connection string |
| `AUTOSECURE_SECRET_KEY` | JWT signing key |
| `AUTOSECURE_DISCORD_TOKEN` | Discord bot token |
| `AUTOSECURE_HYPIXEL_API_KEY` | Hypixel API key |

## Deployment

See [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md) for production setup on Ubuntu 24.04 with PostgreSQL, Redis, and nginx.
