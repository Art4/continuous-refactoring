# 09: `Fulfilled nodes` has a shrunken role the docs don't reflect — and Housekeeping's reconciliation still reads it

**What to build:** Settle what `Fulfilled nodes` is for now that the Safety Net and Guardrails Tracks
carry their own `Open`/`Out-of-scope` state, then bring the docs and the one reader that got left behind
in line with that answer. Two concrete symptoms, one root cause.

**Why:** Found while answering "what is the `Fulfilled nodes` list still for?". Since ADR-0055, a Safety
Net or Guardrails Track node is **never** written to `Fulfilled nodes`
(`skills/continuous-refactoring/references/refactoring-bookkeeping.md`, `## Fulfilled nodes`). What's left
is a cache for nodes outside both Tracks (`loop-config` for sure; anything else outside the two Tracks
still lands there, and old-schema repos keep their existing entries without migration). Two places
haven't caught up:

1. **The docs describe one reader, but there are two.** `refactoring-bookkeeping.md` says the field
   "only matters to the manual/LLM tree-walk fallback"
   (`skills/refactor-scan/references/tree-walk-prompt.md`). The Housekeeping Track's reconciliation
   (`skills/continuous-refactoring/references/housekeeping-track.md`, "Reconcile, then read the
   accumulated checklist") also reads it: "read `bookkeeping.md`'s `Fulfilled nodes`, and for each listed
   slug whose own tree-doc names a `Housekeeping` field, append that line to `housekeeping-template.md`
   if it isn't already there."
2. **That reconciliation probably misses Guardrails nodes.** The nodes carrying a `Housekeeping` field
   include Guardrails nodes (`composer-audit`, `semgrep`, `php-minimal-version`) and others
   (`composer`, `phpstan`). A Guardrails node is not in `Fulfilled nodes` and its section holds only
   `Open`/`Out-of-scope`, so "fulfilled" has no bookkeeping entry at all for it. The reconciliation's own
   purpose is catching nodes fulfilled *without* a delivering MR that would have contributed the line
   (fulfilled before `## Housekeeping` existed, or adopted by hand) — for a Guardrails node that gap
   can't be closed by reading `Fulfilled nodes`. Found by reading the code, not by a run: verify with a
   fixture before deciding the fix.

Also noticed: the schema example in `refactoring-bookkeeping.md` lists `ci-runner (#78)` under
`Fulfilled nodes`, but `ci-runner` is a Safety Net node (`CONTEXT.md`, **Safety Net**), so the example
shows a state the doc itself says can't occur.

**Blocked by:** none — but decide first, by grilling, whether the answer is "shrink `Fulfilled nodes`'
documented role and fix the reconciliation to derive fulfilment from the parser/tree walk", "retire the
field entirely", or something else. This ticket doesn't pre-empt that decision.

**Status:** needs-triage

- [ ] A decision on the field's future is recorded (keep as a narrow cache, or retire it), with the
      reasoning — an ADR if it changes the bookkeeping schema.
- [ ] `refactoring-bookkeeping.md` names every reader of the field (tree-walk fallback **and**
      Housekeeping reconciliation), or the second reader is removed.
- [ ] Housekeeping's reconciliation picks up a fulfilled Guardrails node's `Housekeeping` line that never
      got contributed by a delivering MR — covered by a new fixture, seeded with a fulfilled Guardrails
      node (e.g. `composer-audit`), a `housekeeping-template.md` missing its line, and no `Fulfilled
      nodes` entry for it.
- [ ] The schema example no longer lists a Track node under `Fulfilled nodes`.
- [ ] Old-schema repos still need no migration (`php-safety-net-old-schema`, `php-guardrails-old-schema`
      fixtures unchanged).
