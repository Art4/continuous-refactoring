---
name: refactor-prioritize
description: Rank the refactoring backlog and recommend the next candidate to work on. Part of the continuous refactoring loop.
---

# Refactor Prioritize

Rank the **backlog** — the open `refactor:candidate` issues — and recommend the next one to tackle. The loop's value comes from working the *right* candidate next, not from working any candidate.

## Process

### 1. Load the backlog

Query the issue tracker for all open issues labeled `refactor:candidate` (see `docs/agents/issue-tracker.md`). If the backlog is empty, report that and stop — there's nothing to prioritise.

### 2. Rank

For each candidate, assess four factors:

- **Heat** — is it in a hot spot (frequently changing area)? A candidate in a hot spot pays off faster because it unblocks more upcoming change.
- **Leverage** — how much future change does deepening this module unlock? A module many others call is high-leverage; a leaf nobody calls is not.
- **Tooling pressure** — is the fulfilled tooling (PHPStan, Rector, style) actively flagging it? If so, it's re-failing every CI run until fixed.
- **Risk** — how hard to reverse / how wide the blast radius? Prefer reversible, low-risk refactors early in the loop while the habit is forming.

Present the ranking as a short list, oldest-first within each tier, with a one-line rationale per candidate.

### 3. Recommend

Name the single next candidate and say why it wins. If two are close, call the tie out and let the user decide.

## Completion criterion

The backlog is ranked with a one-line rationale per candidate, and a single next candidate is recommended with a reason.