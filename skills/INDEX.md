# Skills Index & Quick Reference

Comprehensive guide to all 10 professional skills. Dengan agent recommendations untuk setiap skill.

## 📚 All Skills Overview

| # | Skill | Focus | Size | Agent |
|---|-------|-------|------|-------|
| 0 | **api-design** | REST/JSON contracts, auth, integrations, response helper | - | Backend |
| 1 | **python-async-pro** | Celery, RabbitMQ, task queues | 4KB | senior-backend-architect |
| 2 | **fastapi-clean-architecture** | FastAPI layering and pragmatic DDD | 10KB | senior-fullstack-architect |
| 3 | **frontend-design-pro** | React 19, Next.js 16, shadcn/ui, MUI | 18KB | senior-frontend-reviewer |
| 4 | **pubsub-messaging** | RabbitMQ, Redis pub/sub patterns | 12KB | senior-backend-architect |
| 5 | **mermaid-diagrams** | 12 diagram types, rendering, CI/CD | 30KB | system-architect |
| 6 | **redis-caching** | Data structures, patterns, optimization | 30KB | senior-backend-architect |
| 7 | **database-design** | PostgreSQL, DDL/DML, triggers, stored procedures | 40KB | senior-backend-architect |
| 8 | **code-review-pro** | Feasibility, features, security, error handling | 25KB | production-code-reviewer |
| 9 | **graphql-patterns** | Apollo, Hasura, federation, subscriptions, optimization | 35KB | senior-backend-architect |

---

## 🚀 Quick Start by Technology

### Backend (Python/FastAPI)

```
1. Start: fastapi-clean-architecture (DDD patterns)
   ↓ For background jobs:
2. Add: python-async-pro (Celery + RabbitMQ)
   ↓ For real-time features:
3. Add: pubsub-messaging (Pub/Sub patterns)
   ↓ For performance:
4. Add: redis-caching (Cache patterns)
   ↓ For data:
5. Add: database-design (PostgreSQL + triggers)

Recommended Agent: senior-backend-architect
```

### Frontend (React/Next.js)

```
1. Start: frontend-design-pro (Next.js 16 + shadcn/ui/MUI)
   ↓ For state management:
   - Integrated: Zustand patterns included
   ↓ For visualization:
2. Add: mermaid-diagrams (Architecture diagrams)
   ↓ For backend integration:
3. Reference: python-async-pro (task queues)
4. Reference: pubsub-messaging (real-time data)

Recommended Agent: senior-frontend-reviewer
```

### Full Stack (Backend + Frontend + Database)

```
1. Core Backend: fastapi-clean-architecture
2. Async: python-async-pro
3. Frontend: frontend-design-pro
4. Messaging: pubsub-messaging
5. Cache: redis-caching
6. Database: database-design
7. Diagrams: mermaid-diagrams (for documentation)

Recommended Agents:
- Architecture: senior-backend-architect
- Frontend: senior-frontend-reviewer
- Debugging: expert-bug-hunter
- Pre-prod: production-code-reviewer
```

---

## 📋 Skill Details

### 0. api-design
**Focus:** REST/JSON API contract design, with auth and third-party integration guides plus a legacy response helper.
**Canonical contract:** `api-design/SKILL.md`
**Helper:** `api-design/tools/` (response envelope without a JSON `status` field)
**Guides:** `api-design/README.md`

---

### 1. python-async-pro
**Focus:** Celery task queues, RabbitMQ, async job processing
**Files:** 4 guides
- README.md
- PIKA_GUIDE.md
- GUIDE.md (400+ lines)
- templates/ (FastAPI + Celery template)
- docker-compose (RabbitMQ + Redis + Celery)

**When to use:**
- Background job processing
- Scheduled tasks
- Long-running operations
- Async notifications

**Agent:** senior-backend-architect

---

### 2. fastapi-clean-architecture
**Focus:** FastAPI boundaries, clean layering, and domain modeling where useful
**Files:** 3 resources
- SKILL.md (workflow and architecture rules)
- README.md (entry point)
- ARCHITECTURE_GUIDE.md (layer examples and review checklist)

