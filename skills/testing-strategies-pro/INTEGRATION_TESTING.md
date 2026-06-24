# Integration Testing Guide

## Database Integration Tests (Python)

### Using pytest-postgresql
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from myapp.database import Base
from myapp.models import User
from myapp.repositories import UserRepository

@pytest.fixture(scope="session")
def db():
    # Create test database
    engine = create_engine("postgresql://user:password@localhost/test_db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def session(db):
    connection = db.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

def test_user_repository(session):
    repo = UserRepository(session)
    
    # Create
    user = User(name="John", email="john@example.com")
    repo.save(user)
    
    # Read
    fetched = repo.get_by_email("john@example.com")
    assert fetched.name == "John"
    
    # Update
    fetched.name = "Jane"
    repo.save(fetched)
    
    # Verify
    updated = repo.get_by_email("john@example.com")
    assert updated.name == "Jane"
```

### Using testcontainers
```python
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres.get_connection_url()

def test_with_real_postgres(postgres):
    engine = create_engine(postgres)
    # Run actual database tests
```

## API Integration Tests

### Testing FastAPI Endpoints
```python
import pytest
from fastapi.testclient import TestClient
from myapp.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Setup test database
    create_test_db()
    yield
    # Teardown
    drop_test_db()

def test_create_user_endpoint(client):
    response = client.post("/users", json={
        "name": "John",
        "email": "john@example.com"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John"

def test_get_user_endpoint(client):
    # First create a user
    client.post("/users", json={"name": "John", "email": "john@example.com"})
    
    # Then fetch it
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "John"

def test_list_users_pagination(client):
    # Create multiple users
    for i in range(25):
        client.post("/users", json={
            "name": f"User{i}",
            "email": f"user{i}@example.com"
        })
    
    # Test pagination
    response = client.get("/users?page=1&per_page=10")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 10
```

### Testing Go HTTP Handlers
```go
package handlers

import (
    "testing"
    "bytes"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "github.com/stretchr/testify/assert"
)

func TestCreateUserHandler(t *testing.T) {
    // Setup
    repo := NewMockUserRepository()
    handler := NewUserHandler(repo)
    router := setupRouter(handler)
    
    // Create request
    user := map[string]string{"name": "John", "email": "john@example.com"}
    body, _ := json.Marshal(user)
    req := httptest.NewRequest("POST", "/users", bytes.NewReader(body))
    
    // Execute
    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)
    
    // Assert
    assert.Equal(t, http.StatusCreated, w.Code)
    var response map[string]interface{}
    json.NewDecoder(w.Body).Decode(&response)
    assert.Equal(t, "John", response["name"])
}
```

## Service Integration Tests

### Testing Microservices Together
```python
import pytest
from docker.client import DockerClient
import time

@pytest.fixture(scope="session")
def services():
    client = DockerClient()
    
    # Start services
    db = client.containers.run("postgres:15", detach=True)
    api = client.containers.run("myapp:latest", detach=True)
    
    # Wait for services to start
    time.sleep(5)
    
    yield
    
    # Cleanup
    api.stop()
    db.stop()

def test_end_to_end_flow(services):
    # Call API which uses database
    response = requests.post("http://localhost:8080/users", json={
        "name": "John"
    })
    assert response.status_code == 201
```

## External Service Integration Tests

### Mocking External APIs
```python
import pytest
import responses

@responses.activate
def test_with_mocked_external_api():
    # Setup mock
    responses.add(
        responses.GET,
        "https://api.example.com/users/123",
        json={"id": "123", "name": "John"},
        status=200
    )
    
    # Test code that calls external API
    service = ExternalService()
    user = service.fetch_user("123")
    assert user["name"] == "John"
```

### Using VCR for Recording
```python
import pytest
import vcr

@vcr.VCR(
    cassette_library_dir='tests/cassettes',
    record_mode='once'  # Record on first run, replay after
)
def test_external_api_call():
    # First run: records actual API call
    # Subsequent runs: plays back recorded response
    service = ExternalService()
    result = service.call_api()
    assert result is not None
```

## Redis Integration Tests
```python
@pytest.fixture
def redis():
    import fakeredis
    return fakeredis.FakeStrictRedis()

def test_cache_operations(redis):
    from myapp.cache import CacheService
    cache = CacheService(redis)
    
    # Set
    cache.set("key", "value", ttl=60)
    
    # Get
    assert cache.get("key") == "value"
    
    # Expire
    time.sleep(1)
    assert cache.get("key") == "value"
```

## Test Database Factories
```python
import factory
from myapp.models import User, Post

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    id = factory.Faker('uuid4')
    name = factory.Faker('name')
    email = factory.Faker('email')

class PostFactory(factory.Factory):
    class Meta:
        model = Post
    
    id = factory.Faker('uuid4')
    title = factory.Faker('word')
    content = factory.Faker('text')
    author = factory.SubFactory(UserFactory)

def test_with_factories(session):
    user = UserFactory()
    posts = [PostFactory(author=user) for _ in range(5)]
    
    assert len(user.posts) == 5
```
