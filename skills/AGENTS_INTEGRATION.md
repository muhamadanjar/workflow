# Agents Integration with Skills

Guide untuk menggunakan built-in agents dengan skills yang sudah dibuat.

## Available Agents

Agents in `agents/` yang tersedia:

- **senior-fullstack** - Implementasi fitur lintas frontend dan backend
- **senior-fullstack-architect** - Menyelaraskan arsitektur fitur lintas frontend, backend, dan data
- **system-architect** - Batas layanan, integrasi antarsistem, deployment, dan operasi
- **senior-backend-architect** - Desain dan implementasi API, domain, data, dan integrasi backend
- **senior-frontend-architect** - Arsitektur aplikasi frontend, komponen, state, dan data fetching
- **frontend-engineer** - Implementasi frontend
- **production-code-reviewer** - Review kode umum dengan fokus khusus React/Next.js/TypeScript
- **security-auditor** - Audit kode, dependency, secret, dan konfigurasi keamanan
- **qa-engineer** - Strategi dan pelaporan pengujian
- **expert-bug-hunter** - Debugging kompleks dan root-cause analysis
- **document-engineer** - Dokumentasi teknis

**Plan agent** adalah agent bawaan untuk menyusun rencana implementasi.

## Skills & Recommended Agents

### 1. python-async-pro (Celery + RabbitMQ)

**Related Agents:**
- **senior-backend-architect** ✅ BEST
  - Design task queue architecture
  - Redis vs RabbitMQ comparison
  - Celery configuration optimization
  - Worker execution and concurrency strategy
  
- **expert-bug-hunter**
  - Debug worker failures
  - Investigate message queue issues
  - Trace connection timeouts
  
- **production-code-reviewer**
  - Review Celery task code
  - Check error handling
  - Validate retry logic

**Usage:**
```
"I'm implementing Celery with RabbitMQ for background jobs. 
Should I use Prefork, Solo, or Gevent worker pool?
Which one is best for 10k daily tasks?"

→ Use: senior-backend-architect
```

---

### 2. fastapi-clean-architecture

**Related Agents:**
- **senior-backend-architect** ✅ BEST
  - Domain-driven design and bounded contexts
  - Repository and layer boundaries
  - Dependency injection, CQRS, and event sourcing where appropriate
  
- **production-code-reviewer**
  - Audit domain/application/infrastructure layers
  - Check service isolation
  - Validate dependency inversion

**Usage:**
```
"I'm building an e-commerce system with clean architecture.
How should I organize: Order aggregate, OrderService, OrderRepository?
Where does payment logic go?"

→ Use: senior-backend-architect (for backend architecture and API design)
```

---

### 3. frontend-design-pro (React/Next.js + shadcn/ui + MUI + Zustand)

**Related Agents:**
- **senior-frontend-architect** ✅ BEST for frontend architecture
  - Component architecture
  - TypeScript type safety
  - State management patterns
  - Zustand store design
  - Server/client boundaries, API integration, and performance strategy
  
- **production-code-reviewer**
  - React component and hook review
  - Type safety and accessibility findings
  - Memory leak and performance issues

**Usage:**
```
"I have 50 form inputs across multiple pages. 
Should I use react-hook-form + Zustand or Context API?"

→ Use: senior-frontend-architect
```

```
"My Next.js app loads 2MB of data on home page.
How to optimize with Server Components and ISR?"

→ Use: senior-frontend-architect (for data fetching strategy)
→ Use: production-code-reviewer (to review the components)
```

---

### 4. pubsub-messaging (RabbitMQ + Redis Pub/Sub)

**Related Agents:**
- **senior-backend-architect** ✅ BEST
  - Message broker selection
  - Event-driven architecture
  - Pub/Sub vs message queue comparison
  - Scaling messaging system
  
- **expert-bug-hunter**
  - Message delivery failures
  - Dead letter queue debugging
  - Consumer lag issues
  
- **production-code-reviewer**
  - Event handler validation
  - Message serialization safety

**Usage:**
```
"Should I use RabbitMQ topic exchange or Redis pub/sub 
for real-time notifications to 100k users?"

→ Use: senior-backend-architect
```

---

### 5. mermaid-diagrams

**Related Agents:**
- **system-architect** ✅ BEST for system-level diagrams
  - Design system architecture diagrams
  - Create flow diagrams
  - Visualize data flow
  
- **Plan agent**
  - Create architecture diagrams for plans
  - Visualize implementation roadmap

