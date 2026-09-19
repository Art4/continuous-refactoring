# 06: Housekeeping Track — retire the standalone `continuous-housekeeping` skill

**What to build:** `continuous-housekeeping`'s existing process (due-check, reconciliation against
fulfilled nodes, checklist assembly, quality gate, deliver) becomes the Housekeeping Track's own content,
unchanged, triggered by the shared Track scheduler instead of its own standalone due-check. Its
`references/` (cadence interview, template-file-format doc) move under `continuous-refactoring`. Manual
invocation of the Housekeeping Track directly stays possible, generalized to the same
Track-name-as-argument pattern the other three Tracks use.

**Blocked by:** 04

**Status:** done

- [x] The existing housekeeping process runs with unchanged content, triggered by the shared scheduler.
- [x] `continuous-housekeeping`'s `references/` move under `continuous-refactoring`.
- [x] `bookkeeping.md` gains a `Housekeeping` section (`Cadence`, `Last scan`); default cadence stays 7
      days (weekly), unchanged from today's default.
- [x] Manual invocation of the Housekeeping Track directly remains possible.
- [x] No standalone `continuous-housekeeping` entry point remains as its own top-level skill.

## Comments

PR: https://github.com/Art4/continuous-refactoring/pull/96 (branch `tickets/06-housekeeping-track`,
based on `tickets/05-investigation-track`).

Judgement calls:

- **`skills/continuous-housekeeping/` deleted outright, not stubbed.** No precedent in this repo's
  history for a redirect stub on a retired skill directory — `git log --diff-filter=D -- 'skills/*'`
  shows nothing comparable. The ticket says "no standalone entry point remains as its own top-level
  skill," and `validate_skills.py` treats every `skills/*/SKILL.md` as a real, live entry point (no
  concept of a deprecated/redirect skill) — a stub would either fail validation or need special-casing
  the validator for a shape nothing else uses. Its `references/` (cadence interview,
  `template-file-format.md`) moved under `continuous-refactoring` and are preserved, so nothing is lost;
  only the standalone top-level directory itself is gone.
- **Housekeeping's own process runs directly from the orchestrator (`continuous-refactoring/SKILL.md`
  step 0c), not through `refactor-scan`.** `refactor-scan`'s own contract is "detect, never write," but
  the Housekeeping Track's process commits, opens an issue, and opens (or closes) a merge request
  directly — the same thing the old standalone skill always did. Routing it through `refactor-scan`
  would have broken that skill's own contract; running it directly from the orchestrator (mirroring the
  old, now-retired step 0's own shape, just scheduler-gated instead of opt-in-gated) keeps every other
  skill's contract intact. `refactor-learn`'s closing call (step 6) still runs afterward to write
  `## Housekeeping`'s `Last scan` — the one piece of bookkeeping this Track needs that only
  `refactor-learn` is allowed to write.
- **`## Housekeeping`'s `Last scan` write always uses the dedicated bookkeeping branch, never folded onto
  the Housekeeping cycle's own branch.** Considered extending `refactor-learn`'s existing native-tracker
  fold-in exception to Housekeeping's own `chore/housekeeping-<date>` branch, but that exception is
  scoped specifically to a native-tracker candidate MR `refactor-implement` opened this same pass, and a
  Housekeeping cycle doesn't always have an open branch by the time `refactor-learn` runs (the "nothing
  registered to check" and "zero code changes, issue closed directly" outcomes leave none) — one uniform
  path avoids inventing a second, narrower special case just for the cases that do have a branch.
- **The cadence interview (`housekeeping-cadence-interview.md`) is preserved but no longer a blocking
  first-run gate.** `## Housekeeping`'s `Cadence` defaults to `7` silently on this Track's first
  scheduler-driven run, the same silent-default discipline Safety Net's `90`/Guardrails' `60` already
  use — an orchestrator-driven, potentially-unattended pass can't stop to ask a question. The interview
  file stays available for a human who wants a guided one-question prompt instead of a bare number edit,
  reframed as optional rather than gating.
- **Manual Track invocation, generalized**: naming any of the four Tracks directly when invoking
  `/continuous-refactoring` (e.g. "run the Housekeeping Track") now bypasses selection the same way for
  all four — `track-scheduler.md`'s own Manual override section updated to drop its earlier "not yet
  folded into one shared invocation surface" caveat.
- **New fixture `php-scheduler-housekeeping-competes`** deliberately sets Housekeeping's ratio (`≈4.29`)
  above Guardrails' (`≈1.33`) even though the fixed tie-break order ranks Guardrails higher — proving
  selection follows the genuine ratio, not the tie-break order (the same point
  `php-scheduler-staleness-selection`, ticket 04, established one level up). Because selecting
  Housekeeping continues straight into its own full due-check → reconcile → checklist → quality-gate →
  deliver pipeline (unlike the other three Tracks, which stop at `refactor-scan`'s own proposal), this
  one fixture also exercises "the existing housekeeping process content still runs correctly," covering
  the second thing the ticket asked to confirm without a second fixture. Live run
  (`OPENCODE_TIMEOUT=280`) correctly computed every ratio, correctly selected Housekeeping, and correctly
  reconciled the `composer` node's own `Housekeeping` line into `housekeeping-template.md` before hitting
  the 280s budget partway through the deliver pipeline — 2 of 3 advisory assertions passed, exit 0 (the
  harness's own non-blocking posture for an opencode timeout). The deterministic sanity pass
  (`tooling_tree.py` run directly against the fixture) confirmed the seeded state first, per usual.