**When to use:**
- New FastAPI projects
- Complex business logic
- Scaling requirements
- Team onboarding

**Agent:** senior-fullstack-architect (DDD/CQRS expert)

---

### 3. frontend-design-pro
**Focus:** React 19, Next.js 16, shadcn/ui, MUI v6, Zustand, TypeScript
**Files:** 6 guides (92KB)
- README.md (updated)
- SHADCN_GUIDE.md (copy-paste components, Radix UI + Tailwind)
- MUI_GUIDE.md (Material Design, themes, data grid)
- NEXTJS16_GUIDE.md (Server Components, App Router, API routes)
- NEXTJS_SHADCN_SETUP.md (step-by-step integration)
- ZUSTAND_PATTERNS.md (state management)

**When to use:**
- React/Next.js projects
- Component library selection
- State management design
- Form handling

**Agent:** senior-frontend-reviewer

---

### 4. pubsub-messaging
**Focus:** RabbitMQ, Redis Pub/Sub, 12+ patterns, event-driven
**Files:** 3 guides (25KB)
- README.md
- PATTERNS_GUIDE.md (12+ patterns)
- rabbitmq_publisher.py
- redis_publisher.py
- requirements.txt

**When to use:**
- Real-time notifications
- Event-driven architecture
- Decoupled services
- Message broadcasting

**Agent:** senior-backend-architect

---

### 5. mermaid-diagrams
**Focus:** 12 diagram types, rendering, CI/CD integration
**Files:** 6 guides (80KB)
- README.md
- BASIC_DIAGRAMS.md (60+ examples)
- INTERMEDIATE_DIAGRAMS.md (40+ examples)
- ADVANCED_DIAGRAMS.md (30+ examples)
- BEST_PRACTICES.md
- CLI_REFERENCE.md

**Diagram types:**
- Flowcharts, sequences, class, state, ER, git, gantt
- Architecture, mindmaps, timeline, C4, pie charts

**When to use:**
- Architecture documentation
- Process visualization
- System design
- CI/CD pipeline diagrams

**Agent:** system-architect

---

### 6. redis-caching
**Focus:** Redis data structures, 12 caching patterns, optimization
**Files:** 6 guides (80KB)
- README.md
- BASICS.md (DDL, DML, constraints, sequences)
- INTERMEDIATE.md (joins, subqueries, CTEs, window functions)
- ADVANCED.md (stored procedures, triggers, transactions)
- PATTERNS.md (design patterns, normalization)
- PERFORMANCE.md (EXPLAIN ANALYZE, indexing)
- SECURITY.md (SQL injection, RLS, encryption)
- EXAMPLES.md (5 real-world schemas)

**Data structures:**
- String, Hash, List, Set, Sorted Set, HyperLogLog

**Patterns:**
- Cache-Aside, Write-Through, Write-Behind
- Refresh-Ahead, Sibling Cache, Session Cache
- Rate Limiting, Leaderboard, Counters, Pub/Sub
- Distributed Lock, Bloom Filter

**When to use:**
- Performance optimization
- Session storage
- Real-time leaderboards
- Rate limiting
- Queue/cache layer

**Agent:** senior-backend-architect

---

### 7. database-design
**Focus:** PostgreSQL, DDL/DML, stored procedures, triggers, optimization
**Files:** 8 guides (120KB)
- README.md
- BASICS.md (DDL, DML, constraints)
- INTERMEDIATE.md (joins, subqueries, CTEs, window functions)
- ADVANCED.md (stored procedures, triggers, transactions)
- PATTERNS.md (normalization, design patterns)
- PERFORMANCE.md (indexing, EXPLAIN ANALYZE)
- SECURITY.md (SQL injection, RLS, encryption)
- EXAMPLES.md (5 real-world schemas)

**Coverage:**
- 1NF/2NF/3NF normalization
- Stored procedures & PL/pgSQL
- Triggers (audit, validation, cascade)
- Window functions
- Partitioning
- JSON/JSONB
- Security patterns

**When to use:**
- Database design
- Schema optimization
- Query performance
- Complex data modeling

