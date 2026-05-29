#!/bin/bash
# API Standard Personal Skill
# Quick reference for standardized API responses

set -e

SKILL_PATH="/home/anjar/.claude/api_standard.py"
DOC_PATH="/home/anjar/Development/base-project-apps/API_RESPONSE_STANDARD.md"
SETUP_PATH="/home/anjar/Development/base-project-apps/API_RESPONSE_SETUP.md"

case "${1:-help}" in
  help|--help|-h)
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║          API STANDARD PERSONAL SKILL COMMAND                   ║
╚════════════════════════════════════════════════════════════════╝

Usage: api-standard [command]

COMMANDS
────────
  help         Show this message
  template     Show quick template
  simple       Show simple example
  pagination   Show pagination example
  builder      Show ResponseBuilder example
  error        Show error example
  python       Show Python code usage
  docs         Show full documentation
  setup        Show implementation guide

EXAMPLES
────────
  $ api-standard template
  $ api-standard pagination
  $ api-standard builder
  $ api-standard docs

QUICK REFERENCE
────────────────
Format: { status, data, metas, message }

Python:
  APIResponse.success(message="OK", data=result)
  ResponseBuilder().with_message("...").with_data(items).build()

Modules:
  Global: /home/anjar/.claude/api_standard.py
  Project: services/*/app/core/response.py
EOF
    ;;

  template)
    python3 << 'PYTHON'
import sys
sys.path.insert(0, '/home/anjar/.claude')
from api_standard import show_standard
show_standard()
PYTHON
    ;;

  simple)
    cat << 'EOF'
SIMPLE SUCCESS
──────────────
from app.core.response import APIResponse

return APIResponse.success(
    message="User retrieved",
    data={"id": 1, "name": "John"}
)

Response:
{
  "status": "success",
  "message": "User retrieved",
  "data": {"id": 1, "name": "John"},
  "metas": {}
}
EOF
    ;;

  pagination)
    cat << 'EOF'
PAGINATION EXAMPLE
───────────────────
from app.core.response import ResponseBuilder

return ResponseBuilder()\
    .with_message("Users retrieved")\
    .with_data(users)\
    .with_pagination(page=1, page_size=10, total=100)\
    .build()

Response:
{
  "status": "success",
  "message": "Users retrieved",
  "data": [{...}, {...}],
  "metas": {
    "page": 1,
    "page_size": 10,
    "total": 100,
    "total_pages": 10,
    "time_elapsed": "12.34ms"
  }
}
EOF
    ;;

  builder)
    cat << 'EOF'
RESPONSEBUILDER PATTERN
────────────────────────
from app.core.response import ResponseBuilder

# Simple
ResponseBuilder()\
    .with_message("Done")\
    .with_data(result)\
    .build()

# With pagination
ResponseBuilder()\
    .with_message("Items")\
    .with_data(items)\
    .with_pagination(page=1, page_size=10, total=100)\
    .build()

# With custom metas
ResponseBuilder()\
    .with_message("Job created")\
    .with_data(job)\
    .add_meta("queue", "etl_jobs")\
    .add_meta("priority", "high")\
    .build()

# Error with details
ResponseBuilder()\
    .with_status("error")\
    .with_message("Validation failed")\
    .add_meta("errors", {"email": "Invalid format"})\
    .build()

Methods:
  .with_status(status)           - "success" | "error"
  .with_message(msg)             - Response message
  .with_data(data)               - Response data
  .add_meta(key, value)          - Add single meta
  .with_metas(dict)              - Add multiple metas
  .with_pagination(...)          - Auto-add pagination
  .build()                        - Build (auto time_elapsed)
EOF
    ;;

  error)
    cat << 'EOF'
ERROR EXAMPLES
───────────────
# Simple error
APIResponse.error(message="User not found")

Response:
{
  "status": "error",
  "message": "User not found",
  "data": null,
  "metas": {}
}

# Error with details
ResponseBuilder()\
    .with_status("error")\
    .with_message("Validation failed")\
    .add_meta("invalid_fields", ["email", "phone"])\
    .add_meta("errors", {
        "email": "Invalid format",
        "phone": "Must be 10+ digits"
    })\
    .build()

Response:
{
  "status": "error",
  "message": "Validation failed",
  "data": null,
  "metas": {
    "invalid_fields": ["email", "phone"],
    "errors": {...}
  }
}
EOF
    ;;

  python)
    cat << 'EOF'
PYTHON MODULE USAGE
────────────────────
Location: /home/anjar/.claude/api_standard.py

Import:
  from api_standard import APIResponse, ResponseBuilder, show_standard

Display template:
  show_standard()

Create response:
  resp = APIResponse.success(message="OK", data={"id": 1})
  resp.to_dict()      # Get dict
  resp.to_json()      # Get JSON string

Build complex response:
  resp = ResponseBuilder()\
      .with_message("Items")\
      .with_data(items)\
      .with_pagination(page=1, page_size=10, total=100)\
      .build()

Auto-features:
  - time_elapsed (auto-added in milliseconds)
  - total_pages (auto-calculated from total/page_size)
EOF
    ;;

  docs)
    if [ -f "$DOC_PATH" ]; then
      head -100 "$DOC_PATH"
      echo ""
      echo "Full docs: $DOC_PATH"
    else
      echo "Documentation not found: $DOC_PATH"
    fi
    ;;

  setup)
    if [ -f "$SETUP_PATH" ]; then
      head -100 "$SETUP_PATH"
      echo ""
      echo "Full guide: $SETUP_PATH"
    else
      echo "Setup guide not found: $SETUP_PATH"
    fi
    ;;

  *)
    echo "Unknown command: $1"
    echo "Run 'api-standard help' for usage"
    exit 1
    ;;
esac
