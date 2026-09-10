# `coverage-floor` — a self-tightening ratchet, not a fixed percentage

## Context

Test coverage was a real, named gap in this suite's own baseline design (`.scratch/php-tooling-tree/
issues/08`, deferred since ADR-0005 as a later-wave concern) — the loop had no measured evidence for
its existing "Untested / hard-to-test" Signal cue beyond reading the test suite by eye. Ticket 08 was
unblocked once its own stated prerequisite (first-wave tickets 10/18) landed, and grilled jointly with
tickets 11/13.

## Decision

A new PHP-tree node, `coverage-floor`, required parent `phpunit`:

- **Signal-producing, not Safety Net.** No `resolved` edge into `php-structural-scan`/`structural-
  scan` — matches the pattern Signals ticket 2 (ADR-0040) already established for `phpmd`/`secret-
  detection`. Feeds the existing **Untested / hard-to-test** cue (`signals.md`) with real per-file
  Clover-XML numbers instead of the generic "read the test suite" heuristic — not a new factor.
- **A ratchet, not a fixed percentage.** `.coverage-floor`, a single committed number in the target
  repo, starts at whatever the first real coverage run measures and only ever rises — via an ordinary
  human-reviewed commit, never a value the node's own CI writes back by itself. A fixed floor picked in
  advance (70%, 80%, …) would be unreachable on day one for plenty of legacy targets and would
  permanently block the node instead of building gradual pressure, the same reasoning `phpstan`'s own
  level chain already applies to static-analysis strictness.
- **No CI auto-commit, even upward.** Raising `.coverage-floor` stays a normal, reviewed commit — the
  same discipline `phpstan-baseline.neon` already follows (it only ever shrinks through a real code
  change, never a silent CI rewrite). A target that wants the floor to climb on its own is free to
  build that itself; this node's own MR scope never wires it in as the default.
- **Driver-agnostic fulfilment check.** PCOV is this node's own **MR scope** default (matches the
  original "PHPUnit + PCOV" pairing this suite's baseline brainstorming already named, and PCOV's own
  lower overhead vs. Xdebug) — but the **Fulfilment check** never inspects which driver actually ran,
  only that a `<coverage>` report is configured and, once CI exists, actually enforced. A reviewer who
  prefers Xdebug on a given target can request that instead without the node being blocked or
  rejected.
- **Self-wired CI gate**, same shape `phpunit`'s own check already uses: local adoption alone (a
  `<coverage>` section plus a committed `.coverage-floor`) fulfils the node before CI exists; once
  `ci-runner` is fulfilled, a CI job that actually runs coverage and fails under the floor is required
  too.

## Considered Options

- **A fixed percentage floor** (e.g. "70% or the node stays unfulfilled forever"). Rejected — see
  *ratchet, not a fixed percentage* above; the level-chain precedent already settled this shape for
  a comparable "how strict, starting from where" question.
- **CI auto-bumps the floor on every green run that exceeds it.** Considered and rejected — the
  target repo's own CI should not create its own commits by default; a target that explicitly wants
  this convenience can still build it, but it isn't this node's own shipped default.
- **PCOV vs. Xdebug baked into the Fulfilment check** (require the CI config to literally name one).
  Rejected — the node cares that coverage is measured and enforced, not which driver measured it;
  hard-coding a driver name would reject a legitimate Xdebug-based setup for no real reason.
- **A dedicated new Signal factor** ("Coverage gap") instead of feeding the existing "Untested /
  hard-to-test" cue. Rejected — the existing cue already names exactly this concept generically; this
  node just gives it a language-specific numeric proxy, the same relationship `phpmd` already has with
  "Understandability"/"Defect density".

## Consequences

`tooling_tree.py`: `_has_coverage_report_config()`, `_coverage_floor_value()` (new), `coverage-floor`'s
own `set_node(...)` call, self-wired against `ci-runner` the same way `phpunit`'s own check already is.
`php-tooling-tree.md`: new node stub, edge-table row (`phpunit → coverage-floor`, required), diagram
node/edge. New extracted node file, `coverage-floor.md`. `signals.md`'s "Untested / hard-to-test" cue
gains a language-specific-proxy sentence. `CONTEXT.md` gains a **Fulfilment check** glossary entry
(pre-existing, widely-used suite jargon that had never actually been defined — surfaced by this
change's own `/code-review`, not itself part of the original design). `scripts/validate_skills.py`'s
`VOCAB_ALLOW` gains one entry (`refactor-prioritize`, `floor`) for this node's own legitimate reuse of
an otherwise-avoided word. Fixture fallout: `phpunit` becoming a two-child node (the pre-existing
`rector-phpunit-set`, now also `coverage-floor`) shifts every fixture's own 10-step `roadmap()`
simulation once it reaches `phpunit` — all 8 fixtures' `expected/roadmap.json` regenerated
(`fixtures/harness/run.sh roadmap <fixture>` green on all 8 afterward); `php-clean` additionally
gained real coverage artifacts (a `<coverage>` block, `.coverage-floor`, a `--coverage`-gated CI step)
so it stays "every reachable leaf resolved," matching how `phpmd`/`secret-detection` were fulfilled
there (not rejected) when each was added.
