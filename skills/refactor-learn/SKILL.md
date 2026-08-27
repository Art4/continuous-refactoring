---
name: refactor-learn
description: The suite's only writer of bookkeeping — acts on refactor-scan's reconciliation findings and refactor-implement's freshly opened merge request, records the ledger, ADRs, CONTEXT.md, and the last-run stamp. Part of the continuous refactoring loop.
---

# Refactor Learn

The only skill in the suite that writes suite bookkeeping (ADR-0010): `docs/refactoring/merge-requests.md`, `docs/refactoring/out-of-scope/`, ADRs, `CONTEXT.md`, `docs/refactoring/config.md`, and issue labels. Every other lifecycle skill may read these directly; only this one writes them.

The orchestrator calls this skill up to **twice** in one pass, never more: an **early call**, right after `refactor-scan`, only when it produced findings; and a **closing call**, always, at the very end. The split exists because `refactor-prioritize` reads the ledger to decide whether two merge requests are already open — a finding this pass just resolved has to be written back before that check runs, not deferred to the end where it would be too late to matter this pass.

## Process

### Early call — findings only (from `refactor-scan`, if any)

Runs only when scan produced findings; skip everything below when it didn't — the closing call still happens regardless, at the end.

For each finding:

- Merged → mark the candidate `done` and close the issue, drop it from `docs/refactoring/merge-requests.md`.
- Closed without merge → if the closing comments support a structural rejection (a maintainer gave a load-bearing reason), mark the candidate `wontfix`, close the issue, and file a learned rejection under `docs/refactoring/out-of-scope/`; otherwise ask the human what to do before deciding.
- Drop the entry from `docs/refactoring/merge-requests.md` either way once resolved.

`done` and `wontfix` are the shared triage-role labels (`docs/agents/triage-labels.md`), not suite-specific ones — closing the issue is what actually takes it out of the backlog; which labels stay attached alongside `done`/`wontfix` doesn't matter for that.

A pass that only makes this call (no fresh candidate reached this run) is still a complete pass — bookkeeping-only completion is valid.

### Closing call — always, at the end of the pass

Given a freshly opened merge request (from `refactor-implement`, if the pass got that far):

- Remember it in `docs/refactoring/merge-requests.md`: URL, candidate issue, the tooling-tree node name (blank for a structural candidate), and base branch. This ledger lives on the default branch regardless of what follows below.
- Clear `docs/refactoring/config.md`'s `Pending issue` field — this candidate now has a merge request, so the marker that would let `refactor-scan` resume it as unfinished work no longer applies.
- Label the candidate `refactor:delivered` (ADR-0009) — never `done` (the merge request isn't merged yet — that's the *next* pass's early call, once it merges) and never `ready-for-human` (that label means "nobody has implemented this yet," the opposite of what just happened).
- If `docs/refactoring/config.md`'s `Create-mode` wasn't set before this pass, record what `refactor-implement` used (`autonomous`, `ask-each-time`, or `human-opens` — per the orchestrator's `## Opening a merge request` guidance).

**`loop-config`-in-flight exception — `config.md` doesn't exist on the default branch yet:** true only before the `loop-config` candidate itself has merged. There's nowhere on the default branch to clear `Pending issue` or record `Create-mode` yet. Write both as a follow-up commit on the candidate's own branch instead — the one exception to "bookkeeping goes to the default branch, not the candidate's branch" (ADR-0009), since `config.md` only exists there until this MR merges, and these fields will ride along in the same review. Once the merge request merges (a later pass's early call sees it), everything is on the default branch as usual from then on.

Then, regardless of whether a merge request was opened this pass:

- Record an ADR (`docs/adr/`) for any decision a future scan must not re-litigate (see `/domain-modeling`).
- Update `CONTEXT.md` with any terms that crystallised this pass.
- Set `docs/refactoring/config.md`'s `Last run` to today — unconditionally, the last thing this skill does. Same `loop-config`-in-flight exception as above: before `loop-config` merges, this stamp lands on that candidate's own branch, not the default branch.

## Fallback

- **`/domain-modeling`**: if installed, use its discipline for the ADR and `CONTEXT.md` side effects. Otherwise skip with a note — the ledger, label, and stamp writes are inline and suite-internal; they run regardless of whether `/domain-modeling` is installed. Crash-safe.

## Completion criterion

**Early call:** every finding this skill was given is resolved (`done`, `wontfix` + out-of-scope entry, or an explicit "asked the human, waiting"), and the ledger reflects it before `refactor-prioritize` runs.

**Closing call:** a freshly delivered candidate (if any) is remembered in the ledger with `Pending issue` cleared and `refactor:delivered` applied, and `Last run` is stamped.
