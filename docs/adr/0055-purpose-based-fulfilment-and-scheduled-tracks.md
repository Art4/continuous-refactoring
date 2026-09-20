# Fulfilment checks move from `tooling_tree.py` to agent judgement against a node's Purpose; scanning reorganized into four scheduled Tracks

> Amends [ADR-0054](0054-onboarding-safety-net-and-signal-wave.md): **Signal wave** is renamed
> **Guardrails**, for symmetry with **Safety Net** once both became **Track** names (below), and to stop
> reading as an alternate spelling of the unrelated **Signal** field. **Onboarding** narrows: only
> `git`/`loop-config` stay their own, separately engineered step; everything from the recognition gate
> onward collapses into "whatever the Safety Net Track's first run finds."
>
> Amends [ADR-0037](0037-continuous-housekeeping-skill-and-node-housekeeping-contributions.md): the
> standalone `continuous-housekeeping` skill is retired. Its mechanism — `housekeeping-template.md`,
> nodes contributing their own recurring-check line, one issue per due cycle — is unchanged; only *how
> it gets triggered* changes, from its own skill-local due-check to the shared Track scheduler below.
> Its `references/` (setup interview, template-file-format doc) move under `continuous-refactoring`.
>
> Amends [ADR-0008](0008-generic-tool-tree-and-structural-scan-gate.md): `structural-scan`'s own gate
> mechanism (`resolved` edges, cascading closure on a rejected required parent) is untouched, but *when*
> it gets scanned for new candidates is now scheduled by the Track model below, under the name
> **Investigation**, rather than simply "proposed once its required parents are decided."
>
> Amended by [ADR-0056](0056-agent-judged-fulfilment.md): `Open` in each Track's `bookkeeping.md`
> section is redefined as the complete, ordered backlog for that Track — every unresolved node of the
> Track's scope, blocked ones included, in script order, hand-reorderable, carrying an issue number
> only while the node is being worked. `Open` empty means the Track is done. `Fulfilled nodes` is
> retired from the schema and ignored where it still exists. The one-time bootstrap exception is
> corrected: it does not wait for Guardrails' `Open`, and the claim that ordinary eligibility keeps
> Guardrails selected after its first scan is removed.

Raised against a live incident: `refactor-scan` proposed adopting `php-cs-fixer` on a target that
already ran Laravel Pint (which wraps PHP CS Fixer internally, under its own config format). The
candidate's own text correctly flagged that a second, separately-configured style tool could collide
with Pint — "worth a human call... before it's ever picked" — but the issue still carried
`ready-for-agent`; only a downstream agent's own refusal to implement it blindly caught the collision
before it landed. `tooling_tree.py`'s Fulfilment checks are hardcoded to specific package names, with no
way to recognize a real, working equivalent under a different one. This isn't specific to Pint: any node
whose ecosystem has more than one viable implementation carries the same blind spot, and code-style
tooling is merely the sharpest example of it in PHP. Settled via `/grill-with-docs`, several rounds.

## Considered Options

- **Hardcode Pint as a named equivalent for `php-cs-fixer`**, the same inline-OR shape `phpunit` already
  uses for Pest. Rejected — solves this one instance, not the underlying class. Every future
  fragmented-ecosystem node would need its own hand-maintained equivalence list, and no such list is ever
  exhaustive; the next unrecognized tool just reproduces the same incident under a different node.
- **A new, third bookkeeping state — a human explicitly attests a node's purpose is served by an
  unrecognized tool.** Examined in detail across several grilling rounds before being dropped. It cannot
  safely reuse `Fulfilled nodes`: that field is a self-healing cache, overwritten wholesale by
  `tooling_tree.py`'s own current fulfilled-set whenever the parser runs, specifically to wipe out
  exactly this kind of manual entry. It cannot safely reuse `out-of-scope/` either, for any node with
  required descendants: rejecting a required parent permanently closes everything beneath it, which
  would be wrong for a node whose purpose is actually served, just not by a recognized name. Once the
  tree walk itself becomes agent-driven (below), the case this state existed to cover — "the tool exists,
  nothing in this suite recognizes it by name" — mostly stops occurring on its own; the narrow remainder
  is handled by reusing `out-of-scope` with a stated caveat (Decision, below), not a new mechanism.
- **Replace `tooling_tree.py`'s script-based Fulfilment checks with agent judgement against each node's
  own Purpose statement, keeping the tree's DAG (nodes, required/recommended/required-any edges,
  cascading rejection) exactly as documented.** Chosen. An agent recognizes any real, working tool that
  serves a node's stated Purpose — Pint satisfies `php-cs-fixer`'s Purpose without being named anywhere —
  for every present and future fragmented-ecosystem node, with no per-node equivalence list to maintain.
  The explicit cost, accepted deliberately rather than overlooked: `tooling_tree.py`'s ~1900 lines and
  `scripts/test_tooling_tree.py`'s 202 deterministic tests lose their role as ground truth for the whole
  tree, not only its fragmented corner — the tree's own CI-checkable precision was never actually the
  goal here; "does this repo genuinely have working code-style tooling" is.

## Decision

### `CONTEXT.md` gains **Track**; **Signal wave** renamed **Guardrails**; `continuous-housekeeping` retired as a standalone skill

Four Tracks: **Safety Net**, **Guardrails**, **Investigation** (the existing structural-scan/Deepening/
Hot-spot search activity, now named as a schedulable Track rather than renaming any of those terms), and
**Housekeeping**. Full definitions: `CONTEXT.md`.

