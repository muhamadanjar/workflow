# API Standard Skill

Personal skill untuk standardisasi API response format dengan struktur: `status`, `data`, `metas`, `message`.

## Quick Start

### Usage

```bash
# Display template
./api-standard.sh template

# Show examples
./api-standard.sh pagination
./api-standard.sh builder
./api-standard.sh error

# Full documentation
./api-standard.sh docs
./api-standard.sh help
```

### Python

```python
from api_standard import APIResponse, ResponseBuilder, show_standard

# Display quick reference
show_standard()

# Simple response
resp = APIResponse.success(message="OK", data={"id": 1})

# Complex response with pagination
resp = ResponseBuilder()\
    .with_message("Users")\
    .with_data(items)\
    .with_pagination(page=1, page_size=10, total=100)\
    .build()

# Error
resp = APIResponse.error(message="Not found")
```

## Response Format

```json
{
  "status": "success" | "error",
  "data": null | {} | [],
  "metas": {
    "page": 1,
    "page_size": 10,
    "total": 100,
    "total_pages": 10,
    "time_elapsed": "12.34ms"
  },
  "message": "General message"
}
```

## Files

- **api_standard.py** - Python module with APIResponse, ResponseBuilder classes
- **api-standard.sh** - Shell script for quick reference commands
- **README.md** - This file

## Classes

### APIResponse

Pydantic-like model for simple responses.

```python
# Success
APIResponse.success(message="OK", data=user, metas={})

# Error
APIResponse.error(message="Error", data=None, metas={})

# Methods
resp.to_dict()   # Get dictionary
resp.to_json()   # Get JSON string
```

### ResponseBuilder

Builder pattern for complex responses with method chaining.

```python
ResponseBuilder()\
    .with_status("success")\
    .with_message("Items")\
    .with_data(items)\
    .add_meta("queue", "etl")\
    .with_pagination(page=1, page_size=10, total=100)\
    .build()

# Methods
.with_status(status)              # "success" | "error"
.with_message(msg)                # Response message
.with_data(data)                  # Response data
.add_meta(key, value)             # Add single metadata
.with_metas(dict)                 # Add multiple metadata
.with_pagination(page, size, total) # Auto-add pagination
.build()                          # Build (auto time_elapsed)
```

## Examples

### GET Single Resource

```python
from app.core.response import APIResponse

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = db.get_user(user_id)
    if not user:
        return APIResponse.error(message="User not found")
    return APIResponse.success(message="User retrieved", data=user)
```

Response:
```json
{
  "status": "success",
  "message": "User retrieved",
  "data": {"id": 1, "name": "John"},
  "metas": {}
}
```

### GET List with Pagination

```python
from app.core.response import ResponseBuilder

@app.get("/users")
async def list_users(page: int = 1, page_size: int = 10):
    users, total = db.list_users(page, page_size)
    return ResponseBuilder()\
        .with_message("Users retrieved")\
        .with_data(users)\
        .with_pagination(page=page, page_size=page_size, total=total)\
        .build()
```

Response:
```json
{
  "status": "success",
  "message": "Users retrieved",
  "data": [{...}, {...}],
  "metas": {
    "page": 1,
    "page_size": 10,
    "total": 100,
    "total_pages": 10,
    "time_elapsed": "15.32ms"
  }
}
```

### POST Create Resource

```python
@app.post("/users")
async def create_user(name: str, email: str):
    if not name or not email:
        return ResponseBuilder()\
            .with_status("error")\
            .with_message("name and email required")\
            .add_meta("required_fields", ["name", "email"])\
            .build()
    
    user = db.create_user(name, email)
    return ResponseBuilder()\
        .with_message("User created")\
        .with_data(user)\
        .add_meta("created_at", user.created_at.isoformat())\
        .build()
```

### DELETE Resource

```python
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    db.delete_user(user_id)
    return ResponseBuilder()\
        .with_message("User deleted")\
        .add_meta("deleted_id", user_id)\
        .build()
```

## Common Metas

| Key | Type | Example | Use Case |
|-----|------|---------|----------|
| `page` | int | `1` | Pagination |
| `page_size` | int | `10` | Pagination |
| `total` | int | `100` | Pagination |
| `total_pages` | int | `10` | Pagination (auto) |
| `time_elapsed` | string | `"12.34ms"` | Performance (auto) |
| `queue` | string | `"etl_high"` | Background jobs |
| `priority` | string | `"high"` | Job priority |
| `worker_id` | string | `"worker_02"` | Processing |
| `created_at` | string | `"2026-05-20T..."` | Timestamps |
| `updated_at` | string | `"2026-05-20T..."` | Timestamps |
| `errors` | dict | `{"field": "message"}` | Validation |
| Custom | any | any | Custom metadata |

## Auto-Features

### time_elapsed
ResponseBuilder automatically tracks execution time:

```python
builder = ResponseBuilder()  # Start time recorded
# ... do work ...
builder.build()  # time_elapsed auto-added in milliseconds
```

### total_pages
Auto-calculated from total and page_size:

```python
ResponseBuilder()\
    .with_pagination(page=1, page_size=10, total=100)\
    .build()
# Auto-adds: total_pages = (100 + 10 - 1) // 10 = 10
```

## Integration

### Project Services

This skill is integrated into:
- ✓ etl_api - `app/core/response.py`
- ✓ payment_api - `app/core/response.py`
- ✓ usermanagement_api - `app/core/response.py`
- ✓ tileserver_api - `app/core/response.py`

All services have identical implementation.

### Import in Endpoints

```python
# From local project
from app.core.response import APIResponse, ResponseBuilder

# Or globally
import sys
sys.path.insert(0, '/home/anjar/.claude/skills/api-standard')
from api_standard import APIResponse, ResponseBuilder
```

## Commands

### Help
```bash
./api-standard.sh help
```

### Display Template
```bash
./api-standard.sh template
```

### Examples
```bash
./api-standard.sh simple       # Simple success
./api-standard.sh pagination   # With pagination
./api-standard.sh builder      # ResponseBuilder pattern
./api-standard.sh error        # Error response
./api-standard.sh python       # Python module usage
```

### Documentation
```bash
./api-standard.sh docs   # Full specification
./api-standard.sh setup  # Implementation guide
```

## Tips

1. **Use ResponseBuilder** for pagination and complex responses
2. **Use APIResponse** for simple success/error
3. **time_elapsed auto-adds** - don't add manually
4. **Chain methods** - ResponseBuilder supports fluent interface
5. **Custom metas** - add as needed with `.add_meta()`
6. **Validation errors** - use `.add_meta("errors", {...})`
7. **Timestamps** - use ISO format for date fields

## Related Documentation

- Full spec: `API_RESPONSE_STANDARD.md` (in project root)
- Setup guide: `API_RESPONSE_SETUP.md` (in project root)
- Global reference: `/home/anjar/.claude/API_STANDARD_SKILL.md`

---

Created: 2026-05-20  
Skill: API Standard v1.0  
Type: Personal Reference Skill
