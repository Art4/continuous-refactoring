# PHP CS Fixer

**Status:** open
**Labels:** refactor:candidate, ready-for-agent
**Filed:** 2026-01-01

## Where

Suite-wide (tooling adoption, no single file).

## Problem

`php-cs-fixer` is unfulfilled — no dev dependency, no config, no formatting pass has run yet.

## Plan

Add `friendsofphp/php-cs-fixer` as a dev dependency, commit a `.php-cs-fixer.php` config, run one
formatting pass across `src/`. MR scope: dependency + config + one formatting pass (per
`skills/refactor-scan/references/php-tooling-tree/php-cs-fixer.md`).

## Comments

(none)
