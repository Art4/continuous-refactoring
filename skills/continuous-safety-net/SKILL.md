---
name: continuous-safety-net
description: Runs one pass of the Safety Net Track by delegating to refactor-loop. Internal — invoked by continuous-refactoring only, not a user entry point.
---

# Continuous Safety Net

The **Safety Net** Track (`CONTEXT.md`) as one loop pass. Works through the Safety Net nodes of the tooling tree — the deterministic tooling settled before agent-driven structural work starts — walking the Track's own `Open` list or scanning afresh. That Track's own logic lives in `../refactor-scan/references/safety-net-track.md` and `../refactor-learn/references/safety-net-write.md`, unchanged. This skill only names the Track and hands it to `refactor-loop`, which runs the pass.

Invoked by `continuous-refactoring` once its Track scheduler selects Safety Net. Not a user entry point — a human who wants this Track runs `/continuous-refactoring safety-net`.

**Direct invocation is a full manual override.** However this skill is reached — by `continuous-refactoring`, by naming the Track (`/continuous-refactoring safety-net`), or typed directly — it runs the Safety Net Track without consulting the scheduler, bypassing the Safety Net blockade and the one-time exception exactly as `../continuous-refactoring/references/track-scheduler.md`'s *Manual override* section describes for a named Track. This skill knows only its own Track and never reads another Track's state.

## Process

1. Run `/refactor-loop` with Track = `safety-net`, and nothing else.
2. Relay `refactor-loop`'s closing report unchanged.

## Completion criterion

`refactor-loop` ran to completion for the `safety-net` Track and its closing report was relayed, or `refactor-loop` aborted and its error was relayed.
