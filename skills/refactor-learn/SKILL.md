---
name: refactor-learn
description: The suite's only writer of bookkeeping — acts on refactor-scan's reconciliation findings and refactor-implement's freshly opened merge request, records the ledger, ADRs, CONTEXT.md, and the last-run stamp.
---

# Refactor Learn

The only skill in the suite that writes suite bookkeeping: `docs/refactoring/merge-requests.md` (only when the target's issue tracker has no native label mechanism — otherwise this data lives on the tracker instead, see `## Process`), `docs/refactoring/out-of-scope/`, ADRs, `CONTEXT.md`, `docs/refactoring/config.md`, and issue labels. Every other lifecycle skill may read these directly; only this one writes them.

The orchestrator calls this skill up to **twice** in one pass, never more: an **early call**, right after `refactor-scan`, only when it produced findings; and a **closing call**, always, at the very end. The split exists because `refactor-prioritize` reads the ledger to decide whether two merge requests are already open — a finding this pass just resolved has to be written back before that check runs, not deferred to the end where it would be too late to matter this pass.

**Land every write below by opening (or reusing) a dedicated bookkeeping branch/MR off the default branch — never a direct commit.** Before writing anything, in either call: confirm you aren't still on the candidate branch `refactor-implement` left checked out — these bookkeeping writes are not part of that review. Pull the default branch's latest, then create (or reuse, if one from an earlier interrupted pass is still open) a small dedicated bookkeeping branch off it, commit the writes below there, and open (or update) that merge request, using the same create-mode policy as the orchestrator's `## Opening a merge request` section. The one exception is the `loop-config`-in-flight case below, where the file being written doesn't exist anywhere except the `loop-config` candidate's own branch yet — that write rides the candidate's own already-open, already-reviewed merge request instead.

**Finding the bookkeeping branch — deterministic, no memory required, never search for a name.** Bookkeeping branches are always named `refactor-learn/bookkeeping-N`, N starting at 1, numbers never reused even once a branch is merged or deleted.

1. `git symbolic-ref refs/remotes/origin/HEAD` (or equivalent) to name the default branch, then `git ls-remote --heads origin 'refactor-learn/bookkeeping-*'` to list every bookkeeping branch that exists remotely. None found → this pass starts fresh at N=1 (step 4).
2. Otherwise take the highest N found. `git merge-base --is-ancestor origin/refactor-learn/bookkeeping-N origin/<default-branch>` exits `0` → already merged, not reusable → go to step 4 with `N+1`.
3. Not an ancestor (still open, unmerged) → **reuse it**: `git fetch origin refactor-learn/bookkeeping-N && git checkout -B refactor-learn/bookkeeping-N origin/refactor-learn/bookkeeping-N`. Skip step 4.
4. Pull the default branch's latest, then `git checkout -B refactor-learn/bookkeeping-<N+1> origin/<default-branch>` (N=1 the first time this convention is ever used against a target).

Never invent a different name, and never `find`/`grep` or browse history/forge PRs to locate "the last bookkeeping branch" — the listing above is authoritative and cheap for a fresh subagent with no memory of earlier passes.

**Never let deleting a branch be the only record that something happened.** Rejecting a candidate mid-flight with no forge API access to formally close its merge request is not a license to delete the branch as "the practical equivalent" of closing it — a bookkeeping write not yet on the default branch (a ledger row, a `Fulfilled nodes` entry, an out-of-scope entry) that exists only on a branch about to be deleted is destroyed along with it, taking the only record that a real merge request ever existed with it. Before deleting or abandoning any such branch — the candidate's own, or a bookkeeping branch stacked on it per the orchestrator's `## Opening a merge request` always-stack rule — land the record of the abandonment first, through an ordinary bookkeeping branch/MR **off the default branch, never one stacked on the branch about to be deleted**: at minimum a `docs/refactoring/out-of-scope/<node>.md` entry (a structural candidate: a closing note on the issue instead) stating what was abandoned and why. If a bookkeeping write already sits stacked on the doomed candidate branch (this pass's early call, or an interrupted earlier one), cherry-pick that commit onto a fresh branch off the default branch before deleting anything beneath it. Only delete the branch(es) after that record has merged. No time to complete the merge right now? Leave the branch undeleted — a stale unmerged branch costs nothing; a silently vanished merge request does.

## Process

### Early call — findings only (from `refactor-scan`, if any)

Runs only when scan produced findings; skip everything below when it didn't — the closing call still happens regardless, at the end. These are bookkeeping writes too — the rule above applies: land them via the dedicated bookkeeping branch/MR (open or reuse one), never a direct commit.

For each finding:

- Merged → mark the candidate `done` and close the issue.
- Closed without merge → if the closing comments support a structural rejection (a maintainer gave a load-bearing reason), mark the candidate `wontfix`, close the issue, and file a learned rejection under `docs/refactoring/out-of-scope/`; otherwise ask the human what to do before deciding. If the load-bearing reason is a minimum PHP version the target doesn't meet, also record it machine-parseably — a `**Blocked by:** PHP >= X.Y` line — so a later pass can detect the reversal automatically (`tooling_tree.py`'s `detect_nodes()`) instead of needing a human to notice.
- If merge requests are tracked in `docs/refactoring/merge-requests.md` (the target's issue tracker has no native label mechanism), drop the entry either way once resolved. When the tracker natively supports labels, closing/labeling the issue already removes it from the `refactor:delivered` set — nothing further to do.
- **PHP-version reversal** (`refactor-scan` step 3 also reports these) → an existing `docs/refactoring/out-of-scope/<node>.md` names a `**Blocked by:** PHP >= X.Y` condition the target now satisfies. Remove that file — the rejection is reversed, the node is proposable again on its own merits, starting from scratch (it is *not* thereby fulfilled). Never do this for a rejection with no `Blocked by:` field, or one that scan didn't report as satisfied — those stay rejected until a human (or an agent with a stated reason) removes them by hand; `refactor-scan` only ever detects and reports this, never removes the file itself.

`done` and `wontfix` are the shared triage-role labels (`docs/agents/triage-labels.md`), not suite-specific ones — closing the issue is what actually takes it out of the backlog; which labels stay attached alongside `done`/`wontfix` doesn't matter for that.

A pass that only makes this call (no fresh candidate reached this run) is still a complete pass — bookkeeping-only completion is valid.

### Closing call — always, at the end of the pass

Given a freshly opened merge request (from `refactor-implement`, if the pass got that far):

- When the target's issue tracker natively supports labels (GitHub, GitLab): nothing to remember here — the `refactor:delivered` label below, plus the merge request's own link back to this issue, already carries it. Otherwise, remember it in `docs/refactoring/merge-requests.md`: URL, candidate issue, the tooling-tree node name (blank for a structural candidate), and base branch — one of the writes the bookkeeping-branch/MR rule above governs.
- Clear `docs/refactoring/config.md`'s `Pending candidates` field — this candidate now has a merge request, so the marker that would let `refactor-scan` resume it as unfinished work no longer applies.
- Label the candidate `refactor:delivered` — never `done` (the merge request isn't merged yet — that's the *next* pass's early call, once it merges) and never `ready-for-human` (that label means "nobody has implemented this yet," the opposite of what just happened).
- If `docs/refactoring/config.md`'s `Create-mode` wasn't set before this pass, record what `refactor-implement` used (`autonomous`, `ask-each-time`, or `human-opens` — per the orchestrator's `## Opening a merge request` guidance).

**`loop-config`-in-flight exception — `config.md` doesn't exist on the default branch yet:** true only before the `loop-config` candidate itself has merged. There's nowhere on the default branch — or on a fresh bookkeeping branch off it — to clear `Pending candidates` or record `Create-mode` yet, because `config.md` doesn't exist there. Write both as a follow-up commit on the `loop-config` candidate's own branch instead, riding along in that already-open, already-reviewed merge request — the one case where bookkeeping doesn't get its own separate branch/MR, per the rule above. Once the merge request merges (a later pass's early call sees it), every closing call after that opens its own dedicated bookkeeping branch/MR as usual.

Then, regardless of whether a merge request was opened this pass — using the same dedicated bookkeeping branch/MR described above (open one even when no candidate MR happened this pass; never assume the current checkout is safe to write to):

- Record an ADR (`docs/adr/`) for any decision a future scan must not re-litigate (see `/domain-modeling`).
- Update `CONTEXT.md` with any terms that crystallised this pass.
- Write `docs/refactoring/config.md`'s `Fulfilled nodes` — unconditionally, the last thing this skill does (`skills/continuous-refactoring/references/refactoring-config.md`'s own field). If this pass ran `tooling_tree.py` (the deterministic parser, `python3` available), **overwrite the whole field** with its complete current fulfilled-set — cheap, and this is what keeps the cache correct across out-of-band changes (a revert, a manual edit) whenever parser access comes back. If this pass instead ran the manual/LLM tree-walk fallback, only *add* whatever slugs that walk itself freshly confirmed fulfilled (the freshly delivered candidate's own node, plus any others the walk happened to evaluate) — never remove or "clean up" entries on a fallback pass, and never guess at nodes the walk didn't actually check this pass. Same `loop-config`-in-flight exception as above: before `loop-config` merges, this write lands on that candidate's own branch, not a separate bookkeeping branch — its first entry is `loop-config` itself.
- Alongside `Fulfilled nodes`, write `Skip streak` (same field, same write, not a separate pass over the tree): when this pass ran the deterministic parser, re-run its unblocked-node check (the same `next`-style set `refactor-scan` proposed from) and, for every `required` tooling node it names that this pass did *not* choose, increment that node's entry by 1 (starting from 1 if it had none); for the node this pass *did* choose or that just became fulfilled, drop its entry entirely rather than writing 0 (per `refactoring-config.md`'s "omit zero entries" rule). When this pass instead ran the manual/LLM tree-walk fallback, only touch entries for nodes that fallback pass itself actually walked this round — same caution as `Fulfilled nodes`, never guess at a node the walk didn't check.

## Fallback

- **`/domain-modeling`**: if installed, use its discipline for the ADR and `CONTEXT.md` side effects. Otherwise skip with a note — the ledger, label, and stamp writes are inline and suite-internal; they run regardless of whether `/domain-modeling` is installed. Crash-safe.

## Completion criterion

**Early call:** every finding this skill was given is resolved (`done`, `wontfix` + out-of-scope entry, a PHP-version reversal's `out-of-scope` file removed, or an explicit "asked the human, waiting"), the remembered set (tracker labels or the ledger, whichever applies) reflects it before `refactor-prioritize` runs, and any file writes went out through the dedicated bookkeeping merge request.

**Closing call:** a freshly delivered candidate (if any) is remembered — via the `refactor:delivered` label, or in the ledger, whichever the target's tracker calls for — with `Pending candidates` cleared and `refactor:delivered` applied, `Fulfilled nodes` and `Skip streak` are written (full re-derivation when the parser ran this pass, additive/narrow otherwise), and every file write went out through a merge request — the dedicated bookkeeping one, or the `loop-config` candidate's own — never a direct commit to the default branch.
