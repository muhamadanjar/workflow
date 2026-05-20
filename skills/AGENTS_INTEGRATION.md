# Agents Integration with Skills

Guide untuk menggunakan built-in agents dengan skills yang sudah dibuat.

## Available Agents

Claude memiliki beberapa specialized agents yang bisa digunakan untuk tasks spesifik:

1. **senior-backend-architect** - Backend architecture, databases, APIs, DevOps
2. **senior-frontend-reviewer** - Frontend code review, React, components, TypeScript
3. **expert-bug-hunter** - Debugging kompleks, root cause analysis, systematic investigation
4. **Plan agent** - Design implementation plans, architecture, trade-offs
5. **production-code-reviewer** - Code audit sebelum production
6. **system-architect** - System design, technology choices, migrations

## Skills & Recommended Agents

### 1. python-async-pro (Celery + RabbitMQ)

**Related Agents:**
- **senior-backend-architect** ✅ BEST
  - Design task queue architecture
  - Redis vs RabbitMQ comparison
  - Celery configuration optimization
  - Worker deployment strategy
  
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
  - Domain-driven design implementation
  - Repository pattern optimization
  - Layer separation validation
  - Dependency injection setup
  
- **senior-fullstack-architect** ✅ EXCELLENT
  - Full DDD implementation
  - Event sourcing patterns
  - CQRS design
  - Bounded context definition
  
- **production-code-reviewer**
  - Audit domain/application/infrastructure layers
  - Check service isolation
  - Validate dependency inversion

**Usage:**
```
"I'm building an e-commerce system with clean architecture.
How should I organize: Order aggregate, OrderService, OrderRepository?
Where does payment logic go?"

→ Use: senior-fullstack-architect (for CQRS/DDD patterns)
→ Use: senior-backend-architect (for API design)
```

---

### 3. frontend-design-pro (React/Next.js + shadcn/ui + MUI + Zustand)

**Related Agents:**
- **senior-frontend-reviewer** ✅ BEST
  - Component architecture
  - TypeScript type safety
  - State management patterns
  - Zustand store design
  - Performance optimization
  
- **senior-backend-architect**
  - API integration patterns
  - Server/Client component split
  - Next.js API routes design
  
- **production-code-reviewer**
  - React component audit
  - Hook best practices
  - Memory leak detection

**Usage:**
```
"I have 50 form inputs across multiple pages. 
Should I use react-hook-form + Zustand or Context API?"

→ Use: senior-frontend-reviewer
```

```
"My Next.js app loads 2MB of data on home page.
How to optimize with Server Components and ISR?"

→ Use: senior-backend-architect (for data fetching strategy)
→ Use: senior-frontend-reviewer (for component structure)
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
- **system-architect** ✅ BEST
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
→ Use: senior-backend-architect (optimization strategy)
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
→ Use: senior-backend-architect (optimization strategy)
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
- New system design → **system-architect** or **senior-backend-architect**
- Refactoring existing → **senior-backend-architect**
- State management → **senior-frontend-reviewer**
- Database schema → **senior-backend-architect**

**Code Review:**
- Backend code → **senior-backend-architect**
- Frontend code → **senior-frontend-reviewer**
- Pre-production → **production-code-reviewer**
- Security-critical → **production-code-reviewer**

**Debugging:**
- Intermittent issues → **expert-bug-hunter**
- Performance problems → **expert-bug-hunter**
- Race conditions → **expert-bug-hunter**
- System-wide issues → **expert-bug-hunter**

**Planning:**
- Implementation roadmap → **Plan agent**
- Architecture decision → **system-architect** or **Plan agent**
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

**Step 2: Architecture Review (senior-backend-architect)**
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

**Step 1: Architecture (senior-frontend-reviewer)**
```
"I need form with 30 fields, nested validation, 
async API calls. Zustand or Context API?"

→ Agent recommends architecture and patterns
```

**Step 2: Implementation Plan (Plan agent)**
```
"Plan the store structure, hooks, components for
e-commerce cart system with coupon code logic."

→ Agent creates detailed implementation roadmap
```

**Step 3: Code Review (senior-frontend-reviewer)**
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

**Step 2: Optimization Strategy (senior-backend-architect)**
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

### senior-backend-architect
✅ Architecture questions
✅ Technology choices
✅ System design
✅ Database design
✅ API design
✅ Scaling strategies
✅ Performance optimization (backend)

❌ Frontend code review
❌ Debugging intermittent issues
❌ Detailed code audits

---

### senior-frontend-reviewer
✅ Component architecture
✅ React/Next.js patterns
✅ TypeScript strictness
✅ State management design
✅ Performance optimization (frontend)
✅ Hook best practices

❌ Backend architecture
❌ Database design
❌ Infra/DevOps

---

### expert-bug-hunter
✅ Intermittent/hard-to-reproduce issues
✅ Performance investigation
✅ Root cause analysis
✅ System-wide issues
✅ Race conditions
✅ Memory leaks

❌ General architecture
❌ Code review for quality
❌ New feature planning

---

### production-code-reviewer
✅ Pre-deployment code audit
✅ Security review
✅ Error handling validation
✅ Architecture compliance check

❌ General guidance
❌ Debugging
❌ Planning

---

### system-architect
✅ Full system design
✅ Technology evaluation
✅ Microservices architecture
✅ System migrations

❌ Code-level details
❌ Frontend specifics
❌ Debugging

---

## Quick Reference

```
Need help with...                    → Use Agent
────────────────────────────────────────────────
"Should I cache this?"               → senior-backend-architect
"How to design this form state?"     → senior-frontend-reviewer
"Why is this slow?"                  → expert-bug-hunter
"Review my code before deploy"       → production-code-reviewer
"Design full architecture"           → system-architect
"Plan the implementation"            → Plan agent
"Is this React pattern good?"        → senior-frontend-reviewer
"PostgreSQL index strategy"          → senior-backend-architect
"Message queue design"               → senior-backend-architect
"Real-time notifications"            → senior-backend-architect
"Debug connection timeout"           → expert-bug-hunter
"TypeScript type safety"             → senior-frontend-reviewer
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

