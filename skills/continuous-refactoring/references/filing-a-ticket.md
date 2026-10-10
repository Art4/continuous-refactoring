# Reference: filing tickets

Turns proposals into tickets on the target's tracker, through one decision point. A ticket is found again
by its subject, so the subject is written in plain words; the suite sets no marker of its own. Commands
come from the target's tracker file; the wording follows `forge-facing-writing.md`.

## 1. Search first

For every proposal, run **Search** over open and closed tickets with the node's `search` words — for a
proposal without a node, with the words that name its subject. Keep every hit that is about the subject,
and settle on one:

| The hits | The proposal |
| --- | --- |
| an open ticket on the subject | continues on that ticket; nothing is filed |
| a recorded rejection of the subject | is dropped: the node is rejected (`rejection.md`) |
| only tickets closed as done, while the node is not fulfilled | is filed new, and its text names the earlier ticket |
| several of these | all are shown; recommended is the open one, else the newest |
| none | is filed new |

## 2. The decision point

- **Findings:** the proposals in the order they were handed in, each with its Name, its Purpose in one
  line, what blocks it, and its hits from step 1. Then what the scan laid out for this step: nodes below
  the PHP floor, with the rejection proposed for each; open tickets whose node is already fulfilled, to
  be closed with a note; the question on a node whose judgement stayed open.
- **Options:** **as recommended**, **file some** — the human names which —, **file none**. Per proposal
  the human may instead **decline the node**, which records a rejection (`rejection.md`).
- **Recommendation:** file every proposal that carries no open question; record the proposed rejections;
  close the tickets whose node is fulfilled. A proposal with an open question is filed once a human
  answered it; an autonomous run leaves it unfiled and carries the question into the closing report.
- A proposal neither filed nor declined is not stored anywhere; the next scan offers it again.

## 3. Write

In the order handed in, so that a ticket's blockers exist before it does:

- **Title** — what gets done, with the node's Name in it: "Introduce PHPStan Level 0", "Raise to PHPStan
  Level 3", "PHPStan Level 2: shrink the baseline".
- **Text** — for a reader who does not know the skill suite: what the tool is and what the project gains
  (the node's Purpose), what the merge request will contain (its MR scope), and both of its `search` words
  written out.
- **Blockers** — the tickets of the nodes that block it, the way **Blocked by** says; without that
  operation as one sentence in the text, `Blocked by: <ticket>, <ticket>`. A blocking node that has no ticket is named in that sentence by its
  Name, in both cases, so the ticket reads as blocked. A blocker out of a `required-any` group adds that
  one of them is enough.
- **Marks** — the **Candidate** mark, where the target has that operation.

Create each ticket the way the tracker file says, report it by itself, and add it to the worklist.

Filing is done when every proposal has a ticket, continues on an existing one, or was declined or left
unfiled by decision.
