---
id: service-docs-lifecycle
name: Service Documentation Lifecycle
version: 1.0.0
description: Create consistent plans, progress records, and durable feature documentation across services.
category: documentation
tags: [documentation, planning, progress, features, workflow]
platforms: [claude, codex, opencode, pi]
---

# Service Documentation Lifecycle

Create and maintain linked plan, progress, and durable feature documents for service work.

## Overview

Use this skill for new features and architectural work across services. It defines when lifecycle documents are required, their shared structure, naming/link rules, progress checkpoints, and completion criteria. Routine bug fixes and small changes do not require a new plan/progress pair unless the service explicitly has a stricter domain requirement.

## Guides

- [GUIDE.md](GUIDE.md) — lifecycle decisions, workflow, and maintenance rules.
- [TEMPLATES.md](TEMPLATES.md) — required concise templates for plans, progress records, and feature documentation.

## Quick Start

1. Load `GUIDE.md` and `TEMPLATES.md` before creating or changing lifecycle documents.
2. For feature or architecture work, create matching plan and progress files before implementation.
3. Maintain links and update progress at meaningful checkpoints.
4. At completion, create a feature document only for a standalone, durable capability.

## Features

- Shared, concise templates with service-specific extensions allowed.
- Matching kebab-case filenames and reciprocal lifecycle links.
- Progress tracking at meaningful decisions and milestones rather than per-session diaries.
- A durable-capability threshold for final feature documentation.
- Evidence-based maintenance of historical records without invented history.

## Usage with Platforms

### Claude

Use `@service-docs-lifecycle` when preparing a feature or architecture change. In services that explicitly reference the canonical file, follow that local instruction and read the skill guides.

### Pi

`@service-docs-lifecycle`

Apply the lifecycle to the requested feature or architecture work.

### Codex / OpenCode

Reference `@service-docs-lifecycle` or read the canonical `skill.md` and linked guides. Service instruction files may point directly to the canonical path when runtime name discovery is unavailable.

## Integration Points

Works with architecture/design skills when clarifying scope and contracts, and with testing/QA skills when defining acceptance and verification.

## Resources

- [Lifecycle guide](GUIDE.md)
- [Required templates](TEMPLATES.md)
