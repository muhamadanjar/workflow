# Code Review Pro (code-review-pro)

Comprehensive code review skill covering feasibility, features, security, and error handling.

## Purpose

Multi-dimensional code review across 4 critical axes:
1. **Feasibility** — Architecture soundness, dependency management, scalability
2. **Features** — Business logic correctness, edge cases, performance
3. **Security** — OWASP Top 10, injection vulnerabilities, auth/secrets
4. **Error Handling** — Input validation, exception safety, recovery strategies

## When to Use

- **Before merging** to production branches
- **New feature branches** (changes > 50 lines)
- **Critical paths** — auth, payments, data processing
- **Third-party integrations** — APIs, databases, external services
- **Refactoring** — large structural changes
- **Security audits** — compliance requirements

## Recommended Agents

| Aspect | Agent |
|--------|-------|
| Full review | production-code-reviewer |
| Backend only | senior-backend-architect |
| Frontend only | senior-frontend-reviewer |
| Security focus | security-auditor |
| Bug hunting | expert-bug-hunter |

## Review Dimensions

### 1. Feasibility

Checks architectural soundness and implementation viability.

**Checklist:**
- [ ] No circular dependencies
- [ ] Layer separation maintained (domain → application → infrastructure)
- [ ] Dependency injection used correctly
- [ ] No tight coupling to external services
- [ ] Scalability path exists (caching, async, partitioning)
- [ ] Performance bottlenecks identified
- [ ] Resource usage reasonable (memory, connections, threads)
- [ ] Backward compatibility maintained
- [ ] Migration path clear (if breaking changes)
- [ ] Monitoring/logging strategy defined

**Bad Pattern:**
```python
# Domain logic depends on FastAPI
from fastapi import HTTPException

class User:
    def validate(self):
        raise HTTPException(status_code=400)  # ❌ Domain knows about HTTP
```

**Good Pattern:**
```python
# Domain logic independent
class ValidationError(Exception):
    pass

class User:
    def validate(self):
        if not self.email:
            raise ValidationError("Email required")  # ✅ Pure domain

# Presentation layer handles HTTP
@router.post("/users")
async def create_user(dto: UserDTO):
    try:
        user = User(**dto.dict())
        user.validate()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 2. Features

Validates business logic correctness and edge case handling.

**Checklist:**
- [ ] Implementation matches requirements
- [ ] Edge cases handled (empty, null, boundary values)
- [ ] Concurrency safe (race conditions prevented)
- [ ] State management correct (immutable where needed)
- [ ] Side effects isolated
- [ ] Idempotency guaranteed (if required)
- [ ] Performance acceptable for data volume
- [ ] Pagination/cursors work correctly
- [ ] Sorting/filtering logic correct
- [ ] Feature flag integration (if applicable)

**Bad Pattern:**
```python
# Missing edge cases
def calculate_average(numbers):
    return sum(numbers) / len(numbers)  # ❌ Crashes on empty list

# Race condition
counter = 0
def increment():
    global counter
    temp = counter
    counter = temp + 1  # ❌ Two threads both increment but only one +1 happens
```

**Good Pattern:**
```python
# Edge cases handled
def calculate_average(numbers):
    if not numbers:
        return None  # ✅ Handle empty case
    return sum(numbers) / len(numbers)

# Atomic operation
from threading import Lock
counter = 0
counter_lock = Lock()

def increment():
    with counter_lock:  # ✅ Thread-safe
        global counter
        counter += 1
```

### 3. Security

OWASP Top 10 + modern vulnerability coverage.

**Checklist:**
- [ ] No SQL injection (parameterized queries, ORM used)
- [ ] No command injection (shell escaping, avoid os.system)
- [ ] No XSS (output encoding, CSP headers)
- [ ] No CSRF (token validation, SameSite cookies)
- [ ] No insecure deserialization (pickle, eval forbidden)
- [ ] No hardcoded secrets (env vars, secret manager)
- [ ] Authentication required (JWT validation, session checks)
- [ ] Authorization enforced (role-based or attribute-based)
- [ ] No path traversal (input sanitization)
- [ ] Sensitive data not logged
- [ ] HTTPS enforced (for web)
- [ ] Dependencies vetted (npm audit, pip audit)

**Bad Pattern:**
```python
# ❌ SQL injection
query = f"SELECT * FROM users WHERE id = {user_id}"
result = db.execute(query)

# ❌ Hardcoded secrets
API_KEY = "sk-1234567890abcdef"

# ❌ Eval dangerous
data = json.loads(user_input)
result = eval(data["expression"])  # Arbitrary code execution!

# ❌ Path traversal
file_path = f"/uploads/{user_filename}"  # User can pass ../../../etc/passwd
```

**Good Pattern:**
```python
# ✅ Parameterized query
query = "SELECT * FROM users WHERE id = ?"
result = db.execute(query, [user_id])

# ✅ Environment secrets
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not set")

# ✅ Safe evaluation
import ast
tree = ast.parse(user_input, mode="eval")  # Parse, don't execute

# ✅ Path traversal prevention
import os
allowed_dir = "/uploads"
requested_file = user_filename
full_path = os.path.normpath(os.path.join(allowed_dir, requested_file))
if not full_path.startswith(allowed_dir):
    raise ValueError("Path traversal attempt")  # Reject
```

### 4. Error Handling

Robust exception handling and graceful degradation.

**Checklist:**
- [ ] All exceptions caught (no bare except)
- [ ] Exception types specific (not catching Exception)
- [ ] Error messages clear (not implementation details)
- [ ] Sensitive data not in error messages
- [ ] Retry logic with exponential backoff (for transients)
- [ ] Circuit breaker for failing services
- [ ] Fallback behavior defined
- [ ] Logging contains context (correlation IDs)
- [ ] User sees appropriate error (not 500)
- [ ] Recovery path exists

**Bad Pattern:**
```python
# ❌ Catch everything
try:
    result = risky_operation()
