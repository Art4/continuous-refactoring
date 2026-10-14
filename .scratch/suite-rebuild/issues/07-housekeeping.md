# 07: Housekeeping

**What to build:** A developer calls `/continuous-housekeeping` and the suite works the open Housekeeping
ticket: the recurring tasks from the template, the refactoring ideas left as comments, the secret scan
over new history — and, as the last task, creates the next ticket. Where the mechanism is missing, the
run offers to set it up, after which the call works without further explanation.

Spec: `../spec.md` (section *Housekeeping*, user stories 34–44). Written new with the
`writing-for-agents` skill. The process lives in the reference `housekeeping-track.md` of
`continuous-housekeeping`; the entry skill of ticket 04 points to it by that name when its Track choice
lands on Housekeeping.

**Blocked by:** 02

**Status:** done

- [x] `continuous-housekeeping` is user-invocable, runs the Housekeeping Track without a Track choice, and
      follows the same interactive and autonomous modes as the run
- [x] The open Housekeeping ticket and the template are found through the **Housekeeping** operation; the
      Track is due when the ticket's stated date is reached
- [x] Mechanism missing → the run proposes the template (rhythm chosen by the human, with a recommendation
      drawn from the target), the first ticket, and the `AGENTS.md` line; the `AGENTS.md` line is written
      only after a human agreed, in an autonomous run too
- [x] The template holds the recurring tasks, the rhythm, and the last item "create the next Housekeeping
      ticket"; the next ticket states from when it is due; several templates may exist side by side
- [x] Each comment proposing a refactoring is carried out in one or more commits of its own; one too big
      is proposed for a ticket of its own
- [x] The `AGENTS.md` line tells agents to propose ideas as a comment on the open Housekeeping ticket
      after the human allowed it, and, with two open, to let the human choose with the younger recommended
- [x] The secret scan over history is a template task: whole history the first time, afterwards the
      commits since the last Housekeeping ticket
- [x] The template the suite proposes carries the task "re-check the tooling Tracks": a scan of Safety Net
      and Guardrails as the scan reference of `continuous-refactoring` describes it, so a tool that went
      missing or a node the tree gained is found; its proposals go through the filing decision point
- [x] Tooling-tree nodes still contribute their Housekeeping line to the template through their own merge
      request, and a fulfilled node whose line is missing gets it added
- [x] The target's quality checks pass before the merge request opens; a cycle without changes closes its
      ticket with a comment
- [x] The ticket's comments say whether Housekeeping needs the **Comment author and time** operation to
      work the proposals left as comments; nothing else in the suite reads it any more (ticket 05), and
      ticket 08 removes it unless this ticket uses it
- [x] No cadence, `Last scan` or bookkeeping is read or written
- [x] No test is written or changed

## Comments

Done on `suite-rebuild`.

- `skills/continuous-housekeeping/SKILL.md` — written new: user-invocable, the call, two steps (Ready,
  Housekeeping). Decision points, the modes and the closing report are pointers into
  `continuous-refactoring/SKILL.md`.
- `references/housekeeping-track.md` — written new: the mechanism, tickets with a merge request, which
  ticket, plan the cycle, work, tickets of their own, the next ticket, deliver; a ticket that comes back
  from review; the secret scan and the re-check of the tooling Tracks.
- `references/housekeeping-setup.md` — new, behind a pointer because only a run without the mechanism
  reaches it: the setup, the proposed template, the **Housekeeping** bullet, the `AGENTS.md` line, a
  template without a ticket, a further template.
- Deleted: `housekeeping-cadence-interview.md`, `housekeeping-template-file-format.md`.
- `continuous-refactoring`: `SKILL.md` step 4 and `track-choice.md` (Housekeeping can come back to Track
  choice as tried; a ticket in review is not "due"), `implement-point.md` (the Housekeeping line goes to
  the first template where several exist).
- Five node docs under `refactor-scan/references/php-tooling-tree/` (`composer`, `composer-audit`,
  `phpstan`, `php-minimal-version`, `semgrep`): the sentence that sent the Housekeeping line to the fixed
  `docs/refactoring/housekeeping-template.md` and to the deleted format reference now points to the
  slice in `implement-point.md`. Nothing else in them was touched.

