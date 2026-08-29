# 32 — `php-cs-fixer`/`composer-audit` starved indefinitely while the PHPStan chain keeps advancing

**What to build:** Determine why, on a real dry run, `php-cs-fixer` and `composer-audit` — both `required` children of `composer` (and `composer-audit` also of `ci-runner`), both parents fulfilled early in the run — were never proposed at all, while the PHPStan level chain kept advancing through five further nodes (`phpstan-level-0-baseline` through `phpstan-level-1`, plus `phpunit`/`test-runner-if-missing`/`rector-dead-code`) in the same run. Fix whichever layer actually causes it.

**Why:** Observed on a real run (`Art4/legacy-todo`, watched via the reviewer-loop playbook). `docs/refactoring/config.md` on the target's `main` read `Fulfilled nodes: ci-runner, composer, loop-config, phpunit, phpstan-level-0-baseline, phpstan-level-1, test-runner-if-missing` at the point this was noticed — `php-cs-fixer` and `composer-audit` never appeared as an issue or MR in the entire run, despite both being unblocked (per the edge table) since shortly after `composer`/`ci-runner` merged.

**Important — this is not (yet) a confirmed bug in this suite's own deterministic parser.** Tracing `skills/refactor-scan/references/tooling_tree.py`'s `next_candidates()` by hand against that exact repo state (composer + ci-runner fulfilled, nothing else): it iterates `tree["order"]` (edge-table order: `loop-config, composer, ci-runner, php-cs-fixer, phpunit, test-runner-if-missing, composer-audit, phpstan-level-0-baseline, ...`) with no special-casing that would skip `php-cs-fixer` — it should have been the **first** node proposed, before `phpunit`. So the Python parser, as currently written, does not reproduce this starvation. The watched run either used the manual/LLM tree-walk fallback (`tree-walk-prompt.md`, e.g. no `python3` access in that harness) instead of the real parser, or the watched agent (a separate application, "opencode") runs its own, non-compliant reimplementation of the tree logic rather than this suite's own skills.

**Blocked by:** none directly, but see 31 (PHP-floor precheck) for a related but distinct prioritization gap in the same neighborhood.

**Priority:** high

**Status:** ready-for-human

- [ ] Determine which code path the watched run actually took (parser vs. LLM fallback vs. a third-party reimplementation) before assuming `tooling_tree.py` needs a fix — it may not.
- [ ] If the LLM tree-walk fallback (`skills/refactor-scan/references/tree-walk-prompt.md`) is the culprit: it currently has no test coverage guaranteeing it enumerates *all* unblocked required children in one pass, not just the ones an LLM's salience naturally gravitates to (the "flashy" PHPStan/Rector chain over pure-infra `php-cs-fixer`/`composer-audit`). Add that coverage, or tighten the prompt's instructions to make the omission harder.
- [ ] If a third-party reimplementation is the culprit: not this suite's bug to fix, but worth recording as a compatibility note somewhere agents integrating with this suite would find it.
- [ ] Either way, decide whether `refactor-scan`'s `## Output` needs a stronger assertion (e.g. "the proposal set names every currently-unblocked node, not a priority-truncated subset past the `limit`") so a future implementation drift like this is easier to catch by inspection.

## Comments

> **2026-08-29:** Filed from the legacy-todo reviewer-loop findings log
> (`.scratch/legacy-todo-loop-observation/findings.md`, "Finding — Rector vor php-cs-fixer vorgeschlagen;
> php-cs-fixer bislang nie propagiert") after the user asked for it to be turned into a real ticket. The
> `tooling_tree.py` code-trace above was done while filing this ticket, not during the original
> observation run.
