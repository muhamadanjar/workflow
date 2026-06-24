# RESTful API Design Guide

## Resource-Oriented Design

### Resource Naming
```
/users              GET all, POST create
/users/{id}         GET one, PUT update, DELETE
/users/{id}/posts   GET user's posts
/users/{id}/posts/{postId}  GET specific post
```

### Avoid Action-Based URLs
```
❌ /users/getAll
❌ /users/createUser
❌ /posts/deletePost

✅ GET /users
✅ POST /users
✅ DELETE /posts/{id}
```

## HTTP Methods

| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Retrieve | ✅ | ✅ |
| POST | Create | ❌ | ❌ |
| PUT | Replace (full) | ✅ | ❌ |
| PATCH | Partial update | ❌ | ❌ |
| DELETE | Delete | ✅ | ❌ |

## Status Codes

### Success (2xx)
```
200 OK - Request succeeded
201 Created - Resource created
202 Accepted - Async operation started
204 No Content - No response body
```

### Client Error (4xx)
```
400 Bad Request - Invalid input
401 Unauthorized - Auth required
403 Forbidden - Auth'd but no permission
404 Not Found - Resource doesn't exist
409 Conflict - Request conflicts with state
422 Unprocessable Entity - Validation failed
429 Too Many Requests - Rate limited
```

### Server Error (5xx)
```
500 Internal Server Error - Unexpected error
502 Bad Gateway - Upstream error
503 Service Unavailable - Maintenance
504 Gateway Timeout - Request timeout
```

## Request/Response Format

### Standard Response Envelope
```json
{
  "data": {
    "id": "123",
    "name": "John",
    "email": "john@example.com"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req-123"
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": [
      {
        "field": "email",
        "message": "required field"
      }
    ]
  }
}
```

### List Response with Pagination
```json
{
  "data": [
    {"id": "1", "name": "User 1"},
    {"id": "2", "name": "User 2"}
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8
  }
}
```

## Pagination

### Query Parameters
```
GET /users?page=2&per_page=50
GET /users?limit=50&offset=100  # Alternative
GET /users?cursor=abc123&limit=50  # Cursor-based
```

### Response Headers
```
Link: <https://api.example.com/users?page=3>; rel="next",
      <https://api.example.com/users?page=1>; rel="prev",
      <https://api.example.com/users?page=8>; rel="last"
```

## Filtering & Sorting

```
# Filtering
GET /users?role=admin&status=active
GET /posts?created_after=2024-01-01&created_before=2024-12-31

# Sorting
GET /users?sort=name,-created_at  # name asc, created_at desc
GET /users?order_by=name&order=asc

# Search
GET /users?search=john
GET /users?q=john@example.com
```

## Versioning

### URL Path
```
GET /v1/users
GET /v2/users
```

### Accept Header
```
GET /users
Accept: application/vnd.myapp.v1+json

GET /users
Accept: application/vnd.myapp.v2+json
```

### Query Parameter
```
GET /users?api-version=2
```

## Request Validation

```python
# Python/FastAPI example
from pydantic import BaseModel, Field, validator

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(..., ge=0, le=150)
    
    @validator('email')
    def email_must_be_unique(cls, v):
        if User.get_by_email(v):
            raise ValueError('Email already registered')
        return v
```

## CORS & Security Headers

```
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400

X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

## API Documentation

### OpenAPI/Swagger
```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0

paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
```

## Rate Limiting Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705329600
```

## Backward Compatibility

- Don't remove fields
- Don't change field types
- Add optional fields with defaults
- Mark deprecated fields
- Use API versioning for major changes
