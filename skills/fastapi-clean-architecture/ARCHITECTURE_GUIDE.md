# FastAPI Clean Architecture and Domain Modeling

This guide describes practical dependency and ownership boundaries for FastAPI services. Adapt names and layout to the target repository; the examples are not a required scaffold.

## Dependency direction

```text
Presentation → Application → Domain
Infrastructure ───────────→ Domain contracts
Composition root → connects presentation, application, and infrastructure
```

The request may travel from presentation to an infrastructure adapter at runtime, but source dependencies point inward. Application code depends on domain behavior and contracts; concrete database, cache, and HTTP clients stay in infrastructure.

| Area | Owns | Avoids |
| --- | --- | --- |
| Domain | Business invariants, entities, value objects, and domain contracts | FastAPI, Pydantic transport schemas, ORM models, sessions, external clients |
| Application | Use cases and application policy | HTTP status codes, SQL/query construction, concrete infrastructure adapters |
| Infrastructure | Database and service adapters, ORM mapping, external integrations | Owning business policy or importing presentation |
| Presentation | HTTP validation, response mapping, approved error translation | Raw SQL, business workflows, constructing concrete repositories |
| Composition root | Dependency providers and application startup wiring | Business rules |

## Choose domain modeling where it helps

Use domain concepts when they carry identity, invariants, lifecycle, or meaningful state changes. Dataclasses are a lightweight option for framework-independent entities and value objects. Define a contract when an application rule needs an abstraction; use the interface or ABC style already established in the repository.

Do not add aggregates, service layers, repository base classes, or a `ports/` directory just to fill a template. Straightforward CRUD can use a simpler established path when no policy needs orchestration.

## Example feature path

An illustrative layout for a user-registration workflow:

```text
app/
├── domain/users/                 # User rules and repository contract
├── application/users/register.py # Registration workflow
├── infrastructure/db/users.py    # SQL implementation and row mapping
├── presentation/api/users.py     # FastAPI request/response handling
└── main.py                       # Application and dependency wiring
```

Feature-oriented or monolithic layouts are equally valid if the ownership and import boundaries remain clear.

### Domain contract and entity

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: str
    email: str


class UserRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    async def save(self, user: User) -> User:
        ...
```

The contract uses domain types. It does not expose a SQLAlchemy model, SQL expression, or database session.

### Application use case

```python
class RegisterUser:
    def __init__(self, users: UserRepository):
        self._users = users

    async def execute(self, email: str) -> User:
        if await self._users.get_by_email(email):
            raise UserAlreadyExists(email)

        return await self._users.save(User(id=create_id(), email=email))
```

The use case owns the workflow and calls the contract. It does not import FastAPI, open a database session, or construct a SQL repository.

### Infrastructure adapter

```python
class SQLUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        row = await load_user_row(self._session, email)
        return to_domain(row) if row else None

    async def save(self, user: User) -> User:
        row = to_user_row(user)
        self._session.add(row)
        await self._session.flush()
        return to_domain(row)
```

Persistence mapping belongs in this adapter or a nearby mapper. Keep ORM models and sessions out of the domain and application contracts.

### FastAPI handler and composition

```python
class RegisterUserRequest(BaseModel):
    email: EmailStr


@router.post("/users", response_model=UserResponse)
async def register_user(
    body: RegisterUserRequest,
    use_case: RegisterUser = Depends(get_register_user),
) -> UserResponse:
    user = await use_case.execute(str(body.email))
    return UserResponse(id=user.id, email=user.email)
```

The dependency provider is the composition root: it creates the concrete SQL adapter and injects it into `RegisterUser`. The handler only translates transport input and output. Map approved application errors to HTTP responses in the repository's established exception handling path.

Keep Pydantic request and response schemas in presentation unless the repository has an explicit convention that places transport DTOs elsewhere. Do not make domain entities double as request bodies or ORM rows.

### Database connection and request usage

The UserManagement database setup is a useful reference for separating resource lifecycle from transaction ownership. Treat the names and layout below as an example; keep the target repository's established transaction boundary if it uses a Unit of Work or another explicit abstraction.

- `DatabaseConnection` creates sync/async engines and session factories, yields sessions, and disposes engines. It owns connection resources, not `begin`, `commit`, or `rollback`.
- `DatabaseManager` selects a configured connection and wraps a session in one transaction. A successful scope commits; an exception rolls it back. Repositories can add or flush rows, but do not commit independently.
- The application lifespan initializes and disposes the manager. A session provider scopes a database session to the request, and presentation composition injects a concrete repository into application behavior.

The connection adapter yields and closes a session without deciding the transaction outcome:

```python
# infrastructure/database/connection.py
@asynccontextmanager
async def get_async_session(self) -> AsyncIterator[AsyncSession]:
    if self._async_session_maker is None:
        await self.get_async_engine()

    async with self._async_session_maker() as session:
        yield session
```

```python
# infrastructure/database/dependencies.py
async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with database_manager.get_async_session("default") as session:
        yield session


# presentation/dependencies/repositories.py
def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IUserRepository:
    return UserRepository(session)


def get_register_user(
    users: IUserRepository = Depends(get_user_repository),
) -> RegisterUser:
    return RegisterUser(users)
```

The manager's current implementation also maps database failures to its error contract; the core transaction scope is:

```python
@asynccontextmanager
async def get_async_session(self, name: str = "default") -> AsyncIterator[AsyncSession]:
    async with self.get_connection(name).get_async_session() as session:
        async with session.begin():
            yield session
```

At startup and shutdown, the composition root owns engine initialization and disposal:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await database_manager.connect()
    try:
        yield
    finally:
        await database_manager.disconnect()
```

This keeps raw sessions and transaction mechanics out of handlers and use cases. Do not copy `DatabaseManager` as a required pattern: when the target repository assigns transaction control to a Unit of Work, keep commit and rollback there and avoid a second owner.

## Transaction and background-work boundaries

Keep database session lifecycle and adapter mechanics in infrastructure/composition. If a workflow needs a transaction across multiple operations, express that boundary using the target repository's established abstraction and let the composition root provide its implementation. Avoid opening or committing database sessions inside route handlers.

Celery tasks, scheduled jobs, and event consumers are entry points like HTTP routes: they translate input, invoke application behavior, and receive dependencies from a composition boundary. They should not duplicate the use case's business rules.

## Common boundary violations

- **Business policy in a route:** move workflow decisions into a use case or domain behavior; keep HTTP validation and error translation in presentation.
- **Application imports a concrete ORM repository:** depend on a domain/application contract and inject the adapter at the composition root.
- **Domain entity is an ORM model:** keep persistence rows in infrastructure and map them to domain types.
- **Pydantic or FastAPI types leak into domain rules:** translate transport input at the presentation boundary.
- **Empty use-case wrappers for simple CRUD:** follow the closest working repository pattern unless a real workflow or policy needs coordination.
- **A directory name is treated as proof:** inspect imports, calls, and data mapping across a real feature path.

## Review checklist

1. Who owns each business invariant?
2. Can domain and application behavior run without FastAPI or a database?
3. Do imports point inward, with infrastructure implementing the contracts it needs?
4. Where are transport and persistence representations mapped?
5. Are authorization, errors, transactions, and audit behavior preserved?
6. Do routes and workers invoke application behavior instead of duplicating it?
