# 1 — refactor-learn precondition, comment-reading, decision trail, MR outlook move, dated secret scan

**What to build:** Six related fixes, decided together in one `/grill-with-docs` session after a
broader review of all five loop skills plus both orchestrators:

1. **`refactor-learn` requires a genuine event.** Both calls (early, closing) gain an explicit
   precondition and stop with "nothing to do" — no branch, no write — when it isn't met. See
   [ADR-0051](/docs/adr/0051-refactor-learn-requires-a-genuine-event.md) for the full reasoning,
   considered options, and consequences.
2. **`refactor-design` reads issue comments, not just the body**, everywhere it grounds itself in an
   issue: `structural-candidate.md` step 3, the externally-labeled-candidate path
   (`refactor-design/SKILL.md` step 1), and PHPStan baseline-shrink planning
   (`phpstan-baseline-shrink.md` step 3).
3. **A Decision trail**: `refactor-design` posts a bundled issue comment recording every
   ADR-bar-qualifying grilling question and its live answer, once grilling settles and before the plan
   is written. See
   [ADR-0052](/docs/adr/0052-grilling-decision-trail-separate-from-decision-gate.md).
4. **The tooling-tree MR's "Outlook" (next-up sentence + diagram) moves off the MR description and
   onto the candidate's own issue** — same computation, same content, `refactor-implement` posts it as
   a comment at the same point it previously wrote it into the MR instead. Structural candidates keep
   having no Outlook at all (unchanged — there's no single next child a deepening unlocks).
5. **`Secret history scan: done` gains a date** — `done (YYYY-MM-DD)` — purely for human-readable
   audit trail; no new re-scan cadence, still a one-time flag removed by hand to force a re-run.

**Why:** All six came out of the same review-and-grill session (2026-09-14): a walkthrough of what
each of `refactor-scan`, `refactor-prioritize`, `refactor-design`, `refactor-implement`,
`refactor-learn`, `continuous-refactoring`, and `continuous-housekeeping` actually does today,
followed by a critical pass on `refactor-learn` specifically (should it exist standalone, does it need
a no-input guard), then a `/grilling` session to sharpen five confirmed follow-ups into something
implementable. Three other ideas surfaced in the same review are explicitly **out of scope** for this
ticket, parked for later: a `refactor-learn` → `refactor-bookkeeping` rename (rejected outright — too
invasive for the value), a `continuous-housekeeping` check for stale CI-config images/tools/actions,
and packaging the skill suite for distribution without its own dev clutter (`.scratch/`, fixtures,
tests).

**Blocked by:** none.

**Priority:** low — internal suite-quality work, no user-facing bug.

**Status:** done — PR #84.

Settled via `/grill-with-docs` (11 questions across 2 rounds, all resolved without disagreement):

- [x] **Q1 — Unify the precondition.** One check per call (early: needs a finding; closing: needs an
  MR or breaking-change finding) rather than two separate mechanisms for "no input" vs. "no standalone
  cache MR" — they turned out to be the same underlying rule. See ADR-0051.
- [x] **Q2 — Comment-reading applies everywhere refactor-design grounds in an issue**, not only the
  structural-candidate path — consistency across all three paths that read "the issue".
- [x] **Q3 — Decision trail stays separate from the decision gate.** The gate blocks (unattended,
  proposes a default); the trail only documents (attended, answer already exists). See ADR-0052.
- [x] **Q4 — Outlook move stays scoped to tooling-tree candidates.** Structural candidates already
  have no Outlook by design (`opening-a-merge-request.md`); that reasoning is unrelated to this move
  and untouched.
- [x] **Q5 — Outlook moves to the candidate's own issue**, written by `refactor-implement` at the same
  point it previously wrote the MR description — not dropped entirely (a later reader of the closed
  issue still benefits from seeing what it unlocked), not deferred to `refactor-learn`'s closing call
  (`refactor-implement` already has the roadmap computation fresh in hand at MR-opening time).
- [x] **Q6 — Secret-scan date is purely informational**, same spirit as `Fulfilled nodes`' own
  `(#issue)` annotation — no new cadence/staleness behaviour, avoiding a materially bigger,
  undiscussed change.
- [x] **Q7 — Orchestrator's closing call stays an unconditional invocation**; `refactor-learn` itself
  owns the precondition check rather than the orchestrator pre-filtering a second time.
- [x] **Q8 — Decision trail posts *after* a question is answered**, bundled at the end of grilling
  (step 4), not live as questions are asked — posting an unanswered question publicly invites
  third-party comment on something still being negotiated live.
- [x] **Q9 — Decision trail reuses the decision gate's own three-factor ADR test** as its filter,
  rather than inventing a second "is this important" standard in the same skill.
- [x] **Q10 — Decision trail is its own comment**, not a section folded into the plan comment — keeps
  the plan comment a pure specification.
- [x] **Q11 — The orchestrator's existing early-call skip (`continuous-refactoring/SKILL.md` step 2)
  stays untouched.** Not part of the original five points; touching it now would be scope creep beyond
  what was actually broken.

**Parked, not part of this ticket:** `refactor-learn` → `refactor-bookkeeping` rename (raised again in
this same review, rejected: too many call sites to touch for the naming clarity gained);
`continuous-housekeeping` CI-config-currency check; skill-suite distribution without dev clutter.

## Comments

> **2026-09-14:** Filed after a two-part session (German): first a broad fact-check of all 5 loop
> skills + 2 orchestrators against the actual `SKILL.md` files (several corrections landed —
> `refactor-scan` never files issues or runs the structural scan itself, `refactor:priority` is a
> pre-filter not a ranking factor, `continuous-housekeeping` is only ever nudged by the orchestrator,
> never by `refactor-scan`), then a critical assessment of whether `refactor-learn` should exist
> standalone at all (kept, but flagged as needing a no-input stop guard) and whether `refactor-design`
> may read/post issue comments during grilling (confirmed yes, with the audience rule from
> `forge-facing-writing.md` applying). The rename idea was explicitly rejected ("wir lassen den namen
> erstmal so, weil die umbenennung zu viele Eingriffe bedeutet"). The remaining six points were then
> run through `/grill-with-docs` and are captured above.

> **2026-09-14 (implement):** Landed on `scratch/refactor-learn-precondition-ticket` (PR #84) across
> four commits. First: the six points themselves — the precondition guard plus the
> `Fulfilled nodes`-bundling rule in `refactor-learn/SKILL.md` (ADR-0051), comment-reading added to
> all three `refactor-design` grounding paths, the Decision trail mechanism in
> `structural-candidate.md` (ADR-0052), the Outlook move to a new
> `refactor-implement/references/outlook-comment.md` (kept `refactor-implement/SKILL.md` from
> tipping the validator's word-count advisory), and the dated `Secret history scan` field — new ADRs,
> `CONTEXT.md`'s **Decision trail** entry, and a changelog fragment included. Two review rounds
> followed: first, dropped a leftover "No outlook in the description" negative-framing bullet from
> `opening-a-merge-request.md` plus three now-stale citations to the old outlook location
> (`continuous-refactoring/SKILL.md`, `tooling_tree.py`'s `--unblocked-by` help string, a test
> docstring, and `outlook-comment.md`'s own header, which also cited the wrong ADRs). Second: noticed
> the four `docs/adr/0051-...` citations added to `skills/`/`references/` content had slipped past
> the validator's `adr_issues()` check, which only regexed the bare `ADR-NNNN` form — removed those,
> then widened the check to also catch backtick-quoted `docs/adr/NNNN-slug.md` paths (two new tests),
> which in turn caught two pre-existing violations (`loop-config-interview.md`'s ADR-0025/0026,
> `refactor-learn/SKILL.md`'s ADR-0026) — cleaned those up too, all three already stated their rule
> inline. 315/315 tests green throughout, validator clean (only the same pre-existing size/duplication
> advisories as on `main`). Ready for review.

> **2026-09-14 (live test finding):** User ran `/refactor-learn` standalone with no input and reported
> it stopped correctly, but still read open MRs and analyzed `bookkeeping.md` *before* stopping — the
> precondition text said "stop immediately" but never said the check itself must rely only on what was
> actually handed to the call. Fixed: the precondition paragraph now explicitly forbids investigating
> to find a satisfying event (querying the tracker, re-reading `bookkeeping.md`/`merge-requests.md`) —
> that's `refactor-scan`'s/`refactor-implement`'s own detection job, never this skill's; a direct
> invocation naming nothing already means "neither present," checked before any other read. 315/315
> tests still green, validator clean.
