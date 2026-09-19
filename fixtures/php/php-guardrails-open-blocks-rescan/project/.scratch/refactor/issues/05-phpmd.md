# PHPMD

**Status:** open
**Labels:** refactor:candidate, ready-for-agent
**Filed:** 2026-01-01

## Where

Suite-wide (tooling adoption, no single file).

## Problem

`phpmd` is unfulfilled — no dev dependency, no ruleset config, no complexity pass has run yet.

## Plan

Add `phpmd/phpmd` as a dev dependency, commit a `phpmd.xml` ruleset config, run one pass over `src/`
(fix or explicitly baseline what the initial run reports). MR scope: dependency + ruleset config + one
pass (per `skills/refactor-scan/references/php-tooling-tree/phpmd.md`).

## Comments

(none)
