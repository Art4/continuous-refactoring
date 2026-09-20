# PHPStan Level 3

**Status:** closed
**Labels:** refactor:candidate, wontfix
**Filed:** 2026-09-05

## Where

Suite-wide (tooling adoption, no single file).

## Problem

`phpstan-level-3` is unfulfilled — PHPStan runs at level 2 with an empty baseline; level 3 (return
types and property types) is not configured.

## Comments

**2026-09-12 — maintainer:** We deliberately keep PHPStan at level 2 and are not raising it. Most of
this codebase is generated glue around a framework whose types we don't own, so the stricter levels
only report noise there and no amount of baseline shrinking changes that. Not adopting level 3 or
any level above it. Closing as `wontfix`.
