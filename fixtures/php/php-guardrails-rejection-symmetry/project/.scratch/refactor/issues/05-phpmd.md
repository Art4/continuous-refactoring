# PHPMD

**Status:** closed
**Labels:** refactor:candidate, wontfix
**Filed:** 2026-08-01

## Where

Suite-wide (tooling adoption, no single file).

## Problem

`phpmd` is unfulfilled — no dev dependency, no ruleset config, no complexity pass has run yet.

## Comments

**2026-08-15 — maintainer:** We already enforce cyclomatic-complexity and code-quality limits purely
through mandatory PR review, with a documented complexity checklist reviewers apply by hand — no
static tool, deliberately, by team convention. Not adopting `phpmd`. Closing as `wontfix`.
