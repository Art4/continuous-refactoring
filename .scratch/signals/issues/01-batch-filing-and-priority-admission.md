# 1 — Batch-file structural/baseline-shrink candidates; priority admission bypasses the backlog cap

**What to build:** `refactor-prioritize`'s Select mode (structural-scan and PHPStan baseline-shrink)
files every genuine friction spot it finds this exploration, not just the single strongest.
`refactor-scan`'s existing "five or more open `refactor:candidate` issues → stop" backlog cap splits
into two counters: an ordinary, capped tier, and an uncapped **priority** tier for candidates whose
signal is Security or Blast Radius (cost of leaving it unfixed keeps rising). A new, curated set of
seven Signal factors (beyond structural-candidate-search.md's existing six friction cues) drives both
Select mode's own internal ranking among found candidates and the priority-tier trigger — documented
in a new, purely descriptive `signals.md` reference (no execution, no adoption tracking). The existing
"Tooling tree" term stays as-is everywhere (CONTEXT.md, file/code names) — "Safety Net" is adopted
only as human-facing prose in `docs/playbooks/loop.md`, not a glossary rename.

**Why:** Triggered by filing `Art4/legacy-todo#179` ("Move HTTP entry points into a public/ webroot")
— a real, severe security finding that today's five ranking factors (Heat, Leverage, Tooling pressure,
Risk, Skip streak) wouldn't have surfaced as urgent on their own, and that Select mode's current
"pick the single strongest, set the rest aside" rule would have delayed indefinitely behind whatever
wins ranking that pass. Also resolves a pre-existing open question,
`.scratch/php-tooling-tree/issues/36-candidate-backlog-stop-threshold.md` (the "5" backlog cap has no
technical basis — confirmed while grilling this ticket) — this ticket supersedes it; close 36 once
this ships, pointing here.

