# Safety Net Track scan

`refactor-scan/SKILL.md` step 4's own Safety-Net-specific process: which nodes this Track covers,
whether it's due this pass, and how a node's Fulfilment check gets judged once it is. Vocabulary:
`CONTEXT.md` (**Track**, **Safety Net**, **Onboarding**, **Fulfilment check**).

## Scope

Every tooling-tree node reachable before `structural-scan` opens, except `git`, `onboarding-setup`, and the
language specialization's own recognition gate (`is-php-project` for PHP) — those stay outside every
Track: `onboarding-setup` is fulfilled by the dispatcher's own onboarding step (`CONTEXT.md`'s **Onboarding**
entry) before any Track runs — its decisions are genuine preferences no scan can derive — so a scan
never proposes it. Concretely, for PHP: every
node in `php-tooling-tree.md` that isn't itself Guardrails-gated
(required on `structural-scan`/`php-safety-net` — `composer-audit`, `phpmd`, `coverage-floor`,
`php-minimal-version`, `phpstan-level-6` and above, `phpstan-deprecation-rules`, `semgrep`) or
`structural-scan` itself. This includes every node with a direct `resolved` edge into `php-safety-net`
(`psr-4`, `phpunit`, `phpstan-level-5`, the `rector-*` family, `psalm-taint-analysis`) *and* every node
upstream of them that gates their proposability without itself carrying a `resolved` edge — `composer`,
`php-cs-fixer`, `test-runner-if-missing`, `static-code-analyzer`, `psalm`, `phpstan-level-0..4` — the
same set `CONTEXT.md`'s **Onboarding** entry names as "everything before `structural-scan` opens." A
node's tree-doc entry — the file `php-tooling-tree.md`'s own per-node *Full definition* pointer
names, not always one-file-per-node (every `rector-*` node points at `php-tooling-tree/rector.md`;
`psalm`/`psalm-taint-analysis` both point at `php-tooling-tree/psalm.md`) — is unchanged by any of
this — same Purpose, Fulfilment check, MR scope, edges; only which bookkeeping section a node in this
scope reads/writes changes (below), and how its Fulfilment check gets evaluated (Judging fulfilment,
below).

## Is the Track due this pass?

Decided once, before `refactor-scan` even starts — the orchestrator's own Track-selection step
(`../../continuous-refactoring/references/track-scheduler.md`, `../../continuous-refactoring/SKILL.md`
step 1) computes every wired Track's `overdue_ratio` against `bookkeeping.md`'s `## Safety Net` section
(`../../continuous-refactoring/references/refactoring-bookkeeping.md`) and hands the winner to
`refactor-scan` as an explicit input. This section covers only what this Track does with that decision —
it never re-derives due-ness itself:

- **This Track wasn't the one step 1 selected** → nothing in this file runs this pass; `refactor-scan`
  continues with whichever Track was actually selected instead (or with everything else it already does,
  if none was due).
- **Selected, and `Open` is non-empty** (the ordinary in-progress case under the Safety Net blockade —
  `track-scheduler.md`'s own same-named section — or a manual override naming this Track directly) →
  the Track is still never rescanned — naming it never forces a scan, and an `Open` still written under
  the old meaning (nodes with filed issues only) is walked like any other. Walk the entries instead, per
  `track-open-processing.md`: workability triage, the pick-up
  Fulfilment re-check, exactly one node worked per pass — its issue filed only when worked (by `refactor-design`, never by the walk), never
  pre-filed. A node the re-check finds now fulfilled is reported as a **fulfilled at pick-up**
  finding for `refactor-learn`'s early call, which removes it from `Open`. The walk's re-check still
  applies this file's "Judging fulfilment" discipline (below); the scan process past this section
  doesn't run — skip straight to `refactor-scan/SKILL.md`'s `## Output`.
- **Selected, `Open` empty** → continue below; this is a genuine scan. A scan runs only in this case.

## Judging fulfilment

Whether a node is fulfilled is the agent's judgement, for every node in this Track's scope — the
script detects nothing and only receives the result (`refactor-scan/SKILL.md` step 4). **Judge by
Purpose, not by name** — the same discipline step 4 already applies to `psr-4`'s
`unwired_entry_points`, generalized here to every node in scope: read the node's own Fulfilment check
and Purpose line — its tree-doc entry, found via `php-tooling-tree.md`'s own per-node *Full
definition* pointer, not always one-file-per-node — then judge the actual repo against it — does a
real, working tool genuinely serve that Purpose, under any name, not only the one the node's own `Tool`
line happens to mention.

- **Direct evidence settles it.** The Fulfilment check's own named evidence present (the named
  dependency, the named config file, the named CI invocation) → fulfilled. Only when it is absent
  does the Purpose question open: does nothing serve the Purpose, or does something serve it under a
  name the Fulfilment check doesn't mention?
