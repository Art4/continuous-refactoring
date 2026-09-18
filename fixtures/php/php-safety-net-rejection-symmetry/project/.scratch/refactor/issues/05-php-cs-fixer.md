# PHP CS Fixer

**Status:** closed
**Labels:** refactor:candidate, wontfix
**Filed:** 2026-08-01

## Where

Suite-wide (tooling adoption, no single file).

## Problem

`php-cs-fixer` is unfulfilled — no dev dependency, no config, no formatting pass has run yet.

## Comments

**2026-08-15 — maintainer:** We already enforce code style purely through mandatory PR review, by
team convention — no formatter, no CI check, deliberately. Not adopting `php-cs-fixer` (or any other
style tool). Closing as `wontfix`.
