# A flagged candidate self-confirms from a plain human comment, instead of waiting on a manual label swap

> Extends [ADR-0053](0053-decision-gate-actively-manages-both-triage-labels.md)'s "actively manage both
> labels" discipline to the return trip: confirming a flagged candidate now gets the same active
> handling filing one already gets, instead of leaving the label swap entirely to the human.

Observed live in `Art4/legacy-todo` (issue #269): `refactor-design` flagged the candidate, wrote a
default plus an open question, and added `needs-info`. The human answered directly on the issue
("Accepted as described.") — but never removed `needs-info` or added `ready-for-agent`, because
`decision-gate.md`'s own instructions ask for exactly that as one single manual act. `refactor-scan`,
per its own documented behavior, treated the still-`needs-info` issue as not resumable and skipped it
silently, every pass, indefinitely. Nothing re-reads a flagged issue's comments once the labels are set;
a human's plain "yes, go ahead" is otherwise invisible to the loop forever, no matter how many passes run
afterward.

This is the same gap ADR-0053 already closed in the other direction: before that ADR, a candidate could
sit with a stale `ready-for-agent` after a question was raised, because nothing actively cleared it.
Here, a candidate can sit with a stale `needs-info` after the question is answered, because nothing
actively clears *that*. Both are the same underlying failure — a label is left for a human to notice and
fix by hand, with no mechanism checking whether that noticing ever happened.

## Decision

**`refactor-scan` detects a candidate comment worth reacting to** (step 2's resume check and step 3b's
externally-labeled scan, wherever a `needs-info`-flagged issue is currently read and skipped): the
issue's most recent comment is newer than `refactor-design`'s own flagging comment, and its author is a
human, not the suite's own bot account. Previously this case was invisible — the field/label state alone
decided everything. Now it changes what happens next: instead of skipping silently, hand the candidate
forward to `refactor-design` for one more look, the same way an unresolved `ready-for-agent`-absent
plan already gets routed there to finish labeling.

**`refactor-design` reads the comment and judges it — same disposition it already reaches during
grilling** (`decision-gate.md`'s own "confirm it as written, or override it" framing was always a
judgment call; only the follow-through was manual):

- **Plainly confirms the stated default, raises no new question** → apply `decision-gate.md`'s existing
  label-management discipline in reverse: remove `needs-info`, add `ready-for-agent`, and post a short
  comment naming that this proceeds on the confirmation above (dated, so a later reader sees why the
  labels moved without a second explanatory paragraph). The candidate is `ready-for-agent` from here
  on — `refactor-loop` may implement it same pass or a later one, exactly like any other confirmed plan.
- **Anything else** — proposes a different choice than the default, asks a new question, or is
  otherwise not a plain yes — **stays flagged**. Post one nudge comment only if the suite hasn't already
  nudged for this exact comment (check: is the suite's own most recent comment already newer than the
  human's? → already nudged, say nothing this pass) — naming plainly that a plain confirmation needs the
  label swap to take effect, or that a different choice needs to be spelled out concretely enough to
  replan against. This never auto-applies an override — only a plain "yes" self-confirms; a stated
  alternative still needs a human to either restate it as confirmable or swap the labels themselves once
  satisfied. Scoped deliberately narrow: teaching the suite to re-plan against an arbitrary override is a
  separate, harder problem, not part of this decision.

**The gate itself is unchanged.** This only shortens the distance between "a human answered" and "the
labels reflect it" for the one case that was always meant to be quick — a plain yes. It never lets the
suite decide a genuine trade-off on the human's behalf; that decision, and the judgment that an answer
actually settles it, still requires the human's own words on the issue. What changes is who transcribes
that settled answer into the two labels.

## Considered Options

- **Nudge only, never swap the labels itself.** Rejected as the sole behavior (kept as the fallback for
  anything but a plain confirmation, above) — for the common case of a one-line "yes, proceed," it just
  relocates the manual step from "swap two labels" to "swap two labels after reading a reminder comment,"
  without shortening the actual wait. The failure this ADR fixes (a plain answer sitting unnoticed
  indefinitely) isn't a labeling-mechanics problem, it's a nobody-ever-looks-again problem — a reminder
  comment doesn't look again either, it just leaves a note for a human who has to come back on their own.
- **Always apply the suite's own read of the comment, override included.** Rejected — this would let the
  suite decide it understood a human's proposed change well enough to act on it unsupervised, exactly the
  live, human trade-off call `decision-gate.md` exists to keep out of the suite's hands. A plain
  confirmation of an already-written, already-reasoned default carries none of that risk; a stated
  alternative does.
- **A dedicated config field (e.g. `Decision-confirm-mode: autonomous | nudge-only`), defaulting to the
  safe nudge-only behavior.** Rejected for now — self-confirming a plain "yes" isn't the same kind of
  choice `MR-create-mode`/`Ticket-create-mode` gate (those decide whether the suite may act on the
  target repo *at all* without asking each time); here the human has already acted, on the record, on
  the issue itself. Revisit only if a live run shows the plain-confirmation judgment call itself
  misfiring often enough to need an escape hatch.

## Consequences

- `skills/refactor-design/references/decision-gate.md` gains a new section for this reverse case,
  alongside its existing "actively manage both labels" bullet.
- `skills/refactor-scan/SKILL.md` steps 2 and 3b's `needs-info`-present branches change from "skip
  silently" to "check for a newer human comment first."
- `CONTEXT.md`'s **Flagged candidate** entry is corrected: a flagged candidate no longer waits purely on
  a human's own label edit — it can self-confirm from a plain comment.
- `docs/playbooks/tracks.md`, `docs/playbooks/loop.md`, and `docs/known-limitations.md`'s `needs-info`
  references are corrected the same way, so none of them still describe answering a flagged question as
  requiring the human to also swap the labels by hand.
- No change to `decision-gate.md`'s forward direction (flagging a candidate) — only the return trip.
- A human who answers with an explicit alternative, or asks a further question, still needs to either
  restate their answer as a plain confirmation or swap the labels themselves once satisfied — unchanged
  from before this ADR.
