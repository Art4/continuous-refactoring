---
name: continuous-guardrails
description: Runs one pass of the Guardrails Track by delegating to refactor-loop. Internal — invoked by continuous-refactoring only, not a user entry point.
---

# Continuous Guardrails

The **Guardrails** Track (`CONTEXT.md`) as one loop pass. Works through the Guardrails nodes of the tooling tree — the ones proposed only once the Safety Net has closed — walking the Track's own `Open` list or scanning afresh. That Track's own logic lives in `skills/refactor-scan/references/guardrails-track.md` and `skills/refactor-learn/references/guardrails-write.md`, unchanged. This skill only names the Track and hands it to `refactor-loop`, which runs the pass.

Invoked by `continuous-refactoring` once its Track scheduler selects Guardrails. Not a user entry point — a human who wants this Track runs `/continuous-refactoring guardrails`.

**Direct invocation is a full manual override.** However this skill is reached — by `continuous-refactoring`, by naming the Track (`/continuous-refactoring guardrails`), or typed directly — it runs the Guardrails Track without consulting the scheduler, bypassing the Safety Net blockade and the one-time exception exactly as `skills/continuous-refactoring/references/track-scheduler.md`'s *Manual override* section describes for a named Track. This skill knows only its own Track and never reads another Track's state.

## Process

1. Run `/refactor-loop` with Track = `guardrails`, and nothing else.
2. Relay `refactor-loop`'s closing report unchanged.

## Completion criterion

`refactor-loop` ran to completion for the `guardrails` Track and its closing report was relayed, or `refactor-loop` aborted and its error was relayed.
