# 22 — A hand edit in the tool's own commit

Type: task
Status: done
Blocked by: —

**What the plays showed** (tickets 11 and 12, ticket 17, r7 A for ticket 21; named three times, so a ticket under
Q81). `implement-point.md` step 3 says that a tooling ticket's tool run "is one commit and holds nothing typed by
hand", and that for a baseline ticket "the tool's own run is the commit". `php-cs-fixer.md`, *Taking in a rule*, and
the Q80 split for PHPMD and ESLint put a hand edit into that commit: the `false` line or the `<exclude>` deleted, or
the override block written, together with the run that satisfies it. Players followed the Tool file as the more
specific text, but read the two as a contradiction.

**To decide**

- Whether `implement-point.md` allows, in the tool's commit, the one config edit that switches the rule on, as Q80
  decided, and names it so.
- Whether the Tool files then need no change.

**Done when** `implement-point.md` and the Tool files read alike, the scenarios that cover the rollout commits pass,
and tests and validator are green.
