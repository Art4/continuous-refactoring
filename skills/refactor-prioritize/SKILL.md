---
name: refactor-prioritize
description: Rank refactor-scan's proposals and recommend the next one to work on, or say why nothing should start this pass.
---

# Refactor Prioritize

Rank the **proposals** `refactor-scan` handed the orchestrator this pass, and recommend the single one to work on next. The loop's value comes from working the *right* thing next, not from working any of them.

## Process

### 1. Check whether anything should start at all

Get the remembered set of in-flight suite MRs: every issue labeled `refactor:delivered` when `docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab), otherwise the Refactoring Notes' `merge-requests.md` directly. **Two or more already open?** Stop here: report which, and that the pass ends without starting new work while they await review/merge. Overrides everything below.

Otherwise drop any proposal already in that set — it already has an open MR, so it isn't something to *start*.

`refactor-scan` handed over a single resumed pending issue, not a fresh batch? That *is* the recommendation — skip ranking, go straight to step 3.

### 2. Rank

For each surviving proposal, assess:

- **Heat** — in a hot spot (frequently changing area)? Pays off faster, unblocks more upcoming change.
- **Leverage** — how much future change does deepening this module unlock? A module many others call is high-leverage; an uncalled leaf is not.
- **Tooling pressure** — is the fulfilled tooling (PHPStan, Rector, style) actively flagging it? If so it's re-failing every CI run until fixed.
- **Risk** — how hard to reverse, how wide the blast radius? Prefer reversible, low-risk refactors early while the habit is forming.
- **Skip streak** — consecutive prior passes that proposed this without choosing it (the Refactoring Notes' `config.md`'s `Skip streak`, read-only here — `refactor-learn` writes it). A longer streak weighs increasingly toward choosing it, so a `required` sibling that never wins on the other four alone doesn't starve indefinitely — but it's one factor among five, not a forced pick.

Tooling-tree node: read its Purpose in the tree doc to reason about what it unlocks — node-detail data beyond that Purpose line isn't a maintained source yet.

Present the ranking as a short ordered list of Names only (never slugs) — save the rationale for the winner for step 3.

### 3. Recommend

Name the single next candidate by its Name (never slug); one line why it wins, one line what choosing it unlocks (the next node(s), per the tree doc, or the module/area it deepens for `structural-scan`). Two lines total — this **is** the `## Output` payload, not a separate report. Close call → call it out and let the user decide.

A proposable tooling-tree node is a strong default recommendation — the loop's structural work compounds faster once the underlying tooling is in place. Still a recommendation, not a **required edge** — the user may pick something else.

Nothing survived step 1's filtering (every proposal already in flight, or scan proposed nothing) → report that explicitly instead; the orchestrator ends the pass here.

## Output

Step 3's two lines, verbatim, → `refactor-design`, **or** "nothing to do, because …" → the orchestrator ends the pass.

## Completion criterion

Either a single next candidate is recommended with a reason and what it unlocks, or the pass is explicitly reported as having nothing to start — never both.
