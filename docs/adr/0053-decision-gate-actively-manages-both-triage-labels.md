# The decision gate actively manages `ready-for-agent` and `needs-info`, not just withholds one

> Amends [ADR-0050](0050-pre-implementation-decision-gate.md): the same gate, the same two labels,
> now actively set/cleared instead of one being passively withheld.

ADR-0050's gate only ever withheld `ready-for-agent` — it never checked for, or cleared, a
**pre-existing** one. An externally-labeled candidate (`refactor-scan` step 3b — an issue a human
files directly with `refactor:candidate`) can plausibly arrive already carrying `ready-for-agent`,
set by the filer believing the request was fully specified. `refactor-design` grounds/grills it,
finds a decision meeting the ADR bar, writes the flag and the open question — and leaves that
pre-existing label untouched. `refactor-scan` steps 2 and 3b then read the label's mere presence as
"confirmed, safe to implement" and route straight to `refactor-implement`, without any human ever
having seen the flagged question. The exact scenario the gate exists to prevent, bypassed by a label
set before the gate ever ran.

A second, related gap surfaced while designing the fix: `refactor-scan` steps 2/3b only ever checked
for a **plan comment** — the shape a structural/externally-labeled/baseline-shrink candidate's plan
takes. A tooling-tree node's plan lives in the issue **body** instead
(`refactor-design/SKILL.md` step 5), so a fully-designed tooling-tree-node issue, rediscovered by a
manually-run `refactor-scan` pass outside the orchestrator's own same-pass hand-off, had no reliable
way to be recognized as "already designed" at all.

## Considered Options

- **Only clear `ready-for-agent` defensively when flagging, otherwise leave the label untouched.**
  Rejected on the mattpocock/skills reading: `ready-for-agent` isn't a private signal scoped to
  whoever set it — the whole shared-label convention (docs/agents/triage-labels.md) treats it as one
  canonical, ecosystem-wide truth value ("fully specified, ready for an AFK agent"). `refactor-design`
  is exactly the process best positioned to assert that value once it has actually assessed the
  candidate — in both directions, not just downward.
- **A new, suite-specific label instead of reusing `ready-for-agent`.** Rejected — ADR-0050 already
  chose to reuse the shared label deliberately; the gap this ADR fixes is a reason to manage that
  shared label correctly, not a reason to abandon sharing it. `needs-info` — an existing mattpocock
  label, not a new one — already covers the "visible, waiting-on-human" half the gap was missing.
- **Route "plan present, label absent" straight back to `refactor-implement`/treat it as always safe
  to resume.** Rejected — collapses two genuinely different states (a human hasn't answered a flagged
  question yet, vs. `refactor-design` itself was interrupted before its own final labeling step) into
  one. `needs-info`'s presence is exactly what tells them apart without guessing.

## Decision

`refactor-design`, at the end of its own step 5 (`refactor-design/SKILL.md`), now actively manages
both labels for every candidate it plans, not only the three decision-gate-eligible types:

- **Flagged** (a decision meets the ADR bar) → add `needs-info`; remove `ready-for-agent` if the
  issue already carries one, stating so plainly in the flag comment. A human resolves this by
  commenting, removing `needs-info`, and adding `ready-for-agent`.
- **Ordinary** (decision gate found nothing, or never applies — a tooling-tree node/`loop-config`) →
  set `ready-for-agent`, unconditionally, as the last step — whether the plan was freshly written,
  updated, or already complete from an earlier interrupted pass. Design's own explicit confirmation,
  not its silence.
- **Breaking change** → unchanged from ADR-0050: no plan, no label touched by `refactor-design` at
  all; `refactor-learn` applies its existing rejection machinery instead.

`refactor-scan` steps 2 and 3b widen from checking for a "plan comment" to a "plan (comment, or —
tooling-tree node/`loop-config` — the issue body)", and their resume logic becomes a three-way read
of the two labels together, not `ready-for-agent` alone:

- `ready-for-agent` set → resume straight to `refactor-implement`. Presence alone is enough now —
  `refactor-design` already guarantees it's accurate, no separate flagged/unflagged tracking needed.
- `ready-for-agent` absent, `needs-info` present → flagged, still waiting on a human — not resumable
  this pass, same treatment as before.
- **Neither label set** (new case) → `refactor-design` itself was interrupted before its own final
  labeling step — not a human waiting. Resume straight to `refactor-design`; its own idempotent
  checks mean it completes only what's missing, never redoes the plan itself.

## Consequences

- `refactor-design/references/decision-gate.md`'s ADR-bar branch actively manages both labels instead
  of only withholding one; its intro paragraph is reworded from "nothing else changes" to name the
  labels as what does.
- `refactor-design/SKILL.md` step 5 gains the new, universal "set `ready-for-agent`, last"
  instruction, applying to every candidate type it plans — including tooling-tree nodes and
  `loop-config`, which never run the decision gate at all. Its own Completion criterion is updated to
  match.
- `refactor-scan/SKILL.md` steps 2 and 3b (both the resume logic and the `## Output` summary) are
  reworded for the plan-comment-vs-body distinction and the new three-way label read.
  `continuous-refactoring/SKILL.md` step 1 mirrors the same three-way routing, since it summarizes
  `refactor-scan` step 2's own resume logic.
- `CONTEXT.md`'s **Flagged candidate** entry is updated to describe both labels.
- No change to `refactor-implement`, and no change to the gate's actual enforcement point (the
  orchestrator still skips implementation for a still-flagged candidate) — only how reliably the two
  labels reflect reality, and how a resumed pass reads that, changes.
