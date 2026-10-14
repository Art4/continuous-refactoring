# Waiting and workability live in comments, never in labels

> Supersedes [ADR-0053](0053-decision-gate-actively-manages-both-triage-labels.md) and the label part of
> [ADR-0066](0066-flagged-candidate-self-confirms-from-a-plain-comment.md).

The decision gate used to set and clear `needs-info` and `ready-for-agent` on a flagged candidate, and a
human answer had to be followed by a label swap, or by the suite doing the swap for them. The labels
were the triage vocabulary of the engineering skills, and every target needed them.

The suite sets and reads no triage label now. A ticket is **waiting** while its newest comment is an
open question; any newer comment ends the wait, and the next run's design point reads it. A ticket is
**workable** when it carries a plan comment. Both are found by reading the ticket, so they work in a
tracker without labels and for a ticket a human wrote. The repository keeps no triage vocabulary of its
own either.

## Consequences

- A waiting ticket shows as waiting only to someone who reads its last comment. A target that wants it
  in a filtered list marks it by hand.
- The suite is compatible with the engineering skills' conventions but depends on none of them.
