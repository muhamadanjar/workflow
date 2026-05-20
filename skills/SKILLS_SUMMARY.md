# Claude Code Skills Summary

Professional skill packages for full-stack development.

## Installed Skills

### 1. Python Async/Background Tasks (python-async-pro)
**For:** FastAPI & Django projects with async task handling
- **Broker Options:**
  - FastAPI: RabbitMQ + Pika (default) or Redis
  - Django: Redis (configurable)
- **Features:** CLI scaffolding, templates, Docker Compose, Pika configuration
- **Location:** `~/.claude/skills/python-async-pro/`

**Quick Start:**
```bash
python ~/.claude/skills/python-async-pro/cli.py scaffold --name myapi --framework fastapi
```

See: `python-async-pro/PIKA_GUIDE.md` for FastAPI + RabbitMQ + Pika setup

---

### 2. FastAPI Clean Architecture (fastapi-clean-architecture)
**For:** Production-grade FastAPI projects with clean architecture
- **Pattern:** Domain → Application → Infrastructure → Presentation
- **Based on:** usermanagement_api (battle-tested patterns)
- **Features:** Scaffolding, templates, testing guides, CLI validation
- **Location:** `~/.claude/skills/fastapi-clean-architecture/`

**Quick Start:**
```bash
python ~/.claude/skills/fastapi-clean-architecture/cli.py scaffold --name myproject
```

**Documentation:**
- `README.md` — Project structure & quick start
- `ARCHITECTURE_GUIDE.md` — Detailed patterns & principles

---

### 3. Frontend Design Pro (frontend-design-pro)
**For:** React/Next.js projects with modern design patterns
- **Tech Stack:** Tailwind CSS v4 + MUI v6 + Zustand
- **Features:** Component library, state management patterns, design system
- **Location:** `~/.claude/skills/frontend-design-pro/`

**Quick Start:**
```bash
npx create-next-app@latest myapp --typescript --tailwind
# Copy components & stores from templates
```

**Documentation:**
- `README.md` — Tech stack, component examples, setup
- `ZUSTAND_PATTERNS.md` — State management patterns (10+ examples)

---

## Architecture Overview

```
Backend (FastAPI + Clean Architecture)
├── Domain Layer (business logic)
├── Application Layer (use cases)
├── Presentation Layer (HTTP API)
└── Infrastructure Layer (database, cache, APIs)
         ↕️ API (JSON)
Frontend (React/Next.js + Zustand)
├── Components (Tailwind + MUI)
├── State (Zustand stores)
├── Hooks (custom logic)
└── Types (TypeScript)
```

## Project Templates

### FastAPI Project
```
myproject/
├── app/
│   ├── domain/          # Entities, repositories, services
│   ├── application/     # Use cases, DTOs, services
│   ├── presentation/    # Routes, controllers
│   ├── infrastructure/  # Database, cache, external APIs
│   └── core/           # Config, exceptions, security
├── tests/
├── migrations/
└── docker-compose.yml
```

### Frontend Project
```
myapp/
├── src/
│   ├── components/     # UI components (Tailwind + MUI)
│   ├── stores/        # Zustand stores (state)
│   ├── hooks/         # Custom React hooks
│   ├── types/         # TypeScript definitions
│   └── app/           # Next.js routes
├── __tests__/
└── tailwind.config.ts
```

## CLI Commands

### FastAPI Clean Architecture
```bash
# Scaffold new project
python cli.py scaffold --name myproject

# Scaffold domain entity
python cli.py scaffold-entity --name User

# Scaffold use case
python cli.py scaffold-use-case --name LoginUser

# Scaffold API endpoint
python cli.py scaffold-endpoint --name users

# Validate architecture
python cli.py validate-architecture
```

### Python Async
```bash
# Scaffold FastAPI + Celery
python cli.py scaffold --name myapi --framework fastapi --broker rabbitmq

# Validate configuration
python cli.py validate --config celery.conf.json

# Start worker
python cli.py worker --queues default,high --concurrency 4

# Start scheduler
python cli.py beat

# Monitor
python cli.py flower
```

