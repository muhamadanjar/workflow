"""
Personal API Standard Skill
===========================

Generate standardized API response with status, data, metas, message.

Usage:
  from claude.api_standard import APIResponse, ResponseBuilder, show_standard

  # Simple response
  show_standard()  # Display template

  # Code snippet
  resp = APIResponse.success(message="OK", data={"id": 1})

  # Builder (recommended)
  resp = ResponseBuilder()\
      .with_message("Items")\
      .with_data(items)\
      .with_pagination(page=1, page_size=10, total=100)\
      .build()
"""

from typing import Optional, Any, Literal, Dict
from dataclasses import dataclass, field, asdict
import time
from datetime import datetime


@dataclass
class APIResponse:
    """Standard API response model"""
    status: Literal["success", "error"]
    message: str
    data: Optional[Any] = None
    metas: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), indent=2, default=str)

    @staticmethod
    def success(message: str = "OK", data: Optional[Any] = None, metas: Optional[dict] = None) -> "APIResponse":
        return APIResponse(
            status="success",
            message=message,
            data=data,
            metas=metas or {}
        )

    @staticmethod
    def error(message: str = "Error", data: Optional[Any] = None, metas: Optional[dict] = None) -> "APIResponse":
        return APIResponse(
            status="error",
            message=message,
            data=data,
            metas=metas or {}
        )


class ResponseBuilder:
    """Builder for constructing API responses"""

    def __init__(self):
        self._status: Literal["success", "error"] = "success"
        self._message: str = "OK"
        self._data: Optional[Any] = None
        self._metas: Dict[str, Any] = {}
        self._start_time: float = time.time()

    def with_status(self, status: Literal["success", "error"]) -> "ResponseBuilder":
        self._status = status
        return self

    def with_message(self, message: str) -> "ResponseBuilder":
        self._message = message
        return self

    def with_data(self, data: Any) -> "ResponseBuilder":
        self._data = data
        return self

    def add_meta(self, key: str, value: Any) -> "ResponseBuilder":
        self._metas[key] = value
        return self

    def with_metas(self, metas: Dict[str, Any]) -> "ResponseBuilder":
        self._metas.update(metas)
        return self

    def with_pagination(self, page: int, page_size: int, total: int) -> "ResponseBuilder":
        self._metas.update({
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        })
        return self

    def build(self) -> APIResponse:
        self._metas.setdefault("time_elapsed", f"{(time.time() - self._start_time) * 1000:.2f}ms")
        return APIResponse(
            status=self._status,
            message=self._message,
            data=self._data,
            metas=self._metas
        )


def show_standard() -> None:
    """Display API standard template"""
    template = """
╔════════════════════════════════════════════════════════════════╗
║              API STANDARD RESPONSE TEMPLATE                    ║
╚════════════════════════════════════════════════════════════════╝

FORMAT
──────
{
  "status": "success" | "error",
  "data": null | {} | [],
  "metas": { "page": 1, "time_elapsed": "12.34ms", ... },
  "message": "General message"
}


QUICK USAGE
───────────
# Simple
APIResponse.success(message="OK", data=user)

# Complex (recommended)
ResponseBuilder()\\
    .with_message("Users")\\
    .with_data(items)\\
    .with_pagination(page=1, page_size=10, total=100)\\
    .build()


RESPONSE BUILDER METHODS
─────────────────────────
.with_status("success" | "error")
.with_message(msg)
.with_data(data)
.add_meta(key, value)
.with_metas(dict)
.with_pagination(page, page_size, total)
.build()  # Auto-adds time_elapsed


COMMON METAS
────────────
- page, page_size, total, total_pages  (pagination)
- time_elapsed                          (auto)
- queue, priority, worker_id            (jobs)
- created_at, updated_at                (timestamps)
- errors, warnings                      (validation)


EXAMPLES
─────────

Success (no data):
  APIResponse.success(message="Deleted")

Success (with data):
  APIResponse.success(message="User", data={"id": 1})

Success (with pagination):
  ResponseBuilder()\\
    .with_data(users)\\
    .with_pagination(page=1, page_size=10, total=100)\\
    .build()

Error:
  APIResponse.error(message="Not found")

Error (with details):
  ResponseBuilder()\\
    .with_status("error")\\
    .with_message("Validation failed")\\
    .add_meta("errors", {"email": "Invalid"})\\
    .build()


SERVICES
─────────
✓ etl_api
✓ payment_api
✓ usermanagement_api
✓ tileserver_api

Documentation: /home/anjar/Development/base-project-apps/API_RESPONSE_STANDARD.md
"""
    print(template)


# Auto-display on import with verbose mode
if __name__ == "__main__":
    show_standard()
