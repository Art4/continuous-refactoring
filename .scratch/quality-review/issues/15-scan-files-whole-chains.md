# 15 — A scan files a whole chain at once

Type: task
Status: open
Blocked by: —

**What the plays showed** (r8 for ticket 08, then r8 on 2026-11-11; named twice, so a ticket under Q54). A due scan
turns every Stage of the backlog into a proposal. On a target with PHPStan Level 6 in review, it files Levels 7–10 at
once, each blocked behind the one before, and it files the PHPMD Rollout before PHPMD itself exists; r8's Variant A
filed eleven tickets in one run. No text caps or defers the far members of a chain, and nothing says whether that is
intended. A human who sees four PHPStan tickets that cannot start for months may read it as noise. A related gap: a
rollout Stage proposed before its adoption has no title rule (`track-scan.md` gives "PHPMD: take in the remaining
rules" only for a config with `Not yet:` excludes; `filing-a-ticket.md` gives "Introduce …" and "Raise to …"), so the
player improvised one.

**To decide**

- Whether a scan files a whole chain (every Stage known, each blocked by the one before), or only the next member of
  each chain, the rest found by a later scan once it is unblocked.
- If only the next member: how the scan report still tells the human what lies behind it.
- The title of a rollout Stage filed before its adoption, or whether that case disappears with the first answer.

**Done when** the scan's text says which members of a chain it files, the title rule covers what is filed, the
scenarios that cover the scan (r8 among them) pass, and tests and validator are green.

## Comments

**2026-11-12 — Decided** (Q63–Q69). A scan files a chain at most two levels deep, counted over the whole tracker
(open tickets at their own level). The parser computes the levels and returns `beyond_horizon` per Track; a Stage
beyond it is accounted for in the trace. The horizon is a fixed 2, with a new ADR amending ADR-0073. The scan report
names the held-back Stages in one line; a call naming such a Stage files it with the blockers between. A rollout
Stage is always titled "<Tool>: take in the remaining rules".
