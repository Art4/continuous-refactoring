# Candidate: style violations in bootstrap.php

**Status:** open
**Labels:** `refactor:candidate`

## Where
`src/bootstrap.php`

## Problem
bootstrap.php is missing `declare(strict_types=1)` and uses the deprecated `each()` function. These are tooling-pressure candidates — PHPStan and Rector will flag them automatically.

## Signal
Tooling pressure: missing strict types, deprecated function usage. Deterministic tools (PHP-CS-Fixer, Rector) can fix these automatically.
