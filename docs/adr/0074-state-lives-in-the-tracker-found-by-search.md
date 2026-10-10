# The suite keeps no state of its own — tickets are the worklist, everything else is found by search

> Extends [ADR-0001](0001-backlog-in-issue-tracker.md): the reasoning that put the backlog on the tracker
> now covers all of the suite's state.
>
> Supersedes [ADR-0064](0064-bookkeeping-state-lives-in-an-issue-or-a-local-file.md) and
> [ADR-0072](0072-remote-bookkeeping-belongs-to-the-target.md) (the bookkeeping document, its pointer, the
> config file, local and remote bookkeeping), [ADR-0012](0012-remembered-merge-requests-follow-the-tracker.md)
> and [ADR-0026](0026-drop-delivered-label-use-native-pr-linkage.md) (remembered merge requests),
> [ADR-0034](0034-bookkeeping-write-reads-fresh-origin-main.md),
> [ADR-0060](0060-track-open-entries-record-their-issue-number.md),
> [ADR-0062](0062-fulfilled-nodes-field-removed-from-the-schema.md),
> [ADR-0065](0065-investigation-gets-its-own-open.md),
> [ADR-0068](0068-investigation-open-supports-more-than-one-entry.md) and
> [ADR-0069](0069-drop-the-top-level-pending-candidates-field.md) (fields of that document and the rules
> for writing them), and [ADR-0047](0047-tooling-tree-proposals-are-pre-filed-before-ranking.md) (which
> proposals get a ticket, and when).
>
> Supersedes in part [ADR-0006](0006-loop-delivers-remembered-merge-requests.md) (merge requests are
> found, not remembered), [ADR-0055](0055-purpose-based-fulfilment-and-scheduled-tracks.md) and
> [ADR-0056](0056-agent-judged-fulfilment.md) (the per-Track sections with `Last scan`, `Open` and
> `Out-of-scope`), [ADR-0048](0048-skip-streak-replaced-by-issue-age-and-priority-override.md) (the age
> factor and the `Filed` line; a ticket marked as priority still comes first),
> [ADR-0024](0024-loop-config-interview-decides-tracker-create-mode-storage.md) and
> [ADR-0025](0025-agents-md-gets-a-create-mode-pointer-not-the-value.md) (the storage question and the
> `Bookkeeping:` line; `Focus areas` and `Refactoring goal` stay human-written lines), and
> [ADR-0058](0058-onboarding-is-a-dispatcher-step.md) (what triggers onboarding), and
> [ADR-0023](0023-never-delete-a-branch-as-a-candidates-only-close.md) (the bookkeeping cases it names;
> never deleting a branch that holds the only record of a decision stands).
>
> Amends [ADR-0071](0071-tracker-through-operations-tracker-and-forge-apart.md): the cut of the
> operations changes, the idea does not. Amends
> [ADR-0036](0036-refactoring-goal-field-steers-structural-candidates.md): `Refactoring goal` is a
> human-written project line, not a field of a bookkeeping document.

The suite kept its own record of which nodes were open, when a Track last ran, what was rejected and
which merge request belonged to which ticket — a bookkeeping document, a pointer to it, a config file, a
local and a remote variant, and a single skill allowed to write it. That record duplicated what the
tracker and the forge already show, went stale whenever a human worked outside the suite, and was the
largest source of rules in the skill texts. Tickets were recognised by a fixed marker, so a ticket a human
wrote without it was invisible.

## Decision

The suite reads and writes the tracker and the forge, and nothing of its own.

- **Open tickets are the worklist.** At the start of a run the suite searches them and assigns each to a
  Track: a ticket matching a node belongs to that node's Track, the open Housekeeping ticket to
  Housekeeping, everything else to Investigation. *Workable* means an open ticket whose blockers are all
  done.
- **A scan runs only when a Track has no tickets, when all of them are done, or on request.** It runs the
  fulfilment checks and offers a ticket for every node neither fulfilled nor rejected, blocked ones
  included and marked as blocked. Before a ticket is worked, its node's fulfilment check runs again; a
  fulfilled node's ticket is closed with a note.
- **Found by search, not by marker.** A ticket names its subject in plain words in title and text, so a
  later search finds it. Before filing, the suite searches for an existing ticket on the subject, open or
  closed; several hits are all shown, one recommended. A ticket's merge request is found by searching too.
- **A run begins by reconciling:** which of the suite's merge requests were merged or closed, and what
  follows — close the ticket, record a rejection, ask.
- **A rejection is a closed ticket with its reason, or a file, wherever the target says.** One whose
  stated blocker is machine-readable (a minimum PHP version) is offered for reversal once the blocker is
  met. Rejecting a node others depend on is a decision point: close the dependents as rejected (required
  edge) or remove the blocker (recommended edge).
- **The parser reads no file of the suite.** Which nodes are fulfilled and which rejected is handed in.

**Refactoring operations** in the new cut — required: **Search** (new), **Done**, **Merge requests**;
optional: **Candidate** and **Priority** (now hints for search and order), **Linked merge request**,
**Comment author and time**, **Claim**, **Rejected** (new), **Blocked by** (new), **Housekeeping** (new).
**Bookkeeping** and **Filed date** are removed. Without **Blocked by** the dependency is a sentence in the
ticket; without **Rejected** the suite proposes a place when the first rejection is recorded.

Onboarding asks where the tickets live and how the operations work there, and nothing else. A target is
onboarded when its tracker file has a `## Refactoring operations` section; a section without **Search**
gets it added by onboarding.

There is no migration. Files under the suite's old scratch folder are no longer read; a developer who
wants old rejections kept where they are names that place under **Rejected**.

## Considered

- **Keep a small cache next to the tracker.** Rejected — every cache needs a writer, an invalidation rule
  and a story for the human who edits the tracker by hand; those rules are what this decision removes.
- **Keep the fixed marker and add search on top.** Rejected — a marker the suite requires is a ticket a
  human forgot to mark. **Candidate** stays as a hint a target may give.
- **Migrate existing bookkeeping into tickets.** Rejected — every known target is maintained by the
  suite's owner, and a first scan rebuilds the worklist.

## Consequences

`CONTEXT.md` gains **Worklist**; **Refactoring Notes**, **Bookkeeping document**, **Bookkeeping pointer**,
**Local / Remote bookkeeping**, **Config file** and the cadence leave it. The rule that only one skill
writes goes with the document it protected ([ADR-0075](0075-one-skill-with-references-the-targets-own-skills-first.md)).
A known limit: on a large tracker a freely written ticket is found only through a **Candidate** hint or by
being named in the call. Moving a target over from 0.6.0 is a breaking change — run onboarding again,
delete the old files, remove the old symlinks. No tests were written or changed; the parser's tests change
with the parser.
