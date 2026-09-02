---
name: refactor-prioritize
description: Rank refactor-scan's proposals and recommend the next one to work on, or say why nothing should start this pass.
---

# Refactor Prioritize

Rank the **proposals** and recommend the single next candidate.

## Process

### 1. Should anything start?

Get the in-flight set (issues labeled `refactor:delivered`). **Two or more open?** Stop here — report which ones, pass ends. Drop any proposal already in that set.

If scan handed a single resumed pending issue, that *is* the recommendation — skip ranking.

### 2. Rank

Five factors per proposal (see `references/ranking.md`): **Heat**, **Leverage**, **Tooling pressure**, **Risk**, **Skip streak**. Present as short ordered list of Names only.

### 3. Recommend

Name the single next candidate. Two lines: why it wins, what it unlocks. If two are close, call the tie and let the user decide.

A proposable tooling-tree node is a strong default — structural work compounds once tooling is in place. Still a recommendation, not required.

## Output

Two lines (candidate + rationale) → `refactor-design`, or "nothing to do, because …" → pass ends.

## Completion criterion

Either a single candidate recommended with reason, or nothing to start explicitly reported — never both.