## Key Technologies

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14+ | React framework |
| **Styling** | Tailwind CSS v4 | Utility-first CSS |
| **Components** | MUI v6 | Material Design |
| **State** | Zustand | Lightweight state management |
| **API** | FastAPI | Async Python framework |
| **Architecture** | Clean | Domain-driven design |
| **Background** | Celery | Task queue (RabbitMQ/Redis) |
| **Persistence** | SQLAlchemy | ORM |
| **Testing** | pytest + @testing-library | Unit & integration tests |

## Best Practices

### Backend (FastAPI)
1. **Strict layer separation** — No circular dependencies
2. **Dependency inversion** — Domain depends on nothing
3. **Repository pattern** — Abstract data access
4. **Use cases** — One operation per class
5. **DTOs** — For API boundaries

### Frontend (React/Next.js)
1. **Component composition** — Small, reusable components
2. **Selective store subscriptions** — Use selectors
3. **Type safety** — Strict TypeScript
4. **Custom hooks** — Extract logic
5. **Performance** — Optimize re-renders

### Tasks (Celery)
1. **Idempotent tasks** — Safe to run multiple times
2. **Queue routing** — Different priorities
3. **Proper timeouts** — Soft + hard limits
4. **Error handling** — Retry logic with backoff
5. **Monitoring** — Flower UI + metrics

## Common Workflows

### Create New Feature (Backend)

1. **Define domain entity:**
   ```bash
   python cli.py scaffold-entity --name Product
   ```

2. **Create use case:**
   ```bash
   python cli.py scaffold-use-case --name CreateProduct
   ```

3. **Scaffold API endpoint:**
   ```bash
   python cli.py scaffold-endpoint --name products
   ```

4. **Implement repository** → Database layer
5. **Write tests** → Unit + integration
6. **Document** → API docs

### Create New Component (Frontend)

1. **Design in Figma/Miro**
2. **Create component** (Tailwind + MUI)
3. **Create Zustand store** (if state needed)
4. **Create custom hook** (combine logic)
5. **Integrate in page**
6. **Test** → Unit + integration
7. **Document** → Storybook

## Documentation Hierarchy

### Backend
1. **README.md** — Quick start
2. **ARCHITECTURE_GUIDE.md** — Detailed patterns
3. **Code comments** — Why, not what
4. **API docs** — Auto-generated (FastAPI)

### Frontend
1. **README.md** — Tech stack, setup
2. **ZUSTAND_PATTERNS.md** — State management
3. **Component library** — Storybook
4. **Type definitions** — TypeScript interfaces

## Testing Strategy

### Unit Tests (Domain Logic)
- Pure business logic
- No frameworks
- Fast, isolated

### Integration Tests (API)
- Database queries
- API endpoints
- Real dependencies

### E2E Tests (UI)
- User workflows
- Full request → response
- Browser testing

## Deployment

### Docker
```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up
```

### Kubernetes
See deployment manifests in skill packages

### CI/CD
GitHub Actions / GitLab CI examples included

## Performance

### Backend
- Async/await throughout
- Database query optimization
- Caching (Redis)
- Background tasks (Celery)

### Frontend
- Code splitting
- Image optimization
- Store selectors
- Memoization

## Monitoring

### Backend
- Flower (task monitoring)
- Application logs
- Database performance
- API metrics

### Frontend
- Error boundaries
- Console logging
- Performance monitoring
- User analytics

## Support & Resources

1. **Read GUIDE.md** in each skill
2. **Check templates/** for examples
3. **Review examples/** for patterns
4. **Read code comments** for specifics
5. **Test patterns** locally first

## Next Steps

1. **Choose your stack:**
   - Backend: FastAPI + Clean Architecture
   - Frontend: React/Next.js + Zustand
   - Tasks: Celery + RabbitMQ (FastAPI) or Redis (Django)

2. **Scaffold initial project:**
   ```bash
   python cli.py scaffold --name myproject
   ```

3. **Review architecture/patterns:**
   ```bash
   cat ARCHITECTURE_GUIDE.md  # Backend
   cat ZUSTAND_PATTERNS.md    # Frontend
   ```

4. **Implement features:**
   - Use scaffolding for consistency
   - Follow patterns from templates
   - Write tests
   - Document as you go

5. **Deploy:**
   - Use Docker Compose locally
   - Deploy to Kubernetes/cloud
   - Set up monitoring
   - Configure CI/CD

---

**All skills ready to use. Start building!**
