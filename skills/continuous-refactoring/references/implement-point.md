# Reference: the implement point

Ends with a **branch whose checks are green**, holding the planned change and nothing else. Handed in: the
ticket with its plan, its Track, the run's mode, for a tooling ticket the Stage's slug and its Tool's `details` file,
and for a ticket in review its merge request with the review's comments. Every slice keeps
`foundational-refactoring-rules.md`.

## 1. Who implements

Decided as `design-point.md` step 2 decides who plans, with two differences: a skill fits here when its
description says it builds a planned ticket, and the `AGENTS.md` sentences that count are those on how
work is implemented, tested and reviewed. It has no option for the human implementing: that choice was
offered with the plan (`design-point.md`, step 5). An autonomous run implements the suite's own way,
which is steps 3 to 5 below.

*Done when* it is said who implements.

## 2. The branch

Check the working tree first (`../SKILL.md`, *A clean working tree*). Then the first row that applies:

| Found | The branch |
| --- | --- |
| the ticket came with its merge request | that merge request's branch, checked out and up to date; the review's comments are triaged (*The review's comments*, below), and what is to be fixed becomes findings for step 3 |
| a branch for this ticket — named in one of its comments, or carrying its reference — holds commits the default branch lacks, and no merge request ever came from it | that branch; read its commits before adding to them |
| neither | a new one from the default branch's current tip, named by the target's convention, else `refactor/<ticket reference>-<subject in two or three words>`; for a baseline ticket, or a plan cut into parts, the subject is the part's name |

A plan that lists parts is built one part at a time: the first part whose commits are not yet on the default
branch.

A new branch always starts from the default branch, also when another open merge request holds work this
ticket builds on: a forge closes a merge request whose base branch is deleted.

*Done when* the branch is checked out and the working tree is clean.

## 3. Build

**The target's skill** → run it with this brief: the ticket and its plan, the branch, the review's
comments where the ticket came with them, `foundational-refactoring-rules.md`, `principles.md` as guidance, and the outcome wanted —
the plan's slices committed on this branch, its `Done when` commands passing. Whether it also opens the
merge request is its own matter. Then go to step 4.

**The suite's own**, by the kind of ticket:

- **A tooling ticket** → make the change the plan's slices name: a dependency, configuration, a CI job.
  Where the tool rewrites code (Rector, a code-style fixer), the tool's own run is one commit and holds
  nothing typed by hand. No test is written.
- **A baseline ticket** → fix file by file, one commit per file, following the tool's diagnosis. Then
  regenerate the baseline with the command the plan names and commit it by itself. No test is written:
  the existing suite is what notices a behaviour change.
- **Any other ticket** → first the pin: where the plan's pin is new, write it, run it on the code as it
  stands and see it pass, and commit it before any commit moves structure; where it names existing tests,
  run them the same way. Then slice by slice, test-first at the plan's seam: write one failing test through the
  seam's public interface, watch it fail for the expected reason, write the code that makes it pass,
  commit. Tests go where the target's `tests/README.md` puts them; where that file is missing, the
  target's language may have a layout among the Tools' `details` files (`tooling-parser.md` says where they are;
  PHP: `phpunit.md`, *Test layout*). Which tests are kept: `reviewing-a-change.md`, *Tests worth
  keeping*. After a rename or a move, search the whole repository for the old name — strings, docs,
  configuration and tests too, not only the references a tool found; a hit is fixed, or named in the
  merge request because it stays on purpose.

An equivalence script as pin runs the old side from the base commit, in a throwaway worktree outside the
tree, and the new side from the branch, on the same inputs. The outputs are equal. It runs again with every
pass of the checks (step 4); a difference is a red check, so the code is fixed, never the script. The script
is thrown away unless it meets *Tests worth keeping*.

**The work turns out to need a behaviour change** → stop building. The branch stays as it is, and the run
goes to `design-point.md`, the first of the *Two findings*.

A pin that holds only internals and fails *Tests worth keeping* (`reviewing-a-change.md`) is removed in
the branch's last commit; any other stays as a test of the target.

*Done when* every slice of the plan is committed on the branch, and for any other ticket the pin's commit
comes before the first one that moves structure.

## 4. Checks

Run all of these on the branch, after the last commit:

- the plan's `Done when` commands — for a tooling ticket the Stage's Fulfilment check, for a baseline
  ticket the regenerated baseline without the part's entries;
- the target's whole test suite;
- every tool the target already runs as a check — static analysis, code style, the ones its CI file
  calls — over the files this branch touched.

A red check → fix it on the branch and run them all again; the fix changes the code, never the check
(`foundational-refactoring-rules.md`). The same check red again after a second attempt → *A fix that does
not hold*. A check outside the plan's `Done when` that
was already red on the default branch is named as such and left alone.

**The one fact.** For a structural ticket that renames, moves or deletes something that can be referred to
from outside the seam — by a string, configuration, a container, serialisation, reflection, another
language — name the one fact the change is safe because of, and prove it as far as is cheap, best with a
small script or test that calls the real code. Three steps up from nothing: read in the source (file and
line); shown that the bad case cannot occur; run. A fourth, reproduced in the running application, where
that is cheap. "Said" is no step. What stays unproved is recorded as unproved. A script is thrown away
unless it meets *Tests worth keeping* (`reviewing-a-change.md`), then it stays as a test. Where the fact
touches security, privacy, authentication, permissions, a migration, idempotency or concurrency and stays
unproved, the run asks (`design-point.md`, *Open questions*) instead of going on. Not asked of a tooling
or baseline ticket.

*Done when* every command above ran after the last commit and passed, or is named as red before this
work, and where the paragraph above applies the fact is named with how far it was proved.

## 5. Review

The diff of the branch against the default branch is reviewed on two axes, per `reviewing-a-change.md`.
The review may run in a subagent handed that reference, the diff and the plan; it returns its findings sorted per *Sorting the findings* there.
A finding to fix → back to step 3 for it, then steps 4 and 5 again. A slice that lowers reader load nowhere is
not reworked: it is taken off the branch. When no slice is left, the run ends without a merge request;
a comment on the ticket names what the review found, and no rejection is recorded — that stays with a
human.

The notes are handed on to the merge request, the dismissals to the closing report.

A target's skill that built the branch has reviewed it its own way. The suite then reads the diff once
against the plan; a slice found missing is built the suite's own way (step 3) and checked (step 4).

*Done when* the final diff holds every slice of the plan and no finding to fix is left.

## A fix that does not hold

Reached from step 4 or step 5: the same red check, or the same finding, came back after a fix attempt and
a second attempt did not hold either. No count decides it, only that the run is not getting further.

The branch stays as it is, local: not pushed, no merge request. The run lays out a decision point.

- **Findings:** what failed, what was tried twice, and why it did not hold.
- **Options:** leave it as an open question on the ticket (the recommendation); the human takes over the
  branch; end the run.
- An autonomous run takes the recommendation. An interactive run waits for the answer.

The open question (`design-point.md`, *Open questions*) names the branch and says in plain words what
was tried and where it fails, then asks how to go on. The ticket waits until a human replies. The closing
report names the branch and the comment.

The run's checks stay what they were: nothing is deleted, loosened or ignored to turn them green.

## The review's comments

A ticket that comes with its merge request brings the comments on it. They are not all findings. Read them
with the tool the target's **Merge requests** operation names; where it cannot read them, the closing
report says so and the run goes on with what it can see. The author type on the forge tells a bot from a
person; when unsure, a comment counts as a person's.

- **A person's comment** is fixed or answered in its thread, and asked about when it is unclear. The suite
  never dismisses it on its own.
- **A bot's comment** is first checked where that is cheap: when it cites a test or a command, run it. Then:
  - **fix** — it names a plausible defect, a change in behaviour, or a real breach of the target's
    standards;
  - **dismiss** — it is wrong, noise, or contradicts the plan, the pin or a principle (a method to extract
    that has one caller, against `principles.md`, *Reader load*). The reason is concrete;
  - **ask** — it is new, serious, or unclear. In doubt, ask. Whatever touches security, privacy,
    authentication, permissions, a migration, idempotency or concurrency is asked, never dismissed.

The comments with their class are the decision point's findings; the options are to go on as classified
(the recommendation), to change some, or to leave all to the human. An autonomous run may dismiss a bot's
comment with its reason, and turns each *ask* into an open question on the ticket (`design-point.md`,
*Open questions*).

Under each comment handled, one short reply in plain words: for a fix the commit, for a dismissal the
reason, following `forge-facing-writing.md`. The suite does not resolve threads; that stays with the
reviewer. What the target wants kept as a standing pattern belongs in its own `AGENTS.md`, which the suite
reads; it keeps no list of its own.

## Slices every kind of ticket can have

The plan lists them where they apply; they are built in step 3 like any slice, each as one commit.

- **ADR** — for each entry of the plan's `Decisions` that a human answered or confirmed, where the
  target's domain docs (`docs/agents/domain.md`, or what its `AGENTS.md` names in its place) say where
  ADRs are kept: one ADR in the form and numbering of the newest one there. Where they name no such
  place, the decision stays in the plan and goes into the merge request's description.
- **Glossary** — where those docs name a glossary file: a term the work introduced, added as a definition
  and nothing else.
- **Housekeeping line** — a Tool with a **Housekeeping** field adds that line, as a recurring task, to
  the Housekeeping template the target's **Housekeeping** operation names, the first where it names
  several. Where the target has no such
  operation the line is left out, and the Housekeeping Track adds it once its mechanism exists.
- **Ratchet** — where the plan names it (`design-point.md`, *Planning any other ticket*): the step the
  Tool's `details` file gives under its Ratchet, carried out as written once the other slices are built,
  as one commit. For PHPMD it measures again and lowers the limits the change made possible.

## Hand on

To the merge-request step, which names what it needs: with the branch, the one fact and how far it was
proved, where step 4 asked for one.

The implement point is done when the branch holds every slice and step 4's checks are green on its last
commit.
