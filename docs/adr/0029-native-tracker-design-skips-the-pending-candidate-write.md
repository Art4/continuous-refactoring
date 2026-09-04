# On a native-label tracker, `refactor-design` skips writing `Pending candidates`

> Amends [ADR-0011](0011-bookkeeping-goes-through-its-own-merge-request.md): its core discipline —
> bookkeeping writes always go out through a review — is unaffected for every write this ADR
> doesn't name. What narrows is one specific write: on a native-label tracker,
> `refactor-design` no longer writes `Pending candidates` to `bookkeeping.md` at all when it files
> a candidate issue — not via a direct commit, not via a dedicated bookkeeping branch either.
>
> Sibling to [ADR-0028](0028-native-tracker-in-flight-bookkeeping-rides-the-candidate-branch.md):
> both rest on the same resolving observation (ADR-0012/ADR-0026 — a native tracker answers "is
> this candidate in flight" live, not from a committed file) applied to a different write. ADR-0028
> narrowed *where* `refactor-learn`'s closing-call writes land; this ADR removes a write of
> `refactor-design`'s own entirely, for the same underlying reason.

A live reviewer-loop run surfaced this directly: `refactor-design` filed issue #108 ("Tooling tree:
Rector: Code Quality Set"), then opened its own dedicated bookkeeping merge request (PR #109,
`docs(refactor): bookkeeping — set pending candidate Rector: Code Quality Set (#108)`) purely to
set `Pending candidates` to that same issue — no code change alongside it, `refactor-implement`
hadn't run yet this pass. The human reviewing it found this circular: a merge request whose entire
content refers to nothing but the issue this same pass just filed, landing before there is anything
to implement. Unlike the incident behind ADR-0028 (two merge requests reviewing the same delivered
work), this wasn't wasteful in the same way — but it's a merge request that documents an *intention*
rather than a *change*, purely so a future pass can resume if this one dies before `refactor-implement`
runs.

`Pending candidates`'s stated purpose (`refactoring-bookkeeping.md`) is exactly that: a resume
marker for a pass interrupted between design and implement. On a native-label tracker, though, this
protection is only needed for a narrower window than the field currently covers, and for most of
that window something else already provides it:

- **The pass reaches `refactor-implement` and it opens a branch/merge request** (the common case) →
  `refactor-scan` step 3's native-tracker reconciliation already discovers that open merge request
  directly, via the tracker itself — independent of `bookkeeping.md` — and hands it forward as a
  resume-candidate straight to `refactor-implement`. `Pending candidates` was never load-bearing for
  this case to begin with; ADR-0028 already established this for the *closing call*'s writes, and
  the same fact holds here too.
- **The pass dies before `refactor-implement` ever runs** (design ran, filed the issue, then
  stopped) → this is the one case `Pending candidates` was actually protecting. Without it, a
  future `refactor-scan`'s step 2 finds nothing pending and falls through; step 3b (externally-labeled
  candidates) then rediscovers the very same issue — still open, still labeled `refactor:candidate`,
  still carrying its full filed plan — and hands it forward as an ordinary proposal.
  `refactor-design`'s own step 5 dedupe ("an issue titled exactly `Tooling tree: <Name>` is already
  open — that's the issue, don't file a second one") already prevents refiling it. Nothing is lost
  or duplicated; the only real cost is that `refactor-prioritize` re-ranks it against whatever else
  is proposable that pass, instead of resuming it unconditionally as the one pending item.

## Considered Options

- **Keep writing `Pending candidates` via its own dedicated bookkeeping branch, always** (status
  quo). Rejected — on a native tracker this branch's entire reason to exist is protecting a crash
  window that, in the far more common "the pass reaches implement" case, was never actually load-bearing
  (step 3's reconciliation already covers it); the merge request it produces reviews nothing but an
  intention.
- **Move the write onto `refactor-implement`'s own branch instead of dropping it** (bundle it with
  the candidate branch once one exists). Rejected — by the time `refactor-implement` has a branch
  open, step 3's reconciliation already makes the write redundant (see above); writing then
  immediately clearing it again in the same still-unmerged branch (via `refactor-learn`'s closing
  call, ADR-0028) accomplishes nothing a bare skip doesn't. It would also reintroduce a subtler
  risk: if a human merges that branch directly without the closing call ever having run, `Pending
  candidates` would read "this issue" on `main` even though the candidate just delivered.
- **Drop the write only for tooling-tree nodes, keep it for structural candidates.** Rejected —
  no principled difference: both are equally rediscoverable via step 3b once filed, and splitting
  the rule by candidate type adds a distinction with no corresponding difference in what protects
  the crash window.

## Decision

`refactor-design` step 5: native-label tracker (`docs/agents/issue-tracker.md` names GitHub or
GitLab) → **skip the `Pending candidates` write entirely**, for both tooling-tree and structural
candidates. Non-native tracker (or none) → unchanged from ADR-0011: still write it via the
dedicated bookkeeping branch — that tracker has no live, file-independent way to discover an
in-flight candidate, so the original protection stays fully load-bearing there. The `loop-config`
exception (the file doesn't exist yet at all) is untouched either way — it's decided before the
tracker choice is even known.

## Consequences

One fewer merge request per ordinary candidate on a native-label tracker: `refactor-design` files
the issue and hands it straight to `refactor-implement`, nothing else to review in between.
`refactor-scan`'s step 2 ("resume pending work") will simply find nothing pending most of the time
on a native tracker now — expected, not a bug; step 3/3b's native-tracker reconciliation is what
carries the load instead. A pass that dies between design and implement resumes one step later and
one ranking round later than before (step 3b re-proposes rather than step 2 resuming
unconditionally) — accepted, since nothing is silently lost, only slower to resurface, and this
was the specific, disclosed cost of the decision. Non-native trackers are entirely unaffected.

This ADR is maintainer-facing paper trail only — no skill cites it by number, matching ADR-0011 and
ADR-0028; the rule itself is stated inline, in plain prose, in `refactor-design/SKILL.md`.
