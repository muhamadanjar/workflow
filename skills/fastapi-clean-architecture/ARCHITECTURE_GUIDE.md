# FastAPI Clean Architecture - Comprehensive Guide

Complete guide to implementing clean architecture in FastAPI. Based on battle-tested patterns from usermanagement_api.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Layer Breakdown](#layer-breakdown)
3. [Design Patterns](#design-patterns)
4. [Implementation Examples](#implementation-examples)
5. [Common Pitfalls](#common-pitfalls)

---

## Core Principles

### 1. Dependency Inversion

**Rule:** High-level modules (application) should not depend on low-level modules (infrastructure). Both should depend on abstractions (domain).

```python
# ✅ CORRECT

# domain/repositories/user_repository.py (abstraction)
from abc import ABC, abstractmethod
from domain.entities import User

class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User:
        pass

# infrastructure/database/repositories/user_repository.py (implementation)
from domain.repositories import UserRepository
from infrastructure.database.models import UserModel

class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> User:
        db_user = await self.session.get(UserModel, user_id)
        return db_user.to_entity()  # ORM → Domain entity

# application/use_cases/get_user.py (uses abstraction)
from domain.repositories import UserRepository
from domain.entities import User

class GetUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def execute(self, user_id: int) -> User:
        return await self.user_repo.get_by_id(user_id)
```

### 2. Separation of Concerns

Each layer has a specific responsibility:

| Layer | Responsibility | Dependencies |
|-------|-----------------|---------------|
| **Domain** | Business rules (no frameworks) | None |
| **Application** | Use cases, orchestration | Domain |
| **Presentation** | HTTP concerns (routes, serialization) | Application |
| **Infrastructure** | Technical implementations | Domain |

### 3. No Circular Dependencies

```
Presentation → Application → Domain ← Infrastructure
                             (implements via DI)
```

Valid dependency flow:
- Presentation can use Application
- Application can use Domain
- Infrastructure can implement Domain interfaces
- Application can depend on Infrastructure for technical needs (DB, cache)

Invalid:
- ❌ Domain imports from Infrastructure
- ❌ Infrastructure imports from Presentation
- ❌ Domain imports from Application

### 4. Entity Independence

Domain entities should be testable without any framework.

```python
# ✅ CORRECT - No framework dependencies

# domain/entities/user.py
from datetime import datetime
from dataclasses import dataclass

@dataclass
class User:
    id: int
    email: str
    password_hash: str
    created_at: datetime
    
    def verify_password(self, password: str) -> bool:
        # Pure Python, testable without FastAPI/SQLAlchemy
        return bcrypt.verify(password, self.password_hash)
```

---

## Layer Breakdown

### Domain Layer (Business Logic)

**Location:** `app/domain/`

**Responsibility:** Pure business logic, independent of frameworks.

#### Entities
Domain models with business logic:
```python
# domain/entities/user.py
from datetime import datetime
import bcrypt

class User:
    def __init__(self, id: int, email: str, password_hash: str, created_at: datetime):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
    
    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash)
    
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def is_active(self) -> bool:
        return self.status == "active"
```

#### Value Objects
Immutable, reusable objects:
```python
# domain/value_objects/email.py
from dataclasses import dataclass
import re

@dataclass(frozen=True)  # Immutable
class Email:
    value: str
    
    def __post_init__(self):
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', self.value):
            raise ValueError(f"Invalid email: {self.value}")
```

#### Repository Interfaces
Abstract data access:
```python
# domain/repositories/user_repository.py
from abc import ABC, abstractmethod
from domain.entities import User

class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass
    
    @abstractmethod
    async def save(self, user: User) -> User:
        pass
```

#### Domain Services
Business logic across entities:
```python
# domain/services/password_service.py
class PasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        return User.hash_password(password)
    
    @staticmethod
    def verify_password(password: str, hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), hash)
```

#### Domain Events
Notifications of important business events:
```python
# domain/events/user_registered.py
from datetime import datetime
from dataclasses import dataclass

@dataclass
class UserRegisteredEvent:
    user_id: int
    email: str
    created_at: datetime
    
    def __str__(self):
        return f"User {self.email} registered"
```

### Application Layer (Use Cases)

**Location:** `app/application/`

**Responsibility:** Orchestrate domain logic and coordinate with infrastructure.

#### Use Cases
Represent business operations:
```python
# application/use_cases/register_user.py
from domain.entities import User
from domain.repositories import UserRepository
from domain.value_objects import Email
from domain.events import UserRegisteredEvent
from application.dto import RegisterUserDTO

class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, dto: RegisterUserDTO) -> User:
        # Validate email uniqueness
        existing = await self.user_repository.get_by_email(dto.email)
        if existing:
            raise UserAlreadyExistsError(f"Email {dto.email} already registered")
        
        # Create user
        password_hash = User.hash_password(dto.password)
        user = User(
            id=None,
            email=dto.email,
            password_hash=password_hash,
            created_at=datetime.now()
        )
        
        # Persist
        user = await self.user_repository.save(user)
        
        # Publish domain event
        event = UserRegisteredEvent(
            user_id=user.id,
            email=user.email,
            created_at=user.created_at
        )
        self._publish_event(event)
        
        return user
```

#### DTOs (Data Transfer Objects)
Request/response models:
```python
# application/dto/user_dto.py
from pydantic import BaseModel, EmailStr
from datetime import datetime

class RegisterUserDTO:
    email: str
    password: str
    password_confirm: str

class UserDTO(BaseModel):
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # SQLAlchemy → Pydantic
```

#### Application Services
Coordinate use cases:
```python
# application/services/user_service.py
class UserService:
    def __init__(self, register_uc: RegisterUserUseCase, login_uc: LoginUserUseCase):
        self.register_uc = register_uc
        self.login_uc = login_uc
    
    async def register(self, dto: RegisterUserDTO) -> UserDTO:
        user = await self.register_uc.execute(dto)
        return UserDTO.from_orm(user)
    
    async def login(self, dto: LoginDTO) -> LoginResponseDTO:
        result = await self.login_uc.execute(dto)
        return LoginResponseDTO(token=result.token, user=result.user)
```

### Presentation Layer (HTTP API)

**Location:** `app/presentation/`

**Responsibility:** HTTP concerns (routes, serialization, authentication).

#### Routes (Endpoints)
```python
# presentation/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from application.dto import RegisterUserDTO, LoginDTO
from application.services import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    dto: RegisterUserDTO,
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.register(dto)
        return {"status": "ok", "user": user}
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post("/login")
async def login(
    dto: LoginDTO,
    service: UserService = Depends(get_user_service)
):
    result = await service.login(dto)
    return result
```

#### Dependency Injection
```python
# presentation/api/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

def get_user_repository(session = Depends(get_db)):
    return UserRepositoryImpl(session)

def get_register_uc(repo = Depends(get_user_repository)):
    return RegisterUserUseCase(repo)

def get_user_service(register_uc = Depends(get_register_uc)):
    return UserService(register_uc=register_uc)
```

#### Middleware
```python
# presentation/middleware/error_handler.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from core.exceptions import AppException

def setup_error_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "code": exc.code}
        )
```

### Infrastructure Layer (Technical Implementations)

**Location:** `app/infrastructure/`

**Responsibility:** Database, cache, external services, etc.

#### Repository Implementation
```python
# infrastructure/database/repositories/user_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from domain.repositories import UserRepository
from domain.entities import User
from infrastructure.database.models import UserModel

class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.get(UserModel, user_id)
        return result.to_entity() if result else None
    
    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        return db_user.to_entity() if db_user else None
    
    async def save(self, user: User) -> User:
        db_user = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at
        )
        self.session.add(db_user)
        await self.session.flush()
        await self.session.refresh(db_user)
        return db_user.to_entity()
```

#### ORM Models
```python
# infrastructure/database/models/user_model.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base
from domain.entities import User
from datetime import datetime

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    def to_entity(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            password_hash=self.password_hash,
            created_at=self.created_at
        )
```

### Core Layer (Cross-Cutting)

**Location:** `app/core/`

**Responsibility:** Config, logging, security, exceptions.

#### Exceptions
```python
# core/exceptions.py
class AppException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code

class UserAlreadyExistsError(AppException):
    def __init__(self, message: str):
        super().__init__(message, "USER_EXISTS", 409)

class UserNotFoundError(AppException):
    def __init__(self, message: str):
        super().__init__(message, "USER_NOT_FOUND", 404)
```

---

## Design Patterns

### Repository Pattern
Abstracts data access, making tests possible without database.

### Dependency Injection
Loose coupling, testability, flexibility.

### Value Objects
Immutable, reusable, domain-safe objects.

### Domain Events
Decouple business operations from side effects.

### Use Case Pattern
Clear, testable business operation representation.

---

## Implementation Examples

See `templates/` for complete, working examples:
- `user_entity.py` — Entity with business logic
- `user_repository.py` — Repository interface + implementation
- `register_user_use_case.py` — Complete use case
- `auth_routes.py` — API endpoints
- `user_service.py` — Application service

---

## Common Pitfalls

### ❌ Putting Business Logic in Routes
```python
# WRONG
@router.post("/register")
async def register(dto: RegisterUserDTO):
    # Validation in route
    if await db.user.get_by_email(dto.email):
        raise HTTPException(409, "Exists")
    # Hash in route
    hash = bcrypt.hash(dto.password)
    # Create in route
    user = await db.user.create(...)
    return user
```

### ✅ Encapsulate in Use Case
```python
# CORRECT
class RegisterUserUseCase:
    async def execute(self, dto: RegisterUserDTO) -> User:
        # All logic here
        ...

@router.post("/register")
async def register(dto: RegisterUserDTO, uc: RegisterUserUseCase):
    return await uc.execute(dto)
```

### ❌ Domain Entity Depends on Framework
```python
# WRONG
from sqlalchemy.orm import DeclarativeBase

class User(DeclarativeBase):  # Framework dependency!
    __tablename__ = "users"
    id: int
    email: str
```

### ✅ Pure Domain Entity
```python
# CORRECT
class User:  # No framework
    def __init__(self, id: int, email: str, ...):
        self.id = id
        self.email = email
```

### ❌ Direct Infrastructure Access in Application
```python
# WRONG
from infrastructure.database.models import UserModel

class RegisterUserUseCase:
    async def execute(self, dto):
        # Direct DB access - couples to infrastructure
        user = await db.query(UserModel).filter(...).first()
```

### ✅ Repository Abstraction
```python
# CORRECT
from domain.repositories import UserRepository

class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def execute(self, dto):
        # Via repository interface
        user = await self.user_repo.get_by_email(dto.email)
```
