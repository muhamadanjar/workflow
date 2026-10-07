---
id: api-design
name: API Design
version: 1.0.0
description: REST/JSON API contract design, auth and integration references, plus a legacy response helper
category: backend
tags: [api, rest, grpc, graphql, integration]
platforms: [claude, codex, opencode, pi]
---

# API Design Patterns

Use [`SKILL.md`](SKILL.md) as the source of truth for REST/JSON API contracts. This skill also contains supplementary authentication and third-party integration examples and a legacy response helper.

## Overview

Supplementary backend patterns. Adapt the examples to the target project's approved security and integration contracts.

## Guides

- README.md
- REST_GUIDE.md
- AUTH_PATTERNS.md
- THIRD_PARTY.md

## Quick Start

1. Use this skill for REST/JSON endpoint contracts.
2. Reference its guides for authentication or third-party integration examples.
3. Use a specific guide: `@api-design/GUIDE_NAME.md`
4. Combine with other skills for comprehensive coverage

## Features

- Authentication and integration examples
- Cross-reference to the canonical REST standard

## Usage with Platforms

### Claude
```
I need backend help.
Use @api-design patterns for:
- Point 1
- Point 2
```

### Pi
```
@api-design

Show me backend patterns
```

### Codex / OpenCode
Reference in conversation or code prompts.

## Integration Points

Works well with:
- Other backend/frontend skills
- DevOps skills for deployment
- Testing strategies

## Resources

- Full guides in skill directory
- Examples in README.md
- Implementation patterns in specific guides

---
Auto-generated from manifest.json
Platform-compatible format for Claude, Pi, Codex, OpenCode
