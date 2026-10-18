# The PHP Pack

Applies when the repository contains PHP code (`pack.json` holds the sentence the agent judges). The Tools and Stages with what they need are in `pack.json`; each Tool has a file beside it with the prose of its Stages. This file holds what applies to the Pack as a whole.

## The runtime floor

Four PHP Tools carry a `min_runtime` in `pack.json`: the oldest PHP release any published version of the Tool has run on (PHP CS Fixer and PHPUnit 5.3, Composer Audit 7.2, PHPStan 7.0). The agent reads the lowest PHP the target allows from `composer.json` (`config.platform.php` where it is set, otherwise the lowest version `require.php` allows) and hands it to the parser as the seed's `runtime` (`../../tooling-parser.md`). The parser reports a Tool below its minimum in `runtime_blocked`, at the Tool's first Stage, with both versions in the reason. It cannot be set up while the target allows the older PHP, and left undecided it keeps the Safety Net from being fulfilled: PHPUnit and the PHPStan level chain are Safety Net Stages. A scan therefore proposes recording a rejection that carries the minimum as its blocker (`../../rejection.md`, *Below the runtime floor*); the Stage then counts as decided, and the parser reports the reversal once the target's floor reaches that version.

## `require-dev` security advisories

A known security advisory in a `require-dev` package never blocks that package's adoption. Dev-only tooling (test runners, static analysers, style fixers, …) is excluded from production installs (`composer install --no-dev`) and never ships or runs there, so the blast radius stays inside CI and dev machines. More importantly, the tooling a vulnerable dev dependency provides, most of all a test suite, is often the prerequisite for the very refactoring or PHP upgrade that would let a newer, non-vulnerable version of that tool be adopted later; refusing it would block the fix instead of enabling it. This holds for every `require-dev` Tool (PHPUnit is the concrete case that surfaced it). It does not hold for `require` (production) dependencies; that is what Composer Audit exists to police.
