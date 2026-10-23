# Reference: the worklist

The **worklist** is the target's open refactoring tickets, each with a Track and a state. It is built once
per run, read-only, and every later step reads it; a step that files, closes or reopens a ticket updates it
in place. Every command comes from the target's `## Refactoring operations` section.

## 1. Find the open tickets

Run the parser without a seed (`tooling-parser.md`) and take every Stage of `tracks`.

**The call names a ticket** → the worklist is that ticket alone, whatever it carries: read it and go on
with step 2. A ticket it names as its blocker is read for the state, not added. Otherwise:

- **With a Candidate operation** → list the open tickets it marks. The tooling tickets are among them:
  filing sets that mark.
- **Without one** → for each Stage, run **Search** with the Stage's Name, narrowed to the open tickets.
  Where one listing of all open tickets is short enough to read — a local folder, a small tracker — read
  that listing once instead. A place the section gives to the suite's tickets alone counts whole; from
  any other listing keep the tickets that match a Stage.
- **Housekeeping tickets.** With a **Housekeeping** operation, find the open ones the way it says.

A ticket *matches a Stage* when its title or text names that Stage's subject as the thing to be set up or
raised. The Name tells siblings apart: "PHPStan" alone is in every level's ticket, "PHPStan Level 3" in
one. A ticket about shrinking a PHPStan level's baseline matches that level's Stage.

## 2. Assign each to a Track

| The ticket | Track |
| --- | --- |
| matches a Stage | the Track whose `nodes` list holds that Stage |
| is a Housekeeping ticket | Housekeeping |
| anything else | Investigation |

## 3. Give each a state

The first row that applies:

| State | The ticket |
| --- | --- |
| **in review** | has an open merge request (below) |
| **blocked** | names a blocker that is not done, or one that has no ticket yet: per **Blocked by**, or, without that operation, in the sentence `Blocked by: …` in its text |
| **waiting** | its newest comment is an open question (`design-point.md`, *Open questions*); or, for this run, reconcile's question about its closed merge request went unanswered |
| **workable** | none of the above |

## 4. Apply the restriction

A restriction in the call removes every ticket and every Stage it does not cover, before any later step
counts them.

## A Track's trace

A Stage is **known** once the tracker shows it was dealt with before: a ticket of it in any state, or a
recorded rejection of it, of its Tool or of its Role (`rejection.md`, *Finding rejections*). A tooling
Track has a **trace** when every Stage of it that applies is known. Asked only of a Track with no open
ticket, over the Stages of the Track's `nodes` in a call with the Packs that apply (`track-scan.md`,
*Judging*) and without the Stages whose own *Applies when* does not hold: where one listing of all
tickets, open and closed, is short enough, read it once; otherwise run **Search** with each Stage's
`search` words over open and closed tickets, and stop at the first Stage that is not known.

- **A Stage is not known** → the Track's scan is due, and it judges the Stages that are not known.
- **Every Stage is known** → the Track is not scanned again by itself. A Stage of it without an open
  ticket counts as done; a tool that went missing since is found by a scan the call asks for or by the
  Housekeeping task that re-checks the tooling Tracks.

## A ticket's merge request

Where a ticket has several, the newest counts.

- With **Linked merge request** → the way it says.
- Without it, and always for a baseline ticket, whose merge requests deliver a part and carry no closing
  reference → search the forge's merge requests, in every state, for the ticket's reference or title,
  with the tool **Merge requests** names.
- **Merge requests** says `none` → the branch the ticket's comments name stands in: merged when
  `git merge-base --is-ancestor <branch> <default branch>` succeeds or the branch is gone, open
  otherwise. Of several branches named, the newest comment's counts.
