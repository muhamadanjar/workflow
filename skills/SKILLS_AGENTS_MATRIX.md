# Skills × Agents Matrix

Tabel hubungan antara semua 7 skills dan agents yang relevan.

## Matrix Overview

| Skill | Primary Agent | Secondary Agent | Tertiary Agent | Best For |
|-------|---|---|---|---|
| **python-async-pro** | senior-backend-architect | expert-bug-hunter | production-code-reviewer | Celery design, task queues |
| **fastapi-clean-architecture** | senior-fullstack-architect | senior-backend-architect | production-code-reviewer | DDD, layering, architecture |
| **frontend-design-pro** | senior-frontend-reviewer | senior-backend-architect | production-code-reviewer | Components, state, Next.js |
| **pubsub-messaging** | senior-backend-architect | expert-bug-hunter | production-code-reviewer | Event design, message patterns |
| **mermaid-diagrams** | system-architect | Plan agent | - | System visualization |
| **redis-caching** | senior-backend-architect | expert-bug-hunter | production-code-reviewer | Cache strategy, optimization |
| **database-design** | senior-backend-architect | expert-bug-hunter | production-code-reviewer | Schema, performance, SQL |

---

## Detailed Matrix

### 1. python-async-pro

```
Task Type              Primary Agent                   When to Use
────────────────────────────────────────────────────────────────
Architecture           senior-backend-architect        Design task queue
Worker pool choice     senior-backend-architect        Prefork vs Gevent
RabbitMQ config        senior-backend-architect        Setup & optimization
Task retry logic       senior-backend-architect        Error handling
Worker failure         expert-bug-hunter               Debug specific issue
Code review            production-code-reviewer        Before deployment
Task dependency        Plan agent                      Complex workflow planning
```

**Example Usage:**
```python
# Question: "Should I use 10 workers or 50 for 5k tasks/day?"
# → Use: senior-backend-architect

# Question: "Workers crash randomly after 2 hours"
# → Use: expert-bug-hunter

# Question: "Review my Celery config before prod"
# → Use: production-code-reviewer
```

---

### 2. fastapi-clean-architecture

```
Task Type              Primary Agent                   When to Use
────────────────────────────────────────────────────────────────
DDD design             senior-fullstack-architect      Bounded contexts, aggregates
Repository pattern     senior-backend-architect        Abstraction & implementation
Layer separation       senior-backend-architect        Domain/Application/Infra split
Dependency inject      senior-backend-architect        IoC container design
Use case flow          senior-fullstack-architect      CQRS, event sourcing
API design             senior-backend-architect        Endpoint structure
Code review            production-code-reviewer        Architecture compliance
```

**Example Usage:**
```python
# Question: "Should OrderService handle payment or separate PaymentService?"
# → Use: senior-fullstack-architect

# Question: "How to structure repository for complex queries?"
# → Use: senior-backend-architect

# Question: "Review clean architecture compliance"
# → Use: production-code-reviewer
```

---

### 3. frontend-design-pro

```
Task Type              Primary Agent                   When to Use
────────────────────────────────────────────────────────────────
Component design       senior-frontend-reviewer        Structure & composition
State management       senior-frontend-reviewer        Zustand vs Context
Form handling          senior-frontend-reviewer        react-hook-form patterns
TypeScript safety      senior-frontend-reviewer        Type strictness
Performance opt        senior-frontend-reviewer        Re-render, bundle size
Next.js patterns       senior-backend-architect        Server/Client components
Data fetching          senior-backend-architect        SSR vs ISR vs CSR
Code review            production-code-reviewer        React best practices
```

**Example Usage:**
```typescript
// Question: "50 form fields in 5 pages. State management approach?"
// → Use: senior-frontend-reviewer

// Question: "Optimize homepage load (2.5MB initial load)"
// → Use: senior-frontend-reviewer (component level)
//    or senior-backend-architect (data fetching)

// Question: "Review React code quality"
// → Use: production-code-reviewer
```

---

### 4. pubsub-messaging

```
Task Type              Primary Agent                   When to Use
────────────────────────────────────────────────────────────────
Broker selection       senior-backend-architect        RabbitMQ vs Redis vs Kafka
Message pattern        senior-backend-architect        Topic vs fanout vs direct
Event design           senior-backend-architect        Event structure & schema
Scaling strategy       senior-backend-architect        Consumer groups, sharding
Message loss issue     expert-bug-hunter               Debug delivery failures
Dead letter queue      senior-backend-architect        DLQ strategy
Code review            production-code-reviewer        Handler validation
```

