# Python/FastAPI Code Review Examples

Practical examples for reviewing Python/FastAPI code across all 4 dimensions.

## Example 1: User Registration Endpoint

### Code Under Review

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, Session
import hashlib

app = FastAPI()
Base = declarative_base()
engine = create_engine("postgresql://user:password@localhost/db")

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String)
    password = Column(String)

class UserCreate(BaseModel):
    email: str
    password: str

@app.post("/users")
def create_user(data: UserCreate):
    # Hash password
    hashed = hashlib.sha1(data.password).hexdigest()
    
    user = User(id=str(uuid.uuid4()), email=data.email, password=hashed)
    session = Session(engine)
    session.add(user)
    session.commit()
    
    return {"user_id": user.id}
```

### Feasibility Review ❌

**Issues:**
1. **Database connection per request** — Creates new session every request. Use dependency injection.
2. **No input validation** — Email format not checked.
3. **No error handling** — Duplicate email will crash.
4. **No logging** — Can't debug production issues.
5. **Hard-coded credentials** — DB URL in code.

**Feedback:**
```
Move database connection to dependency:
@lru_cache()
def get_db():
    return SessionLocal()

@app.post("/users")
async def create_user(data: UserCreate, db: Session = Depends(get_db)):
    ...
```

### Features Review ❌

**Issues:**
1. **No email validation** — "notanemail" passes.
2. **Weak hashing** — SHA1 is not for passwords (use bcrypt).
3. **No duplicate check** — Same email creates multiple users.
4. **Synchronous** — Blocks event loop on DB I/O.
5. **Missing test cases** — Edge cases uncovered.

**Edge Cases Not Covered:**
- Empty email
- Very long password
- Unicode characters
- Concurrent duplicate registration
- Case-sensitive email matching

**Feedback:**
```
Use Pydantic for validation:
from pydantic import EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)

Duplicate check:
existing = db.query(User).filter(User.email == data.email.lower()).first()
if existing:
    raise HTTPException(status_code=409, detail="Email already registered")
```

### Security Review 🔴

**Critical Issues:**

1. **Weak hashing** — SHA1 + plain password
   ```python
   # ❌ Bad
   hashed = hashlib.sha1(data.password).hexdigest()
   
   # ✅ Good
   from passlib.context import CryptContext
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   hashed = pwd_context.hash(data.password)
   ```

2. **Hard-coded credentials**
   ```python
   # ❌ Bad
   engine = create_engine("postgresql://user:password@localhost/db")
   
   # ✅ Good
   from decouple import config
   database_url = config("DATABASE_URL")
   engine = create_engine(database_url)
   ```

3. **No email verification** — Attacker can register with fake email
   ```python
   # ✅ Add
   user.email_verified = False
   # Send verification email before allowing login
   ```

4. **Password exposed in logs** — If exception occurs, password might be logged
   ```python
   # ✅ Exclude from logging
   class UserCreate(BaseModel):
       email: EmailStr
       password: str
       
       class Config:
           # Don't include in logs
           pass
   ```

5. **No rate limiting** — Brute force or spam registration
   ```python
   # ✅ Add
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/users")
   @limiter.limit("5/minute")
   async def create_user(...):
   ```

**Recommendation:** 🔴 **BLOCK** — Critical security issues

### Error Handling Review ❌

**Issues:**

1. **No exception handling**
   ```python
   # ❌ This crashes on duplicate email
   session.add(user)
   session.commit()
   ```

2. **Bare exception would hide errors**
   ```python
   # ❌ Bad
   try:
       ...
   except:
       raise HTTPException(status_code=500)
   ```

3. **No input validation** — Invalid email crashes
   ```python
   # ✅ Add
   from pydantic import validator, EmailStr
   
   class UserCreate(BaseModel):
       email: EmailStr
       password: str
   ```

4. **No logging context**
   ```python
   # ✅ Add
   import logging
   logger = logging.getLogger(__name__)
   
   try:
       user = User(...)
       session.add(user)
       session.commit()
   except IntegrityError as e:
       logger.error("User registration failed", extra={
           "email": data.email,
           "error": "Duplicate email"
       })
       raise HTTPException(status_code=409, detail="Email already registered")
   ```

**Recommendation:** 🔴 **BLOCK** — Missing critical error handling

---

## Example 2: Product Search with Pagination ✅

### Good Code

```python
from fastapi import FastAPI, Query, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class ProductSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=100)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class ProductDTO(BaseModel):
    id: int
    name: str
    price: float

class ProductSearchResponse(BaseModel):
    items: list[ProductDTO]
    total: int
    page: int
    page_size: int
    total_pages: int

