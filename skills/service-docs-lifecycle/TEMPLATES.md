# Lifecycle Document Templates

Use English for these shared templates. Keep each section concise and service-specific. Add sections only when they improve the reader's understanding. Feature documents must include a Created and Last updated timestamp in the metadata table, formatted as ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`).

## Plan — `docs/plans/<feature-slug>.md`

```markdown
# <Feature or Architecture Title>

## Goal
<Problem and intended outcome.>

## Scope and Decisions
- In scope: <...>
- Out of scope: <...>
- Decisions/contracts: <...>

## Implementation
1. <Dependency-ordered step.>
2. <...>

## Acceptance Criteria
- [ ] <Observable behavior or invariant.>

## Verification
- <Relevant checks or manual scenarios to run.>

## Risks
- <Material risk and mitigation, or “None identified”.>
```

When execution begins, add this near the top below the title:

```markdown
Related Progress: [<Feature> progress](../progress/<feature-slug>.md)
```

## Progress — `docs/progress/<feature-slug>.md`

The first line must be a prominent plan link:

```markdown
Related Plan: [<Feature> plan](../plans/<feature-slug>.md)

# Progress: <Feature>

**Status:** Planned | In progress | Blocked | Complete

## Completed
- <Meaningful milestone or decision, with date when useful.>

## Remaining
- <Unfinished acceptance criterion or task.>

## Blockers and Scope Changes
- <Material blocker/change and its impact, or “None”.>

## Verification
- <Checks/scenarios actually run and their observed result; state pending checks plainly.>
```

Use checkpoint entries rather than a per-session transcript. Remove stale “Remaining” and blocker items when resolved; retain important decision history briefly.

## Feature — `docs/features/<feature-slug>.md`

```markdown
# <Durable Capability Title>

| Field | Timestamp (UTC) |
|---|---|
| Created | `<YYYY-MM-DDTHH:MM:SSZ>` |
| Last updated | `<YYYY-MM-DDTHH:MM:SSZ>` |

Related Plan: [<Feature> plan](../plans/<feature-slug>.md)  
Related Progress: [<Feature> progress](../progress/<feature-slug>.md)

## Purpose
<Who uses this capability and what it enables.>

## How It Works
<Core behavior, workflow, and important constraints.>

## Usage and Operations
<How to use, configure, support, or operate it.>

## Contract and Access
<Relevant routes/API contracts, permissions, integration boundaries, or state transitions.>

## Verification
<How a consumer/operator can verify expected behavior.>
```

Omit irrelevant sections and add domain-specific sections as needed. Keep this document focused on enduring behavior and use, not implementation chronology.