**Example Usage:**
```
# Question: "Which broker for 100k concurrent users notifications?"
# → Use: senior-backend-architect

# Question: "Messages not reaching all subscribers"
# → Use: expert-bug-hunter (debug message routing)

# Question: "Review pub/sub event handlers"
# → Use: production-code-reviewer
```

---

### 5. mermaid-diagrams

```
Task Type              Primary Agent                   When to Use
────────────────────────────────────────────────────────────────
System architecture    system-architect               Full system visualization
Flow design            Plan agent                     Process & workflow
Component relations    system-architect               Module dependencies
Deployment diagram     system-architect               K8s, containers, services
Sequence flow          system-architect               Interaction sequences
Database schema        system-architect               ER diagrams
Timeline planning      Plan agent                     Project roadmap
```

**Example Usage:**
```
# Question: "Create system architecture diagram for microservices"
# → Use: system-architect

# Question: "Plan implementation timeline and create roadmap"
# → Use: Plan agent

# Question: "Visualize 10-step payment flow"
# → Use: system-architect
```

---

### 6. redis-caching

```
Task Type              Primary Agent                   When to Use
────────────────────────────────────────────────────────────────
Cache strategy         senior-backend-architect        Which cache pattern?
TTL tuning             senior-backend-architect        Expiry strategy
Invalidation pattern   senior-backend-architect        Manual vs event-driven
Memory optimization    senior-backend-architect        Eviction policies
Hit ratio low          expert-bug-hunter               Debug miss rate
Connection timeout     expert-bug-hunter               Network/cluster issues
Code review            production-code-reviewer        Cache code safety
Performance issue      expert-bug-hunter               Throughput bottleneck
```

**Example Usage:**
```
# Question: "Cache hit rate 45%, how to improve?"
# → Use: expert-bug-hunter (systematic investigation)

# Question: "Best cache invalidation pattern for user profiles?"
# → Use: senior-backend-architect

# Question: "Review Redis caching code"
# → Use: production-code-reviewer
```

---

### 7. database-design

```
Task Type              Primary Agent                   When to Use
────────────────────────────────────────────────────────────────
Schema design          senior-backend-architect        Normalization level
Index strategy         senior-backend-architect        Which columns to index
Query optimization     senior-backend-architect        Joins vs denormalization
Stored procedures      senior-backend-architect        Complex business logic
Trigger design         senior-backend-architect        Audit & cascade
Transaction design     senior-backend-architect        Isolation level
Slow query            expert-bug-hunter               EXPLAIN ANALYZE debug
Deadlock issue        expert-bug-hunter               Transaction ordering
Migration safety       production-code-reviewer        Zero-downtime deploys
Security audit         production-code-reviewer        SQL injection, RLS
```

**Example Usage:**
```
# Question: "Design schema for users-posts-comments 1M records"
# → Use: senior-backend-architect

# Question: "Queries 5s slow, 10M rows, how to fix?"
# → Use: expert-bug-hunter (investigate with EXPLAIN)

# Question: "Deadlock every hour in production"
# → Use: expert-bug-hunter

# Question: "Audit migrations before deploy"
# → Use: production-code-reviewer
```

---

## Integration Workflows

### Workflow 1: Build Complete Backend

```
Step 1: Plan Architecture
├─ Agent: Plan agent
└─ Output: Architecture diagram

Step 2: Design FastAPI Service
├─ Agent: senior-fullstack-architect
├─ Using: fastapi-clean-architecture
└─ Output: Layer structure, use cases

Step 3: Design Database Schema
├─ Agent: senior-backend-architect
├─ Using: database-design
└─ Output: Normalized schema, indexes

Step 4: Add Caching Strategy
├─ Agent: senior-backend-architect
├─ Using: redis-caching
└─ Output: Cache invalidation pattern

Step 5: Add Background Jobs
├─ Agent: senior-backend-architect
├─ Using: python-async-pro
└─ Output: Task queue design

Step 6: Add Real-time Events
├─ Agent: senior-backend-architect
├─ Using: pubsub-messaging
└─ Output: Pub/Sub pattern

Step 7: Create System Diagram
├─ Agent: system-architect
├─ Using: mermaid-diagrams
└─ Output: Architecture visualization

Step 8: Code Review
├─ Agent: production-code-reviewer
└─ Output: Pre-deployment audit
```

