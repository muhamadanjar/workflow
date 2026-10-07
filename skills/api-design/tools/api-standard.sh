#!/usr/bin/env bash
set -euo pipefail

show_template() {
  cat <<'JSON'
Success:
{
  "message": "Users retrieved successfully",
  "data": [],
  "meta": {"pagination": {"page": 1, "per_page": 20, "total": 0, "total_pages": 0}}
}

Error:
{
  "message": "The requested user was not found",
  "details": [{"code": "USER_NOT_FOUND", "message": "No user exists with that ID"}]
}

HTTP status codes are returned in the HTTP response, not in a JSON status field.
JSON
}

show_success() {
  cat <<'JSON'
{
  "message": "User retrieved successfully",
  "data": {"id": 1, "name": "Ada"},
  "meta": {}
}
JSON
}

show_pagination() {
  cat <<'JSON'
{
  "message": "Users retrieved successfully",
  "data": [],
  "meta": {"pagination": {"page": 1, "per_page": 20, "total": 0, "total_pages": 0}}
}
JSON
}

show_error() {
  cat <<'JSON'
{
  "message": "The requested user was not found",
  "details": [{"code": "USER_NOT_FOUND", "message": "No user exists with that ID"}]
}
JSON
}

case "${1:-help}" in
  template|docs) show_template ;;
  success|simple) show_success ;;
  pagination) show_pagination ;;
  error) show_error ;;
  help|-h|--help)
    cat <<'HELP'
Usage: ./tools/api-standard.sh [command]

Commands:
  template    Show success and error response envelopes
  success     Show a successful response example
  pagination  Show a paginated response example
  error       Show an error response example
  docs        Same as template
  help        Show this help

JSON response bodies do not contain a status field. Set HTTP status codes in the framework response.
HELP
    ;;
  *) echo "Unknown command: $1" >&2; exit 2 ;;
esac
