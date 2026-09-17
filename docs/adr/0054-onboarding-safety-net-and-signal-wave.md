# Onboarding/Safety Net split; Signal wave nodes wait for the Safety Net to close; `php-structural-scan` renamed `php-safety-net`

> Amends [ADR-0040](0040-signal-tool-nodes-and-tree-edge-simplification.md): `secret-detection` and `phpmd`
> were introduced as Signal-producing nodes proposed as early as their domain-specific required parent
> allowed — this ADR moves them (and every other Signal-producing node, plus two nodes reclassified out of
> the Safety Net here) behind the Safety Net closing instead.
>
> Amends [ADR-0017](0017-php-structural-scan-aggregation-node.md): `php-structural-scan` is renamed
> `php-safety-net`. Same node, same mechanism — resolved once its (now nine, was eleven) leaves are
> resolved, still the PHP tree's sole `resolved` contribution to `structural-scan` — new name, because
> other nodes now read its resolved-ness too, not only `structural-scan`.

Raised against a live UX complaint: security-relevant nodes (`composer-audit`, `secret-detection`, …) were
surfacing in the very first proposal wave, before the deterministic Safety Net had even closed — a target's
very first passes could be asked to wire up a secret scanner before `phpunit`/`phpstan` existed at all.
Settled via `/grill-with-docs`, several rounds, directly against `skills/refactor-scan/references/
{tooling-tree.md,php-tooling-tree.md}` and the affected node files.

## Considered Options

- **Leave every Signal-producing node gated only by its domain-specific required parent (status quo).**
  Rejected — this is the complaint itself: nothing about a node's *wave* was ever distinct from its
  ordinary required-parent chain, so a cheap, early-unblocked Signal node (e.g. `secret-detection`, whose
  only required parent is `loop-config`) surfaced immediately, regardless of how far along the Safety Net
  actually was.
- **Reclassify `composer-audit` and `psalm-taint-analysis` out of the Safety Net together, since both are
  Security-signal nodes.** Rejected for `psalm-taint-analysis` — Security-as-signal and Safety-Net-as-wave
  are orthogonal axes, not the same thing: `psalm-taint-analysis` finds taint bugs a structural refactor
  could itself introduce (the exact "collides with agent-driven structural work" criterion `structural-scan`
  was built around), while `composer-audit` audits third-party CVEs that a target's own structural
  refactoring neither creates nor fixes. `composer-audit`'s Safety Net membership predates the Safety
  Net/Signal distinction entirely (ADR-0008, before ADR-0040 introduced that vocabulary) and was never
  re-examined against it until now; `psalm-taint-analysis` (ADR-0019) was reasoned about using exactly this
  criterion from the start and stays put.
- **Fully replace every reclassified/moved node's existing required parent with the Safety Net gate**,
  mirroring how `semgrep`'s `composer` parent gets dropped below. Rejected for six of the seven moved nodes
  (`composer-audit`, `phpstan-deprecation-rules`, `phpmd`, `coverage-floor`, `php-minimal-version`,
  `phpstan-level-6`): each of their existing required parents encodes genuine operational necessity — a
  *rejected* (not merely undecided) `phpunit`/`rector-php-set`/`phpstan-level-5`/`composer` must still
  permanently close the dependent node, the ordinary required-edge convention — but a rejected *resolved*
  parent still counts as resolved, so gating on the Safety Net node alone would silently let a node open
  even though the ancestor it actually depends on was explicitly declined. `php-minimal-version.md`'s own
  doc already states this outright for `rector-php-set`: proposable "only once genuinely fulfilled, not
  merely decided". Kept additively (both parents required) instead. `semgrep` is the one clean exception —
  its own doc states Semgrep needs no Composer at all; the `composer` parent was purely an incidental
  rejection-cascade-closure technicality, made redundant once `php-safety-net` is the gate.
- **Persist "target recognized as PHP" as a `bookkeeping.md` flag**, to gate the PHP-specific Signal wave
  nodes independent of language once a second specialization exists. Rejected — `is-php-project` is
  deliberately re-derived fresh every pass (its own doc states this explicitly, precisely so a target that
  only later becomes PHP opens the tree retroactively with no separate mechanism); a persisted flag would
  duplicate that source of truth and could drift. Solved for free instead: `php-safety-net` (like
  `php-structural-scan` before it) can only ever resolve via the PHP recognition path today — the same
  "Known gap" `is-php-project.md` already documents for the non-PHP path — so gating the PHP-specific
  Signal wave nodes on `php-safety-net` already carries the language check with it, no new mechanism
  needed.
