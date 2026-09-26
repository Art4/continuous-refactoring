# Expected behavior — `Ticket-create-mode: ask-each-time`

An onboarded target whose `config.md` says `Ticket-create-mode: ask-each-time` and `MR-create-mode: human-opens`
(the seed is `php-onboarding-second-invocation`'s project with those two values). Confirms the loop asks before it
creates a ticket and never creates one on its own — the rules in
`skills/continuous-refactoring/references/filing-a-ticket.md`. Not deterministically checkable; run via
`fixtures/harness/run.sh agent-loop php-ticket-create-mode-ask`, local-only and advisory, same posture as the
`php-onboarding-*` fixtures. Asserts what the invocation says, asks and writes, not the wording of skill prose.

## Seeded state

The minimal PHP project of `php-onboarding-second-invocation`, Local Markdown tracker, no Track section in
`bookkeeping.md` (the Safety Net Track is selected and walks its `Open` list, which needs the node's ticket).

## Expected: `/continuous-refactoring`, human answers yes

1. The pass starts as an ordinary Safety Net pass and the loop reports each step before and after it.
2. Once a node is chosen, the loop asks **one question**: whether to create the ticket for it — before anything
   exists on the tracker. No question about a batch is asked (a Track node is never pre-created; only the
   chosen one is asked about).
3. On *yes*: the ticket is created by the loop, reported on its own line with its number, and design writes the
   plan onto that same ticket. No lifecycle skill creates a ticket by itself.
4. `MR-create-mode: human-opens` still governs the merge request: the loop stops with the prepared branch, it
   does not open one. The ticket question and the merge-request mode are independent.

## Expected: human answers no

The pass ends with a report: the node stays a proposal, no ticket, no branch, no `Open` entry change. In the same
message the loop offers once to reject the node for good. Answering *reject* makes `refactor-learn`'s closing
call write the node's `out-of-scope/` entry (and take it out of `Open`); no issue is closed or commented on.
Answering *not for good* leaves everything as is — the next pass proposes the node again and asks again.

## Expected: unattended (no human to answer)

Nothing is created. The pass ends with a report that it waits for a confirmation, and adds that
`Ticket-create-mode` can be set to `autonomous` in the config file. No recommendation is
taken as an answer.

## Not covered here

The batch question for tickets proposed up front (Select mode's structural candidates, secret-history findings) and
the Housekeeping cycle's ticket need targets that reach those steps; none of the current fixtures do.

## Verified

Not yet run live — written together with the setting; a first attended run should confirm the question comes
before any ticket exists and that the refused path writes nothing.
