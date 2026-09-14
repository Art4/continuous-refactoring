# `refactor-learn` requires a genuine event before it writes anything

Both of `refactor-learn`'s calls could previously run with nothing real to act on: the early call
only fires when `refactor-scan` reports findings (already guarded by the orchestrator), but the
closing call runs unconditionally every pass, even when neither a candidate was delivered nor
`refactor-design` raised a breaking-change finding — and its own `## Process` still told it to write
the Refactoring Notes' `bookkeeping.md`'s `Fulfilled nodes` field "unconditionally, last" regardless.
Concretely, a pass that stops because two suite MRs are already open (`refactor-prioritize` step 1)
still reached this point and opened a bookkeeping MR whose only content was a cache refresh — and a
human invoking `/refactor-learn` directly, bypassing the orchestrator entirely, had no defined
behaviour at all for "nothing to react to". Settled via a `/grill-with-docs` session
(`.scratch/refactor-learn-precondition/issues/01-refactor-learn-precondition-and-design-trail.md`).

## Considered Options

- **Add a matching proactive skip to the orchestrator's own closing-call step**, symmetric to the
  early call's existing "no findings → skip this call entirely" (`continuous-refactoring/SKILL.md`
  step 2). Rejected — it would mean two places (the orchestrator and `refactor-learn` itself) both
  need to know what counts as "nothing to react to" for the closing call, and only `refactor-learn`
  is guarded against a human calling it directly outside the orchestrator anyway. A duplicate check in
  the orchestrator buys nothing the skill-level check doesn't already cover.
- **Symmetrize by removing the orchestrator's existing early-call skip too**, so the orchestrator
  never pre-filters and always defers to `refactor-learn` itself for both calls. Rejected as
  out-of-scope for this decision — that skip already works, predates this change, and wasn't part of
  what was actually broken; touching it here would be scope creep beyond the batch this ticket set out
  to fix.

## Decision

`refactor-learn` gains a single precondition, checked at the top of each call: the early call
requires at least one finding from `refactor-scan`; the closing call requires either a freshly opened
merge request from `refactor-implement` or a design-time breaking-change finding from
`refactor-design`. Absent that, the call stops immediately — no branch opens, no write happens
(ledger, ADR, `CONTEXT.md`, `Fulfilled nodes`, labels, `out-of-scope/` all included) — and it reports
"nothing to do".

`Fulfilled nodes` specifically loses its "unconditionally, last" framing: it's still written last,
but only as part of a branch a genuine delivery or rejection this same call already justifies —
never as the sole reason to open one. This matters in practice mainly for the manual/LLM tree-walk
fallback, the only consumer that ever reads this cache (`refactoring-bookkeeping.md`); the
deterministic parser re-derives fulfilment from the filesystem every pass regardless and never reads
it at all, so delaying a refresh until the next genuine event costs that path nothing.

The orchestrator itself is untouched: it keeps calling the closing call unconditionally every pass
(`refactor-learn` now short-circuits internally instead), and its own existing early-call skip stays
exactly as it is.

## Consequences

- `refactor-learn/SKILL.md` gains an explicit precondition at the top of both the Early call and the
  Closing call sections, and its Completion criterion is reworded to name "stopped, nothing to do" as
  a valid, complete outcome for both calls — not only a fallback described for the early call.
- `refactor-learn/references/fulfilled-nodes-write.md` and
  `continuous-refactoring/references/refactoring-bookkeeping.md` (the `Fulfilled nodes` field's own
  "Write" description, both prose and the Fields table) drop "unconditionally"/"every closing call" in
  favour of "only when the closing call has something to record".
- `continuous-refactoring/SKILL.md`'s own Completion criterion, which previously stated flatly that
  "`Fulfilled nodes` is written" for every complete pass, is corrected to make that conditional on the
  closing call actually having a genuine event — otherwise it was describing behaviour this ADR just
  removed.
- No change to `continuous-refactoring/SKILL.md` steps 2 or 6 themselves, and no change to the
  fold-in exceptions (native-tracker in-flight, `loop-config`-in-flight) — both already ride a branch
  a real change already justifies, so neither was ever the standalone-cache-MR case this fixes.
