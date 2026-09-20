---
name: refactor-learn
description: The suite's only writer of bookkeeping — acts on refactor-scan's reconciliation findings and refactor-implement's freshly opened merge request, records the ledger, ADRs, CONTEXT.md, and the last-run stamp.
---

# Refactor Learn

The only skill that writes suite bookkeeping: the Refactoring Notes' `merge-requests.md` (only when `docs/agents/issue-tracker.md` names no native-label tracker — otherwise this data lives on the tracker), the Refactoring Notes' `out-of-scope/`, ADRs, `CONTEXT.md`, the Refactoring Notes' `bookkeeping.md`, and issue labels. Every other lifecycle skill may read these; only this one writes them.

The orchestrator calls this skill up to **twice** a pass: an **early call**, right after `refactor-scan`, only when it produced findings; and a **closing call**, always, at the end. The split exists because `refactor-prioritize` reads the ledger to decide whether two MRs are already open — a finding this pass just resolved has to be written back before that check runs.

The closing call also consumes a second kind of input, in place of a freshly opened MR: a design-time
breaking-change finding from `refactor-design`'s own decision gate
(`skills/refactor-design/references/decision-gate.md`), when this pass's design discovered the
candidate can't be done without changing behavior.

**Land every write below via a dedicated bookkeeping branch/MR off the default branch — never a direct commit.** Before writing, in either call: confirm you aren't still on the candidate branch `refactor-implement` left checked out — these writes aren't part of that review. Pull the default branch's latest, then create (or reuse, if one from an earlier interrupted pass is still open) a small bookkeeping branch off it, commit the writes there, and open (or update) that MR, using the create-mode policy at `skills/continuous-refactoring/references/opening-a-merge-request.md`.

**Exception — native-tracker in-flight fold-in**: `docs/agents/issue-tracker.md` names a native-label tracker, and `refactor-implement` opened a candidate MR this same pass → the closing call's writes ride that branch as a follow-up commit, no separate bookkeeping MR — stay checked out on it. `loop-config` is this exception's narrowest case (the file exists nowhere else yet). The same applies to the early call's own **fold-in still owed** finding below — that candidate's branch already exists from an earlier pass, so its writes ride there too, never the dedicated bookkeeping branch. Doesn't otherwise apply to the early call (no candidate branch exists yet for any other finding type), a pass with no candidate MR, or a non-native tracker — those keep using the dedicated bookkeeping branch below.

**Finding the bookkeeping branch — deterministic, no memory required, never search for a name.** Named `refactor-learn/bookkeeping-N` (N starting at 1, never reused). Algorithm: `skills/refactor-learn/references/bookkeeping-branch.md`.

**Before deleting or abandoning any branch carrying an unmerged bookkeeping write**, land that record first: `skills/refactor-learn/references/never-delete-without-record.md`.

## Process

**Precondition, both calls: a genuine event that was actually handed to this call, or stop — never go
looking for one.** Neither call writes anything — no branch opens, no ledger, ADR, `CONTEXT.md`,
issue-label, or `out-of-scope` write happens — unless it has something real to act
on. Early call: at least one finding, named by whoever invoked this call (ordinarily `refactor-scan`,
in its own `## Output`). Closing call: a freshly opened MR, named by `refactor-implement`; a
design-time breaking-change finding, named by `refactor-design`; **or** a Safety Net, Guardrails,
Housekeeping, or Investigation Track's own scan/process having actually run this pass
(`skills/refactor-scan/references/safety-net-track.md` /
`skills/refactor-scan/references/guardrails-track.md` /
`skills/continuous-housekeeping/references/housekeeping-track.md` /
`skills/refactor-scan/references/investigation-track.md`), even when it found nothing to propose or
nothing registered to check — the event this pass's `refactor-scan` step 4 itself reports (or, for
Housekeeping, `continuous-housekeeping`, which runs this Track directly rather than through
`refactor-scan`), not something this call goes looking for on its own; this third case exists solely so
`## Safety Net`'s/`## Guardrails`'s/`## Housekeeping`'s/`## Investigation`'s own `Last scan` write
(`safety-net-write.md`/`guardrails-write.md`/`housekeeping-write.md`/`investigation-write.md`) can
actually happen on an all-clear scan, per those files' own "write `Last scan` regardless" rule — it
authorizes only that one write. This is step zero, before any other
read — querying the tracker for open MRs, re-reading `bookkeeping.md`, scanning `merge-requests.md` to
see whether a precondition might be satisfiable is exactly the detection work `refactor-scan`/
`refactor-implement` already own; this skill only ever acts on what the pass that produced it named,
the same "detect, never write" discipline `refactor-scan` already holds itself to. Neither named →
stop immediately, report "nothing to do", before reading anything else. In the ordinary orchestrated pass this mostly
guards the closing call — the orchestrator already skips calling the early call when scan found
nothing (`skills/refactor-loop/SKILL.md` step 2), but still calls the closing call unconditionally
every pass, including one where nothing above it produced anything. This same check is also what
makes a human's direct, standalone `/refactor-learn` invocation — bypassing the orchestrator
entirely — safe: named nothing, it stops before touching any state, instead of inventing work by
going to check for itself.

