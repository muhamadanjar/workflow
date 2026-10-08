# Claude Code Skills Summary

Professional skill packages for full-stack development.

## Installed Skills

### 0. Code Review Pro (code-review-pro) — NEW
**For:** Pre-merge code review covering all critical dimensions
- **Dimensions:** Feasibility, Features, Security, Error Handling
- **Quick Process:** 30-sec critical scan → 5-min review → 15-min detailed → 30-min ultra
- **Location:** `~/.claude/skills/code-review-pro/`

**Quick Start:**
```bash
# Fast check: critical issues only
Review: hardcoded secrets, injection, circular deps, data loss risks

# 5-min review: all dimensions
Use QUICK_CHECKLIST.md for Feasibility → Features → Security → Error Handling

# Full review: use agent
/code-review ultra --comment
```

See: `code-review-pro/QUICK_CHECKLIST.md` for checklist template

---

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

### API Integration (api-integration)
**For:** Implementing or changing clients that consume an existing API across languages and frameworks
- **Contract source:** Read the matching OpenAPI specification or official API documentation before API-specific implementation
- **Fallback:** If documentation is unavailable, request a folder or resource to analyze; do not guess the contract
- **Location:** `skills/api-integration/SKILL.md`

---

### 2. FastAPI Clean Architecture (fastapi-clean-architecture)
**For:** FastAPI projects that need clear business and technology boundaries
- **Pattern:** Presentation → Application → Domain; Infrastructure implements domain contracts
- **Features:** Inspect-first architecture review, pragmatic domain modeling, explicit boundary mapping
- **Location:** `skills/fastapi-clean-architecture/`

**Documentation:**
- `SKILL.md` — Workflow and architecture rules
- `README.md` — Entry point
- `ARCHITECTURE_GUIDE.md` — Layer examples and review checklist

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

## Skill References and CLI Commands

### FastAPI Clean Architecture
Use `skills/fastapi-clean-architecture/SKILL.md` for the workflow and `ARCHITECTURE_GUIDE.md` for examples. This skill provides guidance; it does not include an executable scaffold CLI.

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

---

### 9. GraphQL Patterns (graphql-patterns)
**For:** Modern GraphQL API design with Apollo + Hasura
- **Server:** Apollo Server + authentication
- **Client:** React hooks, caching, real-time subscriptions
- **Advanced:** Federation, fragments, directives, batch ops
- **Optimization:** N+1 fixes, query complexity, pagination
- **Hasura:** Instant GraphQL from PostgreSQL
- **Location:** `~/.claude/skills/graphql-patterns/`

**Quick Start:**
```bash
# Server setup
Read: FUNDAMENTALS.md → APOLLO_SERVER.md

# Client integration
Read: APOLLO_CLIENT.md

# Production optimization
Read: OPTIMIZATION.md

# Quick GraphQL API
Read: HASURA.md
```

See: `graphql-patterns/ADVANCED.md` for federation + subscriptions

---

**All skills ready to use. Start building!**
