---
name: continuous-investigation
description: Runs one pass of the Investigation Track by delegating to refactor-loop. Internal — invoked by continuous-refactoring only, not a user entry point.
---

# Continuous Investigation

The **Investigation** Track (`CONTEXT.md`) as one loop pass. Runs the Track's single `structural-scan` gate — the scheduler's permanent fallback, always due — and files the concrete candidate it selects. That Track's own logic lives in `skills/refactor-scan/references/investigation-track.md` and `skills/refactor-learn/references/investigation-write.md`, unchanged. This skill only names the Track and hands it to `refactor-loop`, which runs the pass.

Invoked by `continuous-refactoring` once its Track scheduler selects Investigation. Not a user entry point — a human who wants this Track runs `/continuous-refactoring investigation`.

**Direct invocation is a full manual override.** However this skill is reached — by `continuous-refactoring`, by naming the Track (`/continuous-refactoring investigation`), or typed directly — it runs the Investigation Track without consulting the scheduler, bypassing the Safety Net blockade and the one-time exception exactly as `skills/continuous-refactoring/references/track-scheduler.md`'s *Manual override* section describes for a named Track. This skill knows only its own Track and never reads another Track's state.

## Process

1. Run `/refactor-loop` with Track = `investigation`, and nothing else.
2. Relay `refactor-loop`'s closing report unchanged.

## Completion criterion

`refactor-loop` ran to completion for the `investigation` Track and its closing report was relayed, or `refactor-loop` aborted and its error was relayed.
