# Candidate MRs open as draft until the fold-in bookkeeping lands

> Amends [ADR-0028](0028-native-tracker-in-flight-bookkeeping-rides-the-candidate-branch.md): its
> mechanism — the closing call's in-flight writes ride the candidate's own already-open merge
> request on a native-label tracker — is unchanged. What's added is a visible signal for it:
> `refactor-implement` opens that same merge request as a **draft**, and `refactor-learn` marks it
> ready for review once the fold-in commit actually lands. A second addition, for the case ADR-0028
> didn't need to consider — a pass interrupted between the two — gives `refactor-scan` a new
> reconciliation finding so that case resolves itself on a later pass rather than sitting silently
> incomplete forever.
>
> Builds on the same live-tracker-query reasoning as ADR-0028/[ADR-0012](0012-remembered-merge-requests-follow-the-tracker.md):
> a candidate's draft status is answerable live, the same way "is a merge request open for this
> candidate" already is — nothing new needs committing to `bookkeeping.md` to track it.

A live reviewer-loop run caught a candidate merge request mid-pass: the implementation commit was
already pushed, CI was pending, but the fold-in bookkeeping commit ADR-0028 describes hadn't landed
yet. The reviewer had to notice this by inspecting the commit count and wait a few minutes before
reviewing — the right call, but one that required inference rather than being read off the merge
request's own state. Draft status makes the same fact mechanical: a reviewer (human or automated)
sees "draft" and knows not to look yet, no inference required; the transition to "ready for review"
becomes the actual, unambiguous signal that a candidate's full cycle — implementation and
bookkeeping both — has landed.

This raises a case ADR-0028 never had to resolve, because at the time nothing made an in-flight
candidate's incompleteness visible: what if the pass dies *between* `refactor-implement` opening the
draft merge request and `refactor-learn`'s closing call landing the fold-in commit? Without a fix,
that merge request would sit open, in draft, forever — `refactor-scan` step 3's existing
reconciliation only escalates a still-open merge request to a resume-candidate when a reviewer has
actually commented on it, which nobody will, precisely because it correctly reads as "not ready
yet." Draft status is itself the exact, unambiguous signal that the fold-in is still owed — no
commit-counting or timestamp comparison needed to detect it.

## Considered Options

- **Draft status only, no reconciliation change.** Rejected — this is the case above: a crashed pass
  leaves a permanently-invisible incomplete candidate, worse than before the draft convention
  existed (a non-draft open MR with no activity was at least equally invisible, but nothing
  previously depended on that state resolving itself either; adding draft without also adding its
  resolution path trades one silent steady state for another).
- **Reuse the existing `CHANGES_REQUESTED`/reviewer-activity resume-candidate path for this too**
  (treat "still draft" as if it were reviewer feedback). Rejected — conflates two different signals:
  reviewer activity means a human wants something *changed*; a stuck draft means the *suite itself*
  never finished a step it owns. Handing a stuck draft to `refactor-implement` (the reviewer-activity
  path's destination) would be wrong regardless — there is no code to fix, only bookkeeping to
  finish, which is `refactor-learn`'s job under the suite's single-writer rule.
- **Check reviewer activity and draft status in either order, first match wins.** Considered
  reviewer-activity-first specifically (not draft-first): a human can comment on a draft too, and
  that comment should still win — a stuck draft with no activity is the *only* case that should
  fall through to the new fold-in-owed finding. Draft-first would have let a genuine review comment
  on a draft go unnoticed, mishandled as routine fold-in completion instead.

## Decision

`refactor-implement` step 5: `refactor-learn`'s native-tracker in-flight fold-in exception applies
to this candidate → open the merge request as a **draft** (`gh pr create --draft` / `glab mr create
--draft`). Every other case → open it normally, unchanged.

`refactor-scan` step 3's reconciliation, for a still-open merge request: check reviewer activity
first, exactly as before, regardless of draft status — a comment or review always wins. Only once
that comes back empty does draft status get checked: still marked draft → a new finding, **fold-in
still owed**, handed to `refactor-learn`. Not draft (or draft status unreadable, e.g. the git-only
fallback) → no finding, as before.

`refactor-learn`'s early call gets a new case for this finding: check out the candidate's own branch
(the fold-in exception, not the dedicated bookkeeping branch — the branch already exists, still
open, from the interrupted pass), perform the exact same fold-in writes the closing call would
(`Fulfilled nodes`/`Skip streak`/ADR/`CONTEXT.md`), then mark the merge request ready for review.
The closing call's own write list gains the matching "mark ready" step, last of all, covering both
origins (opened as draft this same pass, or resumed via this new finding) with one instruction.

## Consequences

A candidate merge request's draft/ready transition becomes the durable, at-a-glance signal that its
full cycle is complete — no more inferring it from commit counts. A pass that dies between implement
and the fold-in no longer leaves a permanently-silent incomplete candidate: a later pass's
`refactor-scan` discovers and finishes it via the new finding, the same way it already discovers a
merged or closed candidate. `docs/playbooks/reviewer-loop.md` gains a rule for the human/automated
reviewer: skip a draft MR without treating it as a hang, escalate only if it stays draft across
several rounds with no new commits (the suite's own stuck-fold-in case, not a hang the suite already
resolves on its own the moment a later pass runs). `CONTEXT.md`'s **Findings** definition broadens
to include this new outcome — it is neither "merged" nor "closed," the only two outcomes it
previously named.

This ADR is maintainer-facing paper trail only — no skill cites it by number, matching ADR-0011,
ADR-0028, and ADR-0029; the rule itself is stated inline, in plain prose, in `refactor-implement/SKILL.md`,
`refactor-scan/SKILL.md`, `refactor-learn/SKILL.md`, and `opening-a-merge-request.md`.
