# Code Review Pro — Quick Checklist

30-second review checklist for fast code review.

## ⚡ 30-Second Review (Critical Only)

```
🔴 BLOCK if ANY of these:
☐ Hardcoded secrets (API keys, passwords, DB credentials)
☐ SQL injection vulnerable (no parameterized queries)
☐ Path traversal / directory escape
☐ Command injection (os.system, subprocess without shlex)
☐ Eval/exec on user input
☐ Circular imports / circular dependencies
☐ Data loss risk (drop table, delete without backup)
☐ Breaking change without migration path
```

## ⏱️ 5-Minute Review (High Priority)

### Feasibility (1 min)
```
☐ Dependencies: no circular imports
☐ Database: uses ORM or parameterized queries
☐ Async: async/await used, not blocking event loop
☐ Config: secrets in env vars, not hardcoded
```

### Features (1 min)
```
☐ Validation: input validated before use
☐ Edge cases: handles empty, null, boundary values
☐ Pagination: math correct, limit enforced
☐ Concurrency: shared state protected (locks, atomic ops)
```

### Security (2 min)
```
☐ Input validation: length limits, type checks
☐ Authentication: required where needed
☐ Authorization: roles/permissions enforced
☐ Logging: no passwords/PII in logs
☐ Dependencies: no known CVEs
```

### Error Handling (1 min)
```
☐ Exceptions: specific types caught, not generic Exception
☐ HTTP errors: correct status codes (400, 401, 403, 500)
☐ Messages: user-friendly, no internal details
☐ Logging: includes context (user_id, action, error)
```

## 🎯 Dimension-Specific Checklist

### FEASIBILITY

```
Architecture
☐ Domain → Application → Infrastructure → Presentation layers
☐ No dependencies pointing backwards (Infrastructure → Domain)
☐ Domain logic independent of frameworks
☐ Dependency injection or service locator used

Scalability
☐ Database queries: efficient (explain analyze < 100ms)
☐ Indexes on frequently filtered columns
☐ Pagination implemented (not loading all records)
☐ Caching strategy defined (if hotspot)
☐ Async tasks for long operations (> 1 second)

Dependencies
☐ No circular imports/dependencies
☐ External service calls wrapped in adapter
☐ Version pinning (requirements.txt, package.json)
☐ Monolithic, not split into too many files

Configuration
☐ Secrets in environment variables
☐ No hardcoded: API keys, DB URLs, credentials
☐ Config per environment (dev, staging, prod)
☐ .env.example shows all required vars

Monitoring & Logging
☐ Structured logging (JSON or key=value)
☐ Log levels: DEBUG, INFO, WARN, ERROR used correctly
☐ Correlation IDs for tracing
☐ No sensitive data in logs (passwords, PII)
```

### FEATURES

```
Correctness
☐ Implementation matches requirements/acceptance criteria
☐ Business logic correct
☐ State transitions valid
☐ Invariants maintained

Edge Cases
☐ Empty list/null → handled (no crash)
☐ Boundary values (0, negative, max_int)
☐ Concurrent access → race conditions prevented
☐ Duplicate operations → idempotent if needed
☐ Long strings/large datasets → truncated/paginated

Performance
☐ Algorithm: correct time/space complexity
☐ Database: N+1 queries eliminated (use joins)
☐ Loops: not nested deeply (O(n) not O(n²))
☐ Memory: reasonable for data volume
☐ API response: < 500ms typical case

Behavior
☐ Sorting: ascending/descending correct
☐ Filtering: all fields filterable / safe fields only
☐ Pagination: math correct, no off-by-one
  - offset = (page - 1) * size
  - total_pages = ceil(total / size)
☐ Caching: invalidation logic correct
```

### SECURITY (OWASP Top 10)