Carried over from the old texts: the template's lines are instructions carried out as written; a
hand-adopted tool gets its line through Housekeeping; Housekeeping keeps current what exists and adopts
nothing; a result that is not green is never shipped; the quality checks before the merge request; a
cycle without changes closes its ticket with a comment; the secret scan reuses the target's scanner and
its own file of known findings and never writes a secret's value. Not carried over: the cadence, `Last
scan`, the onboarded-target check against bookkeeping, the closing call to `refactor-learn`, the fixed
title and path, one ticket per due cycle, the standing `AGENTS.md` check.

### Comment author and time

**Housekeeping does not need it; ticket 08 can remove the operation.**

- *Time* — nothing is computed from a comment's time. Which comments belong to a cycle follows from the
  ticket they are on; which were already dealt with follows from their position below the suite's newest
  `Ideas` comment, in the order the tracker shows them. The secret scan's range comes from the commit the
  earlier ticket's scan task recorded, not from a date of a comment.
- *Author* — a comment is weighed as a proposal whoever wrote it. What protects the target is the class,
  not the author: only a behaviour-keeping change of structure covered by tests is carried out; anything
  else (a command, a dependency, CI, credentials) is left alone. Knowing the author would not help
  without also knowing who is trusted, which the operation never stated.

For ticket 08's known limitations: on a tracker strangers can write to, an autonomous Housekeeping run
takes a stranger's comment up as a proposal like anyone else's. It is carried out only as a
behaviour-keeping refactoring and arrives in a merge request a human reviews.

### Decided here, not stated by the spec

**Entry and due date**

- `/continuous-housekeeping` runs the Ready step (onboarding where the operations are missing) and the
  Track; it builds no worklist and runs no general reconcile. The Track reconciles its own tickets.
- A ticket states its date as a line `Due from: YYYY-MM-DD`; one without a date is due. Not due → the
  recommendation is "nothing to work", so a daily scheduled autonomous call on a weekly rhythm ends
  without writing. "Now" in the call, a named ticket, or a human choosing Housekeeping at Track choice
  works it early.
- One ticket per run: of several due, the one due longest; the others are named for a further call.
- Reached from Track choice with nothing to work, Housekeeping returns there as tried, so that an
  autonomous run goes on to Investigation (story 16).
- The next ticket's date is today plus the rhythm (or the next date the rhythm names), counted from the
  day the cycle is worked, not from the old due date. It is created during the cycle, before the merge
  request, after a search for one that already exists.

**The cycle**

- One decision point plans the cycle (tasks, new lines, ideas with their class) and covers its writes up
  to the merge request; filing tickets and opening the merge request keep their own.
- The ticket's task list is the cycle's record: new lines and fitting ideas are added to it, each task is
  ticked with a one-line result. A run that was interrupted continues at the unticked tasks.
- An idea **fits** when it keeps behaviour, needs no choice between designs, touches code that tests or a
  tool cover, and reads as a few commits. Otherwise it is **too big** (ticket of its own, written as an
  Investigation candidate) or **no refactoring** (left alone with the reason).
- One comment opening with `Ideas` says what became of every idea; it also marks which comments a later
  run of the same cycle has already dealt with.
- A task with no clean way through (an advisory without a fix) is ticked with what was found, and its
  rest is proposed as an ordinary ticket without the **Candidate** mark. The same for a secret-scan
  finding.
- Housekeeping tasks are done by the suite itself; there is no "who implements" choice. The checks are
  those of the implement point, the review covers the idea commits.
- A merge request closed without a merge: comments naming a defect → the ticket is reworked on the same
  branch; any other reason or none → the recommendation is to close the ticket, since the next one
  already exists. A ticket in review is reworked when the call names it.

**Secret scan**

- The scan task's result records the commit scanned up to; the next scan takes the commits since. The
  spec says "since the last Housekeeping ticket's date" — the recorded commit is exact, and the date is
  the fallback when the commit is gone. No earlier record → the whole history.
- No scanner in the target → the task is ticked as not run; the whole history stays owed.
- Where people outside the project can read the tracker, the recommendation is to file no ticket for a
  finding and to report it in the conversation only.

**Re-check of the tooling Tracks**

- Both scans run as "a scan the call asked for", Safety Net first; proposals go through
  `filing-a-ticket.md`, and the scan's return to Track choice is replaced by going on with the cycle.

**Setup**

- The template, the bullet and the `AGENTS.md` line are committed on the first ticket's branch and reach
  the default branch through the first cycle's merge request; the first ticket is due today and its
  cycle runs in the same run. Until that merge the mechanism looks missing on the default branch, so the
  setup first searches for an open Housekeeping ticket whose merge request adds a template and waits
  for it.
- Rhythm recommendation from the commits of the last 90 days on the default branch: more than 300 →
  daily, 30 to 300 → weekly, fewer → monthly. The rhythm is a free line of the template.
- Recommended path `docs/refactoring/housekeeping-template.md` (where 0.6.0 put it, so an existing file
  is found and kept); an existing file listing recurring tasks is proposed as the template.
- Ticket shape, as the proposed bullet states it: title `Housekeeping, due from <date>`, the lines
  `Due from:` and `Template:`, the tasks as a checklist. It is the target's and can be changed there.
- The proposed template's tasks are written for a reader who does not know the suite; a node's
  Housekeeping field is reworded for it.
- The `AGENTS.md` line is proposed once, at setup. Left out, every later closing report says it is
  missing, and a call that asks for it adds it; the run does not ask again by itself. In a target with
  only `CLAUDE.md` it goes there.
- A template without an open ticket: one decision point, the ticket due today.
- Several templates: the first one the bullet names holds the secret scan, the re-check and the tools'
  Housekeeping lines; a further template holds the tasks the human names and its own "create the next
  ticket".

### Changed after the review

Both review axes found dead ends and wrong shapes in the first draft. Changed: a setup or cycle merge
request closed without a merge no longer blocks every later call; a ticket in review can be reworked;
Track choice no longer counts a ticket in review as due; secret findings and unfixable tasks are no
longer filed as refactoring candidates; several templates no longer collect the same tasks, and the
listing search finds their titles; a resumed cycle no longer classes its ideas twice; the recurring
`AGENTS.md` check was dropped from the proposed template (an autonomous cycle could never finish it);
the `AGENTS.md` rule and the mode are no longer restated beside their source.

Left as it is: `php-minimal-version.md` still says the Housekeeping Track is "triggered on its own fixed
cadence" a few lines below the sentence changed here, and the nodes' **Housekeeping** fields still use
the suite's words (`_current_php_floor`, "this node's own Fulfilment check") — tree-doc content for
ticket 08.

### Red afterwards

No unit test is newly red (the same two). What changed in the validator is in a comment on ticket 09.
