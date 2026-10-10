# Reference: the Investigation Track

Investigation works the tickets that ask for a change of structure: candidates the suite filed after an
exploration, and tickets a human wrote. It ends by handing one ticket to the design point, or by
returning to Track choice with Investigation marked as tried. Reads the worklist (`worklist.md`); the
order everywhere is `signals.md`, *Order of signal*.

## 1. The tickets

Take the worklist's Investigation tickets — every open ticket found that matches no tooling-tree node and
is no Housekeeping ticket — within the call's restriction. On a tracker that also holds other work, a
ticket a human wrote is among them only through the target's **Candidate** mark or by being named in the
call.

The first row that applies:

| Found | Then |
| --- | --- |
| the call named a ticket | step 4 with that ticket alone |
| the call asked for a scan | step 2 |
| workable tickets | step 4 |
| open tickets, none of them workable | a decision point. Findings: the tickets with their states and merge requests. Options: return to Track choice with Investigation marked as tried (the recommendation), or explore for further candidates → step 2 |
| no open ticket | step 2 |

*Done when* one row is taken.

## 2. Explore

Say in one sentence why the run explores. With no open ticket, add the limit from step 1, so the human
can name a ticket of their own instead.

Run `structural-candidate-search.md`, handing it the call's restriction; it returns **proposals**. For
each, run **Search** over open and closed tickets with the words that name its subject — the module, its
files:

| The hits | The proposal |
| --- | --- |
| an open ticket on the subject | is dropped; that ticket joins the worklist with Track and state, unless it is there already |
| a recorded rejection of the subject (`rejection.md`, *Finding rejections*) | is dropped |
| only tickets closed as done | stays, and its text will name the earlier ticket |
| none | stays |

- **Proposals left** → step 3.
- **None left** → say which places were read and what became of each proposal, then go on as step 3
  ends.

*Done when* every proposal is dropped or stays.

## 3. File

One decision point:

- **Findings:** every proposal left, in order of signal, each with Where, Problem and Signal; then the
  proposals dropped, with the ticket or rejection that covers each.
- **Options:** **file the three strongest** (the recommendation; with fewer than three proposals, all of
  them), **file others** — the human names which, as many as they want —, **file none**.
- Say before the answer is taken: a proposal that is not filed is stored nowhere. A later exploration may
  come upon it again.
- **The tracker also holds other work and the target has no Candidate operation** → the same decision
  point asks how these tickets are marked. Options: a label, named by the human or proposed here (the
  recommendation); no mark. Write the answer as the **Candidate** bullet into the target's
  `## Refactoring operations` section, in the shape `refactoring-operations.md` gives under *Bullets the
  target chooses*. With no mark, say that a later run works these tickets when the call names them.

Write each ticket chosen, strongest first, following `forge-facing-writing.md`:

- **Title** — what gets done, in the target's names for its code: "Gather order pricing behind one
  module".
- **Text** — three parts for a reader who does not know the skill suite. **Where**: the module and its
  files. **Problem**: the friction. **Signal**: in plain words what makes this spot worth the work, with
  the evidence ("changed in 31 of the last 200 commits, called from 14 files"). Then one sentence saying
  that what the application does stays the same.
- **Marks** — the **Candidate** mark. The **Priority** mark is the human's to set.

Create each the way the tracker file says, report it by itself, and add it to the worklist as workable.

Step 3 ends one of two ways:

- **The worklist holds a workable Investigation ticket** — just filed, joined in step 2, or there before
  → step 4.
- **It holds none** → return to Track choice with Investigation marked as tried.

*Done when* every proposal chosen has a ticket, and the others are left unfiled by decision.

## 4. Select

Order the workable tickets:

1. Tickets carrying the **Priority** mark first, where the target has that operation.
2. Then in order of signal. Read each ticket's text and the code it names; a ticket that states no
   signal gets one named from the catalogue.

Then check the first ticket against the code: the module or files it names still exist, and the friction
it describes is still there. A ticket whose subject is gone — removed, or already reworked — is to be
closed with a note saying what was found; check the next one.

The decision point:

- **Findings:** the tickets whose subject is gone; the workable tickets in order, each with its signal
  and its place in a few words; in one line the tickets in review, blocked and waiting.
- **Options:** close those whose subject is gone and work the first remaining ticket (the
  recommendation); work another one; end the run.
- A ticket the human chooses gets the same check before the hand-over. Its subject gone → this decision
  point is laid out again with it among the first group.

Close each ticket whose subject is gone per **Done**, with its note, and report each.

**A ticket the call named** is treated as `selection.md` step 1 treats one, the check above standing in
for the pick-up check.

*Done when* one ticket whose subject still stands is chosen, or the list is used up.

## 5. Hand over

- **A ticket to work** → assign it per **Claim**, where the target has that operation, and hand it to the
  design point (step 8 of the run) with: the ticket, the Track, the run's mode and the call's
  restriction.
- **None** — every ticket was closed or left → say so and return to Track choice with Investigation
  marked as tried.

Investigation is done when one ticket is handed to the design point, or Investigation is marked as tried.
