# Recommended edges gate on decision, not just fulfilment

> Revises [ADR-0007](0007-required-recommended-edges.md). That ADR's "a recommended edge advises: the child stays proposable even when its recommended parent was rejected" said what happens once a recommended parent is *rejected* — that part is unchanged and restated below — but said nothing about the parent sitting *undecided* (neither fulfilled nor rejected), which in practice meant a recommended edge never withheld its child at all: the child was proposable from the moment its own required parents were satisfied, recommended or not. This ADR closes that gap.

A real reviewer-loop observation run surfaced Rector's dead-code suite (`rector-dead-code`) introduced while `php-cs-fixer` had never even been proposed yet — not a `required`-edge violation (its only required parent, `phpstan-level-0-baseline`, was fulfilled), but a direct contradiction of `php-cs-fixer`'s own documented purpose: automated style so later Rector output lands styled. `refactor-prioritize`'s Skip-streak factor (a separate fix, for `required` tooling siblings that never win on their own ranking merits) incidentally reduces how often this specific instance occurs, since `php-cs-fixer` is itself a `required` child of `composer` — but it doesn't eliminate the underlying gap: a target that rejects `php-cs-fixer` outright as out-of-scope would still hit it, since Skip-streak has nothing left to boost once a node is rejected rather than merely neglected.

## The rule

A node with one or more `recommended` parents is proposed only once **every** one of those parents has reached a **decided** state:

- **Fulfilled** — releases the child, same as a required parent would.
- **Rejected** — releases the child too (unlike a required parent, which instead cascades the rejection and closes the child permanently). A parent counts as rejected either directly (its own out-of-scope entry) or transitively, when one of *its* required ancestors is itself decided-rejected — the same closure a required edge already causes for proposability, just made explicit here because a recommended edge needs to tell "permanently rejected" apart from "not reached yet."
- **Anything else — including not yet reached at all** (still blocked by its own required edges) — leaves the child withheld. A recommended parent several required-edge hops away (e.g. `phpstan-level-3`, reachable only after levels 1 and 2) withholds its child for exactly as long as it takes to get there and be decided, not just for the one pass in which both happen to be proposable simultaneously.

A node with two or more recommended parents (e.g. `rector-type-coverage`: `php-cs-fixer` and `phpstan-level-3`) waits on **all** of them independently — one being decided doesn't release the child while another sits undecided.

## Considered Options

- **A ranking-weight nudge in `refactor-prioritize`**, biasing the ranking toward a recommended parent whenever it and the child are simultaneously proposable. Rejected: a child that can genuinely never be chosen while its recommended parent remains undecided isn't a matter of ranking it lower — it isn't eligible for choice at all, and a candidate list is the wrong place to carry an unconditional veto.
- **An outlook-note-only response** — extend the existing rejected-parent outlook mechanism to the undecided case too, without changing proposability at all. Rejected: this only explains the outcome (unstyled Rector output) after the fact, in whichever other candidate's merge request happens to get chosen instead; it doesn't prevent it, which is what the triggering observation actually called for.
- **A full decided-gate in `refactor-scan`, structurally identical to a required edge except for what a rejection does to the child.** Accepted — see *The rule* above.

## Consequences

- `refactor-prioritize` gains no new ranking factor. The gate lives entirely in `refactor-scan`'s candidate computation (the deterministic parser and its manual tree-walk fallback), the same layer that already enforces required-edge gating — a withheld node is excluded from the proposal set outright, not merely deprioritized within it.
- A withheld node is named explicitly in `refactor-scan`'s output, together with which parent(s) it's still waiting on. It never gets a merge request of its own this pass, so there's nowhere else for that explanation to live — silently shrinking the proposal set would look like a scan gap, not a pending decision.
- More than five nodes can be genuinely unblocked at once even without this rule (`composer`'s required children alongside `phpstan-level-1` already reach six on a fresh target), so `refactor-scan`'s five-node proposal cap is lifted entirely as part of the same change. The uncapped set is never truncated; `roadmap()`'s own forward-simulation depth is a separate, already-bounded concept and is unaffected.
- `roadmap()`'s existing forward-simulated treatment of recommended parents (an outlook note, not a gate) is deliberately left as-is — it's a speculative lookahead already documented as distinct from the real `next` set, and retrofitting its simulation to this rule is a separate concern from this ADR.
- This is a rule change to `recommended` edges generically, not to the PHP tree specifically — it currently only has visible effect there, since no other specialization tree declares a `recommended` edge yet.
- [ADR-0010](0010-orchestrator-explicit-data-flow.md)'s "`refactor-scan` proposes up to five tree nodes" describes the cap this ADR lifts. Left as-is, unedited — it's a historical record of that ADR's own decision (explicit data flow between lifecycle skills), not a live count; the count itself now lives, uncapped, in `CONTEXT.md` and `refactor-scan/SKILL.md`.

This ADR is maintainer-facing paper trail only — no skill cites it by number, per the suite's own convention; the rule itself is stated inline, in plain prose, in `CONTEXT.md`, `php-tooling-tree.md`, and `refactor-scan/SKILL.md`.