**Agent:** senior-backend-architect

---

### 8. code-review-pro
**Focus:** Multi-dimensional code review across feasibility, features, security, error handling
**Files:** 3 guides (25KB)
- README.md (4 dimensions, integration guide)
- PYTHON_FASTAPI_EXAMPLES.md (practical examples)
- QUICK_CHECKLIST.md (30-sec to 30-min review)

**Coverage:**
- Feasibility: architecture, dependencies, scalability, config
- Features: correctness, edge cases, concurrency, performance
- Security: OWASP Top 10, injection, auth, secrets, logging
- Error Handling: exception types, HTTP status, retry logic, fallbacks

**When to use:**
- Before merging to production
- New features (> 50 lines)
- Critical paths (auth, payments, data)
- Security audits
- Refactoring large changes

**Quick Process:**
1. 30-sec scan: check critical issues (hardcoded secrets, injection)
2. 5-min review: feasibility + features + security + errors
3. 15-min detailed: full checklist per dimension
4. 30-min ultra: use production-code-reviewer agent

**Agent:** production-code-reviewer (for ultra review)

---

### 9. graphql-patterns
**Focus:** Apollo Server/Client, Hasura, federation, subscriptions, performance
**Files:** 6 guides (35KB)
- README.md (overview, quick start)
- FUNDAMENTALS.md (types, resolvers, mutations, schema design)
- APOLLO_SERVER.md (server setup, authentication, error handling, plugins)
- APOLLO_CLIENT.md (React hooks, caching, subscriptions, custom hooks)
- ADVANCED.md (federation, subscriptions, fragments, directives, batch ops)
- OPTIMIZATION.md (N+1 queries, query complexity, pagination, monitoring)
- HASURA.md (instant APIs, permissions, webhooks, remote schemas, events)

**Coverage:**
- Apollo Server + Client (full stack)
- Schema design + composition (federation)
- Real-time subscriptions
- Performance optimization (caching, pagination, N+1 fixes)
- Hasura instant GraphQL APIs
- Permissions & row-level security

**When to use:**
- Building GraphQL APIs (Apollo Server)
- React/TypeScript clients with Apollo
- Real-time features (subscriptions)
- API federation (multiple services)
- Quick API generation (Hasura)
- Performance optimization

**Quick Process:**
1. Schema design → FUNDAMENTALS.md
2. Server implementation → APOLLO_SERVER.md
3. Client integration → APOLLO_CLIENT.md
4. Advanced patterns → ADVANCED.md
5. Optimization → OPTIMIZATION.md
6. No-code API → HASURA.md

**Agent:** senior-backend-architect

---

## 🔗 Skill Relationships

```
Database Design ────────────┐
                            ↓
Redis Caching ────────→ FastAPI Clean Architecture ←────── Python Async Pro
                            ↓
                      Pub/Sub Messaging
                            ↓
Frontend Design Pro ←────────┤
(React/Next.js)            │
       ↓                   │
Mermaid Diagrams ───────────┘
(Visualization)
```

**Data Flow:**
1. Database (PostgreSQL) stores data
2. FastAPI service retrieves and caches (Redis)
3. Async jobs update data (Celery)
4. Pub/Sub broadcasts changes (RabbitMQ/Redis)
5. Frontend receives updates (Next.js)
6. Architecture documented (Mermaid)

---

## 🎯 Common Implementation Patterns

### Pattern 1: Complete Backend Stack

```yaml
Layer 1 - Presentation:
  - FastAPI REST API
  - WebSocket connections
  
Layer 2 - Application:
  - FastAPI Clean Architecture
  - Use cases, DTOs, error handling
  
Layer 3 - Domain:
  - Entities, value objects
  - Domain services, repositories
  
Layer 4 - Infrastructure:
  - Database (PostgreSQL)
  - Cache (Redis)
  - Message Queue (RabbitMQ)
  
Layer 5 - Background:
  - Celery workers
  - Scheduled tasks
  - Event consumers
```

**Files to use:**
- fastapi-clean-architecture
- database-design
- redis-caching
- python-async-pro
- pubsub-messaging