### Fulfilment checks move to agent judgement against a node's Purpose

Unchanged: the tree's shape, every edge type and its semantics, cascading closure on a rejected required
parent. Changed: a node's Fulfilment check is no longer `tooling_tree.py` matching a dependency name —
it's an agent, walking the tree during its Track's scan, judging whether the node's stated Purpose is
genuinely served, by whichever real tool turns out to do it. Node slugs stay as they are (`php-cs-fixer`
remains `php-cs-fixer`) — Purpose, not the slug, is now what fulfilment actually reads; renaming slugs
toward their Purpose was considered and deferred, not rejected, pending a concrete reason to pay the
rename cost.

### `bookkeeping.md`: one section per Track, no `Done` cache, `Open`/`Out-of-scope` delta only

Replacing `Fulfilled nodes` and the single global `Pending candidates`:

- **Safety Net** / **Guardrails** sections: `Cadence`, `Last scan`, `Open` (`- <slug> (#issue)`),
  `Out-of-scope` (`- <slug>` + pointer to the existing `out-of-scope/<slug>.md`, format unchanged). A
  Track already holding `Open` work is never rescanned; existing entries are worked through the ordinary
  propose → design → implement → learn pipeline first. `refactor-learn` removes an entry from `Open` on
  merge, or on rejection removes it and writes the `out-of-scope/` entry — the same symmetry the tree
  already applies to every other rejection.
- **Investigation**: no section content. The issue tracker / `merge-requests.md` stays authoritative, as
  today.
- **Housekeeping**: `Cadence` and `Last scan` only; the swept content stays in
  `housekeeping-template.md`, unchanged.
- A Track's section doesn't exist until its first run completes — absence means "never run." The first
  run always writes `Last scan`, even when `Open`/`Out-of-scope` end up empty, so a repo that's already
  fully compliant still gets that Track's cadence honored afterward instead of being rescanned every
  pass.
- No migration for repos on the old schema: old fields simply stop being read or written, `out-of-scope/`
  is reused unchanged, and a pre-existing repo's first Track scan under this model is just a one-time,
  fuller version of the same "the tree grew, check the delta" mechanism a Track already runs whenever its
  own scope grows in the future.

### Scheduling: per-Track cadence, staleness ratio, one one-time bootstrap exception

Default cadences: Safety Net 90 days, Guardrails 60 days, Housekeeping weekly (unchanged from today),
Investigation continuous (no fixed interval — the lowest-priority fallback). Each pass runs the due
Track with the highest `(today − Last scan) / Cadence`; ties, and which Track's open work gets
design/implement effort when several hold `Open` simultaneously, both fall back to the fixed order
Safety Net > Guardrails > Housekeeping > Investigation.

One deliberate, one-time exception per target: the pass right after Safety Net's `Open` first empties
runs Investigation, then Guardrails, then Housekeeping, one turn each, in that order — before the
ordinary priority order takes over permanently. This extends the same UX reasoning ADR-0054 already used
to move Guardrails nodes behind the Safety Net closing, one step further: a target should see one real
piece of delivered refactoring value before being asked to adopt more tooling or sit through maintenance.

The scheduler lives in `continuous-refactoring/SKILL.md`, at the start of a pass; `refactor-scan` becomes
Track-aware, told which Track to scan rather than deciding on its own. Manual override per Track stays
available (e.g. `/continuous-refactoring housekeeping`), generalizing today's `continuous-housekeeping`
invocation to all four.

### `loop-config` stays a distinct, mandatory human interview

The tooling-detection part of Onboarding collapses into "the Safety Net Track's first run" (above), but
`git`/`loop-config` remain their own step ahead of it, unchanged from today's interview
(`refactoring-bookkeeping.md`) — `bookkeeping.md` has to exist before any Track can write to it, and
Create-mode/Focus areas/Refactoring goal are genuine preferences, not facts a scan can derive.

### The "Confirmed node" idea is dropped; `decision-gate.md` is unchanged

An agent-undetectable equivalent (code style enforced purely by convention, no committed artifact at
all) goes through an ordinary `out-of-scope` entry with a stated reason, reusing existing machinery
rather than adding a third state — safe specifically because it's scoped to nodes without required
descendants (Considered Options, above); a future node that needs this and does have required
descendants would need this revisited. `decision-gate.md`'s Flagged-candidate escalation (`needs-info`)
remains the path for genuinely ambiguous agent judgement calls — two plausible tools present at once, or
real uncertainty about collision risk — unchanged.

## Consequences

`tooling_tree.py` and `scripts/test_tooling_tree.py`'s 202 deterministic tests lose their role as the
tree's ground truth; the fixture harness's `tier2`/`tier3` precision-recall tiers, built around them,
need rethinking or retirement — a separate follow-up, not decided here. `CONTEXT.md`'s **Fulfilment
check**, **Onboarding**, **Safety Net**, and **Housekeeping** entries are updated in this same change;
every other reference to "Signal wave" (18 files, chiefly `php-tooling-tree.md` and individual node
docs) still reads the old name and needs updating as that follow-up lands, not silently left
inconsistent. The Psalm/PHPStan mutual-exclusion housekeeping write (`psalm.md`'s own entry) is likely
redundant once an agent walks the tree directly instead of trusting a cache — left for that node's own
doc to reconcile then, not decided here. `continuous-housekeeping`'s own ADR-0037 stands as the record of
why the mechanism looks the way it does; only its standalone-skill shape is superseded.
