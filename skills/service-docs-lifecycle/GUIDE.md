# Service Documentation Lifecycle Guide

## Purpose and Scope

Apply this lifecycle to new features and architectural work in a service. Do not require new lifecycle files for routine bug fixes, small UI refinements, or routine maintenance unless a local product, compliance, or operational rule explicitly requires them. Update the relevant existing durable feature documentation when a small change materially changes its documented behavior.

Service-specific domain facts, API details, decisions, acceptance conditions, and verification steps belong in the service documents. This skill standardizes lifecycle structure; it does not replace service architecture rules or add domain policy.

## Required Locations and Naming

For an applicable feature or architecture task, use:

- `docs/plans/<feature-slug>.md`
- `docs/progress/<feature-slug>.md`
- `docs/features/<feature-slug>.md` only when the work introduces a standalone, durable capability

Use a lowercase kebab-case slug, consistent across the lifecycle documents. Use existing repository naming conventions for already-established records; do not rename historical files solely to normalize them. Avoid date prefixes for new lifecycle documents unless the service explicitly uses date-prefixed plan names.

## Workflow

1. **Assess applicability.** Confirm this is feature or architectural work. If it is a small fix or routine change, do not create a new plan/progress pair solely to satisfy this skill.
2. **Create the plan and progress record before implementation.** Initialize both documents with the templates in `TEMPLATES.md`. Put a prominent `Related Plan` link at the very top of progress. The plan must state the scope and observable acceptance criteria.
3. **Link execution.** When work starts, add a `Related Progress` link to the plan. Keep the plan's decisions and acceptance criteria current if the scope changes.
4. **Record meaningful checkpoints.** Update progress when the plan is initialized, a significant decision or milestone occurs, a blocker or scope change affects delivery, and when work completes. Keep entries factual and concise; do not write a diary of every session or command.
5. **Complete the record.** Mark progress complete and record actual verification performed. Do not claim checks that were not run.
6. **Decide whether a feature document is warranted.** Create one only for a distinct, standalone capability with lasting user, operator, developer, or service-contract value. Examples include a new service integration, a major operator workflow, a permission-governed area, or a persistent configuration surface. Small fixes, visual refinements, internal refactors, pagination/search changes, loading states, routing adjustments, and migrations normally update an existing parent feature document instead of creating a new one.
7. **Link and timestamp the final feature document.** A feature document must link to both its plan and progress records and include a metadata table with Created and Last updated timestamps in ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`). Set Created when the file is first created; update Last updated when its content changes. The document explains how the capability works and how to use, configure, operate, or integrate with it; it is not a progress diary.

## Linking Rules

Use repository-relative Markdown links, not absolute filesystem paths. For `docs/progress/<slug>.md`, link to the plan as `../plans/<slug>.md`. For a plan, link to active progress as `../progress/<slug>.md`. For a feature document, link to plan and progress using `../plans/<slug>.md` and `../progress/<slug>.md`.

If a related historical document does not exist, do not create a reconstructed substitute. Only add links to files that exist and whose relationship is supported by repository evidence. Preserve supersession notes and historical context.

## Service Instructions and Skill Loading

A service instruction file should point contributors to the canonical skill and state that its lifecycle rules replace copied local lifecycle policy. Preserve unrelated service-specific instructions. If the runtime does not discover the skill by name, read the canonical path referenced by the service instructions. Do not claim a name-based invocation is available unless verified in that runtime.

## Review Checklist

Before finishing applicable work, confirm:

- Plan and progress existed before implementation began.
- Both use the same feature slug; progress begins with a valid plan link.
- Plan links to active progress once execution starts.
- Progress captures meaningful milestones, blockers/scope changes, and actual verification.
- A feature document was created only if the durable-capability threshold is met.
- Any feature document links to the plan and progress, has accurate Created/Last updated UTC timestamps, and describes lasting usage/contract information.
- Every link target exists; no historical content was fabricated.
