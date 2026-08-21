# Loop delivers via remembered merge requests

A completed **candidate** is delivered as a **merge request**, remembered in the target repo’s suite state (`docs/refactoring/`). The **loop pass** does not wait for merge or a quiet review. Later passes react to that state. At most two suite merge requests are open; only those the loop remembered count. Outlook and typed rationales are not part of this decision (ticket 19).

Waiting for merge or for review comments to go quiet would trap a pass on human time. Closing the candidate when the merge request appears would lose merge vs. rejection on the backlog. Counting every open forge reviewable would let unrelated team work stop the loop.

## Considered Options

- **Pass completes only when the merge request is merged or the review is quiet.** Rejected: a pass must be able to finish in one agent conversation.
- **Mark the candidate `done` when the merge request is opened.** Rejected: merge and close-without-merge are different outcomes.
- **Cap open reviewables across the whole repo.** Rejected: only suite-remembered merge requests are the loop’s in-flight work.
- **Write the create-mode into `AGENTS.md` / `CLAUDE.md`.** Rejected: those files are read as hints; suite state is not mixed into the human’s agent config.
- **Unlimited new merge requests per pass.** Rejected: two open is the stop; the human is pointed at them.

## Consequences

The pass **starts** from remembered merge-request state: comments → follow-up commits; merged → candidate `done`; closed without merge → `wontfix` plus out-of-scope when the comments support it, otherwise ask the human. If follow-up commits landed, that pass does not also start a new candidate. Bookkeeping-only (merge recorded, rejection learned) may still complete one new candidate if a slot is free.

While a merge request is open, the candidate is `ready-for-human`. Learn on create records the URL and that label — it does not close the issue. One candidate, one branch, one merge request; slices stay on that branch.

A second merge request is allowed only when fewer than two suite ones are open. Stack it (base = the open branch) only when the new candidate is a tooling-tree child of what is in flight or the design depends on it; otherwise parallel onto the default branch. After the parent merges, the next pass retargets or rebases the child.

How to open: read `AGENTS.md` / `CLAUDE.md` first; if neither says, propose `autonomous` and remember `autonomous` | `ask-each-time` | `human-opens` under `docs/refactoring/`. Skills say **merge request**; conversation with the human uses the forge’s word.

The description in this decision is plain: link the candidate, what changed, which tests survive, what CI proves. What the work unlocks (outlook) and any type enum live in ticket 19.

This amends the learn step implied by the orchestrator (issue `done` at pass end) and sits on ADR-0004’s own-branch rule and ADR-0005’s suite root. ADR-0005’s “outlook names the child” waits on ticket 19.
