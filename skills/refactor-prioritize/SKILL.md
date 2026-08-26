---
name: refactor-prioritize
description: Rank the refactoring backlog and recommend the next candidate to work on. Part of the continuous refactoring loop.
---

# Refactor Prioritize

Rank the **backlog** — the open `refactor:candidate` issues — and recommend the next one to tackle. The loop's value comes from working the *right* candidate next, not from working any candidate.

## Process

### 1. Load the backlog

Query the issue tracker for all open issues labeled `refactor:candidate` (see `docs/agents/issue-tracker.md`). Then read `docs/refactoring/merge-requests.md` — the loop's remembered-merge-request ledger — and drop any candidate already listed there from the backlog: it already has an open merge request delivering it, so it is not something to *start* work on, regardless of what label state the issue itself happens to carry.

Two distinct empty-ish outcomes can result. Report whichever applies and stop — they are not the same thing and need different messages:

- **No open `refactor:candidate` issues at all.** Report the backlog is empty.
- **One or more open `refactor:candidate` issues, but every one of them is already listed in `docs/refactoring/merge-requests.md`.** Report that the backlog is not empty but nothing is currently actionable — name each excluded candidate together with the merge request already delivering it (URL + branch from the ledger).

Only candidates that survive this filter move on to ranking.

### 2. Rank

For each surviving candidate, assess four factors:

- **Heat** — is it in a hot spot (frequently changing area)? A candidate in a hot spot pays off faster because it unblocks more upcoming change.
- **Leverage** — how much future change does deepening this module unlock? A module many others call is high-leverage; a leaf nobody calls is not.
- **Tooling pressure** — is the fulfilled tooling (PHPStan, Rector, style) actively flagging it? If so, it's re-failing every CI run until fixed.
- **Risk** — how hard to reverse / how wide the blast radius? Prefer reversible, low-risk refactors early in the loop while the habit is forming.

Present the ranking as a short list, oldest-first within each tier, with a one-line rationale per candidate.

### 3. Recommend

Name the single next candidate and say why it wins. If two are close, call the tie out and let the user decide.

If the (already-filtered) backlog contains a proposable **tooling tree** node (`loop-config`, or a node from `docs/php-tooling-tree.md`), treat it as a strong default recommendation — the loop's structural work compounds faster once the underlying tooling is in place, and `refactor-scan` only ever files one such candidate at a time. Still let the user pick a structural deepening instead; this is a recommendation, not a **required edge** (ADR-0005, ADR-0008).

## Completion criterion

The backlog is ranked with a one-line rationale per candidate, and a single next candidate is recommended with a reason — or, when every open candidate is already in flight per `docs/refactoring/merge-requests.md`, that is reported explicitly instead of a recommendation.