**Usage:**
```
"Create architecture diagram for microservices system:
API Gateway → Auth Service → Order Service → Payment Service"

→ Use: system-architect
```

---

### 6. redis-caching

**Related Agents:**
- **senior-backend-architect** ✅ BEST
  - Caching strategy design
  - Cache invalidation patterns
  - Redis optimization
  - Memory management
  
- **expert-bug-hunter**
  - Cache hit ratio problems
  - Stale data issues
  - Memory leaks in Redis
  
- **production-code-reviewer**
  - Cache code review
  - Error handling validation

**Usage:**
```
"Cache hit ratio is 45% on our Redis cluster.
How to improve? Is it cache invalidation or TTL issue?"

→ Use: expert-bug-hunter (systematic investigation)
→ Use: senior-backend-architect (backend optimization strategy)
```

---

### 7. database-design (PostgreSQL)

**Related Agents:**
- **senior-backend-architect** ✅ BEST
  - Schema design
  - Normalization strategy
  - Index optimization
  - Query optimization
  - Transaction design
  
- **expert-bug-hunter**
  - Slow query investigation
  - Deadlock debugging
  - Migration issues
  
- **production-code-reviewer**
  - SQL security audit
  - Trigger validation
  - Stored procedure review

**Usage:**
```
"Database queries taking 5+ seconds. 
Should I add indexes, denormalize, or partition?"

→ Use: expert-bug-hunter (to find actual bottleneck)
→ Use: senior-backend-architect (database optimization strategy)
```

```
"Designing user-post-comment schema. 
How many tables? Normalization level?"

→ Use: senior-backend-architect
```

---

## Agent Selection Matrix

### By Task Type

**Architecture & Design:**
- System boundaries, deployment, or platform design → **system-architect**
- Backend architecture, APIs, database, cache, or messaging → **senior-backend-architect**
- Frontend architecture and state management → **senior-frontend-architect**
- Aligning a feature across UI, API, and data → **senior-fullstack-architect**
- Refactoring existing architecture → choose the specialist by affected layer; use **senior-fullstack-architect** for cross-layer refactors

**Implementation:**
- End-to-end feature → **senior-fullstack**
- Backend-only change → **senior-backend-architect**
- Frontend-only change → **frontend-engineer**

**Code Review:**
- Backend code → **production-code-reviewer**
- Frontend code → **production-code-reviewer**
- Pre-production → **production-code-reviewer**
- Security-critical → **security-auditor**

**Debugging:**
- Intermittent issues → **expert-bug-hunter**
- Performance problems → **expert-bug-hunter**
- Race conditions → **expert-bug-hunter**
- System-wide issues → **expert-bug-hunter**

**Planning:**
- Implementation roadmap → **Plan agent**
- Architecture decision → the relevant architect above; **Plan agent** for implementation roadmap
- Refactoring strategy → **Plan agent**

---

## Integration Examples

### Example 1: Add Caching to FastAPI Service

**Step 1: Design (Plan agent)**
```
"I want to add Redis caching to my FastAPI service.
Plan the implementation: where to cache, TTL strategy, 
invalidation pattern."

→ Agent creates step-by-step plan
```

**Step 2: Backend Architecture Review (senior-backend-architect)**
```
"My caching plan: cache user profiles (1h TTL), 
posts (30min), search results (5min). Is this good strategy?"

→ Agent reviews strategy and suggests improvements
```

**Step 3: Code Review (production-code-reviewer)**
```
"Here's my caching decorator. Review it before I deploy."

→ Agent audits error handling, edge cases, thread-safety
```

**Step 4: Debug Issues (expert-bug-hunter)**
```
"Production: cache hit rate dropped from 80% to 20%.
Logs show no errors. What's wrong?"

→ Agent systematically investigates root cause
```

---

### Example 2: Build React Component with Complex State

**Step 1: Frontend Architecture (senior-frontend-architect)**
```
"I need form with 30 fields, nested validation, 
async API calls. Zustand or Context API?"

→ senior-frontend-architect recommends the frontend structure and patterns
```

**Step 2: Implementation Plan (Plan agent)**
```
"Plan the store structure, hooks, components for
e-commerce cart system with coupon code logic."

→ Agent creates detailed implementation roadmap
```

**Step 3: Code Review (production-code-reviewer)**
```
"Review my Zustand store and React components."

→ Agent checks TypeScript safety, hook dependencies, 
  selector performance, memory leaks
```

---

### Example 3: Database Performance Issue

