# PHPStan Level 1

**Status:** open
**Labels:** refactor:candidate, ready-for-agent
**Filed:** 2026-09-05

## Where

Suite-wide (tooling adoption, no single file).

## Problem

`phpstan-level-1` is unfulfilled — PHPStan runs at level 0 with an empty baseline; level 1 is not
configured.

## Plan

Raise `phpstan.neon` from `level: 0` to `level: 1`, fix (or explicitly baseline) what the first run
reports, and keep the baseline shrinking. MR scope: config bump plus the fixes it needs (per
`skills/refactor-scan/references/php-tooling-tree/phpstan.md`).

## Comments

(none)
