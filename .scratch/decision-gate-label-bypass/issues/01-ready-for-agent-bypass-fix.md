# 1 — Fix: the decision gate can be silently bypassed via a pre-existing `ready-for-agent` label

**What to build:** `refactor-design`, at the end of step 5, now actively manages both
`ready-for-agent` and `needs-info` for every candidate it plans, in both directions — not just
withholding `ready-for-agent`. `refactor-scan` steps 2/3b (and the orchestrator's mirrored routing)
widen from checking a "plan comment" to a "plan (comment, or — tooling-tree node/`loop-config` — the
issue body)", and read both labels together as a three-way signal instead of `ready-for-agent` alone.
See [ADR-0053](/docs/adr/0053-decision-gate-actively-manages-both-triage-labels.md) for the full
decision, considered options, and consequences.

**Why:** An externally-labeled candidate (a human files an issue directly with `refactor:candidate`)
can plausibly arrive already carrying `ready-for-agent`, set by the filer believing the request was
fully specified. If `refactor-design` then finds a decision meeting the ADR bar, the old gate
(ADR-0050) wrote the flag and open question but never checked for — let alone cleared — that
pre-existing label. `refactor-scan`'s resume checks read the label's mere presence as "confirmed,
safe to implement" and route straight to `refactor-implement` without any human ever seeing the
flagged question — the exact scenario the gate exists to prevent, bypassed by a label set before the
gate ever ran.

**Blocked by:** none.

**Priority:** high — silently defeats a documented safety guarantee (ADR-0050).

**Status:** done — PR TBD.

Settled via `/grill-with-docs` (4 questions, one round each plus a follow-up from live discussion):

- [x] **Q1 — Scope: `ready-for-agent` management applies to every candidate design plans**, not only
  the three decision-gate-eligible types — including tooling-tree nodes and `loop-config`. Confirmed
  by a concrete scenario from the user: running the skills by hand (`refactor-scan` → `refactor-design`
  → re-running `refactor-scan` manually) had no way to tell a fully-designed tooling-tree-node issue
  apart from a freshly-proposed one, since its plan lives in the issue body, not a comment — the same
  bug in a different shape. Confirming this widened scope also required broadening `refactor-scan`'s
  "plan comment" check to "plan (comment or body)" — corrects an earlier claim in this same
  discussion that `refactor-scan` wouldn't need any change at all.
- [x] **Q2 — The flag comment explicitly says when a pre-existing `ready-for-agent` was found and
  removed** ("this issue already carried `ready-for-agent`; removed pending the question above") —
  a label disappearing silently would be exactly the kind of surprising action this suite avoids
  elsewhere (`forge-facing-writing.md`). No such note needed for the ordinary case's positive
  labelling — the label alone is self-explanatory per the shared mattpocock/skills convention.
- [x] **Q3 — A new, small ADR (0053, "Amends ADR-0050"), not an in-place edit to ADR-0050 itself** —
  matches this repo's own precedent (ADR-0014 extends ADR-0013 the same way) of keeping ADRs as
  point-in-time records and layering corrections on top, rather than rewriting history.
- [x] **Q4 — The interrupted-pass edge case** (design wrote the plan but crashed before its own final
  labeling step) is resolved without new branch logic in `refactor-scan`: setting `ready-for-agent`
  becomes the *last, unconditional* action of design's step 5, so `refactor-scan` only ever needs to
  ask "which of the two labels is set" — `ready-for-agent` set → implement; `needs-info` set (not
  `ready-for-agent`) → flagged, waiting on a human; **neither** set → design itself was interrupted,
  route back to `refactor-design`, whose own idempotent checks complete only what's missing.
- [x] **Follow-up (live discussion, not a formal grilling question) — reuse `needs-info` rather than
  invent a new label.** User's own suggestion: mattpocock/skills already has `needs-info` ("Waiting
  on reporter for more information"), which maps exactly onto the flagged state — a visible "waiting
  on you" signal that today's design (label withheld, nothing added) never gave. Turned out to also be
  load-bearing for Q4's fix: it's the one signal that tells "flagged, human's turn" apart from
  "design was interrupted, design's turn to finish" for the neither-label-set case.

**Parked, not part of this ticket:** none.

## Comments

> **2026-09-15:** Filed after a bug report written up in English (per this suite's own convention
> for forge-facing/handoff text) by a separate review pass, then discussed and grilled in German.
> The report's own "Not in scope of this handoff: picking the fix" section named three directions;
> the grilling settled on a refined version of its first ("actively manage the label") once the user
> pointed out `ready-for-agent`'s mattpocock/skills semantics (one shared, canonical truth value, not
> a private per-setter signal) — which resolved the reviewer's own initial objection that clearing a
> label the suite didn't set would be an inappropriate side effect.

> **2026-09-15 (implement):** [ADR-0053](/docs/adr/0053-decision-gate-actively-manages-both-triage-labels.md)
> added. Changed: `decision-gate.md` (active label management, reworded intro), `refactor-design/SKILL.md`
> (new "Set `ready-for-agent`, last" step 5 instruction applying to every candidate type, updated
> Decision-gate-first paragraph, updated Completion criterion), `refactor-scan/SKILL.md` (steps 2/3b's
> resume logic widened to the three-way label read and plan-comment-vs-body distinction, `## Output`
> and Completion criterion reworded to match), `continuous-refactoring/SKILL.md` step 1 (mirrors the
> same three-way routing), `CONTEXT.md`'s **Flagged candidate** entry. 315/315 tests green, validator
> clean (only pre-existing size/duplication advisories, `refactor-scan/SKILL.md`'s word count grew
> further with the expanded routing logic). Ready for review.
