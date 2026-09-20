# Guardrails Track scan

`refactor-scan/SKILL.md` step 4's own Guardrails-specific process: which nodes this Track covers,
whether it's due this pass, and how a node's Fulfilment check gets judged once it is. The same
mechanism `safety-net-track.md` already established, applied to a second node set — read that file
first if you haven't; this one only states what differs. Vocabulary: `CONTEXT.md` (**Track**,
**Guardrails**, **Safety Net**, **Fulfilment check**).

## Scope

The nodes `safety-net-track.md`'s own Scope section explicitly excludes from the Safety Net — every
node required on `structural-scan`/`php-safety-net` themselves, not merely reachable before
`structural-scan` opens. Concretely, for PHP: `composer-audit`, `phpmd`, `coverage-floor`,
`php-minimal-version`, `phpstan-level-6` and above, `phpstan-deprecation-rules`, `semgrep` (every
edge confirmed against `skills/refactor-scan/references/php-tooling-tree.md`'s current edge table).
Every one of these already carries its own required parent inside the tree (e.g. `composer` for
`composer-audit`, `phpstan-level-5` for `phpstan-level-6`) *and* an additional required parent on
`php-safety-net` itself — both must be satisfied, the ordinary AND-combination every node with more
than one required parent already gets. A node's tree-doc entry (`php-tooling-tree/<node>.md`) is
unchanged by any of this — same Purpose, Fulfilment check, MR scope, edges; only which bookkeeping
section a node in this scope reads/writes changes (below), and how its Fulfilment check gets
evaluated (Judging fulfilment, below).

## Is the Track due this pass?

The exact same mechanism `safety-net-track.md`'s own section of this name already documents, read
against `bookkeeping.md`'s `## Guardrails` section instead of `## Safety Net` — due-ness is decided once,
before `refactor-scan` starts, by the orchestrator's own Track-selection step
(`skills/continuous-refactoring/references/track-scheduler.md`, `skills/continuous-refactoring/SKILL.md`
step 0b); this file never re-derives it. Not selected this pass → nothing here runs. Selected with
`Open` non-empty → still never rescanned — the entries are walked instead
(`skills/refactor-scan/references/track-open-processing.md`), which owns the workability triage, the
pick-up Fulfilment re-check, and the one-node-per-pass rule, and reports any node its re-check finds
now fulfilled as a **fulfilled at pick-up** finding for `refactor-learn`'s early call to remove from
`Open`; skip straight to `refactor-scan/SKILL.md`'s `## Output`, the rest of this file doesn't run.
Selected with `Open` empty → continue below, a genuine scan.

Independent of the above, and unchanged from today: a Guardrails node is never actually unblocked in
the tree until `php-safety-net` itself is resolved (the Scope section's own required-parent edges) —
this Track being "due" per its own `Cadence` never overrides that. A target whose Safety Net hasn't
closed yet simply finds every Guardrails node still blocked when this Track's scan runs, same as
`tooling_tree.py`/the tree-walk fallback already reports for any other still-blocked node.

## Judging fulfilment

Run `python3 references/tooling_tree.py <target-repo>` once, same as `refactor-scan/SKILL.md` step 4
already does — its `detected` map is a first signal, not the verdict, for every node in this Track's
scope. **Don't take a Guardrails node's `fulfilled` value at face value** — the exact same discipline
`safety-net-track.md` already applies, generalized here to this Track's own seven nodes: read the
node's own Purpose line (`php-tooling-tree/<node>.md`), then judge the actual repo against it — does a
real, working tool genuinely serve that Purpose, under any name, not only the one the node's own `Tool`
line happens to mention.

- **The parser's own signal still counts.** `fulfilled: true` from the parser is never wrong to trust
  outright. Judgement only has work to do when the parser reports `false`.
- **A working example**: `composer-audit`'s Purpose is "dependency vulnerability visibility, enforced
  as a CI gate," its own Fulfilment check reads for a CI job whose text literally invokes
  `composer audit`. A target that instead defines a `composer.json` script (e.g.
  `"scripts": {"security-check": "composer audit"}`) and invokes that script from CI (`composer run
  security-check`) never matches the parser's literal substring check — it reports `fulfilled: false`
  — but genuinely runs the same underlying command, gated the same way, on every pipeline run. Judged
  against the Purpose line instead: the CI gate is real, just invoked through a level of indirection
  the parser's own text match doesn't follow. Never propose `composer-audit` here.
- **Genuinely ambiguous** — two plausible tools present at once, or real uncertainty about whether one
  actually serves the Purpose — routes through the existing Flagged-candidate mechanism (`needs-info`,
  `skills/refactor-design/references/decision-gate.md`), unchanged.
- **No committed artifact at all, purpose stated as served some other way** — not a fulfilment
  judgement call at all: an ordinary `out-of-scope/<slug>.md` rejection with the maintainer's stated
  reason, same as `safety-net-track.md` already documents. Only safe for a node without a required
  child of its own within the tree — every node in this Track's scope qualifies (none of the seven
  carries an outgoing required edge to another node).
- **Required/Recommended/Required-any edge semantics and cascading closure on a rejected required
  parent are unchanged** — same as `safety-net-track.md`.

## Proposing and recording

Every node in scope still unresolved (neither fulfilled by judgement above, nor already rejected under
`out-of-scope/`) and currently unblocked (`php-safety-net` resolved, plus its own domain-specific
required parent already fulfilled, per the tree's ordinary edge semantics) → propose it by Name, same
as `refactor-scan/SKILL.md` step 4 already does for any other node. Its slug is added to `##
Guardrails`'s `Open` list — `refactor-learn`'s own side of this,
`skills/refactor-learn/references/guardrails-write.md`. **No candidate issue is created at this
point** — the node's issue is created only when it is actually worked via the `Open` walk
(`skills/refactor-scan/references/track-open-processing.md`), not pre-filed during the
scan.

## Filling `Open`

A scan that runs this Track evaluates every node of the scope by agent judgement (all Fulfilment checks,
including gate nodes), hands that fulfilled set to the script as a seed file (the `--seed` argument or
the Refactoring Notes' `fulfilled-set.json`), and records every unresolved node of the scope into
`## Guardrails`'s `Open` in the script's order, blocked nodes included. The seed file ensures the
script's graph logic (dependency edges, rejection cascades) computes the same backlog the agent's
judgement already decided — the agent judges, the script orders.

The `Open` list is the complete, ordered backlog for this Track: every node of the Track's scope that
is neither fulfilled nor out-of-scope, in script order, hand-reorderable, blocked ones included. One per
bulleted line, `- <slug> (#<issue>)`. `- none` when empty. Non-empty `Open` means the Track is never
rescanned this pass — same resume-before-propose discipline `## Safety Net`'s own `Open` already
follows.

**Every node in scope resolved, nothing to propose** → still a completed scan: `refactor-learn`'s
closing call writes `Last scan` and an empty `Open` regardless (`guardrails-write.md`), so a
fully-compliant target gets this Track's `Cadence` honored afterward instead of being rescanned every
pass. `Out-of-scope` stays however it already was (typically empty, on a target with nothing rejected).
