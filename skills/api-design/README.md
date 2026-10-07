# API Design Patterns

This folder is the single home for API design standards, supplementary auth and integration references, and the legacy response helper.

## Guides

- [SKILL.md](SKILL.md) — canonical REST/JSON endpoint contracts, schemas, errors, search, pagination, authorization, OpenAPI, and compatibility.
- [REST_GUIDE.md](REST_GUIDE.md) — quick checklist for applying the canonical contract.
- [AUTH_PATTERNS.md](AUTH_PATTERNS.md) — authentication and authorization examples.
- [THIRD_PARTY.md](THIRD_PARTY.md) — outbound API and webhook integration examples.
- [API_STANDARD_README.md](API_STANDARD_README.md) and [API_STANDARD_USAGE.md](API_STANDARD_USAGE.md) — response helper documentation. Response bodies omit `status`; HTTP status codes are sent separately.
- `tools/` — helper source files.

Use the supplementary examples as starting points and adapt them to the target project's approved security model and public contract.
