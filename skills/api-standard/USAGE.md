# API Standard Skill - Usage Guide

Personal skill untuk standardisasi API response di semua services.

## Location

`/home/anjar/.claude/skills/api-standard/`

Files:
- `api_standard.py` - Python module
- `api-standard.sh` - Shell script
- `README.md` - Full documentation
- `USAGE.md` - This file

## Quick Start

### Shell Command

```bash
cd /home/anjar/.claude/skills/api-standard

# Display template
./api-standard.sh template

# Show examples
./api-standard.sh simple
./api-standard.sh pagination
./api-standard.sh builder
./api-standard.sh error

# Documentation
./api-standard.sh help
./api-standard.sh docs
```

### Python Module

```python
import sys
sys.path.insert(0, '/home/anjar/.claude/skills/api-standard')
from api_standard import APIResponse, ResponseBuilder, show_standard

# Display quick reference
show_standard()

# Create response
resp = APIResponse.success(message="OK", data={"id": 1})
print(resp.to_dict())
print(resp.to_json())

# Build complex response
resp = ResponseBuilder()\
    .with_message("Users")\
    .with_data(users)\
    .with_pagination(page=1, page_size=10, total=100)\
    .build()
```

### In Project Endpoints

Each service has `app/core/response.py`:

```python
from app.core.response import APIResponse, ResponseBuilder

# Simple success
return APIResponse.success(message="User retrieved", data=user)

# Simple error
return APIResponse.error(message="User not found")

# Complex with pagination
return ResponseBuilder()\
    .with_message("Users retrieved")\
    .with_data(users)\
    .with_pagination(page=1, page_size=10, total=100)\
    .build()

# Error with details
return ResponseBuilder()\
    .with_status("error")\
    .with_message("Validation failed")\
    .add_meta("errors", {"email": "Invalid format"})\
    .build()
```

## Response Format

```json
{
  "status": "success" | "error",
  "message": "General message",
  "data": null | {} | [],
  "metas": {
    "page": 1,
    "page_size": 10,
    "total": 100,
    "total_pages": 10,
    "time_elapsed": "12.34ms"
  }
}
```

## Classes

### APIResponse

Simple success/error responses.

```python
# Success
APIResponse.success(message="OK", data=user, metas={})

# Error
APIResponse.error(message="Error", data=None, metas={})

# Methods
resp.to_dict()   # Dictionary
resp.to_json()   # JSON string
```

### ResponseBuilder

Complex responses with method chaining.

```python
ResponseBuilder()\
    .with_status("success")\
    .with_message("Message")\
    .with_data(data)\
    .add_meta("key", "value")\
    .with_pagination(page=1, page_size=10, total=100)\
    .build()
```

Methods:
- `.with_status(status)` - "success" or "error"
- `.with_message(msg)` - Response message
- `.with_data(data)` - Response data (dict, list, or null)
- `.add_meta(key, value)` - Add single metadata
- `.with_metas(dict)` - Add multiple metadata
- `.with_pagination(page, page_size, total)` - Auto-add pagination
- `.build()` - Build response (auto-adds time_elapsed)

## Auto-Features

### time_elapsed
Automatically tracks execution time in milliseconds:

```python
builder = ResponseBuilder()  # Timer starts
# ... do work ...
resp = builder.build()  # time_elapsed auto-added
```

### total_pages
Auto-calculated from total and page_size:

```python
ResponseBuilder()\
    .with_pagination(page=1, page_size=10, total=100)\
    .build()
# Auto-calculates: total_pages = (100 + 10 - 1) // 10 = 10
```

## Common Patterns

### GET Single Resource

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = db.get_user(user_id)
    if not user:
        return APIResponse.error(message="User not found")
    return APIResponse.success(message="User retrieved", data=user)
```

### GET List with Pagination

```python
@app.get("/users")
async def list_users(page: int = 1, page_size: int = 10):
    users, total = db.list_users(page, page_size)
    return ResponseBuilder()\
        .with_message("Users retrieved")\
        .with_data(users)\
        .with_pagination(page=page, page_size=page_size, total=total)\
        .build()
```

### POST Create

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

### DELETE

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

| Key | Type | Example |
|-----|------|---------|
| `page` | int | `1` |
| `page_size` | int | `10` |
| `total` | int | `100` |
| `total_pages` | int | `10` |
| `time_elapsed` | string | `"12.34ms"` |
| `queue` | string | `"etl_jobs"` |
| `priority` | string | `"high"` |
| `worker_id` | string | `"worker_02"` |
| `created_at` | string | `"2026-05-20T10:30:00Z"` |
| `errors` | dict | `{"field": "message"}` |

## Services

All services have identical implementation:
- ✓ etl_api - `app/core/response.py`
- ✓ payment_api - `app/core/response.py`
- ✓ usermanagement_api - `app/core/response.py`
- ✓ tileserver_api - `app/core/response.py`

## Tips

1. Use `ResponseBuilder` for pagination and complex responses
2. Use `APIResponse` for simple success/error
3. Don't manually add `time_elapsed` - it's auto-added
4. Chain methods for readable code
5. Use `.add_meta()` for custom metadata
6. Use `.add_meta("errors", {...})` for validation errors
7. Use ISO format for timestamps

## Test Example

```python
import sys
sys.path.insert(0, '/home/anjar/.claude/skills/api-standard')
from api_standard import APIResponse, ResponseBuilder

# Test 1
resp1 = APIResponse.success(message="Test", data={"id": 1})
print(resp1.to_json())

# Test 2
resp2 = ResponseBuilder()\
    .with_message("Items")\
    .with_data([1, 2, 3])\
    .with_pagination(page=1, page_size=10, total=100)\
    .build()
print(resp2.to_json())
```

## Next Steps

1. Copy `api_standard.py` to your project if needed
2. Import `APIResponse` and `ResponseBuilder` in endpoints
3. Replace existing response logic
4. Test GET, POST, DELETE endpoints
5. Verify pagination format
6. Check error response format

---

Updated: 2026-05-20
Version: 1.0