except:  # Catches KeyboardInterrupt, SystemExit, etc!
    print("Error")

# ❌ Expose internals
try:
    db.query(sql)
except Exception as e:
    return {"error": str(e)}  # Leaks SQL details

# ❌ No retry logic
response = requests.get(url, timeout=1)  # Fails on transient network error
```

**Good Pattern:**
```python
# ✅ Specific exceptions
try:
    result = risky_operation()
except ValueError as e:
    logger.warning("Invalid input", extra={"error": str(e)})
except TimeoutError as e:
    logger.error("Timeout", extra={"url": url, "timeout": 5})

# ✅ Safe error messages
try:
    db.query(sql)
except DatabaseError as e:
    logger.error("Database error", exc_info=True)
    return {"error": "Database operation failed"}  # Generic for user

# ✅ Retry with exponential backoff
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_with_retry(url):
    return requests.get(url, timeout=5)
```

## Code Review Process

### Step 1: Feasibility Scan (5 min)

```
□ Architecture soundness (layers, dependencies)
□ Scalability path exists
□ Resource usage reasonable
□ Migration path clear
□ Backward compatibility maintained
```

### Step 2: Feature Verification (10 min)

```
□ Requirements matched
□ Edge cases covered
□ Concurrency safe
□ Performance acceptable
□ Pagination/filtering correct
```

### Step 3: Security Audit (15 min)

```
□ No injection vulnerabilities
□ Authentication required
□ Authorization enforced
□ Secrets not hardcoded
□ Sensitive data not logged
□ Dependencies audited
```

### Step 4: Error Handling Review (5 min)

```
□ Specific exceptions caught
□ Error messages safe
□ Retry logic present (if needed)
□ Recovery path exists
□ Logging has context
```

### Step 5: Summary

```
Issues Found:
- Critical: [list]
- High: [list]
- Medium: [list]

Recommendation:
- 🔴 Block merge (critical issues)
- 🟡 Request changes (high issues)
- 🟢 Approve (medium/low only)
```

## Technology-Specific Guidance

### Python/FastAPI

**Feasibility:**
- Repository pattern for data access
- Dependency injection container
- No circular imports

**Features:**
- Use async/await for I/O
- Pydantic for validation
- Type hints throughout

**Security:**
- SQLAlchemy with parameterized queries
- python-jose for JWT
- python-decouple for env vars

**Error Handling:**
- Custom exceptions (not generic Exception)
- FastAPI exception handlers
- Logging with structlog

### Node.js/React

**Feasibility:**
- Module boundaries clear
- No barrel exports (circular dependencies)
- Tree-shakeable components

**Features:**
- Hooks properly dependencies
- No infinite renders
- Memoization where needed

**Security:**
- DOMPurify for sanitization
- Helmet.js for headers
- Environment secrets in .env.local

**Error Handling:**
- Error boundaries for React
- Try-catch around async operations
- winston for structured logging

### SQL/Database

**Feasibility:**
- Normalization to 3NF
- Indexes on foreign keys
- Partition strategy (if large tables)

**Features:**
- Query performance acceptable (< 100ms)
- Pagination with cursors
- Proper NULL handling

**Security:**
- Row-level security enabled
- No SELECT * in views
- Secrets not in DDL

**Error Handling:**
- Constraints for data integrity
- Transaction atomicity
- Backup strategy

## Integration with Agents

### Using production-code-reviewer

```
This is production code. Use /code-review ultra --comment
```

Agent runs all 4 dimensions, posts findings as inline comments.

### Using security-auditor

```
Focus on security dimension only. Use security-auditor agent.
```

### Using senior-backend-architect

```
For architecture/feasibility focus on FastAPI code.
```

## Checklist for Contributors

Before submitting PR:

```markdown
## Code Review Self-Check

### Feasibility
- [ ] Architecture follows clean/domain-driven design
- [ ] No circular dependencies
- [ ] Scalability considered
- [ ] Backward compatible or migration documented

### Features
- [ ] All requirements met
- [ ] Edge cases handled
- [ ] Concurrency safe
- [ ] Performance acceptable (benchmarked if needed)

### Security
- [ ] No secrets hardcoded
- [ ] Authentication/authorization checked
- [ ] Input validation present
- [ ] Dependencies audited

### Error Handling
- [ ] Specific exceptions caught
- [ ] User-friendly error messages
- [ ] Retry/fallback logic where needed
- [ ] Logging includes context

### Testing
- [ ] Unit tests for happy path + edge cases
- [ ] Integration tests for external services
- [ ] Security tests (injection, auth bypass)
```

## Examples by Technology

See companion files:
- `PYTHON_FASTAPI_EXAMPLES.md` — FastAPI patterns
- `NODEJS_REACT_EXAMPLES.md` — Node/React patterns
- `DATABASE_EXAMPLES.md` — SQL/migration examples

## When to Block Merge

```
🔴 BLOCK if:
- Security vulnerability (injection, auth bypass)
- Data loss risk (migration without backup)
- Performance regression (5x+ slowdown)
- Breaking change without migration path
- Hardcoded secrets
- Circular dependencies
```

## When to Request Changes

```
🟡 REQUEST CHANGES if:
- Missing error handling
- Insufficient test coverage
- Performance optimization possible
- Code quality issues (long functions, poor naming)
- Incomplete documentation
```

## When to Approve

```
🟢 APPROVE if:
- All 4 dimensions pass
- Minor issues (style, non-critical)
- Documentation clear
- Tests adequate
- No blocking issues
```

---

**Last Updated:** 2026-06-25
**Maintained by:** Code Review Team
