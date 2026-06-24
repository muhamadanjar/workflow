# Unit Testing Guide

## Python: pytest + unittest.mock

### Basic Test
```python
import pytest
from myapp.services import UserService
from unittest.mock import Mock, patch

class TestUserService:
    def test_get_user_success(self):
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = {"id": "123", "name": "John"}
        service = UserService(repository=mock_repo)
        
        # Act
        result = service.get_user("123")
        
        # Assert
        assert result["name"] == "John"
        mock_repo.get_by_id.assert_called_once_with("123")
    
    def test_get_user_not_found(self):
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None
        service = UserService(repository=mock_repo)
        
        with pytest.raises(UserNotFoundError):
            service.get_user("invalid")
```

### Test with Fixtures
```python
@pytest.fixture
def user_service():
    mock_repo = Mock()
    return UserService(repository=mock_repo)

@pytest.fixture
def sample_user():
    return {"id": "123", "name": "John", "email": "john@example.com"}

def test_create_user(user_service, sample_user):
    user_service.repository.create.return_value = sample_user
    
    result = user_service.create(sample_user)
    assert result["id"] == "123"
```

### Mocking External Calls
```python
from unittest.mock import patch

@patch('myapp.services.requests.get')
def test_fetch_external_data(mock_get):
    mock_get.return_value.json.return_value = {"data": "value"}
    
    service = ExternalService()
    result = service.fetch_data()
    
    assert result["data"] == "value"
    mock_get.assert_called_once()
```

## Go: testing + testify

### Basic Test
```go
package services

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestGetUser(t *testing.T) {
    // Arrange
    repo := &MockUserRepository{}
    repo.GetByIDFunc = func(id string) (*User, error) {
        return &User{ID: "123", Name: "John"}, nil
    }
    service := NewUserService(repo)
    
    // Act
    user, err := service.GetUser("123")
    
    // Assert
    require.NoError(t, err)
    assert.Equal(t, "John", user.Name)
    assert.Equal(t, 1, repo.GetByIDCallCount)
}
```

### Table-Driven Tests
```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        email string
        valid bool
        name  string
    }{
        {"user@example.com", true, "valid email"},
        {"invalid.email", false, "missing domain"},
        {"@example.com", false, "missing local part"},
        {"", false, "empty email"},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := ValidateEmail(tt.email)
            assert.Equal(t, tt.valid, result)
        })
    }
}
```

### Mocking Interfaces
```go
type MockRepository struct {
    GetByIDFunc func(id string) (*User, error)
    SaveFunc    func(user *User) error
}

func (m *MockRepository) GetByID(id string) (*User, error) {
    return m.GetByIDFunc(id)
}

func (m *MockRepository) Save(user *User) error {
    return m.SaveFunc(user)
}

func TestUserService(t *testing.T) {
    mock := &MockRepository{
        GetByIDFunc: func(id string) (*User, error) {
            return &User{ID: id, Name: "Test"}, nil
        },
    }
    
    service := NewUserService(mock)
    user, _ := service.GetUser("123")
    assert.Equal(t, "Test", user.Name)
}
```

## React: Jest + React Testing Library

### Component Test
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import UserProfile from './UserProfile';

describe('UserProfile', () => {
    it('displays user name', () => {
        const user = { id: '1', name: 'John', email: 'john@example.com' };
        render(<UserProfile user={user} />);
        
        expect(screen.getByText('John')).toBeInTheDocument();
    });
    
    it('calls onDelete when delete button clicked', () => {
        const onDelete = jest.fn();
        render(<UserProfile user={{ id: '1' }} onDelete={onDelete} />);
        
        fireEvent.click(screen.getByRole('button', { name: /delete/i }));
        
        expect(onDelete).toHaveBeenCalled();
    });
});
```

### Async Component Test
```javascript
import { render, screen, waitFor } from '@testing-library/react';
import UserList from './UserList';

it('loads and displays users', async () => {
    jest.spyOn(window, 'fetch').mockResolvedValue({
        json: async () => [
            { id: '1', name: 'John' },
            { id: '2', name: 'Jane' }
        ]
    });
    
    render(<UserList />);
    
    await waitFor(() => {
        expect(screen.getByText('John')).toBeInTheDocument();
        expect(screen.getByText('Jane')).toBeInTheDocument();
    });
});
```

### Hook Test
```javascript
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

it('increments counter', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
        result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
});
```

## Test Pyramid

```
        /\
       /E2E\         Few
      /-----\
     /Integ/\
    /------/\
   /Unit/  /\       Many
  /------\/--\
```

### Ratios
- Unit tests: 70%
- Integration tests: 20%
- E2E tests: 10%

## Test Coverage

### Python Coverage
```bash
# Run with coverage
pytest --cov=myapp tests/

# Generate report
coverage report
coverage html  # Creates htmlcov/index.html
```

### Go Coverage
```bash
# Run with coverage
go test -cover ./...

# Generate HTML report
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

## Common Mistakes to Avoid

- ❌ Testing implementation, not behavior
- ❌ Tests that are too brittle
- ❌ Not testing error cases
- ❌ Incomplete mocking
- ❌ Tests that depend on each other
- ❌ Ignoring edge cases
- ❌ Slow tests that don't scale
- ❌ Copy-pasting test code
