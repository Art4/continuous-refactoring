# 04: The run, through Safety Net and Guardrails

**What to build:** A developer calls `/continuous-refactoring` and is led through one run as a chain of
decision points — reconcile, Track choice, scan, file tickets, select — each with findings, options and
one recommendation. With the autonomous hint the suite takes its own recommendations. The call's free
text can name a Track, a restriction, a ticket or the mode. For the two tooling Tracks the run reaches a
selected, workable ticket and hands it to the design point.

Spec: `../spec.md` (sections *The run*, *Track choice*, *Tickets as the worklist*, *Rejections*, and
*Shape of the suite*). The entry skill and its references are written new with the `writing-for-agents`
skill. Scan and selection are references of this skill, not skills.

Design and implement are named here as hand-over points; ticket 05 writes them. Investigation's own
scan is ticket 06. The Housekeeping Track is the reference `housekeeping-track.md` of
`continuous-housekeeping`, written by ticket 07; this ticket points to it by that name.

**Blocked by:** 01, 02, 03, 10

**Status:** done

- [x] The entry skill checks for the `## Refactoring operations` section first and goes to onboarding when
      it or **Search** is missing
- [x] Interactive is the default; the autonomous mode is taken from the call's free text or from the human
      saying so mid-run; one chain serves both
- [x] Without the hint and with nobody answering, the run ends at the first decision point with a report
      and has written nothing
- [x] Reconcile: merged and closed merge requests of the suite are found by search and laid out with what
      follows (close the ticket, record a rejection, ask); a rejection whose blocker is now met is offered
      for reversal
- [x] Track choice: open tickets are searched and assigned to Tracks through the parser's per-Track node
      list; the recommendation follows the fixed order; an autonomous run stops at an unfinished Safety Net
      with nothing workable, a human may choose otherwise; later Tracks are tried within the same run once
      Safety Net is fulfilled
- [x] Scan runs only when the Track has no tickets, all are done, or it was asked for; it hands the node
      state to the parser and offers a ticket for every node neither fulfilled nor rejected, blocked ones
      marked through **Blocked by** or a sentence in the ticket
- [x] A ticket names its subject in plain words; before filing, existing tickets on the subject, open or
      closed, are searched and shown
- [x] Selection follows the tree's order, a **Priority** hint first; the node's fulfilment check runs again
      before the hand-over, and a fulfilled node's ticket is closed with a note
- [x] Declining a node records a rejection where **Rejected** says, or proposes a place; dependents are a
      decision point following the kind of edge
- [x] "Safety Net is fulfilled" is read from the gate, never judged: the parser's computed state of
      `structural-scan` (ticket 10). The per-Track `fulfilled` flag is a different question and decides
      neither the autonomous stop nor moving on to the next Track
- [x] A node below the target's PHP floor is laid out with the recommendation to record a rejection
      carrying that PHP version as its blocker, so the gate is not held shut and the parser offers the
      reversal once the floor rises
- [x] `CONTEXT.md` gains an entry for the aggregation node (state computed from its leaves, never handed
      in, never a ticket), and **Recognition-only gate node** no longer gives `structural-scan` as an
      agent-judged example
- [x] No cap on open merge requests or open candidates appears anywhere
- [x] Nothing reads or writes a bookkeeping document, a config file or a cadence
- [x] Text to the human says "skill suite" and "run"
- [x] No test is written or changed

## Comments

### Done — what exists now

Under `skills/continuous-refactoring/`, all written new:

- `SKILL.md` — the call, the decision-point rules, the ten steps of the run, the end of a run.
- `references/worklist.md` — finding the open tickets, Track, state, a ticket's merge request.
- `references/reconcile.md`, `references/track-choice.md`, `references/track-scan.md`,
  `references/filing-a-ticket.md`, `references/selection.md`, `references/rejection.md`.
- `references/tooling-tree-parser.md` — the only place that names the parser's path, its call, its
  output and the gate question. Ticket 08 moves the parser by changing two lines there.
- `references/reporting-progress.md` and `references/forge-facing-writing.md` — rewritten in the new
  words, content carried over.
- `references/track-scheduler.md` — deleted; `track-choice.md` replaces it.
- `CONTEXT.md` — new entry **Aggregation node**; **Recognition-only gate node** now gives
  `is-php-project` as its example.

Not touched: `opening-a-merge-request.md`, `foundational-refactoring-rules.md`,
`triage-labels-template.md` (ticket 05), `refactoring-bookkeeping.md`, `remote-bookkeeping.md` (ticket
08; nothing new points to them), the old `refactor-*` and `continuous-*` skills, the tree docs.

### Names this ticket hands to the next ones

`SKILL.md` points to three references that do not exist yet:

