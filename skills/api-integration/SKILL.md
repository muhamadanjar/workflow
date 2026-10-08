---
name: api-integration
description: Implement or change a project that consumes an existing HTTP API. Ground the client in that API's OpenAPI specification or official API documentation, across languages and frameworks.
---

# API Integration

Use this skill when a project consumes an existing API. It is consumer-focused: use the API design skill when creating or changing the API provider's public contract.

## Required contract discovery

Read the API contract before writing or changing API-specific integration code. Do not rely on remembered endpoints, names, sample payloads, or assumptions from another project.

1. Read the target repository's `AGENTS.md`, relevant plans, configuration, existing API clients, and nearby call sites. Identify the API and environment from the task and the project's configured base URL or service name. Do not reveal secret values while inspecting configuration.
2. Locate the matching `openapi.json` or other OpenAPI document in the repository or the API documentation URL configured by the project. If the documentation URL is a UI, follow its links or configuration to the published OpenAPI JSON when available. Prefer documentation for the service and environment actually being integrated.
3. Read the specification's global context before selecting operations: OpenAPI version, `servers`, global and operation-level security, reusable parameters, schemas, and response components. Then inspect each relevant operation and follow all referenced schemas. A text search hit alone is not contract review.
4. If multiple specifications or documentation URLs are plausible, compare their service names, base URLs, versions, environment, and existing client usage. If the intended source remains ambiguous, ask the user which API to integrate before coding against it.
5. If no OpenAPI document or API documentation URL is available, ask the user for the folder or other resource that can be analyzed. Do not guess the API contract. Analyze the supplied source, schemas, generated clients, or other artifacts as evidence; clearly identify inferred behavior and ask about unresolved contract decisions before depending on them.

If a task has work independent of the API contract, that work may continue while the contract source is being clarified. Do not implement the dependent API behavior from guesses.

## Resolve conflicting sources

- Compare a local specification with the API service's documentation when both exist. Report meaningful differences instead of silently merging them. Prefer the current service documentation that matches the target environment; if its authority or environment is unclear, ask the user which contract to follow.
- If observed API behavior conflicts with OpenAPI or official documentation, show the affected operation and the difference, then ask which source is authoritative before baking the discrepancy into the client.
- Do not make live requests that mutate data just to discover the contract. Use documented, safe read operations only when the task and available credentials permit them.

## Build an operation map

Before implementation, map the required feature to the documented operations. Record the relevant:

- HTTP method, path, `operationId`, server/base URL, and API version;
- path, query, and header parameters, including requiredness, types, enums, and constraints;
- request media type and body schema, including referenced types and nullable fields;
- success response codes, media types, schemas, and no-content behavior;
- documented error responses and machine-readable error fields;
- authentication/security scheme and any operation-level overrides;
- pagination, filtering, sorting, rate-limit, retry, and idempotency details used by the feature.

Use this map to choose the narrowest client operation that fulfills the task. Do not invent endpoint paths, parameter names, response fields, or authentication headers.

## Implement in the target project

- Follow the repository's existing HTTP client, dependency, configuration, serialization, error-mapping, and testing conventions. Reuse its client and dependencies; introduce a new abstraction or dependency only when the project needs one.
- Keep the external wire contract at the API boundary. Parse and send the shapes documented by the provider. Do not impose this repository's own response envelope on another API, remove provider-defined fields, or invent a JSON `status` field; preserve a `status` property if the provider's schema explicitly defines it.
- Use the documented authentication flow and the project's existing secret/configuration mechanism. Never hardcode credentials or expose tokens, secrets, or sensitive request/response bodies in logs.
- Set request timeouts using project conventions. Retry only when the operation is safe/idempotent or the API contract supports an idempotency mechanism and retry. Respect documented retry-after and rate-limit behavior; do not blindly retry mutations.
- Follow the API's documented pagination and filtering. Fetch additional pages when the feature requires the full result set; do not assume the first page is complete.
- Map API errors into the project's established error model without discarding useful machine-readable information. Preserve HTTP semantics and distinguish transport failures, authentication/authorization failures, validation errors, not-found responses, rate limits, and server errors where the contract supports that distinction.

## Verify and report

Use the project's available checks to compare the implementation with the selected contract: operation path and method, parameters, request/response models, authentication, pagination, and error mapping. Keep evidence distinct:

- Static inspection or type checks show that code matches the reviewed specification or local types.
- Tests with fixtures show behavior for the cases they cover.
- A live API check shows behavior only for the environment, credentials, operations, and cases actually exercised.

Do not claim live compatibility based only on reading OpenAPI or passing local tests. If the API cannot be reached or safely exercised, state that boundary and identify the remaining live validation.
