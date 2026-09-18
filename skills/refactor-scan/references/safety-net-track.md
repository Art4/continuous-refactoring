# Safety Net Track scan

`refactor-scan/SKILL.md` step 4's own Safety-Net-specific process: which nodes this Track covers,
whether it's due this pass, and how a node's Fulfilment check gets judged once it is. Vocabulary:
`CONTEXT.md` (**Track**, **Safety Net**, **Onboarding**, **Fulfilment check**).

## Scope

Every tooling-tree node reachable before `structural-scan` opens, except `git`, `loop-config`, and the
language specialization's own recognition gate (`is-php-project` for PHP) — those stay outside every
Track: `loop-config` remains its own mandatory human interview (`CONTEXT.md`'s **Onboarding** entry),
since `bookkeeping.md` doesn't exist yet and its own decisions are genuine preferences no scan can
derive. Concretely, for PHP: every
node in `skills/refactor-scan/references/php-tooling-tree.md` that isn't itself Guardrails-gated
(required on `structural-scan`/`php-safety-net` — `composer-audit`, `phpmd`, `coverage-floor`,
`php-minimal-version`, `phpstan-level-6` and above, `phpstan-deprecation-rules`, `semgrep`) or
`structural-scan` itself. This includes every node with a direct `resolved` edge into `php-safety-net`
(`psr-4`, `phpunit`, `phpstan-level-5`, the `rector-*` family, `psalm-taint-analysis`) *and* every node
upstream of them that gates their proposability without itself carrying a `resolved` edge — `composer`,
`php-cs-fixer`, `test-runner-if-missing`, `static-code-analyzer`, `psalm`, `phpstan-level-0..4` — the
same set `CONTEXT.md`'s **Onboarding** entry names as "everything before `structural-scan` opens." A
node's tree-doc entry (`php-tooling-tree/<node>.md`) is unchanged by any of this — same Purpose,
Fulfilment check, MR scope, edges; only which bookkeeping section a node in this scope reads/writes
changes (below), and how its Fulfilment check gets evaluated (Judging fulfilment, below).

## Is the Track due this pass?

Decided once, before `refactor-scan` even starts — the orchestrator's own Track-selection step
(`skills/continuous-refactoring/references/track-scheduler.md`, `skills/continuous-refactoring/SKILL.md`
step 0b) computes every wired Track's `overdue_ratio` against `bookkeeping.md`'s `## Safety Net` section
(`skills/continuous-refactoring/references/refactoring-bookkeeping.md`) and hands the winner to
`refactor-scan` as an explicit input. This section covers only what this Track does with that decision —
it never re-derives due-ness itself:

- **This Track wasn't the one step 0b selected** → nothing in this file runs this pass; `refactor-scan`
  continues with whichever Track was actually selected instead (or with everything else it already does,
  if none was due).
- **Selected, and `Open` is non-empty** — only reachable via a manual override naming this Track
  directly (`track-scheduler.md`'s own ratio selection never picks a Track with non-empty `Open` in the
  first place) → the Track is still never rescanned. Hand its entries forward the same way `Pending
  candidates` already hands forward a resumable node — resuming at whichever step is next for each (no
  plan yet → `refactor-design`; plan present, `ready-for-agent` set → `refactor-implement`). Skip
  straight to `refactor-scan/SKILL.md`'s `## Output`; the rest of this file doesn't run.
- **Selected, `Open` empty** → continue below; this is a genuine scan.

## Judging fulfilment

Run `python3 references/tooling_tree.py <target-repo>` once, same as `refactor-scan/SKILL.md` step 4
already does — its `detected` map is a first signal, not the verdict, for every node in this Track's
scope. **Don't take a Safety Net node's `fulfilled` value at face value** — the same discipline step 4
already applies to `psr-4`'s `unwired_entry_points`, generalized here to every node in scope: read the
node's own Purpose line (`php-tooling-tree/<node>.md`), then judge the actual repo against it — does a
real, working tool genuinely serve that Purpose, under any name, not only the one the node's own `Tool`
line happens to mention.

- **The parser's own signal still counts.** `fulfilled: true` from the parser is never wrong to trust
  outright — it already found direct evidence (the named dependency, the named config file). Judgement
  only has work to do when the parser reports `false`: is that because nothing serves the Purpose, or
  because something does, under a different name the parser doesn't know to look for?
- **A working example**: `php-cs-fixer`'s Purpose is "automated code style so later Rector output lands
  styled," its `Tool` line names `php-cs-fixer`. A target running Laravel Pint (`laravel/pint` installed,
  `pint.json` committed, `vendor/bin/pint --test` clean) has no `friendsofphp/php-cs-fixer` dependency at
  all — the parser reports `fulfilled: false`. Judged against the Purpose line instead: Pint wraps PHP
  CS Fixer internally and genuinely serves "automated code style," so the node reads fulfilled. Never
  propose `php-cs-fixer` here — proposing a second, separately-configured style tool risks exactly the
  collision Pint's own presence already avoided.
- **Genuinely ambiguous** — two plausible tools present at once, or real uncertainty about whether one
  actually serves the Purpose or might collide with it — routes through the existing Flagged-candidate
  mechanism (`needs-info`, `skills/refactor-design/references/decision-gate.md`), unchanged. Don't guess
  past a real collision risk; flag it instead, the same as any other genuinely ambiguous design decision.
- **No committed artifact at all, purpose stated as served some other way** (e.g., code style enforced
  by convention/review, no tool involved) — not a fulfilment judgement call at all: an ordinary
  `out-of-scope/<slug>.md` rejection with the maintainer's stated reason, same as any other rejection
  (below). Only safe for a node without a required child of its own within the tree — rejecting a
  required parent closes everything beneath it (`CONTEXT.md`'s **Required edge**), which would wrongly
  close a genuinely-served node's own descendants; every node in this Track's scope qualifies.
- **Required/Recommended/Required-any edge semantics and cascading closure on a rejected required
  parent are unchanged** — this section only changes which authority (script vs. judgement) decides a
  node's own `fulfilled` boolean, never how the tree's edges combine those booleans into what's
  proposable.

## Proposing and recording

Every node in scope still unresolved (neither fulfilled by judgement above, nor already rejected under
`out-of-scope/`) and currently unblocked (its own required/recommended parents already resolved/decided,
per the tree's ordinary edge semantics) → propose it by Name, same as `refactor-scan/SKILL.md` step 4
already does for any other node. Once `refactor-prioritize`/`refactor-design` files it, its slug (with
issue # once known) is added to `## Safety Net`'s `Open` list — `refactor-learn`'s own side of this,
`skills/refactor-learn/references/safety-net-write.md`.

**Every node in scope resolved, nothing to propose** → still a completed scan: `refactor-learn`'s closing
call writes `Last scan` regardless (`safety-net-write.md`), so a fully-compliant target gets this Track's
`Cadence` honored afterward instead of being rescanned every pass. `Open` and `Out-of-scope` both stay
however they already were (typically both empty, on a target with nothing rejected).