- `references/design-point.md` and `references/implement-point.md` — ticket 05. Selection hands over:
  the ticket, its node's slug and tree-doc file, the Track, the run's mode, the call's restriction. A
  ticket in review that the call named arrives with its merge request and the review's comments.
- `references/investigation-track.md` — ticket 06. It is entered from Track choice and hands a selected
  ticket to step 8.
- `../continuous-housekeeping/references/housekeeping-track.md` — ticket 07; the file exists in its old
  form.

Step 10 points to the existing `opening-a-merge-request.md`, which still reads `MR-create-mode`
(ticket 05).

### Decided here, not stated by the spec

**The run**

- After onboarding wrote the section and its **Search** was verified, one more decision point offers to
  go on with the run in the same call (recommended). In every other outcome of the interview the run ends.
- What the call states counts as the human's answer to the choice it addresses: a named Track answers
  the Track choice, a named ticket answers Track choice and selection. A write that choice did not cover
  (closing a named ticket found fulfilled) is still laid out.
- A run whose call named a Track or a ticket stays there: when that has nothing workable the run ends
  and does not move on to another Track.
- A restriction is applied once, to the worklist and the node lists, before any step counts them. "The
  Track has no open ticket" is therefore read within the restriction. In a scan it narrows what is
  proposed; nodes outside it are still judged where a covered node hangs on them, so no proposal is
  marked as blocked by something that is in place.
- "Nobody answers" is defined as: the question cannot be put to a human, or comes back unanswered.
  Everything before the first decision point is read-only; the parser's seed file is written to a
  temporary directory outside the target.
- A reconcile with no findings is one sentence, not a decision point. The first decision point of such a
  run is the Track choice.
- Decision points stay in the main conversation. A subagent may only read and judge (the fulfilment
  judgements of a scan).
- The closing report keeps the two lines Status / Next.

**Worklist and states**

