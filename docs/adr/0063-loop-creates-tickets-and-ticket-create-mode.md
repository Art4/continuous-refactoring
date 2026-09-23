# The loop creates tickets, gated by a `Ticket-create-mode`; `Create-mode` becomes `MR-create-mode`

> Amends [ADR-0010](0010-orchestrator-explicit-data-flow.md): `refactor-loop` stays a thin pipe for
> everything except one write — creating a new ticket. It creates the ticket from a draft a lifecycle
> skill hands back.
>
> Amends [ADR-0047](0047-tooling-tree-proposals-are-pre-filed-before-ranking.md): pre-filing is no
> longer done inline by `refactor-prioritize`; the loop does it from prioritize's drafts.
>
> Amends [ADR-0024](0024-loop-config-interview-decides-tracker-create-mode-storage.md) and
> [ADR-0025](0025-agents-md-gets-a-create-mode-pointer-not-the-value.md): `Create-mode` is renamed,
> and the interview gains one question.

Two things surfaced while watching runs. First, `bookkeeping.md`'s `Create-mode` reads as if it governed
everything the loop creates, but it only governs how a **merge request** gets opened. Second, there is no
way to be asked before a **ticket** is created, although creating one is as visible to a team as opening
a merge request — and a full run can create several tickets before the human sees any work
(ADR-0047's pre-filing of every unblocked node).

A ticket-create-mode cannot live in the skills that create tickets today. `refactor-prioritize`,
`refactor-design` and the Select mode run in fresh subagents, and a subagent cannot ask the human.
Only `refactor-loop` can — the same reason it already finishes a push or a merge-request opening that
`refactor-implement`'s subagent could not.

## Decision

**`Create-mode` is renamed `MR-create-mode`**, values unchanged (`autonomous`, `ask-each-time`,
`human-opens`). A `bookkeeping.md` still carrying `Create-mode` is read as `MR-create-mode`;
`refactor-learn` writes the new name the next time it writes that file.

**A new `Ticket-create-mode` field** with two values: `autonomous` and `ask-each-time`. No `human-opens`
— the loop needs the ticket's number straight away, so a human-created ticket has no place in the flow.
The field's absence means `autonomous`, so no existing target changes behaviour or is asked anything on
update. The onboarding interview asks it as a new question right after the tracker question and before
the merge-request question; the Summarize/Record steps and `AGENTS.md`'s pointer section name both
modes.

**The loop creates new tickets; the skills hand it drafts.** A lifecycle skill that would create a
ticket instead returns a draft — title, labels, body, and the key used to recognise an existing ticket
(`Tooling tree: <Name>`, or Where/Problem/Signal for a structural candidate). The loop applies the mode,
creates the ticket and passes its number to whoever needs it. Only creation moves: comments, body
updates and label changes on an existing ticket stay with the skills. The creation sites are
`refactor-prioritize` (pre-filing and Select mode), `refactor-design` (which no longer creates a ticket
of its own — the loop has already created it right after ranking, and design updates it), `refactor-learn`
(secret-history findings) and the Housekeeping Track's own cycle ticket, which reads the same rule from
the shared reference because it does not run through `refactor-loop`. The rule, the draft's shape and the
dedupe live in `skills/continuous-refactoring/references/filing-a-ticket.md`, alongside
`opening-a-merge-request.md`.

**`ask-each-time` semantics.**
- *Pre-filing:* one batched question per pass — "create tickets for these N unblocked nodes?". Yes →
  all of them; no → none, and only the ticket of the chosen candidate is asked about afterwards.
- *Chosen candidate:* asked before it is created. A refusal ends the pass with a report; the node stays
  a proposal. The loop offers once to reject it for good (an `out-of-scope/` entry, written by
  `refactor-learn`), so it does not come back to be asked every pass.
- *No human to ask (unattended run):* nothing is created. The pass reports that it waits for a
  confirmation, and points out that `Ticket-create-mode` can be set to `autonomous` in `bookkeeping.md`.

## Considered Options

- **`refactor-scan` creates the tickets.** Rejected: scan always runs in a subagent and cannot ask, so
  `ask-each-time` would need a hand-back anyway; it only sees tooling-tree nodes, not structural
  candidates or findings; and it would give up "detect, never write" (ADR-0010) for one of the four
  creation sites.
- **The loop only gates, the skills still create** (a "approved" flag handed down). Rejected: it keeps
  the mode's logic and the ticket mechanics in several skills. It would matter only if the lifecycle
  skills were meant to run on their own; the docs already call them implementation detail.
- **Also let the loop do comments, body updates and labels.** Rejected: only creation needs the human's
  answer, and it would make the loop a tracker client.
- **A `human-opens` value for tickets.** Rejected, see above.
- **Ask for each pre-filed node separately, or skip pre-filing whenever `ask-each-time` is set.**
  Rejected: the first turns one pass into five or ten questions; the second removes the early visibility
  ADR-0047 wanted, and the age signal for nodes never chosen.
- **`Issue-create-mode` as the field name.** Rejected: the settings and questions the human sees use the
  word "ticket" (the engineering skills' own wording); the glossary's **Ticket** entry ties it to "issue".

## Consequences

- Prioritise's Rank mode no longer has the side effect of creating tickets; it returns drafts. Ranking
  still scores a freshly created ticket's **Age** as zero, as before.
- Design's "file fresh" branch disappears; the ticket always exists when design starts. Design's
  update-in-place branch for a minimal ticket becomes the only path.
- `refactor-loop` gains the mode check and the creation step (after ranking); the skill files that
  create tickets today, `opening-a-merge-request.md`'s sibling `filing-a-ticket.md`, the Housekeeping
  process, the onboarding interview, `refactoring-bookkeeping.md`, the docs and the 38 fixtures naming
  `Create-mode` change accordingly.
- The `ticket` glossary entry is a human-facing name, not a rename: skills keep saying "issue".
