# Reference: reconcile

Brings tracker and forge into agreement before anything new starts. Reads the worklist (`worklist.md`);
Housekeeping tickets are left to the Housekeeping reference.

Where the call names a ticket, the worklist holds that ticket alone, and so do the findings: its merge
request and whether its Stage was dropped. Rejections and every other ticket are left to a run whose call
names none.

Every decision point here is laid out as `../SKILL.md`, *Decision points*, says: the findings go into the
conversation as a message of their own, then the question — in an autonomous run, then the recommendation
taken.

## 1. Collect the findings

**Merge requests that are no longer open.** For every open ticket whose merge request is merged or closed:

| The merge request | What follows | Recommendation |
| --- | --- | --- |
| merged, and it delivered the ticket's subject | close the ticket per **Done** | close it |
| merged, and it delivered a part — it says so, or a baseline ticket's baseline still has entries | the ticket stays open and is workable again | keep it open |
| closed, and its comments say the change is not wanted | record a rejection (`rejection.md`) | record it, with those comments as the reason |
| closed, and its comments name a defect of the attempt | the ticket stays open and is workable again | keep it open |
| closed, with no reason given | ask the human which of the two it is | ask; in an autonomous run the ticket is left as it is, its state becomes waiting, and the closing report carries the question |

**Rejections whose blocker is met.** Read the recorded rejections (`rejection.md`, *Finding rejections*),
hand them to the parser as `rejected` with their blockers (`tooling-parser.md`), and take each entry
of its `reversals`: what follows is reversing the rejection (`rejection.md`, *Reversing*), and that is the
recommendation.

**Tickets of a Stage the Packs no longer hold.** An open ticket whose title or text names a Stage that was
dropped when the tooling tree became Roles, Tools and Stages: "Test Runner (fallback)" is taken over by
the Stage PHPUnit of the Role Testing. What follows is closing it with a note that says, in plain words and
without the suite's terms, what covers it now (here: PHPUnit as the project's test runner); that is the recommendation. A dropped Stage that never had tickets (the gates and the
aggregation steps) needs nothing.

**In review.** The tickets whose merge request is still open are named in one line, with their merge
requests; nothing follows for them. One whose review asks for changes is named as such; it is worked when the call names
it.

## 2. Lay them out

No finding → say so in one sentence and go on; this is no decision point.

Otherwise one decision point for all of them: each finding with what follows. Options: **do all as
recommended** (the recommendation), **decide one by one**, **leave everything as it is**.

## 3. Act

Carry out what was decided, each write reported by itself, and update the worklist.

Reconcile is done when every finding is acted on or left as decided.
