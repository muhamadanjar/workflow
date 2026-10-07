---
name: fastapi-clean-architecture
description: Use when designing, implementing, refactoring, or auditing FastAPI applications with Clean Architecture and domain modeling where it adds value.
---

# FastAPI Clean Architecture

Keep business rules independent from FastAPI, persistence, and external services. Use domain-driven design when it clarifies real business concepts; treat the architecture as dependency and ownership boundaries, not as a mandatory folder tree.

## Before changing code

1. Read the target repository's `AGENTS.md`, architecture docs, ADRs, plans, and relevant tests. Follow its existing planning and progress workflow.
2. Trace one nearby feature from the FastAPI route through dependency construction, application behavior, domain contracts, adapters, and persistence. Use configured code graph tools when available.
3. Record the API, authorization, error, transaction, and audit behavior the change must preserve.
4. Separate intentional design choices from incomplete migrations and accidental boundary violations. Names and folders alone do not prove that a boundary is respected.

Ask only when an unresolved domain rule or architecture trade-off would materially change the result. Otherwise follow the nearest established pattern and state material assumptions.

## Dependency boundaries

- **Domain:** owns business invariants and domain behavior. Keep it independent of FastAPI, ORM models, database sessions, Celery, caches, and external clients.
- **Application:** coordinates use cases and workflows through domain behavior and contracts. Keep HTTP and persistence mechanics out of it; do not import concrete infrastructure adapters or query builders.
- **Infrastructure:** implements contracts and owns database queries, ORM conversion, storage, and external clients. Keep business policy in the domain or application.
- **Presentation:** FastAPI handlers validate transport input, invoke ready-to-use application behavior, map results, and translate approved errors. Keep raw SQL, workflow policy, transaction orchestration, and concrete repository construction out of handlers.
- **Composition root:** dependency providers or the application entry point wire concrete adapters into use cases. Background workers follow the same boundary rules as HTTP entry points.

Use repository or service contracts when they express a real boundary. Follow the target repository's accepted contract style; do not add a `ports/` package, base repository, or interface convention just to match another codebase.

## Domain modeling

- Give business concepts explicit names. Use entities, value objects, aggregates, and domain services when they represent identity, validation, invariants, or meaningful state transitions.
- Keep transport schemas and persistence models at their own boundaries. Translate persistence representations to domain types in an explicit adapter or mapper.
- Use dedicated use cases for workflows and business policies. Avoid empty wrappers around straightforward CRUD when the repository's established pattern does not need them.
- Keep application behavior testable with fakes and domain behavior independent of framework setup.

## Review and report

Trace imports and calls across the feature path. Check who owns each invariant, whether application behavior can run without the database/framework, where mapping occurs, and whether handlers or workers contain business or transaction logic. Report concrete locations and distinguish confirmed violations from intentional conventions or migration work.

Preserve public contracts and existing authorization, error, transaction, and atomic audit semantics unless behavior change is explicitly requested. See [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) for layer examples and common failure modes.
