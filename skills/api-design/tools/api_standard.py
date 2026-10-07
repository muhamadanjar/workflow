"""Helpers for the shared REST/JSON response envelope."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json


@dataclass
class APIResponse:
    """A JSON response body; HTTP status is carried by the HTTP response."""

    message: str
    data: Optional[Any] = None
    meta: Optional[Dict[str, Any]] = None
    details: Optional[List[Dict[str, str]]] = None

    def to_dict(self) -> dict:
        payload = {"message": self.message}
        if self.details is not None:
            payload["details"] = self.details
        else:
            payload["meta"] = self.meta or {}
            if self.data is not None:
                payload["data"] = self.data
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)

    @staticmethod
    def success(
        message: str = "OK",
        data: Optional[Any] = None,
        meta: Optional[dict] = None,
    ) -> "APIResponse":
        return APIResponse(message=message, data=data, meta=meta or {})

    @staticmethod
    def error(
        message: str = "Error",
        details: Optional[List[Dict[str, str]]] = None,
    ) -> "APIResponse":
        return APIResponse(message=message, details=details or [])


class ResponseBuilder:
    """Builder for successful JSON responses."""

    def __init__(self):
        self._message = "OK"
        self._data: Optional[Any] = None
        self._meta: Dict[str, Any] = {}

    def with_message(self, message: str) -> "ResponseBuilder":
        self._message = message
        return self

    def with_data(self, data: Any) -> "ResponseBuilder":
        self._data = data
        return self

    def add_meta(self, key: str, value: Any) -> "ResponseBuilder":
        self._meta[key] = value
        return self

    def with_meta(self, meta: Dict[str, Any]) -> "ResponseBuilder":
        self._meta.update(meta)
        return self

    def with_pagination(self, page: int, per_page: int, total: int) -> "ResponseBuilder":
        self._meta["pagination"] = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page if total else 0,
        }
        return self

    def build(self) -> APIResponse:
        return APIResponse.success(
            message=self._message,
            data=self._data,
            meta=self._meta,
        )


def show_standard() -> None:
    """Print the shared response envelope and short usage examples."""
    print(
        '''SUCCESS
{
  "message": "Users retrieved successfully",
  "data": [],
  "meta": {"pagination": {"page": 1, "per_page": 20, "total": 0, "total_pages": 0}}
}

ERROR
{
  "message": "The requested user was not found",
  "details": [{"code": "USER_NOT_FOUND", "message": "No user exists with that ID"}]
}

Usage:
  APIResponse.success(message="OK", data=user)
  APIResponse.error(message="Not found", details=[{"code": "NOT_FOUND", "message": "Missing"}])
  ResponseBuilder().with_data(users).with_pagination(page=1, per_page=20, total=100).build()

HTTP status codes belong to the HTTP response, not to a JSON `status` field.'''
    )


if __name__ == "__main__":
    show_standard()