- A ticket has one of four states: in review (an open merge request), blocked, waiting (an unanswered
  question — from the design point, or reconcile's about a merge request closed without a reason),
  workable. A ticket whose blocker has no ticket yet (filed with "file some") counts as blocked. The spec defines workable as "open, blockers done"; a ticket
  with an open merge request is not selected again — this is what makes repeated calls end at "waiting
  for merges" (user story 12). How "waiting" is marked is ticket 05's.
- Without a **Candidate** operation the tooling tickets are found with one **Search** per node, by the
  node's Name; a short listing of all open tickets may be read once instead. How Investigation finds its
  tickets beyond the **Candidate** list and the ticket named in the call is left to ticket 06.
- A ticket's merge request: **Linked merge request**, else a search of the forge for the ticket's
  reference or title; the newest one counts. With **Merge requests** `none`, the branch named in the
  ticket's comments stands in for it — this expects ticket 05 to leave the branch name as a comment.

**Reconcile**

- It starts from the open tickets: a merge request counts as "the suite's" when it belongs to an open
  ticket of the worklist. Housekeeping tickets are left to the Housekeeping reference.
- A closed merge request: comments saying the change is not wanted → record a rejection; comments naming
  a defect of the attempt → keep the ticket open; no reason → ask. An autonomous run leaves such a ticket
  untouched, does not select it, and carries the question in its closing report.
- A merged merge request that delivered only a part keeps its ticket open.
- An open merge request whose review asks for changes is only named. It is worked when the call names the
  ticket. The old "resume-candidate" path is not carried over.

**Track choice and the gate**

- A tooling Track "has something" with a workable ticket, or with no open ticket at all (its scan is
  due). A Track is "tried" for the rest of the run once its scan left nothing, nothing was filed, or
  selection found nothing workable; that is how the run moves on within one call.
- Consequence worth knowing: a Track whose tickets are all done is scanned on every run that reaches it,
  all its fulfilment checks included. The spec says so ("when all of them are done"); nothing is cached.
- The gate is read from `detected["structural-scan"]["fulfilled"]`. Where no scan of this run produced
  the node state, it is read in two steps: a best-case seed first (every node without an open ticket
  taken as fulfilled); only if the gate is fulfilled under that seed are those nodes judged for real.
- The autonomous stop says "Safety Net is waiting for merges", followed by the tickets in review and the
  tickets that cannot be worked with their reasons — the second list covers the target where nothing is in
  review (a target that is not a PHP project).

**Scan and tickets**

- Node state for the parser: rejected from the recorded rejections; every other node in scope judged. In
  a Safety Net scan the Guardrails nodes stay undecided; in a Guardrails scan the Safety Net nodes are
  judged unless they have an open ticket or were judged earlier in the run.
- A node that waits behind something no ticket can change — an unfulfilled recognition-only node, or a
  node below the PHP floor — gets no ticket and is named as "out of reach". On a target that is not a PHP
  project this keeps the scan from offering a ticket for every PHP node.
- A judgement that stays open (two tools competing for one Purpose) leaves the node undecided and puts
  the question into the filing decision point. The old route through a flagged candidate is not used
  here.
- **PHPStan baseline:** with `phpstan-baseline-empty` unfulfilled the scan proposes one ticket "PHPStan
  Level N: shrink the baseline" for the highest fulfilled level. It counts as a ticket of that level's
  node (so it is Safety Net up to level 5), and the next level's ticket is blocked by it. The old cut made
  this an Investigation candidate with one ticket per group of findings; in the new order that would
  leave an autonomous run stuck at Safety Net. A baseline ticket's pick-up check is the baseline itself
  (no entries left → close), not the level's Fulfilment check. How the ticket is planned is ticket 05's.
- What blocks a ticket is read from `tree.edges`: undecided `required` and `recommended` parents; for an
  aggregation node its undecided leaves in its place; a `required-any` group blocks together with the
  note that one member is enough.
- Filing is one decision point for the whole list (as recommended, file some, file none); per proposal
  the human may decline the node instead. The recommendation files every proposal without an open
  question, records the proposed PHP-floor rejections and closes tickets whose node is fulfilled; a
  proposal with an open question is not filed by an autonomous run. A proposal neither filed nor declined is stored
  nowhere.
- Ticket titles say what gets done and contain the node's Name ("Introduce PHPStan Level 0"); the text
  carries both search words. The fixed title `Tooling tree: <Name>` is gone.
- Search hits before filing: an open ticket on the subject is continued; a recorded rejection drops the
  proposal; tickets closed as done while the node is unfulfilled lead to a new ticket that names the old
  one.

**Selection**

- Order: **Priority** mark first, then the node's position in the parser's seedless `backlog`.
- The pick-up check runs before the decision point, ticket by ticket, until one is found to work; the
  decision point then shows the fulfilled ones (to close with a note), the unworkable ones and the rest.
  It also judges the recognition-only parents of the node and looks at `php_floor_blocked`.
- **Claim** is applied at the hand-over.

**Rejections**

- The machine-readable blocker is one line in the record: `Blocker: PHP >= X.Y`. (The old spelling
  `**Blocked by:** PHP >= X.Y` would collide with the **Blocked by** operation.)
- Without a **Rejected** operation the proposed place is `.out-of-scope/` where the target has it, a
  closed ticket otherwise; the answer is written as the **Rejected** bullet into the tracker file.
- A rejection as a closed ticket for a node that has no ticket: the ticket is filed and closed in one
  move, so a search finds it.
- Dependents: `required` (and a `required-any` group with no member left) → close the ticket with the
  reason "depends on <Name>, which was declined"; `recommended`, a `resolved` edge through an aggregation
  node, or a `required-any` group with a member left → remove the blocker. A record whose only reason is
  that dependence is not handed to the parser as a rejection; the parser derives it.
- Reversing: a closed ticket is reopened, a file is deleted and a ticket filed; tickets closed because
  they depended on it are reopened.
- Below the PHP floor: the blocker is the minimum the parser's reason names, the reason is the target's
  declared PHP version.
- **Rejecting the floor-blocked node alone does not open the gate.** Tried on a PHP 5.6 target with
  `phpstan-level-0` rejected: the PHPStan levels are closed by the rejection, but `rector-php-set` and
  `psalm-taint-analysis` hang on it through a `required-any` group whose other member is the
  recognition-only `psalm`; the parser neither closes them nor can anything fulfil them, and
  `structural-scan` stays unfulfilled. The text therefore records such stranded nodes as rejected with the
  same blocker in the same decision; with that the gate is fulfilled, and all three come back as
  `reversals` once the floor rises (both tried against the parser). Teaching the parser to close a
  `required-any` child whose whole group is rejected or out of reach would make this rule unnecessary —
  a parser change, not made here.

**Glossary**

- **Recognition-only gate node** also gained the sentence about nodes "out of reach".

### Red afterwards

No unit test is newly red (the same two as before). The validator has new errors; they are listed in a
comment on ticket 09.

### Changed after review

- **When a scan is due.** A tooling Track is scanned by itself only while it has no trace in the
  tracker — no ticket of its nodes, open or closed, and no recorded rejection. With a trace, a node
  without an open ticket counts as done and the gate is computed on that, with nothing judged.
  Re-checking the tooling Tracks is a task of the Housekeeping template (ticket 07). This replaces "a
  Track whose tickets are all done is scanned on every run" and the second step of reading the gate.
- **Finding the tooling tickets.** With a **Candidate** operation the marked open tickets are the list;
  one **Search** per node only without it.
- **Stranded nodes** behind a rejected `required-any` member are the parser's to close: ticket 11.
