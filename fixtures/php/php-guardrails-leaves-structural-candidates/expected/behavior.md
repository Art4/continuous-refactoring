# Expected behavior — a Guardrails pass leaves structural candidates for Investigation

A structural candidate that already has an issue belongs to the Investigation Track: a Safety Net or Guardrails pass
doesn't pick it up (`skills/refactor-scan/SKILL.md` step 3b, *Track-scoped*). Seeded from `php-guardrails-first-run` —
every Guardrails node already resolved, no `## Guardrails` section yet, so the Guardrails Track is selected and finds
nothing to propose — plus an open, unplanned `refactor:candidate` issue (`.scratch/refactor/issues/01-shallow-greeter.md`)
that is not a tooling-tree node's. Not deterministically checkable; run via
`fixtures/harness/run.sh guardrails-track php-guardrails-leaves-structural-candidates --opencode`, local-only and
advisory.

## Expected: `refactor-scan` pass (Guardrails selected)

1. Step 3b finds the issue and **does not** hand it forward: no proposal, no design, no implement. The scan's output says
   only that one candidate waits for an Investigation pass.
2. The pass ends with the Guardrails Track's own outcome — `## Guardrails` written with `Last scan` and an empty `Open`
   (as in `php-guardrails-first-run`) — and the closing **Status** line names the waiting candidate count ("1 other candidate
   waits for an Investigation pass").
3. The issue file is untouched: no plan, no label change, no `Open` entry.

## Variants

- The same issue carrying `refactor:priority`: it is picked up in this same Guardrails pass (priority is exempt).
- The same target with **Investigation** selected: the issue is proposed as usual.
