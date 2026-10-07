# API Response Helper

The helper in `tools/api_standard.py` follows the shared envelope in [`SKILL.md`](SKILL.md). It never adds a JSON `status` field. Choose the HTTP status code in the framework response itself.

## Success

```json
{
  "message": "Users retrieved successfully",
  "data": [],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 0,
      "total_pages": 0
    }
  }
}
```

`message` and `meta` are always present. Include `data` when the operation returns a payload. Use `meta: {}` when there is no additional metadata.

## Error

```json
{
  "message": "The requested user was not found",
  "details": [
    {"code": "USER_NOT_FOUND", "message": "No user exists with that ID"}
  ]
}
```

Errors use `message` and `details`; they do not include success metadata. Return the appropriate HTTP status separately.

## Python

```python
from api_standard import APIResponse, ResponseBuilder

# Success
body = APIResponse.success(message="User retrieved", data={"id": 1})
return JSONResponse(body.to_dict(), status_code=200)

# Error
body = APIResponse.error(
    message="User not found",
    details=[{"code": "USER_NOT_FOUND", "message": "No user exists with that ID"}],
)
return JSONResponse(body.to_dict(), status_code=404)

# Paginated success
body = (
    ResponseBuilder()
    .with_message("Users retrieved successfully")
    .with_data(users)
    .with_pagination(page=1, per_page=20, total=100)
    .build()
)
```

`ResponseBuilder.with_pagination` uses the `meta.pagination` shape from the shared standard. Validate query parameters at the endpoint boundary (`page >= 1`, `1 <= per_page <= 100`).

## CLI

Run commands from `skills/api-design/`:

```bash
./tools/api-standard.sh template
./tools/api-standard.sh success
./tools/api-standard.sh pagination
./tools/api-standard.sh error
```