---

### Pattern 2: Real-Time Frontend

```
Frontend (React/Next.js)
    ↓ API calls
Backend (FastAPI)
    ↓ Pub/Sub events
Redis / RabbitMQ
    ↓ Subscribe
Frontend (WebSocket)
    ↓ Updates in real-time
```

**Files to use:**
- frontend-design-pro (Next.js 16 + shadcn/ui)
- pubsub-messaging (event delivery)
- python-async-pro (background processing)

---

### Pattern 3: Performance Optimization

```
Slow Query
    ↓
Database Indexing (database-design)
    ↓ Still slow?
Add Query Cache (redis-caching)
    ↓ Still slow?
Background Pre-compute (python-async-pro)
    ↓
Monitor & Profile (EXPLAIN ANALYZE)
```

---

## 📖 Learning Path

### Beginner → Full Stack Developer

**Week 1-2: Foundations**
- Read: database-design/BASICS.md
- Read: fastapi-clean-architecture/SKILL.md
- Read: fastapi-clean-architecture/README.md
- Read: frontend-design-pro/README.md

**Week 3-4: Architecture**
- Read: fastapi-clean-architecture/ARCHITECTURE_GUIDE.md
- Read: database-design/PATTERNS.md
- Read: redis-caching/PATTERNS_GUIDE.md

**Week 5-6: Advanced**
- Read: python-async-pro/GUIDE.md
- Read: pubsub-messaging/PATTERNS_GUIDE.md
- Read: frontend-design-pro guides (all)

**Week 7-8: Performance & Security**
- Read: database-design/PERFORMANCE.md
- Read: database-design/SECURITY.md
- Read: redis-caching/SECURITY.md
- Read: AGENTS_INTEGRATION.md (use agents for review)

**Week 9-10: Visualization & Deployment**
- Read: mermaid-diagrams guides
- Create architecture diagrams
- Use agent: system-architect for validation

---

## 🤖 Agent Quick Reference

**For each skill, recommended agent:**

```
Skill                           Agent
─────────────────────────────────────────────
python-async-pro               senior-backend-architect
fastapi-clean-architecture     senior-fullstack-architect
frontend-design-pro            senior-frontend-reviewer
pubsub-messaging               senior-backend-architect
mermaid-diagrams               system-architect
redis-caching                  senior-backend-architect
database-design                senior-backend-architect
```

**When to use multiple agents:**

```
Task: Build e-commerce API + React frontend
─────────────────────────────────────────
1. Plan agent → design architecture
2. senior-backend-architect → API design, database schema
3. senior-frontend-reviewer → component architecture
4. system-architect → create system diagrams
5. production-code-reviewer → audit before deploy
```

---

## 📝 Documentation

All skills include:
- ✅ 100+ runnable code examples
- ✅ Good/bad pattern comparisons
- ✅ Real-world use cases
- ✅ Best practices checklists
- ✅ Anti-patterns to avoid
- ✅ Performance tips
- ✅ Security guidelines

---

## 📞 Support

**Need help?**
- Specific skill question → read relevant guide
- Architecture decision → use senior-backend-architect or system-architect
- Code review → use senior-frontend-reviewer or production-code-reviewer
- Debugging → use expert-bug-hunter
- Planning → use Plan agent

---

## 🔄 Skills Update Status

All skills updated as of: **2026-06-25**

- ✅ python-async-pro (Celery + Pika)
- ✅ fastapi-clean-architecture (DDD patterns)
- ✅ frontend-design-pro (Next.js 16 + shadcn/ui + MUI)
- ✅ pubsub-messaging (RabbitMQ + Redis)
- ✅ mermaid-diagrams (12 diagram types)
- ✅ redis-caching (patterns + monitoring)
- ✅ database-design (PostgreSQL professional)
- ✅ code-review-pro (4 dimensions + quick checklist) — **NEW**
- ✅ graphql-patterns (Apollo + Hasura, federation, optimization) — **COMPLETED**

**Total:** 10 skills, 60+ guides, 500+ code examples
