# On a native-label tracker, in-flight bookkeeping rides the candidate's own branch

> Amends [ADR-0011](0011-bookkeeping-goes-through-its-own-merge-request.md): its core discipline —
> bookkeeping writes always go out through a review, never a direct commit to the default branch —
> is unchanged. What narrows is *which* review: on a native-label tracker, the closing call's
> in-flight writes (`Pending candidates` cleared, `Skip streak` refreshed) ride the candidate's own
> already-open merge request when `refactor-implement` opened one this same pass, instead of a
> second, separate bookkeeping merge request. ADR-0011's `loop-config`-in-flight exception was
> always a special case of exactly this — narrower only because `bookkeeping.md` didn't exist
> anywhere else yet. This ADR generalizes the mechanism ADR-0011 already proved out, to every
> candidate, not just `loop-config` alone.
>
> Does not amend [ADR-0015](0015-suite-merge-requests-always-stack.md): still true that at most one
> candidate branch is open against the default branch at a time. What changes is only whether a
> *second*, bookkeeping-specific branch is still needed alongside it — not the one-candidate-branch
> rule itself.
>
> Builds on [ADR-0012](0012-remembered-merge-requests-follow-the-tracker.md) and
> [ADR-0026](0026-drop-delivered-label-use-native-pr-linkage.md): both already established that a
> native-label tracker makes "is a merge request open for this candidate" answerable live — by
> querying the tracker, not by reading a committed file — so nothing external needs `bookkeeping.md`
> to reflect that fact *before* the candidate's own merge request merges.

A human reviewing a live run of this suite against a real target (`Art4/legacy-todo`, native GitHub
tracker) asked for exactly this simplification: every "in flight" bookkeeping write observed during
that run (e.g. `docs(refactor): bookkeeping — clear pending, phpunit in flight`) opened its own
`refactor-learn/bookkeeping-N` branch and merge request, immediately alongside the candidate's own
already-open one — two merge requests to review per candidate, for information that's entirely
*about* that same candidate and travels with it regardless.

ADR-0011 already considered and rejected folding bookkeeping into the candidate's own branch — but
for a specific, load-bearing reason: at the time, the only way a later pass could tell "is a merge
request already open for this candidate" was by reading `docs/refactoring/merge-requests.md` (or,
after the rename, `bookkeeping.md`) from the default branch; a note trapped on the candidate's own
unmerged branch would be invisible there until it merged, undercounting `refactor-prioritize`'s
open-MR cap and blinding `refactor-scan`'s reconciliation for the entire review window. ADR-0012
already resolved exactly this concern for `merge-requests.md` on a native-label tracker: "is a
merge request open" becomes a live tracker query, not a file read, so nothing needs to be committed
before the candidate merges at all. ADR-0026 deepened this further — the tracker's own native
issue↔PR linkage is now the durable record of what's in flight, with no label to keep in sync
either.

`bookkeeping.md`'s own in-flight fields (`Pending candidates`, and the `Skip streak` entry for the
node just chosen) never had an independent reason to need pre-merge visibility on a native tracker
— nothing outside this same candidate's own review depends on reading them before that review
finishes. `refactor-scan` step 2 already stops and proposes exactly the pending candidate it finds,
which — even mid-review — is the same candidate the open merge request already carries; step 3's
native-tracker reconciliation independently confirms via `gh pr list`/`glab mr list` whether that
candidate already has an open merge request, regardless of what `bookkeeping.md` currently says.
There is nothing left for a separate, immediately-landing bookkeeping merge request to protect on a
native tracker — it was solving a visibility problem that native trackers no longer have.

## Considered Options

- **Keep every closing-call bookkeeping write on its own dedicated branch, always** (status quo).
  Rejected — on a native-label tracker this is now protecting against a staleness window nothing
  actually reads through; it doubles the merge-request count per candidate for no remaining
  correctness benefit.
- **Fold in-flight bookkeeping into the candidate branch on every tracker, including local-Markdown
  ones.** Rejected — ADR-0011's original concern is still fully live there: `merge-requests.md` (or
  its non-native `bookkeeping.md` fields) is the *only* record of what's in flight; trapping it on
  an unmerged branch really does blind `refactor-prioritize`'s cap and `refactor-scan`'s
  reconciliation until that branch merges. The fold-in stays native-tracker-only.
- **Also fold "record delivered" and a newly-designed `Pending candidates` entry into a branch.**
  Rejected — structurally impossible in the general case: "delivered" is only knowable *after* the
  candidate's branch has already merged (nothing to ride by then), and a freshly-designed next
  candidate is chosen independently, sometimes in a later pass entirely. These keep landing via
  their own dedicated bookkeeping branch, exactly as ADR-0011 describes — this ADR only narrows the
  in-flight, same-pass case.

## Decision

`refactor-learn`'s closing call: **native-label tracker** (`docs/agents/issue-tracker.md` names
GitHub or GitLab) **and** `refactor-implement` opened a candidate merge request this same pass →
commit the closing call's writes (`Pending candidates` cleared; `Fulfilled nodes`/`Skip streak`
refreshed) directly onto that candidate's own branch, as a follow-up commit riding its already-open
merge request — no second branch, no second merge request. Every other case is unchanged from
ADR-0011: no candidate merge request opened this pass (nothing to ride), or the tracker has no
native labels → open (or reuse) the dedicated `refactor-learn/bookkeeping-N` branch as before. The
early call (right after `refactor-scan`, when it produced findings) is never affected either way —
it runs *before* `refactor-implement`, so no candidate branch exists yet to ride.

`loop-config`'s own exception in ADR-0011 becomes the first, narrowest instance of this same rule
rather than a one-off: the file not existing anywhere but the candidate's own branch is simply the
most extreme case of "nothing external can read this from the default branch before merge yet" —
already true, more generally, of every native-tracker in-flight write this ADR now covers.

## Consequences

One fewer merge request per ordinary tooling-tree candidate on a native-label tracker: the
candidate's own merge request now carries both the implementation and its in-flight bookkeeping,
reviewed and merged together. `skills/refactor-learn/SKILL.md`'s closing-call section states the
general native-tracker rule directly, with `loop-config` named as its narrowest case rather than a
separate exception. `skills/refactor-learn/references/bookkeeping-branch.md` (the dedicated-branch
lookup algorithm) gains a note that it doesn't run at all in the fold-in case. Non-native trackers,
and any pass where no candidate branch is open to ride, are unaffected — the dedicated bookkeeping
branch/MR mechanism ADR-0011 designed still governs there, unchanged.

This ADR is maintainer-facing paper trail only — no skill cites it by number, per the suite's own
convention (matching ADR-0011 and ADR-0015, the two it sits directly beside); the rule itself is
stated inline, in plain prose, in `refactor-learn/SKILL.md` and `bookkeeping-branch.md`.
