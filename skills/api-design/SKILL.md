---
name: api-design
description: Design and review REST/JSON API contracts, with supplementary authentication, integration, and response helper references.
---

# API Design Standards

Use this skill to design new REST/JSON APIs and to audit or refactor existing contracts when requested. Apply the same contract baseline across projects while adapting framework-specific implementation to the target repository. Treat API behavior as a public contract for clients.

## Inspect before designing

1. Read the repository's `AGENTS.md`, API standards, ADRs, OpenAPI document, and nearby route/schema implementations. Inspect client call sites when available.
2. Use configured code graph tools for route and call discovery; fall back to focused source and documentation search if graph results are unavailable or incomplete.
3. Identify authentication and authorization behavior, error mapping, existing wire formats, compatibility constraints, and protocol-specific endpoints.
4. Separate approved API decisions from incomplete migrations and legacy endpoint behavior. Do not treat every existing route as a correct example.

Before implementation, define the endpoint's resource/action, HTTP method and path, authorization, request parameters/body, success schema, status codes, error shape, pagination/search behavior, and OpenAPI documentation. Ask only for unresolved product or domain decisions that would materially change the public contract.

## Baseline for REST/JSON endpoints

### Paths and methods

- Use resource-oriented paths and standard HTTP methods for resource operations. Use a named subresource or action path only when the operation is not ordinary CRUD.
- Do not add API versioning to paths or query parameters. Preserve compatibility through additive contract changes. If an incompatible change appears necessary, explain client impact and agree on a migration before changing the public contract; do not invent a versioning scheme.
- Keep path parameters for resource identity and query parameters for list selection, search, ordering, and pagination. Validate parameters with the framework's typed schema facilities.

### Search, filtering, and ordering

- Use `search` as the standard free-text search/filter query parameter. Do not invent aliases such as `q`, `keyword`, or endpoint-specific names for the same behavior.
- Give structured filters explicit typed query parameters that match domain concepts. Document how they combine with `search`.
- If sorting is supported, expose consistent `sort_by` and `sort_order` parameters, allowlist sortable fields, validate direction, and define a stable default order.

### Pagination

- Every list endpoint must be paginated, including lists that are usually small.
- For ordinary result sets, use `page` (default `1`) and `per_page` (default `20`, maximum `100`). Validate `page >= 1` and `1 <= per_page <= 100`.
- For large or growing datasets, prefer cursor pagination. Use a documented opaque cursor and stable ordering; do not combine cursor and page pagination in one response.
- Keep pagination metadata in the established response metadata shape: `meta.pagination` contains `page`, `per_page`, `total`, and `total_pages`; `meta.cursor` contains `next`, `previous`, `has_next`, and `has_previous`. A response uses one mode at a time.

### Success and error responses

For ordinary JSON endpoints, use one consistent success envelope:

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

- `message` and `meta` are always present on success. `data` is optional when the operation has no result payload. Do not add a `success` boolean.
- Use `meta: {}` when there is no pagination, cursor, or other response metadata.
- Use the same structured error shape for application and HTTP errors:

```json
{
  "message": "The requested user was not found",
  "details": [
    {"code": "USER_NOT_FOUND", "message": "No user exists with that ID"}
  ]
}
```

- Error responses contain `message` and `details` entries with stable machine-readable `code` values and safe human-readable messages. They do not contain success `meta`.
- Preserve the semantic HTTP status. Common mappings include `201` for creation, `204` for successful no-content operations, `401` for missing or invalid authentication, `403` for denied authorization, `404` for missing resources, `409` for conflicts, `422` for request validation, and `500` for unexpected server failures. Do not expose stack traces, credentials, or internal exception details.

Do not force this generic envelope onto protocol-defined responses. OAuth/OIDC token, authorization, introspection, revocation, UserInfo, JWKS, and discovery endpoints must retain their protocol wire contracts. A `204 No Content` response has no response body.

### Authorization and OpenAPI

- Document whether each endpoint is public or protected, the required authentication scheme, and the needed permission or scope. Authentication alone does not imply authorization.
- Define explicit request and response schemas, including query constraints, nullable fields, status-specific response bodies, and error responses. Avoid undocumented raw dictionaries where a stable public shape is expected.
- Keep OpenAPI summaries, descriptions, tags, parameter constraints, security requirements, and examples aligned with actual runtime behavior. Configure interactive docs according to the target project's exposure policy.

## Compatibility and review

- Treat field names, nullability, status codes, pagination semantics, and error codes as client-facing contracts. Prefer additive changes; do not silently rename, remove, or change meanings.
- For an audit, report the route and the observable contract mismatch, distinguish a legacy exception from an intended standard, and propose a scoped compatible correction. Do not migrate unrelated endpoints unless asked.
- When verification is requested, compare generated OpenAPI with actual route behavior and check representative success, validation, authorization, not-found, conflict, and paginated responses. State what was checked and what remains unverified.

## Source-project guidance

The originating `usermanagement_api` repository established the success envelope, structured errors, and mutually exclusive pagination/cursor metadata. Its migration is incomplete and some routes still have inconsistent pagination inputs, status behavior, or schema coverage. Use the agreed contract above as the baseline; use legacy endpoints to find migration gaps, not to define new API behavior. FastAPI, Pydantic, and the repository's module paths are examples of implementation, not requirements for other HTTP API frameworks.
