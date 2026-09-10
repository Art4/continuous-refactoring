# `semgrep` — OWASP Top 10 coverage behind `psalm-taint-analysis`, not `composer`

## Context

Ticket 11 (OWASP-aware static security analysis) had been deferred since ADR-0005 as a later-wave
concern, unblocked once its stated first-wave prerequisite (tickets 10/18) landed. The suite already
has one deterministic security-scan tool gating structural work, `psalm-taint-analysis` — the open
question this ticket had to settle was whether a second, broader tool adds real coverage or just
duplicates it, and where it should attach given it's the first node in this tree that isn't a Composer
dependency at all.

## Decision

A new PHP-tree node, `semgrep`:

- **Signal-producing, not Safety Net.** No `resolved` edge into `php-structural-scan`/`structural-
  scan` — same pattern ADR-0040 already established, Signal: Security, alongside `psalm-taint-
  analysis`'s own real findings for that factor (`signals.md`).
- **Complements `psalm-taint-analysis`, doesn't duplicate it.** Psalm's taint analysis follows
  tainted-data-flow (strongest for injection-class bugs — A03/A01/A10). Semgrep's OWASP-Top-10
  registry ruleset additionally reaches pattern-matchable categories taint analysis doesn't: crypto
  misuse (A02), misconfiguration (A05), logging gaps (A09).
- **Recommended parent `psalm-taint-analysis`, not a flat `composer`-level required edge.** Unlike
  `phpmd`'s shallow `composer → phpmd`, this node stays withheld until `psalm-taint-analysis` is
  *decided* (fulfilled or rejected) — so Psalm's own taint-flow baseline settles first, the same
  formatting-before-style reasoning `editorconfig → php-cs-fixer` already uses. A rejected
  `psalm-taint-analysis` still releases this node (recommended-edge semantics, ADR-0016), it just goes
  in without that baseline.
- **No "security checklist" for the two-axis review's Standards axis.** The tool's own deterministic
  CI findings already are the check; a parallel manual checklist covering the same ground would be
  duplicate upkeep without real additional coverage.
- **Fulfilment check, tool-agnostic-to-invocation-shape:** a CI job invokes `semgrep`, with an
  OWASP-Top-10 ruleset reference either inline (the common `--config=p/owasp-top-ten` registry shape)
  or inside a committed `.semgrep.yml`/`.semgrep.yaml`. Presence of the invocation, the same
  conservative approximation every other self-wired CI-gate check in this tree already uses.

## Considered Options

- **`composer → semgrep` (required), same shallow shape as `phpmd`.** Rejected — Semgrep genuinely
  benefits from Psalm's own security-analysis groundwork existing first; a flat edge would let it be
  adopted before any taint-flow baseline exists, undermining the "settle Psalm's own scope first"
  rationale that motivated the recommended edge instead.
- **Skip Semgrep entirely, treat `psalm-taint-analysis` as sufficient OWASP coverage on its own.**
  Rejected — Psalm's taint analysis is real but narrow (data-flow only); several OWASP categories
  (A02, A05, A09) have no data-flow shape for it to follow at all, a genuine coverage gap Semgrep's
  broader ruleset closes.
- **A dedicated Semgrep-specific Signal factor**, distinct from the existing `secret-detection`/
  `psalm-taint-analysis` Security factor. Rejected — the existing factor already names the concept
  generically; this node just adds a second real-tool proxy alongside Psalm's, not a new concept (the
  same shape a Signal-producing node reusing an existing factor already takes elsewhere in this tree,
  e.g. `phpmd` strengthening "Understandability"/"Defect density" rather than inventing its own).
- **Keep a manual security checklist as originally scoped in ticket 11**, alongside the tool. Rejected
  during grilling — the tool's own CI-gated findings supersede what a parallel manual document would
  check by hand, for no coverage a human reviewer wouldn't already get from the automated gate.

## Consequences

`tooling_tree.py`: `_has_semgrep_owasp_ci_job()` (new), `semgrep`'s own `set_node(...)` call, placed
right after `psalm-taint-analysis`'s. `php-tooling-tree.md`: new node stub, edge-table row
(`psalm-taint-analysis → semgrep`, recommended), diagram node/edge. New extracted node file,
`semgrep.md`. `signals.md`'s Security cue gains a mention of Semgrep alongside Psalm's taint analysis
as a second language-specific proxy. Fixture fallout: `php-clean` gained a `semgrep --config=p/owasp-
top-ten` CI step so it stays fully resolved (same treatment every other Signal node got there); all 8
fixtures' `expected/roadmap.json` regenerated — the recommended edge shifts the 10-step simulation
for any fixture whose lookahead reaches a decided `psalm-taint-analysis` (including `non-php-project`'s
own open-ended hypothetical-chain fallback).
