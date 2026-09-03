# `AGENTS.md`/`CLAUDE.md` gets a Create-mode pointer, not the value itself

> Cross-references [ADR-0006](0006-loop-delivers-remembered-merge-requests.md): its "Write the
> create-mode into `AGENTS.md` / `CLAUDE.md`" option — rejected there ("those files are read as
> hints; suite state is not mixed into the human's agent config") — was reconsidered and the
> rejection upheld. [ADR-0024](0024-loop-config-interview-decides-tracker-create-mode-storage.md)'s
> reaffirmation of the same constraint stands unchanged too.

A human watching a live run (`docs/playbooks/reviewer-loop.md`) asked whether `Create-mode` should
move into `AGENTS.md`, reasoning that it's exactly the kind of rarely-changing setting a human
would look there for, and that mixing it with `bookkeeping.md`'s fast-churning fields (`Pending
candidates`, `Fulfilled nodes`, `Skip streak`) makes the file harder to scan. The underlying wish —
human visibility of the suite's own configuration from the one file a human already reads — is
real and worth solving; moving the value itself is not the way, per ADR-0006/0024's own reasoning:
a second write-authority for the same fact invites drift the moment either copy is edited without
the other.

## Decision

`bookkeeping.md` stays the sole write-authority for `Create-mode` — nothing about how
`refactor-implement`/`refactor-learn` read or write it changes. `AGENTS.md`/`CLAUDE.md`'s
`## Continuous-refactoring suite` section (already written once, during `loop-config`'s interview)
gains a **read-only pointer line** instead: `Create-mode: see the Refactoring Notes'
bookkeeping.md`. Human visibility without a second write-authority.

The tracker's candidate label name (`refactor:candidate`) is documented in the same section for
the same reason — it was never stored in `bookkeeping.md` to begin with (it lives in
`docs/agents/issue-tracker.md`, per ADR-0012), so this is pure documentation, not a new field.

## Considered Options

- **Move `Create-mode`'s value into `AGENTS.md` itself.** Rejected — exactly the option ADR-0006
  already considered and rejected, for the same reason: two places that can independently drift.
- **Do nothing — leave `AGENTS.md` without any pointer.** Rejected — the human's underlying
  request (visibility from the file they already read) is legitimate and cheap to satisfy without
  reopening the write-authority question.

## Consequences

`loop-config-interview.md`'s `## Record` step writes two lines into `AGENTS.md`/`CLAUDE.md`'s
suite section now, not one — the existing `Refactoring Notes:` line, plus the new `Create-mode:`
pointer and the candidate-label line. No skill's read/write logic for the actual `Create-mode`
value changes.
