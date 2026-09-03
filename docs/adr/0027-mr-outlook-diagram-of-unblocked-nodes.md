# MR outlook: no type enum, and a fan-out diagram of newly-unblocked nodes

> Amends [ADR-0009](0009-merge-request-outlook-and-delivered-label.md): the outlook sentence it
> decided is unchanged. This settles the type-enum question that ADR left open (none) and adds a
> Mermaid diagram alongside the sentence.

Ticket 19 split into two questions when ADR-0009 decided the first: whether the description must
end with an outlook (decided there — yes, tooling-tree candidates only, one plain sentence naming
the next node), and whether a closed type enum names the quality dimension a merge request moved
(left open — "not asked for, adds a closed vocabulary nobody has grilled yet").

Grilling ticket 19's remaining half (`/grill-me zu Ticket 19`) surfaced a real gap in the outlook
sentence itself, not just the type-enum question: `roadmap(steps=1)` names exactly one top-priority
pick, but a single fulfilled node routinely unblocks several real siblings at once (`composer`
alone unblocks `phpunit`, `test-runner-if-missing`, and `phpstan-level-0` — see
`skills/refactor-scan/references/tooling_tree.py`'s `next_candidates()`). The sentence picks one
and silently drops the rest.

## Decision

**Type enum: none.** The outlook sentence's plain-language opener (ADR-0009) already covers most of
what a type would have named — what this unlocks for the project, in the reviewer's own terms — for
less ongoing cost than maintaining a closed vocabulary that needs a new entry every time the tooling
tree grows a node family. Ticket 19 closes.

**Outlook diagram**, tooling-tree candidate only, added alongside the existing sentence (never
replacing it): once the description's outlook sentence is written, also render a Mermaid
`flowchart` naming every node this specific candidate's fulfilment newly makes proposable — not a
multi-step roadmap simulation, only this one candidate's direct effect. Landed node as the root,
one labelled edge (`required`/`recommended`/`required-any`) to each newly-unblocked node, each
labelled by its **Name**. Only when there are **two or more** — a one-box diagram repeats the
sentence for no benefit. Computed by a new function,
`skills/refactor-scan/references/tooling_tree.py`'s `directly_unblocked_children()`, exposed via a
new `--unblocked-by <node>` CLI flag on the same script the sentence's own `--steps 1` call already
uses (`skills/continuous-refactoring/references/opening-a-merge-request.md`). Not available where
`python3` isn't — the sub-agent/inline fallback (`tree-walk-prompt.md`) keeps producing the sentence
only, not extended for this.

## Considered Options

- **A multi-step roadmap chain instead of a fan-out.** Rejected — `roadmap()` simulates a *sequence*
  of `refactor-prioritize` picks that haven't been made yet; drawing it as settled would suggest an
  order the loop hasn't actually decided. The fan-out only reports what this one candidate's
  fulfilment structurally opens, a fact, not a prediction.
- **Replace the sentence with the diagram.** Rejected — the sentence is the only part still legible
  in a terminal (`gh pr view`), a mailer, or any other non-rendering context; the diagram is additive.
- **A full before/after diff of `next_candidates()` to compute "newly unblocked."** Rejected — a
  pass delivers exactly one candidate per merge request
  (`opening-a-merge-request.md`: "one candidate per MR"), so a second full tree scan would answer
  the same question a direct walk over the landed node's own edges already answers, for a fraction
  of the cost.
- **Deciding the type-enum question by not deciding it (leaving ADR-0009's provisional "no enum"
  as-is, without a formal grill).** Rejected — ADR-0009 explicitly flagged it as provisional, not
  decided; ticket 19 stayed open specifically so this got a real answer instead of a default nobody
  actually chose.

## Consequences

`skills/continuous-refactoring/references/opening-a-merge-request.md`'s **Outlook** section gains
the diagram step and the extended CLI invocation. `tooling_tree.py` gains
`directly_unblocked_children()` and the `--unblocked-by` flag — purely additive, `next`/`roadmap`/
`detected` unchanged. Ticket 19 is done; the diagram itself is tracked as its own ticket
(`.scratch/suite-self-containment/issues/47-mr-outlook-diagram-of-unblocked-nodes.md`), implemented
in the same change as this ADR.
