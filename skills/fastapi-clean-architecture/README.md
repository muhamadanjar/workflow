# FastAPI Clean Architecture Skill

Professional-grade FastAPI projects with strict clean architecture layer separation: Domain → Application → Presentation → Infrastructure.

**Based on:** usermanagement_api patterns (battle-tested in production)

## Architecture Overview

```
┌─────────────────────────────────────────┐
│      Presentation Layer (FastAPI)       │
│   Routes, Controllers, Serializers       │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│   Application Layer (Use Cases, DTOs)   │
│  Orchestrates domain & infrastructure   │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│    Domain Layer (Business Logic)        │
│ Entities, Services, Repositories        │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Infrastructure Layer (Implementations) │
│ Database, Cache, External Services      │
└─────────────────────────────────────────┘
```

## Project Structure

```
myproject/
├── app/
│   ├── main.py                 # FastAPI app + lifespan
│   ├── worker.py               # Celery worker setup
│   ├── celery_app.py           # Celery config
│   │
│   ├── domain/                 # ✅ Business Logic
│   │   ├── entities/           # Domain models (User, Order, etc)
│   │   ├── value_objects/      # Immutable objects (Email, Money)
│   │   ├── repositories/       # Repository interfaces
│   │   ├── services/           # Domain services
│   │   └── events/             # Domain events
│   │
│   ├── application/            # 🔄 Use Cases & Orchestration
│   │   ├── use_cases/          # Use case classes (Login, Register)
│   │   ├── dto/                # Data transfer objects
│   │   ├── services/           # Application services
│   │   └── tasks/              # Celery tasks
│   │
│   ├── presentation/           # 🌐 HTTP API Layer
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── users.py    # User endpoints
│   │   │   │   ├── auth.py     # Auth endpoints
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   └── middleware/         # CORS, auth, logging
│   │
│   ├── infrastructure/         # 🛠️ Implementations
│   │   ├── database/           # SQLAlchemy setup
│   │   │   ├── models/         # ORM models
│   │   │   ├── repositories/   # Repository implementations
│   │   │   └── migrations/
│   │   ├── cache/              # Redis cache
│   │   ├── email/              # SMTP/SES
│   │   ├── storage/            # S3/Local storage
│   │   └── external_api/       # Third-party APIs
│   │
│   ├── core/                   # 🔧 Cross-cutting Concerns
│   │   ├── config.py           # Settings management
│   │   ├── exceptions.py       # App-wide exceptions
│   │   ├── security.py         # Auth, passwords
│   │   └── logging.py          # Logging setup
│   │
│   └── config/                 # ⚙️ Configuration
│       └── settings.py         # Environment settings
│
├── tests/
│   ├── unit/                   # Domain logic tests
│   ├── integration/            # Database/API tests
│   └── e2e/                    # End-to-end tests
│
├── migrations/                 # Alembic migrations
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Key Principles

### 1. **Dependency Inversion**
Domain layer doesn't depend on anything. Infrastructure implements domain interfaces.

```python
# domain/repositories/user_repository.py (interface)
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User:
        pass

# infrastructure/database/repositories/user_repository.py (implementation)
class UserRepositoryImpl(UserRepository):
    async def get_by_id(self, user_id: int) -> User:
        # SQLAlchemy query
        pass
```

### 2. **Separation of Concerns**
- **Domain**: Pure business logic (no frameworks)
- **Application**: Use cases that orchestrate domain
- **Presentation**: HTTP concerns only
- **Infrastructure**: Technical implementations

### 3. **No Circular Dependencies**
```
Presentation → Application → Domain
                 ↓
           Infrastructure
             (implements)
```

### 4. **DTOs for Boundaries**
```python
# application/dto/user_dto.py
class UserDTO:
    id: int
    email: str
    created_at: datetime

# presentation/api/v1/users.py
@router.get("/users/{user_id}", response_model=UserDTO)
async def get_user(user_id: int, use_case: GetUserUseCase):
    return await use_case.execute(user_id)
```

## File Structure Details

### Domain Layer
```
domain/
├── entities/
│   ├── user.py          # User entity (id, email, password_hash)
│   └── order.py         # Order entity
├── value_objects/
│   ├── email.py         # Email (validated, immutable)
│   └── money.py         # Money (amount, currency)
├── repositories/
│   ├── user_repository.py    # Repository interface
│   └── order_repository.py
├── services/
│   ├── password_service.py   # Hash, verify passwords
│   └── notification_service.py
└── events/
    ├── user_registered.py    # Domain events
    └── order_created.py
```

### Application Layer
```
application/
├── use_cases/
│   ├── register_user.py         # UseCase class
│   ├── login_user.py
│   └── create_order.py
├── dto/
│   ├── user_dto.py              # Request/response DTOs
│   ├── order_dto.py
│   └── error_dto.py
├── services/
│   ├── user_service.py          # Orchestrates use cases
│   └── order_service.py
└── tasks/
    ├── send_welcome_email.py    # Celery tasks
    └── process_order.py
