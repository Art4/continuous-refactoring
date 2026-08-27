# Merge-request outlook, plain-language opener, and a delivered label of its own

> Amends [ADR-0006](0006-loop-delivers-remembered-merge-requests.md): the description gains a plain-language opener and, for tooling-tree candidates, an outlook naming the next node; the in-flight label changes from `ready-for-human` to `refactor:delivered`.
>
> Amended by [ADR-0010](0010-orchestrator-explicit-data-flow.md): who applies these labels changes — `refactor-learn` writes them, not the orchestrator inline. The labels and description shape decided here are unchanged.
>
> Amended by [ADR-0011](0011-bookkeeping-goes-through-its-own-merge-request.md): bookkeeping writes no longer land as a direct commit to the default branch — they go out through their own merge request.

Testing the suite end-to-end surfaced two problems with what ADR-0006 left the merge-request description as ("plain: link the candidate, what changed, which tests survive, what CI proves. No outlook, no type enum.") and with reusing `ready-for-human` for "a merge request is open, awaiting review."

First, "plain" turned out to mean *terse and suite-internal*, not *readable*. A description that opens "Fulfils #8 — the `loop-config` node of the continuous-refactoring suite's tooling tree" assumes the reader already knows what a tooling tree is. A human reviewing the diff wants to know what it does for the project before the suite's own bookkeeping vocabulary. Ticket 19 had already flagged the missing half of this — an outlook naming what the candidate unlocks — as an open question ("do not treat 'outlook Pflicht, kein Enum' as already decided"), deferred from ADR-0006's own "no outlook" line and from ADR-0005's "the MR outlook names the child" claim, which nothing had implemented yet.

Second, ADR-0006 assigns `ready-for-human` to "while a merge request is open, the candidate is `ready-for-human`." That label already has a meaning from the `triage` skill (`docs/agents/triage-labels.md`): "requires human implementation" — nobody has written this yet. The suite's reuse means the opposite state — an agent already implemented it, a human just needs to review and merge — under the identical label. A repo running both `triage` and this suite can't tell the two states apart from the label alone.

This ADR resolves the outlook half of ticket 19 (the type-enum half stays open — not decided here, no reason to decide it just because outlook did) and gives the in-flight state its own label.

## Considered Options

- **Leave outlook out, per ADR-0006.** Rejected: ticket 19 flagged it as unresolved, not settled, and a reviewer with no outlook has no sense of what merging unlocks — exactly what ADR-0005 assumed would exist ("the MR outlook names the child").
- **Outlook on every merge request, structural included.** Rejected: a tooling-tree node has one well-defined next child; a structural deepening doesn't unlock a single named next thing the same way. Forcing an outlook there would be invented, not reported.
- **Broaden `ready-for-human`'s documented meaning to cover both states instead of introducing a new label.** Rejected: the two states call for different human actions (write the implementation vs. review a diff) and a repo also running `triage` would still have one label doing two jobs — the confusion moves into the label's definition instead of away from it.
- **Decide the type-enum question here too, since outlook is unblocking it anyway.** Rejected: not asked for, adds a closed vocabulary (ticket 19's brainstormed G–J) nobody has grilled yet. Left for a future pass at ticket 19.

## Consequences

The merge-request description now opens with one or two plain-language sentences — what this unlocks for the project, no suite vocabulary assumed — before the existing plain facts (candidate link, what changed, tests, CI).

A tooling-tree candidate's description closes with an outlook: re-run `scripts/lib/tooling_tree.py` against the working tree with the candidate's change already applied, and name whatever node it reports next, quoting that node's Purpose from the tree doc in one line. A structural candidate carries no outlook.

The in-flight label is now `refactor:delivered`, created the same way `refactor:candidate` was (`gh label create` or equivalent in the target repo — not auto-created by any skill). `ready-for-human` is freed back to `triage`'s exclusive meaning. `docs/refactoring/merge-requests.md` gains a `Node` column (blank for structural candidates) so the in-flight tooling node is visible without opening the issue.

No type enum. Ticket 19 remains partially open.
