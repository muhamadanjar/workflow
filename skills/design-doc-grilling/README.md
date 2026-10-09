# Design Doc Grilling

Interview-driven design docs. The `grilling` skill runs the interview (design tree worked in rounds) to extract the technical context, then the result is written into the project's existing design-docs template.

## Guides

- [SKILL.md](SKILL.md) — the four phases: recon, grill, confirm, write. Phase 1 delegates to the installed `grilling` skill read-only; `grill-me` is only the user-invoked front door that runs it. Includes when a design doc is required and the fill rules for each template section.
- [TEMPLATE.md](TEMPLATE.md) — fallback design-doc template. The target project's own `docs/design-docs/TEMPLATE.md` wins when present.

## Why both halves

A PRD says what the business wants. It does not say what breaks, what was rejected, or where the migration is irreversible. Those only come out under questioning — the installed `grilling` skill supplies that protocol (design tree, facts looked up from the repo instead of asked, decisions left to the user). This skill only adds the design-doc deltas on top: code recon first, the risk axes and rejected alternative that the template demands, and the decision log that becomes the doc. The template then makes the answers reviewable.

```
design-doc-grilling
├── Phase 0  recon (repo, PRD, code)
├── Phase 1  /grilling  ← the interview itself
├── Phase 2  confirm shared understanding
├── Phase 3  write into TEMPLATE.md
└── Phase 4  register in design-docs README, status Draft
```

## Quick start

```
Use the design-doc-grilling skill for <feature>.
Recon the repo, run the installed grilling skill, then write the result
to docs/design-docs/ using the project template.
```

## Grill chain (mattpocock skills)

| Skill | Who invokes | Role |
|---|---|---|
| `grill-me` | user only (`disable-model-invocation: true`) | front door; whole content is "Run a `/grilling` session." |
| `grilling` | model | the interview primitive — this is what actually runs, as installed |
| `grill-with-docs` | user only | same interview wired to `CONTEXT.md`/ADRs — not used here |
| `design-doc-grilling` | model | adds design-doc recon + template output around `grilling` |

Integration rule: the grill skills are read-only. This skill reads and runs the installed `grilling`; it never edits, syncs, or replaces `grilling`, `grill-me`, or `grill-with-docs`. Upstream (`github.com/mattpocock/skills`) may move ahead of the installed copies; leave the installed copies untouched regardless.

Status flow: `Draft → In Review → Approved → Implemented`, with `Rejected` and `Deprecated` terminal. The skill stops at `Draft` — human review moves it forward.
