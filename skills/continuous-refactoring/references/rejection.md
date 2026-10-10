# Reference: rejections

A **rejection** is the target's record that something was declined, with the reason: a closed ticket or a
file, in the place the target's **Rejected** operation names. The suite and the human's own triage share
it. Every write here follows from the decision point that led to it — filing, selection or reconcile.

## Recording one

The record names its subject in plain words — for a node its Name and its tool — so that a search finds
it, then the reason as the human or the closed merge request gave it. A blocker a machine can read is one
line of its own: `Blocker: PHP >= 7.4`.

- **Rejected as a closed ticket** → the subject's open ticket is closed the way the operation says, the
  reason with it. No ticket yet → file one per `filing-a-ticket.md` step 3 and close it in the same move.
- **Rejected as a file** → write the file the operation describes; an open ticket on the subject is closed
  with a note pointing to it.

**No Rejected operation yet.** The first rejection is a decision point about the place:

- **Findings:** what is being declined; whether the target has an `.out-of-scope/` folder; how the
  tracker closes a ticket as not wanted.
- **Options:** a file under `.out-of-scope/`; a closed ticket carrying a mark the human names; another
  folder the human names.
- **Recommendation:** `.out-of-scope/` where the target has it, a closed ticket otherwise.

Write the answer as the **Rejected** bullet into the target's `## Refactoring operations` section, in
the shape `refactoring-operations.md` gives under *Bullets the target chooses*, then record the rejection.

## Below the PHP floor

A node in the parser's `php_floor_blocked` cannot be set up while the target allows the older PHP. Left
undecided it would keep Safety Net from ever counting as fulfilled. The recommendation is a rejection whose reason is the target's
declared PHP version and whose blocker is the minimum the parser's reason names: `Blocker: PHP >= 7.0`.
The node then counts as decided, and the parser reports the reversal once the target's floor reaches that
version.

Run the parser again with the rejection in the seed. A node still in the backlog whose `withheld` reason
names the rejected node, with no other parent of that group left to fulfil, is stranded behind it: the
same decision records it as rejected with the same blocker, so it returns together with its parent.

## What depends on a rejected node

After recording a rejection of a node, run the parser with it in the seed (`tooling-tree-parser.md`) and
lay out one more decision point about the tickets that named the node as a blocker. The kind of edge, from
`tree.edges`, gives the recommendation:

| The dependent hangs on the rejected node by | Recommendation |
| --- | --- |
| a `required` edge, or a `required-any` group with no other member left — it is in `closed_by_rejection` | close its ticket, the reason being "depends on <Name>, which was declined" |
| a `recommended` edge, a `resolved` edge through an aggregation node, or a `required-any` group with another member left | remove the blocker from its ticket; the ticket stays |

A dependent without a ticket needs nothing. Options: as recommended, the other way for a ticket the human
names, or leave the tickets as they are.

## Finding rejections

Read them the way **Rejected** says. Each one that names a node's subject is that node's rejection; its
`Blocker:` line, where it has one, becomes the seed's blocker (`{"php": "7.4"}`), and without it `null`.

A record whose only reason is its dependence on another declined node is not handed to the parser: the
parser derives that closure from the parent.

Without a **Rejected** operation nothing is on record.

## Reversing

Offered at reconcile for every entry of the parser's `reversals`, and done whenever a human asks for it.

- A closed ticket → reopen it and remove the rejection's mark; a comment says which blocker is met.
- A file → delete it and file a ticket for the node (`filing-a-ticket.md`).
- Then reopen the tickets that were closed because they depended on it.

A reversed node is undecided again and has an open ticket.