@app.get("/products/search", response_model=ProductSearchResponse)
async def search_products(
    request: ProductSearchRequest,
    db: Session = Depends(get_db),
):
    """Search products by name with pagination."""
    try:
        # Sanitize input
        query = request.query.strip().lower()
        
        # Validate pagination
        offset = (request.page - 1) * request.page_size
        
        # Execute parameterized query
        total = db.query(func.count(Product.id)).filter(
            Product.name.ilike(f"%{query}%")
        ).scalar()
        
        products = db.query(Product).filter(
            Product.name.ilike(f"%{query}%")
        ).offset(offset).limit(request.page_size).all()
        
        total_pages = (total + request.page_size - 1) // request.page_size
        
        return ProductSearchResponse(
            items=[ProductDTO.from_orm(p) for p in products],
            total=total,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        logger.error("Product search failed", extra={
            "query": query,
            "page": request.page,
            "error": str(e)
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed")
```

### Feasibility ✅

- Uses dependency injection for DB
- Pagination prevents memory issues
- Input validation with Pydantic
- Error handling with logging
- Database URL from environment (assumed)

### Features ✅

- Edge cases: empty results, last page
- Case-insensitive search
- Pagination calculation correct
- Concurrency safe (session per request)

### Security ✅

- Input validation (length limits)
- Parameterized queries (ilike safe)
- No sensitive data in response
- Query limits (page_size ≤ 100)

### Error Handling ✅

- Specific exception handling
- Logging with context
- Safe error message to user
- HTTP 500 on server error

**Recommendation:** 🟢 **APPROVE**

---

## Example 3: Async Task Processing ❌→✅

### Before (Bad)

```python
@app.post("/export")
def export_data(request: ExportRequest):
    # This blocks the request for minutes!
    data = db.query(LargeTable).filter(...).all()
    csv = generate_csv(data)
    send_email(request.email, csv)
    return {"status": "done"}
```

**Issues:**
- Blocks event loop for seconds/minutes
- If email fails, user never knows
- No progress tracking
- Timeout likely

### After (Good)

```python
from celery import shared_task
from fastapi import BackgroundTasks

@shared_task
def export_data_task(email: str, filters: dict):
    """Background task for data export."""
    try:
        logger.info("Starting export", extra={"email": email})
        
        db = SessionLocal()
        data = db.query(LargeTable).filter(...).all()
        csv = generate_csv(data)
        
        if not send_email(email, csv):
            logger.error("Email send failed", extra={"email": email})
            return {"status": "failed", "reason": "email_error"}
        
        logger.info("Export completed", extra={"email": email})
        return {"status": "success"}
    except Exception as e:
        logger.error("Export task failed", extra={"email": email}, exc_info=True)
        return {"status": "failed", "reason": str(e)}
    finally:
        db.close()

@app.post("/export")
async def export_data(request: ExportRequest):
    """Enqueue export task."""
    try:
        # Validate input
        if not EmailStr.validate_email(request.email):
            raise HTTPException(status_code=400, detail="Invalid email")
        
        # Enqueue task
        task = export_data_task.delay(
            email=request.email,
            filters=request.dict()
        )
        
        return {
            "status": "queued",
            "task_id": task.id,
            "message": f"Export started, check email {request.email}"
        }
    except Exception as e:
        logger.error("Export request failed", extra={
            "email": request.email,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="Export request failed")

@app.get("/export/{task_id}")
async def get_export_status(task_id: str):
    """Check export progress."""
    task = export_data_task.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.state,
        "result": task.result if task.state == "SUCCESS" else None,
    }
```

**Improvements:**

1. **Feasibility** — Async task, event loop unblocked
2. **Features** — Idempotent (safe to retry), progress tracking
3. **Security** — Email validated, no sensitive data in logs
4. **Error Handling** — Specific exceptions, logging, failed status

**Recommendation:** 🟢 **APPROVE**

---

## Review Checklist Template

```markdown
## Code Review: [PR Title]

### Feasibility
- [ ] Architecture follows clean/DDD design
- [ ] Dependency injection used
- [ ] No circular dependencies
- [ ] Database: efficient queries, proper indexes
- [ ] Async: uses async/await correctly
- [ ] Environment: secrets from env vars
- [ ] Monitoring: logging with context

**Issues:**
- [list]

### Features
- [ ] Requirements implemented
- [ ] Edge cases: empty, null, boundary values
- [ ] Concurrency: race conditions prevented
- [ ] Performance: acceptable for data volume
- [ ] Pagination: correct math, no off-by-one
- [ ] Validation: Pydantic used, length limits

**Issues:**
- [list]

### Security
- [ ] Input validation: Pydantic, string limits
- [ ] Injection: parameterized queries, no eval
- [ ] Auth: JWT validation, roles checked
- [ ] Secrets: no hardcoded values
- [ ] Logging: no passwords, PII redacted
- [ ] Dependencies: pip audit passes

**Issues:**
- [list]

### Error Handling
- [ ] Specific exceptions caught (not bare except)
- [ ] HTTP errors: correct status codes
- [ ] Error messages: user-friendly, no internals
- [ ] Logging: includes correlation ID, context
- [ ] Retry: exponential backoff for transients
- [ ] Fallback: graceful degradation

**Issues:**
- [list]

### Decision
- 🟢 **APPROVE** — No blocking issues
- 🟡 **REQUEST CHANGES** — High priority issues
- 🔴 **BLOCK** — Critical security/data loss risk

**Comment:** [summary]
```

---

**Last Updated:** 2026-06-25
