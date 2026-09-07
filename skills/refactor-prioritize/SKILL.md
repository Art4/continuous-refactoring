---
name: refactor-prioritize
description: Rank refactor-scan's proposals and recommend the next one to work on, or say why nothing should start this pass. For a gate-shaped winner, also selects and minimally files the concrete candidate within it.
---

# Refactor Prioritize

Rank the **proposals** `refactor-scan` handed the orchestrator this pass, and recommend the single one to work on next. The loop's value comes from working the *right* thing next, not from working any of them.

Runs in one of two modes, both dispatched by the orchestrator — never one calling the other inline:

- **Rank mode** (default, steps 1–3): picks the next node to work on.
- **Select mode** (step 4): the orchestrator re-invokes this skill, as a fresh dispatch, only when
  Rank mode's winner was a gate (`structural-scan`, a PHPStan baseline-shrink family) — a name,
  not yet a concrete candidate. Select mode does the actual exploration (codebase or baseline) that
  Rank mode's own declarative ranking never does, picks one concrete candidate, and files it
  minimally. A fresh dispatch, not a continuation of Rank mode's own context, so the exploration
  never bleeds into the (much lighter) ranking reasoning, or vice versa.

## Process

### 1. Check whether anything should start at all

Get the remembered set of in-flight suite MRs: `docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab) → every open `refactor:candidate` issue that carries a linked pull request (the tracker's native issue↔closing-PR cross-reference); otherwise the Refactoring Notes' `merge-requests.md` directly. **Two or more already open?** Stop here: report which, and that the pass ends without starting new work while they await review/merge. Overrides everything below.

Otherwise drop any proposal already in that set — it already has an open MR, so it isn't something to *start*.

A `Pending candidates` entry never reaches this skill at all — `refactor-scan` step 2 routes it
straight to `refactor-design` (not yet planned) or `refactor-implement` (already planned), bypassing
Rank and Select mode both; see `refactor-scan/SKILL.md` step 2 and the orchestrator's own step 1.

### 2. Rank

For each surviving proposal, assess:

| Factor | Question |
|---|---|
| **Heat** | In a hot spot (frequently changing area)? Pays off faster, unblocks more upcoming change. |
| **Leverage** | How much future change does deepening this module unlock? A module many others call is high-leverage; an uncalled leaf is not. |
| **Tooling pressure** | Is the fulfilled tooling (PHPStan, Rector, style) actively flagging it? If so it's re-failing every CI run until fixed. |
| **Risk** | How hard to reverse, how wide the blast radius? Prefer reversible, low-risk refactors early while the habit is forming. |
| **Skip streak** | Consecutive prior passes that proposed this without choosing it (the Refactoring Notes' `bookkeeping.md`'s `Skip streak`, read-only here — `refactor-learn` writes it). A longer streak weighs increasingly toward choosing it, so a `required` sibling that never wins on the other four alone doesn't starve indefinitely — but it's one factor among five, not a forced pick. |

Tooling-tree node: read its Purpose in the tree doc to reason about what it unlocks — node-detail data beyond that Purpose line isn't a maintained source yet.

Present the ranking as a short ordered list of Names only (never slugs) — save the rationale for the winner for step 3.

### 3. Recommend

Name the single next candidate by its Name (never slug); one line why it wins, one line what choosing it unlocks (the next node(s), per the tree doc, or the module/area it deepens for `structural-scan`). Two lines total — this **is** the `## Output` payload, not a separate report. Close call → call it out and let the user decide.

A proposable tooling-tree node is a strong default recommendation — the loop's structural work compounds faster once the underlying tooling is in place. Still a recommendation, not a **required edge** — the user may pick something else.

Nothing survived step 1's filtering (every proposal already in flight, or scan proposed nothing) → report that explicitly instead; the orchestrator ends the pass here.

### 4. Select (Select mode only — a gate won)

Only runs on this second, fresh dispatch — never inline after step 3 in the same context, and never
for a winner that's already concrete (an ordinary tooling-tree node, an externally-labeled candidate
— those go straight to `refactor-design`, this step doesn't apply).

- **Winner is `structural-scan`** → run `skills/refactor-prioritize/references/structural-candidate-search.md` in full.
- **Winner is a "PHPStan Level N — baseline shrink" proposal** → run `skills/refactor-prioritize/references/baseline-shrink-selection.md` in full.

Both end the same way: every genuine candidate found gets filed (minimal fields, never the full
plan — that's `refactor-design`'s job, added as a comment only on the one this pass pursues), sorted
into a **priority** or **capped** admission tier by its Signal
(`skills/refactor-prioritize/references/signals.md`), and the single strongest is this pass's
recommendation, carried forward.

`docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab) → **still write**
`Pending candidates` to this issue, unlike the ordinary design→implement handoff (which native
trackers skip, `skills/continuous-refactoring/references/refactoring-bookkeeping.md`) — a pass
interrupted between this filing and `refactor-design`'s follow-up comment needs `refactor-scan` to
resume exactly this issue next pass, not treat it as a fresh externally-labeled candidate and
potentially select a different one. No native-label tracker → unchanged, same write as always. Either
way, via the dedicated bookkeeping branch — never a direct commit to whatever branch happens to be
checked out, and never to the default branch.

## Output

**Rank mode:** step 3's two lines, verbatim, → `refactor-design`, **or** "nothing to do, because …" → the orchestrator ends the pass.

**Select mode:** the single recommended candidate's issue (number + its minimal fields) →
`refactor-design` — any other candidates filed this same run sit as ordinary open issues, for a
future pass.

## Fallback

- **`/codebase-design`**: installed → use its vocabulary in Select mode's structural-candidate search (`skills/refactor-prioritize/references/structural-candidate-search.md`). Otherwise the vocabulary (module, interface, depth, seam, leverage, locality) is already inline in that same reference file — nothing else needed.

## Completion criterion

**Rank mode:** either a single next candidate is recommended with a reason and what it unlocks, or the pass is explicitly reported as having nothing to start — never both. **Select mode:** the candidate has an issue (newly filed, or resumed) naming Where/Problem/Signal (structural) or the chosen group (baseline-shrink) — no plan yet, that's `refactor-design`'s completion criterion.