```

### Presentation Layer
```
presentation/
├── api/
│   ├── v1/
│   │   ├── users.py             # User endpoints
│   │   ├── auth.py              # Auth endpoints
│   │   ├── orders.py
│   │   └── __init__.py          # Router aggregation
│   └── dependencies.py          # FastAPI depends()
└── middleware/
    ├── cors.py                  # CORS config
    ├── auth.py                  # JWT middleware
    └── error_handler.py         # Exception handlers
```

### Infrastructure Layer
```
infrastructure/
├── database/
│   ├── models/
│   │   ├── user_model.py        # SQLAlchemy User model
│   │   └── order_model.py
│   ├── repositories/
│   │   ├── user_repository.py   # Implements domain interface
│   │   └── order_repository.py
│   └── session.py               # DB session management
├── cache/
│   ├── redis_cache.py           # Redis implementation
│   └── memory_cache.py          # Fallback in-memory
├── email/
│   ├── smtp_email.py            # SMTP implementation
│   └── ses_email.py             # AWS SES
└── external_api/
    ├── stripe_api.py            # Stripe payment
    └── twilio_api.py            # SMS service
```

## CLI Scaffolding

```bash
# Scaffold new project
python cli.py scaffold --name myproject

# Scaffold new domain entity
python cli.py scaffold-entity --name User

# Scaffold new use case
python cli.py scaffold-use-case --name LoginUser --entity User

# Scaffold new endpoint
python cli.py scaffold-endpoint --name users --entity User

# Validate architecture
python cli.py validate-architecture
```

## Quick Start

### 1. Scaffold Project
```bash
python ~/.claude/skills/fastapi-clean-architecture/cli.py scaffold --name myapi
cd myapi
pip install -r requirements.txt
```

### 2. Create Domain Entity
```bash
python cli.py scaffold-entity --name User
```

Generates:
- `app/domain/entities/user.py` — User entity
- `app/domain/repositories/user_repository.py` — Repository interface
- `app/domain/services/user_service.py` — Domain service
- Tests

### 3. Create Use Case
```bash
python cli.py scaffold-use-case --name RegisterUser --entity User
```

Generates:
- `app/application/use_cases/register_user.py`
- `app/application/dto/user_dto.py`
- Tests

### 4. Create API Endpoint
```bash
python cli.py scaffold-endpoint --name users --entity User
```

Generates:
- `app/presentation/api/v1/users.py` — Routes
- Request/response models
- Integration tests

## Testing Strategy

### Unit Tests (Domain)
Test business logic in isolation.
```python
# tests/unit/domain/test_user_entity.py
def test_user_password_hashing():
    user = User(email="test@example.com", password="secret123")
    assert user.password != "secret123"  # Hashed
    assert user.verify_password("secret123")
```

### Integration Tests (Infrastructure)
Test database, cache, external APIs.
```python
# tests/integration/test_user_repository.py
async def test_get_user_by_email(db_session):
    user = await repository.get_by_email("test@example.com")
    assert user.id == 1
```

### E2E Tests (Presentation)
Test full request → response flow.
```python
# tests/e2e/test_auth.py
async def test_register_user(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "password": "securepass"
    })
    assert response.status_code == 201
```

## Dependency Injection

```python
# presentation/api/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

def get_user_repository(session: AsyncSession = Depends(get_db)):
    return UserRepositoryImpl(session)

def get_user_use_case(repo = Depends(get_user_repository)):
    return GetUserUseCase(repo)

# presentation/api/v1/users.py
@router.get("/users/{user_id}")
async def get_user(user_id: int, use_case = Depends(get_user_use_case)):
    return await use_case.execute(user_id)
```

## Documentation Hierarchy

1. **README.md** — Project overview, quick start
2. **ARCHITECTURE.md** — Clean architecture principles
3. **API_DOCUMENTATION.md** — API endpoints (auto-generated)
4. **TESTING_GUIDE.md** — Testing strategy, examples
5. **DEPLOYMENT.md** — Docker, Kubernetes, production setup

## Files Included

- **ARCHITECTURE_GUIDE.md** — Detailed patterns and explanations
- **TESTING_GUIDE.md** — Unit/integration/E2E testing
- **CLI_REFERENCE.md** — All CLI commands
- Templates for all layers
- Docker setup (development + production)
- pytest fixtures and conftest
- Example implementations

## Next Steps

```bash
# 1. Scaffold project
python cli.py scaffold --name myapi --description "My API"

# 2. Create first entity
cd myapi
python cli.py scaffold-entity --name User

# 3. Create use case
python cli.py scaffold-use-case --name RegisterUser --entity User

# 4. Create API endpoint
python cli.py scaffold-endpoint --name auth --entity User --operations register,login

# 5. Run tests
pytest tests/

# 6. Start server
uvicorn app.main:app --reload
```

## Resources

- See **ARCHITECTURE_GUIDE.md** for detailed patterns
- See **TESTING_GUIDE.md** for testing examples
- Templates in `templates/` for reference implementations