### Early call — findings only (from `refactor-scan`, if any)

Runs only when scan produced findings; the closing call still happens regardless, at the end. These are bookkeeping writes too — land via the dedicated bookkeeping branch/MR, except **fold-in still owed** below, which rides the candidate's own branch (the exception above).

For each finding:

- Merged → mark the candidate `done`, close the issue. Slug named in `bookkeeping.md`'s `## Safety Net` or `## Guardrails` section's `Open` list → also remove it from there (`skills/refactor-learn/references/safety-net-write.md`, `skills/refactor-learn/references/guardrails-write.md`), instead of anything below about `Pending candidates`.
- Closed without merge → closing comments support a structural rejection (a maintainer gave a load-bearing reason) → mark `wontfix`, close the issue, file a learned rejection under the Refactoring Notes' `out-of-scope/` — a human-readable entry, written per `skills/continuous-refactoring/references/forge-facing-writing.md`; otherwise ask the human before deciding. Load-bearing reason is a minimum PHP version the target doesn't meet → also record it machine-parseably (`**Blocked by:** PHP >= X.Y`) so a later pass detects the reversal automatically (`tooling_tree.py`'s `reversals` output, from `php_version_reversal_findings()`). Slug named in `## Safety Net`'s or `## Guardrails`'s `Open` → also remove it from there and add the `Out-of-scope` pointer (`safety-net-write.md`/`guardrails-write.md`), plus every node closed by that rejection (as reported by the script's `closed_by_rejection()`) also leaves `Open`, with no new files written for those downstream closures.
- **Fulfilled at pick-up** (scan's Track `Open` walk, `skills/refactor-scan/references/track-open-processing.md` — its re-check ran a node's Fulfilment check right before working it and found the node already served, typically adopted by hand since the last scan) → remove that slug from its Track's `Open` (`safety-net-write.md`/`guardrails-write.md`): no merge request, no rejection, nothing filed — the node is genuinely fulfilled, the outcome its `Open` entry existed to reach. An issue already filed for it on an earlier pass (its `Open` entry carried `(#n)`) closes as `done`, with a one-line note naming the pick-up re-check as the reason; no issue was ever filed → nothing to close. Same detect-never-write split as every finding above: scan only reports it, this call performs the removal.
- Tracked in the Refactoring Notes' `merge-requests.md` (`docs/agents/issue-tracker.md` names no native-label tracker) → drop the entry once resolved, either way. `docs/agents/issue-tracker.md` names a native-label tracker → nothing to remove there; closing the issue (above) already takes it out of the open-`refactor:candidate` remembered set `refactor-scan` reads.
- **PHP-version reversal** (scan step 3 also reports these) → an existing entry in the Refactoring Notes' `out-of-scope/<node>.md` names a `Blocked by` condition the target now satisfies. Remove that file — the rejection is reversed, the node is proposable again on its own merits (not thereby fulfilled). Never for a rejection with no `Blocked by` field, or one scan didn't report as satisfied — those stay rejected until a human (or agent with a stated reason) removes them by hand.
- **Fold-in still owed** (scan step 3's new finding — a still-open, still-draft candidate MR from an earlier interrupted pass) → check out that candidate's own branch (the exception above, not the dedicated bookkeeping branch), perform the same fold-in writes the closing call would (*Then, regardless of which branch...* below), then mark it ready for review as that list's last step — completing what the interrupted pass never finished. The candidate issue itself isn't closed by this — that still waits for the MR to actually merge, an ordinary "Merged" finding on some future pass.
- **Secret history scan finding** (scan step 4c) → file a `refactor:priority` candidate issue per finding, same three-field shape (Where/Problem/Signal) any other candidate issue uses: Where is the file/line, Problem is the scanner's own rule/finding id and a short description — **the secret's value redacted** — Signal is Security (`skills/refactor-prioritize/references/signals.md`). Filed directly rather than surfaced through `refactor-prioritize`'s Select mode — nothing to explore, the finding is already concrete. Once every finding from this pass's scan is filed (zero findings counts as "every finding filed" too), write the Refactoring Notes' `bookkeeping.md`'s `Secret history scan` field to `done (<today's date>)` — e.g. `done (2026-09-14)`, the date this write happens, purely for human-readable audit trail (nothing in the suite ever reads or compares it) — this scan runs at most once per target (`refactor-scan/SKILL.md` step 4c), so this write never repeats.

`done`/`wontfix` are the shared triage-role labels (`docs/agents/triage-labels.md`), not suite-specific — closing the issue is what takes it out of the backlog.

A pass that only makes this call (no fresh candidate this run) is still a complete pass.

### Closing call — always invoked, but only writes when it has something real (see precondition above)

**A design-time breaking-change finding from `refactor-design`** (this pass's design discovered the
candidate can't be done without changing behavior, so `refactor-implement` never ran) → mark
`wontfix`, close the issue, file a learned rejection stating what was found and why: the Refactoring
Notes' `out-of-scope/<node>.md` for a tooling-tree candidate, a closing note on the issue itself for a
structural/externally-labeled/baseline-shrink candidate — the same split the early call's own
rejection handling above already uses. Either one lands on the target repo's own forge —
`skills/continuous-refactoring/references/forge-facing-writing.md`. Clear `Pending candidates` if it
named this candidate, or, for a Safety Net or Guardrails Track candidate, remove it from that Track's
own `Open` and add its `Out-of-scope` pointer instead (`safety-net-write.md`/`guardrails-write.md`) —
plus every node closed by that rejection (as reported by the script's `closed_by_rejection()`) also
leaves `Open`, with no new files written for those downstream closures — never both. No MR to remember,
no `Create-mode` bookkeeping to touch — land this via the dedicated bookkeeping branch, then skip
straight to *Then, regardless of which branch...* below.

Otherwise, given a freshly opened MR (from `refactor-implement`, if the pass got that far):

- `docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab) → nothing to remember here — `refactor-implement` step 5's `Closes #<n>` on the MR is already the durable record, the tracker's own native issue↔PR cross-reference; no label to apply. Otherwise remember it in the Refactoring Notes' `merge-requests.md`: URL, candidate issue, tooling-tree node name (blank for structural), base branch.
- Clear the Refactoring Notes' `bookkeeping.md`'s `Pending candidates` — this candidate now has an MR, so the resume marker no longer applies. A Safety Net or Guardrails Track candidate never set that field in the first place (its `Open` entry only clears once the MR actually merges — `safety-net-write.md`/`guardrails-write.md`) — nothing to do here for one of those.
- `Create-mode` is normally already set — decided once, during `loop-config`'s own interview (`skills/continuous-refactoring/references/loop-config-interview.md`), and written by `refactor-implement` when it created `bookkeeping.md`. Narrow fallback only: `bookkeeping.md` predates this convention and `Create-mode` is genuinely unset → record what `refactor-implement` used this pass and treat it as decided from here on, don't re-derive it every pass.

**Which branch**: the fold-in exception's condition met → stay on the candidate's branch, commit there. Otherwise → the dedicated bookkeeping branch/MR (open one even with no candidate MR this pass; never assume the current checkout is safe to write to). `loop-config`-in-flight (before that candidate merges) is just this exception's narrowest case — `Create-mode` is already set by `refactor-implement`'s own `loop-config` exception, nothing left for this call to record there normally.

Then, regardless of which branch the writes above rode:

- Record an ADR (`docs/adr/`) for any decision a future scan must not re-litigate (see `/domain-modeling`).
- Update `CONTEXT.md` with terms that crystallised this pass.
- ~~`Fulfilled nodes`~~ — retired. No write needed; old files retain entries for historical record, ignored by all lifecycle skills (see `skills/continuous-refactoring/references/refactoring-bookkeeping.md`'s *`Fulfilled nodes`* section).
- This pass's scan ran the Safety Net Track (`skills/refactor-scan/references/safety-net-track.md` — an `Open` entry just resolved above, or the Track's own scan ran this pass with nothing to propose) → write `## Safety Net`'s `Last scan`, and `Open`/`Out-of-scope` if this pass's resolution changed either: `skills/refactor-learn/references/safety-net-write.md`. The Track's `Open` was already non-empty and this pass only worked through an existing entry without the scan itself running → don't touch `Last scan` (that file's own final section).
- Same for the Guardrails Track (`skills/refactor-scan/references/guardrails-track.md`) → write `## Guardrails`'s `Last scan`, and `Open`/`Out-of-scope` if changed: `skills/refactor-learn/references/guardrails-write.md`. Independent of the Safety Net write above — a pass can resolve a Guardrails candidate, a Safety Net candidate, neither, or (once both Tracks are eventually due the same pass) both; each Track's own section is written only when that Track's own scan actually ran or one of its own `Open` entries actually resolved this pass.
- This pass's scan ran the Investigation Track (`skills/refactor-scan/references/investigation-track.md` — its own *Proposing* step was reached, whether or not `structural-scan` itself was actually proposable) → write `## Investigation`'s `Last scan` only: `skills/refactor-learn/references/investigation-write.md`. No `Open`/`Out-of-scope` to write here at all — this section never carries either. A structural candidate resumed via `Pending candidates` at `refactor-scan/SKILL.md` step 2, without Investigation's own scan step ever being reached this pass, doesn't trigger this write — same "resuming isn't scanning" distinction the two bullets above already draw.
- `continuous-housekeeping` ran the Housekeeping Track this pass (`skills/continuous-housekeeping/references/housekeeping-track.md` — its own process was reached, whether it resumed an in-progress cycle, delivered a fresh one, or found nothing registered to check) → write `## Housekeeping`'s `Last scan` only, via the ordinary dedicated bookkeeping branch (never folded onto the Housekeeping cycle's own branch): `skills/refactor-learn/references/housekeeping-write.md`. No `Open`/`Out-of-scope` to write here at all — this section never carries either, the same shape `## Investigation`'s own write already follows, but with a real numeric `Cadence` (`7` unless hand-edited) instead of the literal `continuous`. Housekeeping wasn't the Track step 0b/0c selected this pass → don't touch `## Housekeeping` at all.
- **Last of all**: the branch these writes just landed on carries a candidate MR still marked draft (`opening-a-merge-request.md`'s *Draft candidate MRs* — opened as one this same pass, or resumed via the early call's **fold-in still owed** finding above) → mark it ready for review now that every fold-in write above is actually pushed (`gh pr ready` / `glab mr update <n> --ready`). Not draft (the ordinary non-native-tracker/dedicated-branch case) → nothing to do here.

## Fallback

- **`/domain-modeling`**: installed → use its discipline for the ADR/`CONTEXT.md` side effects. Otherwise skip with a note — the ledger, label, and stamp writes are inline and suite-internal, run regardless. Crash-safe.

## Completion criterion

**Both calls, precondition not met:** the call stopped immediately and reported "nothing to do" — no branch opened, nothing written. This is a complete, valid outcome, not a failure — see the precondition above.

**Early call, precondition met:** every finding is resolved (`done`, `wontfix` + out-of-scope entry, a fulfilled-at-pick-up slug removed from its Track's `Open`, a PHP-version reversal's file removed, a fold-in-still-owed candidate's MR marked ready for review, every secret-history-scan finding filed as a `refactor:priority` candidate with `Secret history scan` written `done (<date>)`, or an explicit "asked the human, waiting"), the remembered set reflects it before `refactor-prioritize` runs, and every write went out through a branch — the dedicated bookkeeping branch (opened as an MR, or — no forge/remote available — handed to the human per `opening-a-merge-request.md`) for every finding type except fold-in-still-owed, which rides the candidate's own already-open branch instead (the exception above).

**Closing call, precondition met:** a freshly delivered candidate is remembered (its MR's `Closes #<n>` link, or the ledger, whichever applies) with `Pending candidates` cleared — or, a design-time breaking-change finding is closed out instead, with its rejection recorded (`wontfix`, closing note or `out-of-scope/` entry) and `Pending candidates` cleared the same way — a candidate MR left in draft by this pass is marked ready for review, and every write went out through a branch — the candidate's own already-open branch (native tracker, MR opened this pass), the dedicated bookkeeping one, or the `loop-config` candidate's own as that exception's narrowest case — never a direct commit to the default branch (opened as an MR where forge access exists).
