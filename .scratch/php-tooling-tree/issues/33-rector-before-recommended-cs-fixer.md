# 33 — Rector introduced ahead of its recommended `php-cs-fixer` parent

**What to build:** Decide whether/how the suite should nudge a `recommended`-gated child (e.g. `rector-dead-code`) away from being proposed while its `recommended` parent (`php-cs-fixer`) is still unfulfilled but itself proposable — today nothing does this; a `recommended` edge only ever advises, never blocks (ADR-0007), so there's no mechanism that makes the suite prefer the parent when both are simultaneously available.

**Why:** Observed on the same run as ticket 32 (`Art4/legacy-todo`): Rector's dead-code suite was introduced (`rector-dead-code`) while `php-cs-fixer` had never even been proposed yet. Not a `required`-edge violation — Rector's only required parent, `phpstan-level-0-baseline`, was fulfilled — but it undermines the documented purpose of the `php-cs-fixer → rector-dead-code` recommended edge: `skills/refactor-scan/references/php-tooling-tree.md`'s own `php-cs-fixer` node prose says its purpose is "automated code style so later Rector output lands styled." Rector's rewrites landed unstyled as a direct, foreseeable consequence.

**Blocked by:** 32 — this finding may simply resolve once `php-cs-fixer` stops being starved (it would likely get proposed before Rector once it's in the candidate pool at all, since it precedes `rector-dead-code` in the edge table's own order). Worth deciding independently anyway, since a target could plausibly reject `php-cs-fixer` outright (an out-of-scope entry) and Rector would then need to run unstyled either way, recommended-edge-compliant per ADR-0007's own design.

**Priority:** high

**Status:** ready-for-human

- [ ] Decide: should `refactor-prioritize`'s ranking (`skills/refactor-prioritize/SKILL.md` step 2 — Heat/Leverage/Tooling pressure/Risk) give a `recommended`-edge parent extra weight whenever both it and a `recommended`-gated child are simultaneously proposable, so the suite naturally orders them without a hard gate? Or is a soft nudge the wrong mechanism entirely (e.g. `refactor-design`/`refactor-implement` should surface an explicit outlook note recommending the parent first, the way a tooling-tree candidate's MR description already carries an outlook for the *next* node)?
- [ ] If ranking weight is the chosen mechanism, specify exactly how much it should move a `recommended` parent up relative to the other three ranking factors — avoid an unweighted rule that always forces parent-before-child regardless of Heat/Leverage/Risk, since `recommended` (per ADR-0007) is explicitly *not* a hard gate.
- [ ] Cross-reference `docs/adr/0007-required-recommended-edges.md` in whatever design doc/ADR results.

## Comments

> **2026-08-29:** Filed from the legacy-todo reviewer-loop findings log
> (`.scratch/legacy-todo-loop-observation/findings.md`, same finding as ticket 32) after the user asked
> for it to be turned into a real ticket, kept separate from 32 since it's a distinct design question
> (recommended-edge ordering) even if 32's fix happens to resolve this instance of it.
