---
name: design-doc-grilling
description: Grill the user with the /grilling skill to extract the real context, then write the design doc into the project's design-docs template. Use when the user wants a design doc, RFC, or technical proposal for a feature, says "grill me", "grill me about this feature", or describes a change that needs agreement before implementation.
---

# Design Doc Grilling

Two halves, one output. Phase 1 runs the `/grilling` skill to extract the context (decisions, constraints, trade-offs). The design-doc template is the only place the result is written. Never skip the interview because a PRD already exists — a PRD states intent, not technical decisions.

## When a design doc is needed

Required for: architecture changes, a new service/component, significant schema change, breaking or new public API, changes touching more than one service, decisions with real trade-offs, or risky data/ops changes.

Not needed for: small bug fixes, copy/UI tweaks, local refactors that change no contract or behavior. Say so and stop instead of producing a document.

## Phase 0 — Recon (facts, no questions yet)

Facts are found, not asked. Before the first question, read what exists:

1. The project's `AGENTS.md`/`CLAUDE.md`, the design-docs `README.md` and `TEMPLATE.md`, existing design docs in the same area.
2. The PRD/ticket, if any. Extract goals, user stories, acceptance criteria, constraints.
3. The code that the change touches: routes, models/schema, callers across services, config, migrations. Use the code graph tool if configured, otherwise focused search.
4. The glossary/`CONTEXT.md` if present.

Only then build the decision tree. Every open point that the recon already answers is deleted from the tree.

## Phase 1 — Grill

**Run the `grilling` skill for this phase — never reimplement it.**

The chain is: `grill-me` is a user-invoked front door (`disable-model-invocation: true`); its entire content is *"Run a `/grilling` session."* The agent therefore never invokes `grill-me` — it runs the `grilling` primitive directly, the moment it is asked to grill.

**The installed grill skills are read-only.** Read the `grilling` skill the harness loads and follow it exactly as it stands. Never edit, rewrite, reimplement, copy over, or "update" `grilling`, `grill-me`, or `grill-with-docs` — not even to bring them in line with a newer upstream version, and not with user approval implied by this skill. This skill is the integration layer; those files stay untouched.

Layer these design-doc constraints on top of the grilling session:

- Drive the interview along the decision tree built in Phase 0, branch by branch, resolving dependencies first. A question that only exists if an earlier choice was made comes after that choice.
- **Always surface at least one real alternative.** If the user presents only one approach, ask what was rejected and why.
- **Cover the risk axes for every proposal**: backward compatibility, data migration and reversibility, performance, security, operational/rollback. Ask about the axes that apply; record why the others do not.
- **Log each resolved decision as one line as you go.** The log is the input to Phase 3: unresolved nodes become "Pertanyaan Terbuka", the risk answers become "Dampak & Risiko", the rejected approach becomes "Alternatif yang Dipertimbangkan".
- Stop when new questions only produce detail, not decisions.

If the `grilling` skill is unavailable in the harness, say so before continuing and run the same protocol yourself.

## Phase 2 — Confirm shared understanding

The session is done when the loaded grilling skill says it is. This is also the grilling skill's own gate, made explicit. Play back the decision log in a short numbered list, ask for explicit confirmation that you share understanding, then ask permission to write the doc. Do not write the doc before the user confirms. No implementation either — the design doc is the deliverable and it needs human review.

## Phase 3 — Write the doc

Use the project's `TEMPLATE.md` from its design-docs directory (fallback: `TEMPLATE.md` next to this skill). Fill it section by section, in the project's documentation language:

- Path: `<design-docs-dir>/YYYY-MM-DD-judul-singkat.md`, slug lowercase with hyphens.
- `Status` = `Draft`. Author = the real user, reviewer/ticket only if known. Never invent names, emails, or ticket IDs.
- Follow the template structure exactly. Do not add, remove, or reorder sections. Irrelevant sections are written `N/A` with a one-line reason, never deleted.
- "Ringkasan" is 1-3 sentences, understandable alone.
- "Alternatif yang Dipertimbangkan": at least two options with a real trade-off table, including the one chosen.
- "Dampak & Risiko": evaluate each of the five axes explicitly, or state why that axis is not affected.
- "Pertanyaan Terbuka": mandatory. Every unresolved decision and every assumption you made.
- Anything the user did not state and you could not verify → `[perlu konfirmasi: ...]`. Never fabricate. Never fill a section with a plausible-sounding guess.
- Technical, compact prose. No marketing language.

## Phase 4 — Register and hand off

1. Add the new doc to the index table in the design-docs `README.md` with its status and date.
2. Tell the user the status flow: `Draft → In Review → Approved → Implemented`, with `Rejected`/`Deprecated` as terminal states. Status only moves to `In Review` after a human review.
3. Report what remains `[perlu konfirmasi: ...]` and which open questions need a specific reviewer.

## Anti-patterns

- Writing the doc first and asking questions after.
- Restating the grilling rules inside this skill instead of running `grilling`.
- Editing, syncing, or overwriting any installed grill skill file.
- Skipping `/grilling` because a PRD or ticket already exists.
- Asking the user for facts that are in the repo.
- Invoking `/grill-me` yourself — it is user-invoked only; the model runs `grilling`.
- Writing your own interview instead of running the `grilling` skill.
- Dripping one question at a time when the loaded grilling skill specifies rounds.
- A single-option "Alternatif" table.
- Deleting a template section instead of marking it `N/A`.
- Inventing ticket numbers, reviewers, or requirements to make the doc look complete.
- Drifting into implementation once the doc is written.