**Step 1: Investigation (expert-bug-hunter)**
```
"Queries on users table take 5s. 
Have 10M rows, 20 indexes, complex joins.
What's the issue?"

→ Agent uses EXPLAIN ANALYZE, profiles, identifies bottleneck
```

**Step 2: Backend Optimization Strategy (senior-backend-architect)**
```
"Should I add another index, denormalize, 
partition, or refactor query?"

→ Agent evaluates trade-offs and recommends solution
```

**Step 3: Schema Review (production-code-reviewer)**
```
"Review my migration and new indexes before deploy."

→ Agent checks for locking, data loss risk, compatibility
```

---

## When to Use Each Agent

### senior-fullstack-architect
✅ Align feature flows and contracts across frontend, backend, and data
✅ Resolve state and data ownership across layers
✅ Plan cross-layer rollout sequencing and compatibility
✅ Break an end-to-end architecture into implementation work

### system-architect
✅ Service boundaries and communication across systems
✅ Platform, infrastructure, deployment, and operational architecture
✅ System-level reliability, scalability, observability, and migration trade-offs
✅ System context, deployment, and interaction diagrams

### senior-backend-architect
✅ Backend architecture and implementation in one focused role
✅ APIs, domain logic, persistence, database migrations, and integrations
✅ Validation, authorization, error handling, transactions, and compatibility
✅ Backend caching, background jobs, messaging, and reliability trade-offs

### senior-frontend-architect
✅ Frontend routes, features, component boundaries, and state ownership
✅ React/Next.js rendering and data-fetching architecture when used
✅ Frontend API consumption, accessibility, and performance strategy
✅ Frontend structure and integration trade-offs

### senior-fullstack
✅ End-to-end feature implementation across frontend and backend
✅ Aligning UI, API, persistence, and service integration
✅ Focused changes that follow existing repository patterns

### production-code-reviewer
✅ Independent review of backend and frontend changes
✅ React/Next.js hooks, component patterns, and TypeScript
✅ Correctness, regression, API compatibility, and performance findings
✅ Actionable production-readiness feedback

### security-auditor
✅ Application security and authorization review
✅ Dependency CVE and secret scanning
✅ Upload, API, cryptography, logging, and infrastructure checks
✅ Evidence-based severity and remediation

### frontend-engineer
✅ Frontend feature implementation
✅ React/Next.js components, forms, accessibility, and API integration

### qa-engineer
✅ Test strategy, scenarios, and regression coverage
✅ Boundary, invalid-input, authorization, failure, and concurrency cases
✅ Clear test results and coverage gaps

### expert-bug-hunter
✅ Intermittent or hard-to-reproduce issues
✅ Evidence-led investigation and root-cause analysis
✅ Performance, race-condition, and system-layer troubleshooting

### document-engineer
✅ Setup, API, architecture, and troubleshooting documentation

---

## Quick Reference

```
Need help with...                    → Use Agent
────────────────────────────────────────────────
"Build an end-to-end feature"     → senior-fullstack
"Should I cache this?"               → senior-backend-architect
"How to design this form state?"     → senior-frontend-architect
"Why is this slow?"                  → expert-bug-hunter
"Review my code before deploy"       → production-code-reviewer
"Design system boundaries"           → system-architect
"Align this UI and API feature"      → senior-fullstack-architect
"Plan the implementation"            → Plan agent
"Review this React pattern"          → production-code-reviewer
"Implement this backend endpoint"    → senior-backend-architect
"PostgreSQL index strategy"          → senior-backend-architect
"Message queue design"               → senior-backend-architect
"Real-time notification topology"    → system-architect
"Debug connection timeout"           → expert-bug-hunter
"TypeScript review"                   → production-code-reviewer
```

---

## Tips for Using Agents

1. **Be Specific**: Give context about constraints, scale, requirements
2. **Show Existing Code**: Agent can review and build on it
3. **Ask for Reasoning**: "Why would you recommend this?"
4. **Request Trade-offs**: "What are the downsides?"
5. **Follow Up**: Use agent's recommendations to refine solution

---

Example of GOOD agent prompt:

```
"I'm building payment processing with FastAPI + PostgreSQL.
- 1000 transactions/minute
- Must handle retries and failures
- Cannot lose transaction data

Should I use:
A) Celery workers + RabbitMQ + database transactions
B) FastAPI async tasks + Redis queue
C) Background jobs in separate service

What are trade-offs? Which scales better to 10k TPS?"

→ Agent provides detailed analysis with recommendations
```

Example of WEAK agent prompt:

```
"How to make payments work?"

→ Too vague, agent gives generic answer
```