**Blocked by:** none (builds on the just-shipped scan-design-split, PR #63).

**Priority:** medium.

**Status:** done

Settled via `/grill-with-docs` (`grilling` + `domain-modeling`, three rounds):

- [x] **Batch filing:** Select mode (structural-scan and PHPStan baseline-shrink, same logic for
  both) files every genuine friction spot / root-cause group found this exploration — not just the
  strongest. The quality bar itself doesn't drop for the sake of filling a batch (see the capped
  tier's own bar below).
- [x] **Two admission tiers:**
  - **Priority** (new label `refactor:priority`, alongside `refactor:candidate`) — the candidate's
    Signal is **Security** or **Blast Radius bei Nicht-Handeln** (leaving it unfixed gets worse over
    time, not just risky as-is). Always filed, regardless of backlog size. Does **not** count toward
    `refactor-scan`'s cap — a `refactor-scan` step 1 that let priority candidates choke off ordinary
    proposals would be the exact failure mode the cap exists to prevent, just relocated.
  - **Capped** (`refactor:candidate` only) — every other Signal. Subject to `refactor-scan`'s
    existing cap, simplified to two states, no middle scaling: under 5 open capped candidates, any
    solid (not necessarily excellent) candidate is admitted; at 5, stop proposing new ones, same as
    today.
  - `refactor-scan` step 1 tracks these as **two separate counters** instead of one combined count.
- [x] **Priority tier affects admission only, not ranking.** Once filed, a priority-tier candidate
  competes in a future `refactor-prioritize` Rank mode exactly like any other proposal, using Rank
  mode's existing five factors unchanged (see next point) — no queue-jump, no ranking boost. The
  guarantee is "gets in immediately and stays visible," not "gets worked next."
- [x] **New Signal factors apply to Select mode only, not Rank mode.** Rank mode's existing five
  factors (Heat, Leverage, Tooling pressure, Risk, Skip streak) are unchanged — they compare
  heterogeneous proposals (tooling nodes, gates, externally-labeled candidates) and most of the new
  factors don't translate to an abstract tooling node ("does PHPStan Level 3 have a bus factor?").
  The new factors live entirely in Select mode's own candidate search and its internal ranking among
  multiple candidates found in one exploration.
- [x] **Seven curated Signal factors**, added to `structural-candidate-search.md`'s existing six
  friction cues (shallow modules, missing locality, low leverage, tightly-coupled seams,
  untested/hard-to-test, tooling pressure): **Security**, **Fehlerdichte** (defect density, distinct
  from Heat's pure churn), **Blast Radius bei Nicht-Handeln**, **Verständlichkeit** (merges bus-factor
  and cognitive load — both "how hard for a person to follow/maintain"), **Beobachtbarkeit**
  (observability — can you tell when it's broken), **Domänenkritikalität** (business/domain
  criticality), **Timing/Sequenzierung** (an upcoming larger change that would fold this in for
  free, or make it urgent). Dependency-lifecycle risk folds into the existing Tooling pressure cue
  instead of becoming an eighth.
- [x] **`signals.md`:** new, single reference file (no generic/language-specialization split — that
  pattern earns its cost only for real adoption-order chains, which a documentation-only mapping
  doesn't have), at `skills/refactor-prioritize/references/signals.md`. Purely descriptive: per
  factor, how to recognize it while exploring (some need nothing beyond git/filesystem — Heat,
  Verständlichkeit's bus-factor half, Timing; others need a language tool — e.g. `phpmd` for
  cyclomatic complexity feeding Fehlerdichte, on the PHP tree). No tool execution by the skill itself
  in this iteration, no adoption/`Fulfilled nodes`-style tracking — a future ticket's decision, not
  this one's.
- [x] **"Safety Net" stays prose-only.** No `CONTEXT.md`/file-name/code rename of "Tooling tree" —
  127 existing references (prose, ADRs, file paths, `tooling_tree.py`) make a real rename
  disproportionate to a naming preference. "Safety Net" appears only in `docs/playbooks/loop.md`
  (the human-facing playbook); `README.md`/`AGENTS.md`/`CONTEXT.md` keep "Tooling tree" unchanged.
- [x] **`CONTEXT.md` gains a `Signal` glossary entry** — the named selection criterion (Heat,
  Leverage, Security, …) that qualifies a candidate as a friction spot; the third field (with Where,
  Problem) on every candidate issue Select mode files.
- [x] **One combined ADR** covering the whole batch-filing/priority-admission mechanism (Considered
  Options: fixed batch count vs. dynamic vs. uncapped; a three-tier scaling quality bar vs. the
  simpler two-state one chosen; which factors trigger priority admission), with a short note on the
  Safety Net prose-renaming as a minor accompanying decision — not a second ADR.

## Comments

> **2026-09-07:** Filed after a `/grill-with-docs` session (German — `grilling` + `domain-modeling`),
> three rounds, triggered by filing `Art4/legacy-todo#179` (a security finding today's factors
> wouldn't surface as urgent) and by the user's own idea to let Select mode file several candidates
> per exploration instead of one. Covered batch-filing mechanics, the two-tier backlog-admission
> split (and its interaction with `refactor-scan`'s existing 5-issue cap and open ticket 36), which
> new Signal factors to add and where they apply (Select mode only, not Rank mode), the `signals.md`
> shape (documentation-only, single file), the Safety Net renaming's actual scope (prose-only, given
> 127 existing "tooling tree" references), a new `CONTEXT.md` glossary entry for `Signal`, and the
> ADR offer. User confirmed shared understanding ("passt"). Ready to implement.
> **2026-09-10:** Status correction — this was already fully implemented (ADR-0039,
> `skills/refactor-prioritize/references/signals.md`, `refactor:priority`/two-counter split live in
> `refactor-scan/SKILL.md` step 1, `CONTEXT.md`'s `Signal` entry) but the `Status` field here was
> never flipped from `ready-for-agent`. Corrected to `done`; no further work needed.
