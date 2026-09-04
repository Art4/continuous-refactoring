# PHPStan baseline-shrink candidates: closing the level chain's stagnation trap

A real gap observed live while reviewer-loop-watching `Art4/legacy-todo` (ticket 51): `phpstan.md`'s
own Stop conditions for the level chain already promised *"the loop proposes shrinking work... until
the baseline becomes empty"* once a fulfilled level's baseline is non-empty — but that mechanism
never existed. Grep confirmed zero mentions of "baseline" in any of `refactor-scan`/
`refactor-prioritize`/`refactor-design`/`refactor-implement`'s `SKILL.md` files; `tooling_tree.py`'s
`next_candidates()` silently skips a level-N node once its predecessor's baseline is non-empty, with
no substitute proposed. A level, once fulfilled with real residual findings, therefore never gets any
follow-up work — the chain stalls forever unless a human intervenes by hand, which also transitively
blocks `php-structural-scan` (requires `phpstan-level-10` resolved). Settled via a `/grill-me` session
(ticket 51).

## Considered Options

- **A new synthetic candidate shape in `tooling_tree.py`** — `next_candidates()` mechanically
  generates one entry per file with residual baseline findings (mirroring `roadmap()`'s existing
  `"structural:<file>"` precedent for its own, non-authoritative simulation fallback). Rejected during
  grilling — grouping by file conflates independent root causes into one MR when a file has more than
  one, and mechanical per-file enumeration can't do what step 2 below actually needs: judging which
  findings share a root cause and are worth fixing together. That judgment belongs to a skill, not a
  deterministic parser.
- **Leave it to `refactor-scan` step 3b's existing externally-labeled-candidate mechanism** (a human
  files an issue by hand once they notice the stall). Rejected — defeats the loop's own "continuous"
  premise; the whole point is that this stagnation is detectable and actionable without a human having
  to notice it first.
- **Require full-empty per candidate** (every reduction MR must clear its entire chosen group in one
  shot). Rejected — a group can be large enough that fixing it all at once breaks the tree's own
  small-bounded-MR ethos; the level-bump MR's own "strictly reduce" wording already accepts partial
  progress one step later in the same chain, and the same principle applies here.

## Decision

**Detection stays mechanical, grouping and fixing don't.** `phpstan-level-N`'s existing
`detect_nodes()` output already exposes `details.baseline_empty` for every level, fulfilled or not —
no `tooling_tree.py` change needed for the raw signal. `refactor-scan` gains step 4b: find the
highest fulfilled `phpstan-level-N`; its baseline non-empty → propose **"PHPStan Level N — baseline
shrink"** alongside the pass's other proposals, generically, the same shape `structural-scan` itself
already gets proposed in (naming the open gate, not yet a specific plan).

**`refactor-design` does the actual baseline read and grouping** — new reference file
`phpstan-baseline-shrink.md`, run in place of the usual tooling-tree-node/structural-candidate paths
for this candidate. Group findings by **root cause** (same message pattern + identifier, not by
file — a root cause commonly spans several files, and one fix approach usually covers the whole
group). Pick one group by ordinary judgment, same as `refactor-prioritize`'s own reasoning elsewhere
— no fixed priority rule.

**Continuity across passes is structural, not a separate tracking field.** A chosen group becomes an
ordinary `refactor:candidate` issue titled `PHPStan Level N: baseline shrink — <group>`; it flows
through the existing scan→implement→learn reconciliation like any other candidate (merged/closed/
resumed), no special-casing needed there. Before filing a new one, `refactor-design` checks for an
already-open issue for the same group and resumes it (re-reading the baseline fresh — if a prior MR
already emptied it, close and pick a different group instead). This mirrors how a structural
candidate's own issue is what gets resumed until its scope is done.

**Reduction suffices per MR, the group stays the active target until it's empty.** Not "one group per
MR" — a large group can take several MRs, each landing whatever slice of the fix is ready, one commit
per file fixed (or otherwise-distinct reduction) even within a single MR, for a clean audit trail.
Matches `refactor-implement` step 5's own pre-existing "a node needing more than one MR to fulfil"
language (which already anticipated exactly this case, just never had anything to attach it to).

**No red → green TDD cycle** — a baseline-shrink fix satisfies a static-analysis finding without
introducing new behavior, so there's no new seam to test at; the existing full test suite (already run
per structural-candidate convention) is what catches an unintended behavior change instead.

**PHPStan-only for now.** Psalm has its own, structurally different suppression mechanism
(`errorLevel`/`<issueHandlers>`, not a per-file baseline); generalizing to it is a separate future
ticket, same smallest-viable-slice pattern as every other ticket this batch.

**`roadmap()`'s existing (already-present, half-finished) phpstan-level empty-baseline simulation
code cleaned up** to a single clear comment — it was never live-authoritative (`refactor-scan`
explicitly reads `next_candidates()`'s `next`, never `roadmap`), so no behavior change, just removing
a confusing dead `pass` and several exploratory comments that no longer reflect the shipped design.

## Consequences

Closes a real stagnation trap: a legacy codebase that adopts PHPStan at all previously had no path
past whatever level its baseline first landed at. No `tooling_tree.py` candidate-shape change, no new
`CONTEXT.md` vocabulary — the mechanism lives entirely in skill prose plus one new reference file,
consistent with treating this as ordinary judgment-driven design work (like a structural candidate)
rather than another deterministic tree node. `refactor-scan`, `refactor-design`, and
`refactor-implement`'s `SKILL.md` files each gain a small, clearly-delimited new case; existing
candidates and every other node's behavior is unchanged.