- **A working example**: `php-cs-fixer`'s Purpose is "automated code style so later Rector output lands
  styled," its `Tool` line names `php-cs-fixer`. A target running Laravel Pint (`laravel/pint` installed,
  `pint.json` committed, `vendor/bin/pint --test` clean) has no `friendsofphp/php-cs-fixer` dependency at
  all — the named evidence is absent. Judged against the Purpose line instead: Pint wraps PHP
  CS Fixer internally and genuinely serves "automated code style," so the node reads fulfilled. Never
  propose `php-cs-fixer` here — proposing a second, separately-configured style tool risks exactly the
  collision Pint's own presence already avoided.
- **Genuinely ambiguous** — two plausible tools present at once, or real uncertainty about whether one
  actually serves the Purpose or might collide with it — routes through the existing Flagged-candidate
  mechanism (`needs-info`, `../../refactor-design/references/decision-gate.md`), unchanged. Don't guess
  past a real collision risk; flag it instead, the same as any other genuinely ambiguous design decision.
- **No committed artifact at all, purpose stated as served some other way** (e.g., code style enforced
  by convention/review, no tool involved) — not a fulfilment judgement call at all: an ordinary
  `out-of-scope/<slug>.md` rejection with the maintainer's stated reason, same as any other rejection
  (below). Only safe for a node without a required child of its own within the tree — rejecting a
  required parent closes everything beneath it (`CONTEXT.md`'s **Required edge**), which would wrongly
  close a genuinely-served node's own descendants; every node in this Track's scope qualifies.
- **Required/Recommended/Required-any edge semantics and cascading closure on a rejected required
  parent are unchanged** — judgement decides each node's own fulfilled value, the tree's edges still decide how
  those values combine into what's proposable.

## Proposing and recording

Every node in scope still unresolved (neither fulfilled by judgement above, nor already rejected under
`out-of-scope/`) and currently unblocked (its own required/recommended parents already resolved/decided,
per the tree's ordinary edge semantics) → propose it by Name, same as `refactor-scan/SKILL.md` step 4
already does for any other node. These are the script's `next` entries inside this Track's scope —
what this pass can work; what gets recorded into `Open` is the wider set below. **No candidate issue is
created at this point** — the node's issue is created only when it is actually worked via the `Open`
walk (`track-open-processing.md`), not pre-filed during the
scan.

## Filling `Open`

A scan that runs this Track evaluates every node of the scope by agent judgement (all Fulfilment checks,
including gate nodes) and hands that fulfilled set to the script as a seed file
(`refactor-scan/SKILL.md` step 4). The script's `backlog` entries inside this Track's scope — every
unresolved node, in the script's order, blocked nodes included — go to `refactor-learn`'s closing call,
which writes them as `## Safety Net`'s `Open` (`../../refactor-learn/references/safety-net-write.md`).
The agent judges, the script orders.

The `Open` list is the complete, ordered backlog for this Track: every node of the Track's scope that
is neither fulfilled nor out-of-scope, in script order, hand-reorderable, blocked ones included. One per
bulleted line, `- <slug> (#<issue>)` (issue # only while the node is being worked, omitted otherwise).
`- none` when empty. Non-empty `Open` means the Track is never rescanned this pass — its existing
entries are worked through the ordinary propose → design → implement → learn pipeline first: resume
before proposing fresh.

**Every node in scope resolved, nothing to propose** → still a completed scan: `refactor-learn`'s closing
call writes `Last scan` and an empty `Open` regardless (`safety-net-write.md`), so a fully-compliant
target gets this Track's `Cadence` honored afterward instead of being rescanned every pass.
`Out-of-scope` stays however it already was (typically empty, on a target with nothing rejected).