- **Require proof of a completed run (not just CI-job presence) for `composer-audit`/`semgrep`'s new
  Housekeeping-line fulfilment fallback**, via a new local ledger file or by giving `tooling_tree.py`
  (otherwise a pure-filesystem parser) forge access. Rejected — `continuous-housekeeping`'s own `SKILL.md`
  deliberately keeps no local "last run" record ("the tracker's own history is the record"); duplicating
  that state locally, or breaking the parser's forge-free design, is disproportionate for two nodes. A
  committed `housekeeping-template.md` line is treated as sufficient instead, matching how every existing
  CI-gated fulfilment check in this tree already works (job exists/invokes the tool — never proof of a
  passing run history).
- **Split `php-structural-scan`'s aggregation role and its new Signal-wave-gate role into two separate
  nodes**, rather than renaming the one node. Rejected — nothing in `tooling_tree.py` forces a split: the
  aggregation-node exclusion (never itself proposed) is derived purely from `resolved_parents`, unaffected
  by how many *required* edges point away from the node. A rename captures what the node actually means now
  ("the PHP-side Safety Net has closed") without new machinery.

## Decision

### New vocabulary: `CONTEXT.md` gains **Onboarding**, **Safety Net**, **Signal wave**

**Onboarding** names the bounded, per-target phase from a bare repo through `git`/`loop-config`/the
recognition gate/the Safety Net, ending once `structural-scan` opens — distinct from **Tooling tree**'s
existing `_Avoid_: onboarding` note, which bans the word only as a synonym for the tree *as a whole* (never
bounded, walked forever). **Safety Net** narrows that to the specific nodes carrying a `resolved` edge into
`structural-scan`/`php-safety-net`. **Signal wave** names the nodes gated on that same closure instead of a
domain-specific parent — orthogonal to the existing **Signal** field (which factor, not when).

### `php-structural-scan` renamed `php-safety-net`

Same nine-of-eleven-now leaves (`composer-audit` and `phpstan-deprecation-rules` removed, see below), same
`resolved` edge into `structural-scan`. Every reference across both tree docs, `tooling_tree.py`,
`tree-walk-prompt.md`, and skill files updated.

### `composer-audit` and `phpstan-deprecation-rules` move from Safety Net to Signal wave

Both drop their `resolved` edge into `php-safety-net`; both gain `php-safety-net` as an *additional*
required parent, keeping their existing one (`composer`, `phpstan-level-5` respectively) — see the
rejected-option above for why additive, not replaced. `composer-audit` additionally: `ci-runner` downgraded
required → recommended, and its Fulfilment check gains a second path — a committed line in
`housekeeping-template.md`, alongside the existing CI-job check.

### Five more nodes join the Signal wave, gated on the Safety Net closing

- `phpmd`, `coverage-floor`, `php-minimal-version`, `phpstan-level-6`: each keeps its existing required
  parent and gains `php-safety-net` additionally (same reasoning as above). Levels 7–10 need no edge of
  their own, inheriting the wait transitively through the existing chain.
- `semgrep`: required parent fully replaced by `php-safety-net` (the one clean full-replacement case); its
  now-redundant `recommended` parent `psalm-taint-analysis` (already one of `php-safety-net`'s own leaves,
  therefore always already decided by the time `php-safety-net` resolves) is dropped too; `ci-runner`
  downgraded required → recommended with the same Housekeeping-line fulfilment fallback as `composer-audit`.
- `secret-detection`: required parent repointed from `loop-config` to the generic root's own
  `structural-scan` directly — stays outside `php-safety-net`, being language-neutral.

The Housekeeping-line fulfilment fallback is scoped to `composer-audit`/`semgrep` for now — both are
point-in-time audits whose value is in repetition, not one-time adoption, unlike `phpunit`/`phpstan`/`psalm`
(whose existing "local adoption alone still fulfils, CI reinforces it" pattern already covers their own
durable, one-time-meaningful local check) — but documented as the pattern to reuse once further audit-style
nodes are added (more are planned).

## Consequences

`php-safety-net`'s own leaf count drops from eleven to nine. `composer-audit.md`'s "Stop conditions" bullet
(b) — a fallback that existed purely to keep `structural-scan` from being permanently blocked by
`composer-audit` — is removed as moot now that `composer-audit` isn't a leaf at all; bullet (a) (a real
`require` dependency must exist) stays, an independent proposability guard. `semgrep.md` loses its
composer-parent justification paragraph, genuinely unneeded now rather than merely situational.

Unlike ADR-0040's own edge simplifications, this is not a pure documentation change: `tooling_tree.py` needs
`_composer_audit_extra_gate()` removed (its whole reason for existing — the Stop-conditions fallback above —
is gone) and a new Housekeeping-line-detection helper added, shared by `composer-audit` and `semgrep`'s
fulfilment checks. `scripts/test_tooling_tree.py` and `fixtures/php/*/expected/roadmap.json` both need
updating/regenerating, matching the scale ADR-0040 already documented for its own restructuring.

`CONTEXT.md`'s **Tooling tree** entry gains a clarifying aside on its existing `_Avoid_: onboarding` note,
distinguishing it from the new, deliberately bounded **Onboarding** term.
