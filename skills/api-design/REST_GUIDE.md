# REST API Design

The canonical contract for REST/JSON APIs lives in [`SKILL.md`](SKILL.md). Use it for endpoint design, request and response schemas, errors, search, pagination, authorization, OpenAPI, compatibility, and contract reviews.

This guide intentionally does not restate those rules. If this guide or another API reference gives conflicting REST advice, follow `SKILL.md` and the target project's explicitly approved contract.

## Protocols and specialized guides

- OAuth/OIDC endpoints retain their protocol-defined wire formats, as described in the canonical standard.
- For authentication and authorization implementation examples, see [AUTH_PATTERNS.md](AUTH_PATTERNS.md). Validate them against current security guidance and the target service's identity model before use.
- For outbound integrations and webhook delivery, see [THIRD_PARTY.md](THIRD_PARTY.md). Those are integration patterns, not the public REST contract for this service.

## Quick design checklist

Before implementing an endpoint, specify its resource or action, method and path, authorization, inputs, success and error schemas, status codes, search and pagination behavior, and OpenAPI documentation. Check existing client usage and compatibility constraints. Do not introduce a new response envelope, pagination scheme, search alias, or versioning policy independently of the canonical standard and the owning project's decisions.
