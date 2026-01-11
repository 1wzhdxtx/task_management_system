# Task Management System

A full-featured task management API built with FastAPI, demonstrating modern Python backend development best practices.

## Features

- **User Authentication** - JWT-based registration and login
- **Task Management** - Create, update, delete, and organize tasks
- **Categories & Tags** - Organize tasks with categories and multiple tags
- **Task Statistics** - Track completion rates and task distribution
- **RESTful API** - Clean, well-documented API with OpenAPI/Swagger
- **Web Interface** - Simple frontend for task management

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Database | MySQL / SQLite |
| ORM | SQLAlchemy 2.0 (async) |
| Authentication | JWT (python-jose) |
| Validation | Pydantic v2 |
| Migrations | Alembic |
| Testing | pytest + pytest-asyncio |
| Containerization | Docker & Docker Compose |

## Project Structure

```
task-management-system/
├── app/
│   ├── api/
│   │   ├── deps.py          # Dependency injection
│   │   └── v1/              # API v1 routes
│   ├── core/
│   │   ├── config.py        # Settings management
│   │   ├── database.py      # Database connection
│   │   ├── security.py      # JWT & password hashing
│   │   └── exceptions.py    # Custom exceptions
│   ├── models/              # SQLAlchemy models
│   ├── repositories/        # Data access layer
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── templates/           # Jinja2 templates
│   ├── static/              # CSS & JavaScript
│   └── main.py              # Application entry point
├── alembic/                 # Database migrations
├── tests/                   # Unit & integration tests
├── scripts/                 # Utility scripts
├── docker/                  # Docker configuration
├── docker-compose.yml       # Development setup
├── docker-compose.prod.yml  # Production setup
├── Dockerfile
├── Makefile
└── requirements.txt
```

## Quick Start

### Option 1: Local Development (SQLite)

```bash
# Clone the repository
git clone <repository-url>
cd task-management-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make dev
# or: pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env - SQLite is configured by default for local dev

# Initialize database
python -c "
import asyncio
from app.core.database import engine, Base
from app.models import *
async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(init())
"

# Run the server
make run
# or: uvicorn app.main:app --reload --port 8000
```

### Option 2: Docker (MySQL)

```bash
# Start all services
make docker-up
# or: docker compose up -d

# View logs
make docker-logs

# Stop services
make docker-down
```

### Access the Application

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Web interface |
| http://localhost:8000/docs | Swagger API documentation |
| http://localhost:8000/redoc | ReDoc API documentation |
| http://localhost:8000/health | Health check endpoint |

## Configuration

Create a `.env` file based on `.env.example`:

```env
# Application
APP_NAME=Task Management System
DEBUG=true

# Database (SQLite for local development)
DATABASE_URL=sqlite+aiosqlite:///./test.db

# Or MySQL
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=task_management

# JWT - CHANGE IN PRODUCTION!
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT token |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user |
| PUT | `/api/v1/users/me` | Update current user |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tasks` | List tasks (with pagination & filters) |
| POST | `/api/v1/tasks` | Create task |
| GET | `/api/v1/tasks/{id}` | Get task details |
| PUT | `/api/v1/tasks/{id}` | Update task |
| DELETE | `/api/v1/tasks/{id}` | Delete task |
| PATCH | `/api/v1/tasks/{id}/status` | Change task status |
| GET | `/api/v1/tasks/statistics` | Get task statistics |

### Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/categories` | List categories |
| POST | `/api/v1/categories` | Create category |
| GET | `/api/v1/categories/{id}` | Get category |
| PUT | `/api/v1/categories/{id}` | Update category |
| DELETE | `/api/v1/categories/{id}` | Delete category |

### Tags
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tags` | List tags |
| POST | `/api/v1/tags` | Create tag |
| GET | `/api/v1/tags/{id}` | Get tag |
| PUT | `/api/v1/tags/{id}` | Update tag |
| DELETE | `/api/v1/tags/{id}` | Delete tag |

## Testing

```bash
# Run all tests
make test

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=html

# Run unit tests only
make test-unit

# Run integration tests only
make test-int

# Quick test (stop on first failure)
make test-fast
```

## Database Migrations

```bash
# Run migrations
make migrate

# Create new migration
make migrate-new
# Enter migration message when prompted

# Rollback one migration
make migrate-down
```

## Development Commands

```bash
# Show all available commands
make help

# Format code
make format

# Run linting
make lint

# Clean cache files
make clean
```

## Docker Commands

```bash
# Build and start
make docker-up

# Start with Adminer (database UI)
make docker-up-tools

# View logs
make docker-logs

# Stop services
make docker-down

# Shell into app container
make docker-shell

# Remove everything (including volumes)
make docker-clean
```

## Production Deployment

1. **Set secure environment variables:**
```bash
export SECRET_KEY=$(openssl rand -hex 32)
export DB_PASSWORD=secure_database_password
export MYSQL_ROOT_PASSWORD=secure_root_password
```

2. **Deploy with production compose file:**
```bash
docker compose -f docker-compose.prod.yml up -d
```

3. **Run migrations:**
```bash
docker compose exec app alembic upgrade head
```

## Architecture

The application follows a layered architecture:

```
┌─────────────────────────────────────┐
│           API Layer                 │  ← Routes, request/response handling
│         (app/api/v1/)               │
├─────────────────────────────────────┤
│         Service Layer               │  ← Business logic
│        (app/services/)              │
├─────────────────────────────────────┤
│       Repository Layer              │  ← Data access, queries
│      (app/repositories/)            │
├─────────────────────────────────────┤
│         Model Layer                 │  ← SQLAlchemy ORM models
│        (app/models/)                │
├─────────────────────────────────────┤
│          Database                   │  ← MySQL / SQLite
└─────────────────────────────────────┘
```

## License

MIT License


