---
name: refactor-prioritize
description: Rank refactor-scan's proposals and recommend the next one to work on, or say why nothing should start this pass.
---

# Refactor Prioritize

Rank the **proposals** `refactor-scan` handed the orchestrator this pass, and recommend the single one to work on next. The loop's value comes from working the *right* thing next, not from working any of them.

## Process

### 1. Check whether anything should start at all

Get the remembered set of in-flight suite merge requests: every issue labeled `refactor:delivered` when the target's issue tracker natively supports labels (GitHub, GitLab), otherwise `docs/refactoring/merge-requests.md` directly (local state docs are fair game for any skill — only the external tracker/git reconciliation is `refactor-scan`'s alone). **Two or more already open?** Stop here: report which ones, and that the pass ends without starting new work while they await review/merge. This overrides everything below.

Otherwise, drop any proposal already in that set from consideration — it already has an open merge request delivering it, so it isn't something to *start*.

If `refactor-scan` handed over a single resumed pending issue (not five fresh proposals), that *is* the recommendation — skip ranking and go straight to step 3 with it.

### 2. Rank

For each surviving proposal, assess four factors:

- **Heat** — is it in a hot spot (frequently changing area)? A candidate in a hot spot pays off faster because it unblocks more upcoming change.
- **Leverage** — how much future change does deepening this module unlock? A module many others call is high-leverage; a leaf nobody calls is not.
- **Tooling pressure** — is the fulfilled tooling (PHPStan, Rector, style) actively flagging it? If so, it's re-failing every CI run until fixed.
- **Risk** — how hard to reverse / how wide the blast radius? Prefer reversible, low-risk refactors early in the loop while the habit is forming.

For a tooling-tree node proposal, read its Purpose in the tree doc (`skills/refactor-scan/references/tooling-tree.md` / the language specialization's tree) to reason about what it unlocks — node-detail data beyond that Purpose line (e.g. what reaching a specific tool level opens up next) is not yet a maintained source and is deliberately out of scope for now; reason from the tree doc and the ranking factors above.

Present the ranking as a short ordered list of Names only (the tree doc's `**Name:**` field for a tooling-tree node, never its slug) — save the rationale for the winning candidate for step 3, don't repeat it here.

### 3. Recommend

Name the single next candidate — by its Name, never its slug, for a tooling-tree node; in one line say why it wins, and in one line say what choosing it unlocks (the next node(s) it opens, per the tree doc, or the module/area it deepens for a `structural-scan` proposal) — two lines total, this **is** the `## Output` payload below, not a separate report. If two are close, call the tie out and let the user decide.

A proposable **tooling tree** node is a strong default recommendation — the loop's structural work compounds faster once the underlying tooling is in place. Still let the user pick something else instead; this is a recommendation, not a **required edge**.

If nothing survived step 1's filtering (every proposal already in flight, or `refactor-scan` proposed nothing), report that explicitly instead of a recommendation — the orchestrator ends the pass here.

## Output

Step 3's two lines (the candidate, plus why it wins and what it unlocks), verbatim, → `refactor-design`, **or** "nothing to do, because …" → the orchestrator ends the pass. Nothing more.

## Completion criterion

Either a single next candidate is recommended with a reason and what it unlocks, or the pass is explicitly reported as having nothing to start (two MRs already open, or every proposal already in flight) — never both.