---

### Workflow 2: Debug Performance Issue

```
Issue: API response time 3+ seconds

Step 1: Investigate Root Cause
├─ Agent: expert-bug-hunter
└─ Output: Identify bottleneck (slow query? cache miss? network?)

Step 2a: If Database Issue
├─ Agent: senior-backend-architect
├─ Using: database-design/PERFORMANCE.md
└─ Output: Index strategy or query refactor

Step 2b: If Cache Issue
├─ Agent: senior-backend-architect
├─ Using: redis-caching/PATTERNS_GUIDE.md
└─ Output: Cache invalidation or TTL adjustment

Step 2c: If Code Issue
├─ Agent: senior-frontend-reviewer (if frontend)
├─ Agent: senior-backend-architect (if backend)
└─ Output: Code optimization

Step 3: Validate Solution
├─ Agent: expert-bug-hunter
└─ Output: Performance baseline before/after

Step 4: Code Review
├─ Agent: production-code-reviewer
└─ Output: Safety & side effect check
```

---

### Workflow 3: Build Full Stack App

```
Phase 1: Architecture
├─ Plan agent → roadmap
└─ system-architect → system diagram

Phase 2: Backend
├─ senior-fullstack-architect → FastAPI structure
├─ senior-backend-architect → Database, cache, queues
└─ production-code-reviewer → Code audit

Phase 3: Frontend
├─ senior-frontend-reviewer → Component architecture
├─ Using: frontend-design-pro (shadcn/ui + Next.js 16)
└─ production-code-reviewer → React code audit

Phase 4: Integration
├─ senior-backend-architect → API contracts
├─ senior-frontend-reviewer → API consumption
└─ Production prep

Phase 5: Deployment
├─ production-code-reviewer → Final audit
└─ system-architect → Deployment diagram
```

---

## Agent Selection Decision Tree

```
┌─ New System?
│  ├─ YES → system-architect (full design)
│  └─ NO → Continue
│
├─ Architecture Decision?
│  ├─ Backend → senior-backend-architect
│  ├─ Frontend → senior-frontend-reviewer
│  ├─ Full System → system-architect or senior-fullstack-architect
│  └─ NO → Continue
│
├─ Performance Problem?
│  ├─ YES → expert-bug-hunter (systematic investigation)
│  └─ NO → Continue
│
├─ Code Review?
│  ├─ Pre-deployment → production-code-reviewer
│  ├─ Feedback loop → specialized agent (backend/frontend)
│  └─ NO → Continue
│
├─ Implementation Plan?
│  ├─ YES → Plan agent
│  └─ NO → Continue
│
└─ Specific Tech Help?
   ├─ FastAPI/Database/Cache → senior-backend-architect
   ├─ React/Next.js → senior-frontend-reviewer
   ├─ Debugging → expert-bug-hunter
   └─ Visualization → system-architect
```

---

## Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHEN TO USE EACH AGENT                                   │
├──────────────────────────────────────────────────────────┤
│ senior-backend-architect                                 │
│   → Backend design, DB, cache, queues, APIs             │
│   → Skills: python-async-pro, fastapi, redis, database  │
│                                                          │
│ senior-frontend-reviewer                                 │
│   → Frontend architecture, React, components, state      │
│   → Skill: frontend-design-pro                          │
│                                                          │
│ senior-fullstack-architect                               │
│   → Full DDD/CQRS, event sourcing, complex patterns     │
│   → Skill: fastapi-clean-architecture                   │
│                                                          │
│ expert-bug-hunter                                        │
│   → Debugging hard issues, root cause analysis           │
│   → For: performance, crashes, race conditions          │
│                                                          │
│ production-code-reviewer                                 │
│   → Pre-deployment audit, security, error handling       │
│   → For: Final code review before production            │
│                                                          │
│ system-architect                                         │
│   → Full system design, technology choices               │
│   → Skill: mermaid-diagrams for visualization          │
│                                                          │
│ Plan agent                                               │
│   → Implementation roadmap, project planning             │
│   → For: Complex multi-step projects                    │
└──────────────────────────────────────────────────────────┘
```

