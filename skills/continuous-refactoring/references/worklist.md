# Reference: the worklist

The **worklist** is the target's open refactoring tickets, each with a Track and a state. It is built once
per run, read-only, and every later step reads it; a step that files, closes or reopens a ticket updates it
in place. Every command comes from the target's `## Refactoring operations` section.

## 1. Find the open tickets

Run the parser without a seed (`tooling-tree-parser.md`) and take every node of `tracks`.

- **With a Candidate operation** → list the open tickets it marks. The tooling tickets are among them:
  filing sets that mark.
- **Without one** → for each node, run **Search** with the node's Name, narrowed to the open tickets.
  Where one listing of all open tickets is short enough to read — a local folder, a small tracker — read
  that listing once instead.
- **Housekeeping tickets.** With a **Housekeeping** operation, find the open ones the way it says.
- **The ticket the call names**, whatever it carries.

A ticket *matches a node* when its title or text names that node's subject as the thing to be set up or
raised. The Name tells siblings apart: "PHPStan" alone is in every level's ticket, "PHPStan Level 3" in
one. A ticket about shrinking a PHPStan level's baseline matches that level's node.

## 2. Assign each to a Track

| The ticket | Track |
| --- | --- |
| matches a node | the Track whose `nodes` list holds that node |
| is a Housekeeping ticket | Housekeeping |
| anything else | Investigation |

## 3. Give each a state

The first row that applies:

| State | The ticket |
| --- | --- |
| **in review** | has an open merge request (below) |
| **blocked** | names a blocker that is not done, or one that has no ticket yet: per **Blocked by**, or, without that operation, in the sentence `Blocked by: …` in its text |
| **waiting** | carries a question no human has answered: one the design point left on it, or reconcile's about its closed merge request |
| **workable** | none of the above |

## 4. Apply the restriction

A restriction in the call removes every ticket and every node it does not cover, before any later step
counts them.

## A Track's trace

A tooling Track has a **trace** once the tracker shows it was scanned before: a ticket of one of its
nodes in any state, or a recorded rejection of one (`rejection.md`, *Finding rejections*). Asked only of a
Track with no open ticket: run **Search** over open and closed tickets with the Names of the Track's
nodes, and stop at the first hit.

- **No trace** → the Track's scan is due.
- **A trace** → the Track is not scanned again by itself. A node of it without an open ticket counts as
  done; a tool that went missing since, or a node the tree gained, is found by a scan the call asks for
  or by the Housekeeping task that re-checks the tooling Tracks.

## A ticket's merge request

Found the first way that applies; where a ticket has several, the newest counts.

- With **Linked merge request** → the way it says.
- Without → search the forge's merge requests, in every state, for the ticket's reference or title, with
  the tool **Merge requests** names.
- **Merge requests** says `none` → the branch the ticket's comments name stands in: merged when
  `git merge-base --is-ancestor <branch> <default branch>` succeeds, open otherwise.
