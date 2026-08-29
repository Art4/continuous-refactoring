# Remembered merge requests follow the tracker when it supports labels natively

> Extends [ADR-0001](0001-backlog-in-issue-tracker.md): the same reasoning — reuse the tracker every contributor already reads, rather than duplicating it in a local file — now also covers which suite merge requests are currently in flight, not just the backlog.
>
> Amends [ADR-0011](0011-bookkeeping-goes-through-its-own-merge-request.md): its bookkeeping-branch/MR discipline no longer applies to `docs/refactoring/merge-requests.md` when the target's issue tracker natively supports labels — there is nothing to commit. It still governs `config.md`, ADRs, `CONTEXT.md`, and `merge-requests.md` itself when the target has no such tracker.
>
> Amends [ADR-0010](0010-orchestrator-explicit-data-flow.md): `refactor-learn` is no longer the unconditional writer of `merge-requests.md` — only in the fallback case below.

Reviewing ADR-0011's design surfaced a cheaper alternative for one specific write. Folding a candidate's "merge request opened" note into that candidate's own (not yet merged) branch — instead of a separate bookkeeping merge request — is appealing: it avoids opening a second merge request just to restate three facts about the first one. But ADR-0011 already rejected exactly this for a load-bearing reason: `refactor-prioritize`'s "two suite merge requests already open?" cap and `refactor-scan`'s reconciliation both read `docs/refactoring/merge-requests.md` from the default branch. A note trapped on the candidate's own unmerged branch is invisible there until that branch merges — undercounting the cap and blinding reconciliation for the entire review window, the cross-pass version of the same-pass staleness bug ADR-0010 already fixed by splitting `refactor-learn` into an early and closing call.

The resolving observation: many target repos already run an issue tracker (GitHub, GitLab) whose labels are visible the moment they're applied, independent of any git commit. `refactor-learn`'s closing call already applies `refactor:delivered` to the candidate issue when its merge request opens — that label change is itself exactly the kind of immediately-visible, non-git-commit update the ledger file was trying to approximate with a commit. Once a native label mechanism exists, nothing needs to be committed at all: "is a merge request open for this candidate" is answered by "does its issue carry `refactor:delivered`," checked live.

This is not universal, though: this suite's own repo tracks its issues as local Markdown files under `.scratch/` (`docs/agents/issue-tracker.md`), where a "Status:" line has exactly the same git-commit-visibility constraint as the ledger file — no independent, git-free side channel exists. For a target repo configured that way (or with no tracker convention at all), the committed ledger, governed by ADR-0011's bookkeeping-branch/MR discipline, remains the only durable way to remember this state.

## Considered Options

- **Keep `docs/refactoring/merge-requests.md` as a committed file always, governed by ADR-0011, regardless of tracker.** Rejected: forces every closing call to open (or reuse) a merge request purely to restate facts (URL, base branch, node) a native-label tracker already carries live and immediately — the file becomes a synchronized duplicate of the tracker, the exact anti-pattern ADR-0001 already rejected for the backlog.
- **Fold the note onto the candidate's own (not yet merged) branch.** Rejected, per ADR-0011: reintroduces cross-pass staleness for the two-MR cap and reconciliation.
- **Derive the remembered set live from the tracker when it natively supports labels; fall back to the committed file (ADR-0011's discipline) only when it doesn't.** Accepted.

## Consequences

Two modes for "which suite merge requests are open":

- **Tracker-native** (the target's issue tracker has real labels — GitHub, GitLab): the remembered set is every issue labeled `refactor:delivered`. Each carries what the ledger used to hold — its merge request (URL, base branch, read from the merge request itself) and, from the issue's own title (`Tooling tree: <node>`, per `refactor-design`'s filing convention), the tooling-tree node, blank when the title doesn't match that pattern (a structural candidate). `refactor-learn` writes nothing to a file for this; the label operation it already performs *is* the write, so no bookkeeping branch/MR is needed for it.
- **Fallback** (no native label mechanism — e.g. this repo's own local-Markdown `.scratch/` convention, or no tracker at all): unchanged from ADR-0011 — `docs/refactoring/merge-requests.md` is a committed ledger, written via `refactor-learn`'s dedicated bookkeeping branch/MR.

`docs/refactoring/config.md` (`Create-mode`, `Focus areas`, `Pending issue`, `Fulfilled nodes`), ADRs, and `CONTEXT.md` are unaffected by either mode — none of that data is tracker-representable, and it remains committed, governed by ADR-0011, regardless of which mode applies to `merge-requests.md`.

As with ADR-0011, this ADR is maintainer-facing paper trail only — no skill cites it by number; the rule is stated inline, in plain prose, in the affected skills.
