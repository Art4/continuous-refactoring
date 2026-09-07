# Select mode batch-files candidates; Security/Blast-Radius signals bypass the backlog cap

> Amends [ADR-0038](0038-candidate-selection-moves-to-prioritize.md): Select mode's own decision to
> "pick the single strongest, set the rest aside" is reversed — it now files every genuine candidate
> found. ADR-0038's other decisions (the two-dispatch mechanism, minimal filing, `refactor-design`
> grounding/grilling/commenting afterward) are unchanged.

Observed live while reviewer-loop-watching `Art4/legacy-todo`: a filed security finding (an
unauthenticated database download, purely a byproduct of web-root layout) would have waited behind
whatever won ranking that pass under the existing "pick the single strongest, set the rest aside"
rule, and today's five ranking factors (heat, leverage, tooling pressure, risk, skip streak) have no
way to mark it urgent in the first place. Settled via `/grill-with-docs` (`signals` ticket 1) —
supersedes `.scratch/php-tooling-tree/issues/36-candidate-backlog-stop-threshold.md`, which had
already flagged `refactor-scan`'s five-issue backlog cap as chosen generously rather than derived from
anything.

## Considered Options

- **Raise or lower the flat five-issue cap** (ticket 36's own original framing, e.g. matching
  `refactor-prioritize`'s two-MR in-flight threshold). Rejected — a single number can't distinguish
  "a queue of ordinary tooling work" from "an unfixed security hole," which is the actual problem;
  changing the number doesn't add that distinction.
- **A three-tier, continuously scaling quality bar** for the capped tier (looser under 2 open, medium
  under 4, strict at the edge). Rejected during grilling — more complexity than the actual benefit
  (filling an empty backlog faster) justifies; a two-state bar (open under 5 → any solid candidate;
  at 5 → stop) does the same job more simply.
- **Let the new Signal factors also drive `refactor-prioritize`'s Rank mode** (comparing tooling nodes
  and gates against each other), not just Select mode. Rejected — most of the new factors (bus
  factor, domain criticality, observability) don't translate to an abstract tooling-tree node; Rank
  mode's existing five factors already fit that comparison well and stay untouched.

## Decision

**Select mode files every genuine candidate found**, not just the strongest — for both a structural
search and a PHPStan baseline-shrink group pick. Ranking among what's found still decides which one
this pass actually pursues (carried to `refactor-design`); the rest become ordinary open issues for a
future pass to rank normally.

**Two backlog-admission tiers**, by the candidate's Signal
(`skills/refactor-prioritize/references/signals.md`, a new documentation-only catalogue — seven new
factors added to the six existing structural friction cues, no execution or adoption tracking):

- **Priority** (`refactor:candidate` + new `refactor:priority` label) — Signal is security or blast
  radius of inaction, the two factors where delay itself makes the problem worse. Always filed,
  exempt from the backlog cap.
- **Capped** (`refactor:candidate` only) — everything else. Filed while fewer than 5 open capped
  issues exist; at 5, filing stops, same shape as today just split from the priority count.

`refactor-scan` step 1 now tracks two counters instead of one, so priority admissions can never choke
off ordinary proposals — a priority issue existing shouldn't itself become the new version of the
problem the cap exists to prevent.

**Priority affects admission only, not ranking.** A priority-tier issue still competes in a future
Rank mode pass using the existing five factors, unchanged — no queue-jump. The guarantee is
"visible immediately," not "worked next."

**"Safety Net" stays prose-only.** `CONTEXT.md`'s "Tooling tree" term, every file/directory name, and
`tooling_tree.py` are unchanged — 127 existing references made a real rename disproportionate to a
naming preference. "Safety Net" appears only in `docs/playbooks/loop.md`, as a human-facing reading
aid for the same concept.

## Consequences

`refactor-scan`, `refactor-prioritize`'s two Select-mode reference files, and `CONTEXT.md` (new
`Signal` glossary entry) each gain a small, clearly-delimited addition. `.scratch/php-tooling-tree/
issues/36-candidate-backlog-stop-threshold.md` closes as superseded by this decision. A backlog can
now legitimately hold more than one unactioned candidate at once by design (previously an implicit,
undocumented possibility) — `refactor-prioritize`'s Rank mode already handles a multi-item backlog
today, so no further change was needed there.
