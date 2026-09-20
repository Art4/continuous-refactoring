# Expected behavior — Safety Net Track: rejection cascade and its reversal

Confirms that rejecting a node that **has required descendants** removes the whole cascade from
`Open` — the rejected node's own entry plus every node the script reports as closed by it — writing
only the one rejection (`out-of-scope/<slug>.md` plus the `Out-of-scope` pointer) and no files for the
downstream closures, and that reversing the rejection makes the next scan bring the reopened nodes
back (`skills/refactor-learn/references/safety-net-write.md`'s *Rejection* section). Spec case 6 of
`agent-judged-fulfilment`. The existing rejection fixtures (`php-safety-net-rejection-symmetry`,
`php-guardrails-rejection-symmetry`) use `php-cs-fixer`/`phpmd`, which have no required descendants,
so they never exercise the cascade.

Not deterministically checkable end to end — the bookkeeping writes are agent behavior. The cascade
itself *is* deterministic and was verified with `tooling_tree.py` (see *Seeded state*). Run via
`fixtures/harness/run.sh safety-net-track php-safety-net-rejection-cascade --opencode`, same non-CI,
local-only, advisory posture as `safety-net-track`.

## Seeded state

The project runs PHPStan at level 2 with an empty baseline (levels 0-2 fulfilled); Composer, PSR-4,
PHP CS Fixer, PHPUnit, CI and the `rector-*` family are all in place, and `psalm-taint-analysis` is
already rejected — so the only unresolved Safety Net scope nodes are `phpstan-level-3`, `-4` and `-5`.
`phpstan-level-3` has required descendants: `phpstan-level-4` → `phpstan-level-5` in the Safety Net,
and (Guardrails scope) `phpstan-level-6..10` and `phpstan-deprecation-rules`.

`docs/refactoring/bookkeeping.md`'s `## Safety Net` section: `Cadence: 90`, `Last scan: 2026-09-01`,
`Open` as a list:
- `phpstan-level-3 (#12)`
- `phpstan-level-4`
- `phpstan-level-5`

and `Out-of-scope` as a list: `- psalm-taint-analysis — out-of-scope/psalm-taint-analysis.md`. There
is no `## Guardrails` section.

`.scratch/refactor/issues/12-phpstan-level-3.md` — already `Status: closed`, `Labels:
refactor:candidate, wontfix`, with a maintainer's closing comment giving a load-bearing structural
reason (types in this codebase are not ours to tighten, so higher levels only report noise).

Verified with `python3 skills/refactor-scan/references/tooling_tree.py --seed <seed> <project>`, where
the seed marks every node fulfilled except `phpstan-level-3..10`, `phpstan-deprecation-rules`,
`composer-audit`, `phpmd`, `coverage-floor`, `php-minimal-version`, `semgrep`, `structural-scan`,
`psalm-taint-analysis` and the gate `php-safety-net` (not yet resolved). The raw `backlog` also carries
entries outside the Safety Net scope (the Guardrails nodes, `structural-scan`, the plumbing node
`php-safety-net`); the lists below name only the Safety Net scope's part of it:

- No rejection recorded: `closed_by_rejection` is empty; `backlog` holds `phpstan-level-3`,
  `phpstan-level-4`, `phpstan-level-5` (in that order) as its Safety Net entries.
- With `docs/refactoring/out-of-scope/phpstan-level-3.md` present: `closed_by_rejection` is
  `phpstan-level-4`, `phpstan-level-5`, `phpstan-level-6`, `phpstan-level-7`, `phpstan-level-8`,
  `phpstan-level-9`, `phpstan-level-10`, `phpstan-deprecation-rules`, and `backlog` no longer holds
  `phpstan-level-3`/`-4`/`-5`. (Read the cascade from `closed_by_rejection` and `backlog`; the
  `withheld_with_reasons` list still names closed nodes.)
- With that file removed again: `backlog` holds `phpstan-level-3`, `phpstan-level-4`,
  `phpstan-level-5` (in that order) again.

## Expected: `refactor-learn` early call (rejection)

Given the finding "closed without merge, `phpstan-level-3`, the issue's closing comment gives a
maintainer's structural reason", it should:

1. Write `docs/refactoring/out-of-scope/phpstan-level-3.md` — the recorded rejection, reason taken from
   the closing comment.
2. Remove `phpstan-level-3` from `## Safety Net`'s `Open`, and add
   `- phpstan-level-3 — out-of-scope/phpstan-level-3.md` to its `Out-of-scope`.
3. Also remove `phpstan-level-4` and `phpstan-level-5` from `Open` — both are closed by the rejection
   (`closed_by_rejection`). `Open` ends up `- none`.
4. Write **no** `out-of-scope/` file and **no** `Out-of-scope` pointer for `phpstan-level-4` or
   `phpstan-level-5` (or any of the Guardrails-scope descendants) — closures are derived, not recorded.
5. Leave `Last scan` untouched (no scan ran) and never create a `## Guardrails` section (that is a
   scan's write).

## Expected: reversal, then the next scan

The maintainer changes their mind: `out-of-scope/phpstan-level-3.md` and its `Out-of-scope` pointer
are removed (by hand, the ordinary reversal path). A Safety Net scan then runs (`Open` is empty and the
Track is due, or the human names the Track explicitly). It should:

1. Judge every scope node again and hand the seed to the script; `phpstan-level-3` is no longer
   rejected, so its descendants are no longer closed.
2. Record `Open`, as a bullet list, in this order, no issue numbers, and write `Last scan` — the
   reopened nodes come back at this scan, not earlier:
   - `phpstan-level-3`
   - `phpstan-level-4`
   - `phpstan-level-5`

## The behavior this regression-tests

Without the cascade rule, rejecting `phpstan-level-3` would leave `phpstan-level-4`/`-5` stranded in
`Open` as permanently blocked entries (their required parent can never be fulfilled), so `Open` never
empties. Without the reversal rule, a reversed rejection would leave those nodes invisible until
someone re-added them by hand.

## Verified

Not yet confirmed live against an opencode model run. The cascade and reversal lists were computed
with `tooling_tree.py` on 2026-09-20.
