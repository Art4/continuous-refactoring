# 1 — File a candidate's issue early (select), spec it later (design)

**What to build:** Today `refactor-design` does candidate search (structural-candidate.md step 2 /
phpstan-baseline-shrink.md steps 1-2), grounding, and grilling all inside one dispatch — the issue
only gets filed at the very end, together with the finished plan. Split this: the *selection* of a
concrete candidate happens early and gets filed immediately (minimal fields); *grounding + grilling*
happens afterward, in a separate dispatch, and adds the full plan as a comment on that already-filed
issue.

**Why:** Observed live while reviewer-loop-watching `Art4/legacy-todo` — the watched agent spent a
single long context grilling itself through multiple candidates (SQL-injection hardening vs.
decoration-consistency vs. dead-code) before any issue existed, all inside one `refactor-design`
subagent. Splitting makes the decision visible early (an issue exists the moment a candidate is
picked, not only once it's fully specced) and keeps each phase's context shorter — the grounding/
grilling phase starts fresh, reading only the filed issue, not the full selection-exploration
transcript.

**Blocked by:** none.

**Priority:** medium.

**Status:** ready-for-agent

Settled via `/grill-with-docs` (`grilling` + `domain-modeling`, two rounds plus follow-ups):

- [x] **Scope:** applies structurally to all three "pick before fully speccing" paths —
  `structural-scan`, PHPStan baseline-shrink, externally-labeled candidate — but the new early-select
  dispatch only actually *fires* for the two gate-shaped cases (`structural-scan`, a baseline-shrink
  family), where there's a real choice among alternatives. An externally-labeled candidate is already
  concrete (a human named it directly) — it flows straight to design unchanged, same as today.
- [x] **Mechanism:** two separate, freshly-dispatched calls to `refactor-prioritize`, not one skill
  looping internally or writing the issue mid-context — otherwise the context-window benefit is lost.
  Dispatch 1: rank proposals declaratively, as today. Winner is a gate → dispatch 2 (fresh context):
  do the actual codebase/baseline exploration, pick the concrete candidate, file it minimally. Winner
  is already concrete → dispatch 2 doesn't run, straight to `refactor-design`.
- [x] **Early filing payload:** today's `refactor-design` step 5 minimal fields — Where/Problem/Signal
  for a structural candidate; title + group description for a baseline-shrink candidate. The full plan
  (deepened module, seam, interface, surviving tests, slice order / the planned fix) is deferred to the
  follow-up comment.
- [x] **Naming:** no new skill. `refactor-prioritize` gains the selection responsibility (it already
  uses the same four factors — heat, leverage, tooling pressure, risk — one level deeper: among
  candidates within a chosen gate, not just among gates). `refactor-design` keeps its name and becomes
  simpler: it always receives an already-concrete, already-minimally-filed candidate, and only does
  grounding + grilling + writes the full plan as a comment — matches `CONTEXT.md`'s existing "Plan:
  produced by `refactor-design`" anchor without needing to change it.
  - `structural-candidate.md`'s step 2 (find a structural candidate) and `phpstan-baseline-shrink.md`'s
    steps 1-2 (resume/read+group) move to new reference file(s) under `skills/refactor-prioritize/
    references/`. `refactor-design` keeps only the grounding/grilling/planning steps (structural-
    candidate.md steps 3-4; phpstan-baseline-shrink.md step 3).
- [x] **Orchestrator shape:** no new numbered pass step, and no `3b`-style label either (that would
  wrongly imply an inline sub-step like `refactor-scan`'s real `3b`/`4b`, which don't get a fresh
  dispatch) — described as prose inside `continuous-refactoring/SKILL.md` step 3 (Prioritise): "if the
  recommended candidate is a gate, run `/refactor-prioritize` a second time (fresh dispatch) to select
  and minimally file the concrete candidate, before continuing to step 4."
- [x] **Resumability:** `Pending candidates` gets written for the new phase-1→phase-2 handoff *even on
  native trackers* (a narrow, deliberate exception — the existing native-tracker skip stays unchanged
  for the old design→implement handoff). This piggybacks on `refactor-scan` step 3b's existing
  exclusion of `Pending candidates` entries from its own search, so no new step 3b logic is needed
  there.
  - Implementation detail found while closing the loop, not a separate decision: on a *non-native*
    tracker, `Pending candidates` already gets written across the old design→implement handoff too, so
    it can now point to either state. `refactor-scan` step 2, on resuming, disambiguates by checking
    whether the issue already carries a plan comment — no plan yet → hand to the prioritize
    second-dispatch; plan already present → hand onward to implement, as today.
- [x] **Glossary:** `CONTEXT.md`'s **Proposals** entry ("not yet candidates, since nothing is filed
  until `refactor-design` picks one and specs it") needs a wording update — filing and speccing are no
  longer the same step/skill. **Candidate**'s own definition ("a backlog item filed...") already holds
  without change.
- [x] **ADR:** yes — `docs/adr/0038-...md` (next free number), short format matching ADR 0033's shape:
  1-3 sentence context/decision, a **Considered Options** section (new `refactor-select` skill vs.
  folding into `refactor-prioritize` — rejected the former to reuse the existing four-factor ranking
  vocabulary instead of duplicating it), a **Consequences** section (`refactor-design` simplifies;
  `refactor-prioritize` gains a conditional second dispatch, early minimal filing, and the
  `Pending candidates` write for this new transition).

## Comments

> **2026-09-07:** Filed after a `/grill-with-docs` session (German — `grilling` + `domain-modeling`),
> triggered by a finding recorded while reviewer-loop-watching `Art4/legacy-todo`
> (`.scratch/legacy-todo-loop-observation/findings.md`, round 12:00). Covered scope, dispatch
> mechanism, early-filing payload, naming (an alternative to a new `refactor-select` skill — folding
> into `refactor-prioritize` instead, on the user's own suggestion, turned out better-grounded: the
> selection logic already shares `refactor-prioritize`'s own four ranking factors), orchestrator
> step-shape, resumability, glossary impact, and the ADR offer. User confirmed shared understanding
> ("passt so."). Ready to implement.
