# Reference: reconcile

Brings tracker and forge into agreement before anything new starts. Reads the worklist (`worklist.md`);
Housekeeping tickets are left to the Housekeeping reference.

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
hand them to the parser as `rejected` with their blockers (`tooling-tree-parser.md`), and take each entry
of its `reversals`: what follows is reversing the rejection (`rejection.md`, *Reversing*), and that is the
recommendation.

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
