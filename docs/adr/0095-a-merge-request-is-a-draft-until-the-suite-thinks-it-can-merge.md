# A merge request is a draft until the suite thinks it can merge

A merge request of the suite opened ready for review, before the Driver's review, and stayed ready through a request
for changes. A human or a reviewer could not tell "the suite is still on it" from "the suite thinks this can merge",
and a human had no way to tell the suite to leave one alone short of closing it.

ADR-0031 opened candidates as drafts until a bookkeeping commit landed; that went with the bookkeeping. Its lesson
stays: a run interrupted between opening and marking ready leaves a draft nothing picks up, unless something looks for
it. pstack opens every pull request ready, never as a draft; the suite goes the other way, because its review comes
after the merge request opens.

## Decision

- **Draft means "the suite does not think this can merge".** Every merge request opens as a draft. Ready only after
  the Driver's verdict mergeable; a run alone — and Housekeeping alone — marks it ready itself once CI is green,
  still running or unreadable, its own review having run before the merge request opened. The Driver's call says
  `under the Driver`.
- **Back to draft** on a request for changes, a question to the human, a handover after the reworks ran out, a rework
  starting on a ready one — always with a comment saying why. A base update leaves the state as it found it.
- **A draft left behind** — a draft of the suite with no comment of the Driver since its last commit — is taken up in
  the Driver's *Ready*: reviewed with green checks, reworked otherwise.
- **The human's hold.** A draft is the suite's when it opened the merge request as a draft and it was never ready
  since, or when its newest change to draft came with the suite's comment. Any other draft is the human's: no
  review, no rework, no base update, no call naming its ticket, until the human marks it ready or comments.
- **CI that skips drafts**: no pipeline for the push where earlier merge requests had one → the run marks it ready
  so CI runs, and says so.

## Considered Options

- **Tell the human's draft by the timeline's actor.** Rejected: the suite often works under the human's own account,
  so the actor is the same for both.
- **Make the merge request a draft during a base update.** Rejected with the option above: a clean update posts no
  comment, so its draft would look like the human's hold if the run stopped midway.
- **Open ready, as before.** Rejected: the state on the forge would keep saying nothing about the suite's view.

## Consequences

- *Draft and ready* in `opening-a-merge-request.md` is the one place for the commands and for whose draft a draft is;
  the Driver, the worklist's base update check and the docs point to it.
- A reviewer or bot that skips drafts — the field eval does — sees a merge request of the suite once it is ready.
- A forge without drafts opens every merge request ready, as before.
