# API Response Helper Usage

The helper is in `skills/api-design/tools/` from the repository root. Its response bodies follow [`SKILL.md`](SKILL.md); HTTP status codes are set separately by the framework.

## Python

```python
from api_standard import APIResponse, ResponseBuilder

success = APIResponse.success(message="User retrieved", data={"id": 1})
error = APIResponse.error(
    message="User not found",
    details=[{"code": "USER_NOT_FOUND", "message": "No user exists with that ID"}],
)

page = (
    ResponseBuilder()
    .with_message("Users retrieved successfully")
    .with_data(users)
    .with_pagination(page=1, per_page=20, total=100)
    .build()
)
```

Convert a body to a dictionary or JSON with `to_dict()` or `to_json()`. Set HTTP codes in the route/response layer, for example `200` for success and `404` for a missing resource.

## CLI

From the `skills/api-design/` directory:

```bash
./tools/api-standard.sh template
./tools/api-standard.sh success
./tools/api-standard.sh pagination
./tools/api-standard.sh error
```
