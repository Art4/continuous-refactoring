# `coverage-floor`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **signal**).

- **Name:** Test Coverage Floor
- **Tool:** PHPUnit's own coverage report — PCOV or Xdebug as the underlying driver, either works; a
  concrete tool choice at adoption time, not pinned here, the same shape `secret-detection.md`'s `any
  secret scanner` already uses.
- **Purpose:** a Signal-producing node for `refactor-prioritize`'s Select mode, not a Safety Net one
  (no `resolved` edge into `php-structural-scan`/`structural-scan`). Turns test coverage from an
  assumption into measured evidence: a self-tightening floor (a ratchet — never a fixed percentage,
  see *Ratchet, not a fixed floor* below) that only ever climbs, plus real per-file numbers that
  strengthen the existing generic "Untested / hard-to-test" recognition cue instead of relying on
  reading the test suite by eye.
- **Required parent:** `phpunit` — coverage is a report over an existing test suite, not a standalone
  concern; nothing to measure before a runner exists.
- **Fulfilment check:** `phpunit.xml.dist` (or `phpunit.xml`) declares a `<coverage>` report section,
  and a coverage-floor value is committed to the target (`.coverage-floor`, a single percentage, e.g.
  `62.5`). Once `ci-runner` is fulfilled, additionally requires a CI job that actually invokes the
  coverage-enabled run and fails when the result drops below the committed floor — self-wired CI gate,
  same shape `phpunit.md`'s own pattern already uses; no CI yet still fulfils the node on local
  adoption alone. Driver-agnostic by design: the check never looks for "pcov" or "xdebug" by name,
  only for coverage actually configured and (once CI exists) enforced — see *PCOV is a default, not a
  requirement* below.
- **MR scope:** `phpunit.xml.dist`'s `<coverage>` section, report format Clover XML (the format Select
  mode reads back — see **Signal** below), a coverage driver wired into the local/CI run, the initial
  `.coverage-floor` value (whatever the very first coverage run actually measures — never invented),
  and — once `ci-runner` is fulfilled — a CI step that fails when a fresh run drops below the
  committed floor.
- **Signal:** Untested / hard-to-test (`skills/refactor-prioritize/references/signals.md`) — once
  fulfilled, Select mode reads the coverage report's real per-file numbers (Clover XML) instead of the
  generic "read the test suite" heuristic: a file sitting more than 20 percentage points under the
  current `.coverage-floor` value is this factor's own real evidence, not a separate criterion.

## Ratchet, not a fixed floor

A fixed percentage picked once (70%, 80%, …) would be unreachable on day one for plenty of legacy
targets and would permanently block this node rather than build gradual pressure — the same reasoning
`phpstan`'s own level chain already applies to static-analysis strictness. `.coverage-floor` instead
starts at whatever the target's first real coverage run measures and only ever rises from there, via
an ordinary human-reviewed commit — never a value this node's own CI writes back by itself, even when
a run exceeds it. Coverage rising is simply what happens when someone adds or strengthens a test; that
shouldn't also force a dedicated bookkeeping MR, but it also shouldn't happen silently outside version
control — a normal commit bumping `.coverage-floor` (by hand, or by whatever local tooling a target
sets up for itself) is exactly the right amount of ceremony, matching how `phpstan-baseline.neon` only
ever shrinks through a real, committed code change, never a silent CI rewrite.

## PCOV is a default, not a requirement

This node's own **MR scope** picks PCOV as the coverage driver to wire in — faster than Xdebug, with
no debugging overhead. A reviewer who prefers Xdebug on a given target can request
that instead during review without the node being blocked or rejected — the **Fulfilment check**
above never inspects which driver actually ran, only that coverage is configured and (once CI exists)
enforced.
