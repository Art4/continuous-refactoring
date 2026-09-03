# Drop the `refactor:delivered` label — reconcile via the tracker's native PR linkage instead

> Amends [ADR-0009](0009-merge-request-outlook-and-delivered-label.md): its actual reasoning
> stands unchanged — the in-flight state must never reuse `ready-for-human` (that label already
> means something else under `triage`). What changes is the mechanism: no dedicated label at all,
> native cross-referencing instead.
>
> Amends [ADR-0012](0012-remembered-merge-requests-follow-the-tracker.md): its
> tracker-representability split stands — a native-label tracker still needs no committed ledger.
> "The remembered set is every issue labeled `refactor:delivered`" becomes "the remembered set is
> every open `refactor:candidate` issue, resolved to its linked pull request." The local-tracker
> path (`merge-requests.md`) is untouched by this decision.

`refactor:delivered` existed only to give the in-flight state ("a merge request is open, review
pending") its own label, since `ready-for-human` already meant something else. `refactor-implement`
step 5 already requires `Closes #<candidate-issue-number>` on a delivering MR — GitHub/GitLab
already track that cross-reference natively (an issue's linked/closing pull request), so the
label was never load-bearing; it duplicated a fact the tracker already recorded elsewhere.

A live run (`docs/playbooks/reviewer-loop.md`, watching an autonomous pass of this suite against a
real target) hit the duplication's actual cost twice: an issue carrying both `refactor:candidate`
and `refactor:delivered` simultaneously after its merge request had already merged — the label
never got cleaned up, because nothing forces the two facts (issue state, label state) to stay in
sync the way a live tracker query does.

## Decision

Drop `refactor:delivered`. The native-tracker remembered set (`refactor-scan` step 3,
`refactor-prioritize`'s two-open-MR gate) becomes: every open `refactor:candidate` issue, each
resolved to its linked pull request via the tracker's own cross-reference. `refactor-learn`'s
closing call no longer labels anything — the `Closes #<n>` `refactor-implement` already wrote *is*
the record. The early-call "merged → close the issue" step is unchanged; closing the issue is what
removes it from the open-`refactor:candidate` set, same as it always removed it from the label
filter.

## Considered Options

- **Keep the label, add a cleanup step that re-syncs it against actual MR state every pass.**
  Rejected — treats the symptom (staleness) rather than the cause (a second copy of a fact the
  tracker already has); a cleanup step is one more thing to forget or get wrong.
- **Broaden `refactor:delivered`'s meaning, or rename it, to make the drift less confusing.**
  Rejected — doesn't remove the duplication, just relabels it.

## Consequences

`gh label create refactor:delivered` (or GitLab equivalent) is no longer part of any target's
setup — `refactor:candidate` is the only suite-specific label a native-label tracker needs.
`docs/refactoring/merge-requests.md`'s `Node` column (ADR-0009) is unaffected — still used on a
local tracker exactly as before. Every skill/reference that named the remembered set as "every
issue labeled `refactor:delivered`" now reads it as "every open `refactor:candidate` issue with a
linked pull request" instead — `refactor-scan`, `refactor-prioritize`, `refactor-learn`, the
orchestrator, and `loop-config-interview.md`'s `## Record` step (which documents the tracker's
native labels to the human).
