# PHPStan Levels 4 and 5 wait for Rector; the Rector PHPUnit Set is a Guardrails Stage

> Amended by [ADR-0086](0086-tools-on-request.md): `after` is renamed `waits_for`.

> Keeps [ADR-0040](0040-signal-tool-nodes-and-tree-edge-simplification.md)'s cut at PHPStan Level 5: the Safety Net still ends there.

The PHPStan level chain and the Rector Stages were independent apart from Rector Type Coverage waiting for Level 3. A
level's baseline was fixed by hand, even where a Rector set would have removed the same findings mechanically a few
merge requests later. Level 4 reports basic dead code (unreachable statements, conditions and type checks that are always
true or false), which is what Rector's Dead Code set removes. Level 5 checks the types of the arguments passed to methods
and functions; fixed before Type Coverage, its findings are judged against docblock types that the rewrites then replace
with native ones, and part of the work is done twice. No Rector set fixes Level 5 findings directly.

Moving Level 5 to Guardrails was weighed and rejected: its argument-type checks are what catches a wrongly passed
argument after a method is moved or a signature changed, the core of the structural work the Safety Net protects.

## Decision

- **`phpstan-level-4` has `after: ["rector-dead-code"]`.**
- **`phpstan-level-5` has `after: ["rector-type-coverage"]`.** Type Coverage itself waits for Dead Code, Code Quality,
  Code Style and Level 3, so Level 5 waits transitively for most of the Rector family. Accepted: the two Tools are used
  side by side, and every Stage involved is a Safety Net Stage, so the Safety Net is not held back longer, only the order
  inside it changes.
- **Both are `after`, not `requires`.** A rejected Rector Stage (or Tool) releases the level instead of closing it.
- **`rector-php-set` and `rector-code-quality` get no edge to the chain.** Their overlap with the levels' findings is too
  small (the PHP 8.1 set's null-to-string casts, at most) to hold the chain for.
- **`rector-phpunit-set` is a Guardrails Stage.** It rewrites only test code, mechanically; a conflict with structural
  work is resolved by running Rector again, and it touches nothing the levels check.

## Considered Options

- **Move PHPStan Level 5 to Guardrails** to shorten the Safety Net by the often largest baseline. Rejected, see above.
- **`requires` instead of `after`.** Would close the level when Rector is declined, and PHPStan does not need Rector to
  work. Rejected.

## Consequences

- On a target with both Tools, the Safety Net proposes Rector Dead Code before PHPStan Level 4 and Rector Type Coverage
  before Level 5.
- A target on Psalm is unaffected: PHPStan is out there.
- Rector's PHPUnit Set is proposed once the Safety Net is fulfilled; an open ticket for it moves to Guardrails by itself,
  since a ticket's Track is read from the model.