```
1. Injection (SQL, OS, Template)
☐ SQL: parameterized queries, ORM used
☐ OS: no os.system, use shlex.quote or subprocess
☐ Template: escape user input
☐ LDAP/NoSQL: parameterized too

2. Broken Authentication
☐ Password: bcrypt/scrypt (not SHA1)
☐ JWT: verified, expiry checked
☐ Session: secure cookies (HttpOnly, SameSite)
☐ MFA: enabled for sensitive operations
☐ Account lockout: after N failed attempts

3. Sensitive Data Exposure
☐ Passwords: never logged
☐ PII: redacted in logs
☐ API responses: no sensitive data leakage
☐ HTTPS: enforced for web
☐ Data at rest: encryption for sensitive columns

4. XML External Entities (XXE)
☐ XML: disable DTD/entity expansion
☐ YAML: use safe_load, not load

5. Broken Access Control
☐ Authorization: on every endpoint
☐ Roles: enforced (admin, user, guest)
☐ Data isolation: user can't see others' data
☐ Admin operations: require admin role

6. Security Misconfiguration
☐ Error pages: no stack traces
☐ Debug mode: OFF in production
☐ Security headers: X-Frame-Options, CSP, HSTS
☐ Dependencies: up to date (npm audit, pip audit)

7. Cross-Site Scripting (XSS)
☐ Output: HTML-escaped
☐ DOM: not innerHTML, use innerText
☐ CSP: Content-Security-Policy header

8. Insecure Deserialization
☐ Pickle: never use for untrusted data
☐ JSON: safe (built-in safe_load)
☐ YAML: use safe_load, not load

9. Using Components with Known Vulnerabilities
☐ Dependencies: no known CVEs
  - npm audit
  - pip audit
  - snyk check
  
10. Insufficient Logging & Monitoring
☐ Failed logins: logged
☐ API changes: logged
☐ Errors: logged with context

Secrets Management
☐ API keys: in env vars
☐ Database passwords: not in code
☐ Private keys: in secure storage
☐ Rotation strategy: documented
```

### ERROR HANDLING

```
Exception Types
☐ Catch specific exceptions (ValueError, TypeError, etc.)
☐ No bare except clause
☐ No catching Exception with print()
☐ Custom exceptions for domain errors

HTTP Status Codes
☐ 200: success
☐ 201: created
☐ 400: bad request (validation error)
☐ 401: unauthorized (needs login)
☐ 403: forbidden (not allowed)
☐ 404: not found
☐ 409: conflict (duplicate, constraint)
☐ 500: server error (unexpected)

Error Messages
☐ User-friendly (not "Exception: KeyError")
☐ No implementation details exposed
☐ No stack traces in API response
☐ Correct HTTP status + message

Logging
☐ Context included (user_id, action, timestamp)
☐ Correlation ID for distributed tracing
☐ Severity: DEBUG, INFO, WARN, ERROR, CRITICAL
☐ No sensitive data (passwords, API keys, tokens)

Retry Strategy
☐ Transient errors: retry with exponential backoff
☐ Idempotent: safe to retry
☐ Max attempts: reasonable (3-5)
☐ Backoff: exponential (1s, 2s, 4s, 8s)
☐ Circuit breaker: fail fast after N failures

Fallback & Recovery
☐ External service down → graceful degradation
☐ Cache miss → query database
☐ Database error → return empty or cached data
☐ Timeout → retry or fallback

Resource Cleanup
☐ Database connections: closed in finally
☐ File handles: closed after use (context manager)
☐ Threads: joined before exit
☐ Locks: released on exception (context manager)
```

## Usage

### For 5-Min Review
1. Check CRITICAL items (hardcoded secrets, injection)
2. Skim feasibility & features
3. Deep dive security (5 min)
4. Quick error handling check

### For 15-Min Review
1. Check all critical items
2. Full feasibility review
3. Feature edge cases
4. Full security checklist
5. Error handling

### For 30-Min Review
Use this with `production-code-reviewer` agent.

## Integration Examples

### With Agent
```bash
# Quick security focus
/code-review --fix  # Auto-fix common issues

# Full review with agent
/code-review ultra --comment  # Posts findings to PR

# Pre-push check
/code-review --fix --check  # Fix or fail
```

### With GitHub Actions
```yaml
- name: Code Review
  run: |
    # Run linting
    pylint app/
    
    # Run security scan
    bandit -r app/
    
    # Run tests
    pytest
```

---

**Last Updated:** 2026-06-25
**How to use:** Print or bookmark for quick reference
