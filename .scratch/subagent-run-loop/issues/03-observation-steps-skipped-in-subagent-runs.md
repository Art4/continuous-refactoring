# 03: Observation — steps skipped by runs inside a subagent

**Status:** done — limit documented, PR #193; skill text unchanged

## Observation

Same loop as 01. Several runs replaced the review step (`implement-point.md`, step 5) with a reading of
their own; round 13 skipped the plan comment and its own review. From round 14 the driving agent added
"do not shorten" to every run prompt. The driving agent's separate review subagent caught the gaps and,
on !73 (Psalm taint), a real defect the run had missed: no taint source for `Server\Request`, `bin/` not
scanned.

## Likely cause

A subagent cannot start subagents of its own in Claude Code. Every step the skill lets a run hand to a
subagent — the review, scan judging, the structural candidate search — runs in the run's own context
instead, which fills up, and the run shortens.

## Why no change yet

Per the rule "fix gaps that force a wrong decision or skip a required step; leave one-off misses to
implementation/review": a required step was skipped more than once, but the loop's separate review
compensated. Watch further loops; if it recurs, decide between a skill-text change and documenting the
limit (`docs/known-limitations.md`: a run inside a subagent does every step in its own context).

## Comments

- 2026-10-23: Documented in `docs/known-limitations.md` with the driving agent's own review as the remedy; skill text still unchanged. Reopen if a run outside a subagent skips steps too.
