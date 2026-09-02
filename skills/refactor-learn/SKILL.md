---
name: refactor-learn
description: The suite's only writer of bookkeeping — acts on refactor-scan's reconciliation findings and refactor-implement's freshly opened merge request, records the ledger, ADRs, CONTEXT.md, and the last-run stamp.
---

# Refactor Learn

The only skill that writes suite bookkeeping: the Refactoring Notes' `merge-requests.md` (only when `docs/agents/issue-tracker.md` names no native-label tracker — otherwise this data lives on the tracker), the Refactoring Notes' `out-of-scope/`, ADRs, `CONTEXT.md`, the Refactoring Notes' `config.md`, and issue labels. Every other lifecycle skill may read these; only this one writes them.

The orchestrator calls this skill up to **twice** a pass: an **early call**, right after `refactor-scan`, only when it produced findings; and a **closing call**, always, at the end. The split exists because `refactor-prioritize` reads the ledger to decide whether two MRs are already open — a finding this pass just resolved has to be written back before that check runs.

**Land every write below via a dedicated bookkeeping branch/MR off the default branch — never a direct commit.** Before writing, in either call: confirm you aren't still on the candidate branch `refactor-implement` left checked out — these writes aren't part of that review. Pull the default branch's latest, then create (or reuse, if one from an earlier interrupted pass is still open) a small bookkeeping branch off it, commit the writes there, and open (or update) that MR, using the create-mode policy at `skills/continuous-refactoring/references/opening-a-merge-request.md`. Exception: the `loop-config`-in-flight case below, where the file being written doesn't exist anywhere except the `loop-config` candidate's own branch yet — that write rides the candidate's own already-open, already-reviewed MR instead.

**Finding the bookkeeping branch — deterministic, no memory required, never search for a name.** Named `refactor-learn/bookkeeping-N` (N starting at 1, never reused). Algorithm: `skills/refactor-learn/references/bookkeeping-branch.md`.

**Before deleting or abandoning any branch carrying an unmerged bookkeeping write**, land that record first: `skills/refactor-learn/references/never-delete-without-record.md`.

## Process

### Early call — findings only (from `refactor-scan`, if any)

Runs only when scan produced findings; the closing call still happens regardless, at the end. These are bookkeeping writes too — land via the dedicated bookkeeping branch/MR.

For each finding:

- Merged → mark the candidate `done`, close the issue.
- Closed without merge → closing comments support a structural rejection (a maintainer gave a load-bearing reason) → mark `wontfix`, close the issue, file a learned rejection under the Refactoring Notes' `out-of-scope/`; otherwise ask the human before deciding. Load-bearing reason is a minimum PHP version the target doesn't meet → also record it machine-parseably (`**Blocked by:** PHP >= X.Y`) so a later pass detects the reversal automatically (`tooling_tree.py`'s `detect_nodes()`).
- Tracked in the Refactoring Notes' `merge-requests.md` (`docs/agents/issue-tracker.md` names no native-label tracker) → drop the entry once resolved, either way. `docs/agents/issue-tracker.md` names a native-label tracker → closing/labeling the issue already removes it from `refactor:delivered`.
- **PHP-version reversal** (scan step 3 also reports these) → an existing entry in the Refactoring Notes' `out-of-scope/<node>.md` names a `Blocked by` condition the target now satisfies. Remove that file — the rejection is reversed, the node is proposable again on its own merits (not thereby fulfilled). Never for a rejection with no `Blocked by` field, or one scan didn't report as satisfied — those stay rejected until a human (or agent with a stated reason) removes them by hand.

`done`/`wontfix` are the shared triage-role labels (`docs/agents/triage-labels.md`), not suite-specific — closing the issue is what takes it out of the backlog.

A pass that only makes this call (no fresh candidate this run) is still a complete pass.

### Closing call — always, at the end of the pass

Given a freshly opened MR (from `refactor-implement`, if the pass got that far):

- `docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab) → nothing to remember here (the `refactor:delivered` label plus the MR's own link already carries it). Otherwise remember it in the Refactoring Notes' `merge-requests.md`: URL, candidate issue, tooling-tree node name (blank for structural), base branch.
- Clear the Refactoring Notes' `config.md`'s `Pending candidates` — this candidate now has an MR, so the resume marker no longer applies.
- Label the candidate `refactor:delivered` — never `done` (not merged yet — that's the *next* pass's early call) and never `ready-for-human` (means "nobody has implemented this yet," the opposite).
- `Create-mode` is normally already set — decided once, during `loop-config`'s own interview (`skills/continuous-refactoring/references/loop-config-interview.md`), and written by `refactor-implement` when it created `config.md`. Narrow fallback only: `config.md` predates this convention and `Create-mode` is genuinely unset → record what `refactor-implement` used this pass and treat it as decided from here on, don't re-derive it every pass.

**`loop-config`-in-flight exception** (true only before the `loop-config` candidate has merged): `config.md` doesn't exist on the default branch yet, nowhere to clear `Pending candidates` yet (`Create-mode` is already set by `refactor-implement`'s own `loop-config` exception — nothing left for this call to record there in the normal case). Write `Pending candidates` as a follow-up commit on the `loop-config` candidate's own branch instead, riding its already-open MR — the one case where bookkeeping skips its own branch/MR. Once merged, every closing call after that opens its own dedicated branch/MR as usual.

Then, regardless of whether an MR opened this pass — via the dedicated bookkeeping branch/MR (open one even with no candidate MR this pass; never assume the current checkout is safe to write to):

- Record an ADR (`docs/adr/`) for any decision a future scan must not re-litigate (see `/domain-modeling`).
- Update `CONTEXT.md` with terms that crystallised this pass.
- Write the Refactoring Notes' `config.md`'s `Fulfilled nodes` — unconditionally, last (`skills/continuous-refactoring/references/refactoring-config.md`). This pass ran `tooling_tree.py` (deterministic parser) → **overwrite the whole field** with its complete current fulfilled-set — keeps the cache correct across out-of-band changes (a revert, a manual edit). This pass ran the manual/LLM tree-walk fallback instead → only *add* what that walk itself freshly confirmed fulfilled — never remove/"clean up" entries, never guess at unchecked nodes. Same `loop-config`-in-flight exception: before it merges, this write lands on its own branch, first entry `loop-config` itself.
- Alongside it, write `Skip streak` (same field, same write): deterministic parser ran → re-run its unblocked-node check and, for every `required` node it names that this pass did *not* choose, increment its entry by 1 (start at 1 if none); the node chosen or newly fulfilled → drop its entry entirely (omit zero, per `refactoring-config.md`). Manual/LLM fallback ran instead → only touch entries for nodes that walk actually checked this round.

## Fallback

- **`/domain-modeling`**: installed → use its discipline for the ADR/`CONTEXT.md` side effects. Otherwise skip with a note — the ledger, label, and stamp writes are inline and suite-internal, run regardless. Crash-safe.

## Completion criterion

**Early call:** every finding is resolved (`done`, `wontfix` + out-of-scope entry, a PHP-version reversal's file removed, or an explicit "asked the human, waiting"), the remembered set reflects it before `refactor-prioritize` runs, and every write went out through the dedicated bookkeeping MR.

**Closing call:** a freshly delivered candidate (if any) is remembered (label or ledger, whichever applies) with `Pending candidates` cleared and `refactor:delivered` applied, `Fulfilled nodes` and `Skip streak` are written (full re-derivation when the parser ran, additive/narrow otherwise), and every write went out through an MR — the dedicated bookkeeping one, or the `loop-config` candidate's own — never a direct commit to the default branch.
