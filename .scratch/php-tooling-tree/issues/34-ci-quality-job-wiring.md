# 34 — Self-wire CI-gating into `phpunit`'s and `phpstan-level-0-baseline`'s own fulfilment checks

**What to build:** `phpunit` and `phpstan-level-0-baseline` currently count as fulfilled once the tool is
adopted and green locally, regardless of whether CI actually runs it. Fold a CI-gating condition directly
into each node's own fulfilment check instead of adding separate `phpunit-ci-job`/`phpstan-ci-job` nodes
(the shape originally sketched below, now superseded — see the 2026-08-30 grilling comment): once
`ci-runner` is fulfilled (a CI config file exists at all), the node additionally requires a CI job that
actually invokes the tool (`vendor/bin/phpunit`/`vendor/bin/pest`, `vendor/bin/phpstan analyse`). No CI
yet still fulfils the node on local adoption alone — nothing to wire in until CI exists.

**Why:** `ci-runner`'s node prose says quality-job children have two parents (this node + their tool).
`composer-audit` is the one example of that shape that got built (ticket 10). No equivalent existed for
`phpunit`/`phpstan`: a target could adopt both, keep them green locally, and never actually run them in
CI, with nothing in the tree noticing. Surfaced by `refactor-scan` output in a freshly generated test
repo (not a real months-long incident — corrected during grilling, see comments).

**Blocked by:** none — `composer-audit`'s CI-gated fulfilment check
(`skills/refactor-scan/references/php-tooling-tree.md`'s `composer-audit` node) is the template for *what
counts as CI-gated*, adapted here to live inside an existing node's own check rather than a new node.

**Priority:** high

**Status:** done

- [x] `phpunit`'s fulfilment check requires, once `ci-runner` is fulfilled, a CI job invoking
  `vendor/bin/phpunit` (or `vendor/bin/pest` when Pest is the adopted equivalent) — same
  substring/glob detection style as `_has_composer_audit_ci_job` (GitHub Actions + GitLab CI).
- [x] `test-runner-if-missing` stays independent of this — it only answers "does *any* runner exist",
  unaffected by whether that runner is CI-gated.
- [x] `phpstan-level-0-baseline`'s fulfilment check requires, once `ci-runner` is fulfilled, a CI job
  invoking `vendor/bin/phpstan analyse` — same detection style. `phpstan-level-1..3` stay unchanged
  (level-independent CI invocation, so gating it once at the baseline node covers the whole chain).
  Deliberately **not** applied to the Psalm-equivalence branch of this same node — Psalm is getting its
  own node in a follow-up ticket, and that is the right place for its own CI check (see comments).
- [x] `ci-runner`'s own MR-scope prose updated to stop promising more two-parent quality-job children for
  phpunit/phpstan — `composer-audit` stays the only one; phpunit/phpstan self-wire instead.
- [x] `roadmap()`'s forward simulation no longer treats `phpunit` fulfilled as implied by
  `test-runner-if-missing` fulfilled (the two could now diverge: runner adopted but not yet CI-gated).
- [x] `phpstan-level-0-baseline`'s formerly-unconditional MR scope note gains one line: once `ci-runner`
  is already fulfilled, this MR also wires the tool into CI — mirrors `phpunit`'s own new MR-scope line.

**Out of scope:** a dedicated `static-code-analyzer`/`psalm` node redesign (ticket 37), and a recurring
"housekeeping" node (ticket 38) — both vetted during the same grilling session and filed as separate
follow-up tickets, not part of this one.

## Comments

> **2026-08-29:** Filed from the legacy-todo reviewer-loop findings log
> (`.scratch/legacy-todo-loop-observation/findings.md`, "Finding — CI-Pipeline führt weder PHPUnit noch
> PHPStan aus, obwohl beide adoptiert sind") after the user asked for it to be turned into a real ticket.
> The original finding explicitly noted this matches the tree's own stated design ("deferred to a later
> wave") rather than being a bug — the gap is that the later-wave ticket itself was never filed, until now.

> **2026-08-30:** Design settled via a `/grill-me` session (in German). Rejected the originally-sketched
> shape (separate `phpunit-ci-job`/`phpstan-ci-job` nodes, mirroring `composer-audit`'s two-required-
> parent template) in favor of folding the CI-gating condition directly into `phpunit`'s and
> `phpstan-level-0-baseline`'s own fulfilment checks — no new nodes, no new edges. Key corrections made
> during grilling:
> - The original "months unnoticed" framing in the Why section above was wrong — no real incident;
>   surfaced same-day in a test repo generated days earlier. Kept the tree-gate approach anyway on its
>   own merits (a tooling-tree gate doesn't require manual review to catch the gap; "locally green" alone
>   already wasn't a reliable signal in the one case observed), not because of a months-long precedent.
> - `composer-audit` was initially cited as a generic precedent for "the tree needs a node whose whole
>   job is detecting missing CI-wiring." That's not why `composer-audit` is CI-gated — `composer audit`
>   is meaningless without continuous re-running (a one-time local scan tells you nothing about
>   advisories disclosed later), so the CI gate *is* the feature there, not a bolt-on enforcement layer.
>   PHPUnit/PHPStan don't share that property (local runs already have standalone value, and
>   `phpstan-level-N`'s own doc explicitly says CI is irrelevant to *that* node's gating) — the
>   CI-gating requirement here rests on its own reasoning (see above), not on `composer-audit`'s.
> - `phpstan-level-1`, not `phpstan-level-0-baseline`, was the first proposed attach point (recommended-
>   edge idea, since abandoned) for symmetry with `php-cs-fixer`/`rector-*`'s existing recommended-edge
>   use — corrected to `phpstan-level-0-baseline`: the baseline this node sets is exactly what CI is
>   meant to hold the line on, and gating at the baseline covers the whole level chain in one place
>   (the CI invocation is level-independent).
> - A recurring "housekeeping" node (required after `composer`, re-proposed >7 days since last run,
>   bundling composer-audit/test-runner-if-missing/`composer update`/CI-wiring checks, last-run date
>   tracked in `docs/refactoring/config.md`) came up as a considered alternative and was deliberately
>   parked as its own future ticket idea instead — it's a genuinely new pattern (a *recurring* node,
>   breaking the tree's current fulfilled-is-sticky assumption) that deserves its own grilling session,
>   not a decision folded into this ticket.
> - A `static-code-analyzer`/`psalm` node redesign (PHPStan and Psalm as mutually-exclusive required
>   children of a new choice node, replacing today's Psalm-as-equivalence-inside-`phpstan-level-0-
>   baseline` approach) also came up, orthogonal to this ticket's CI-wiring concern, and was filed
>   separately rather than folded in here.

> **2026-08-30 (later):** Implemented via `/implement`.
