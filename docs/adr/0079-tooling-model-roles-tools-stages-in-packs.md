# The tooling tree becomes Roles, Tools and Stages in Packs

> Amended by [ADR-0086](0086-tools-on-request.md): a Tool may be *on request*, and `after` is renamed `waits_for`.

> Amended by [ADR-0080](0080-a-role-is-filled-per-scope.md): a Role is filled per scope, not once for the target.

> Supersedes the graph mechanics of [ADR-0007](0007-required-recommended-edges.md) (required and recommended
> edges), [ADR-0008](0008-generic-tool-tree-and-structural-scan-gate.md) (the generic root and the
> `structural-scan` gate), [ADR-0016](0016-recommended-edges-gate-until-decided.md) (recommended edges gate
> until decided), [ADR-0017](0017-php-structural-scan-aggregation-node.md) (the language aggregation node),
> [ADR-0019](0019-static-analyzer-mutual-exclusion-and-taint-analysis-node.md) (PHPStan or Psalm as a
> mutual exclusion), [ADR-0022](0022-is-php-project-recognition-gate.md) (the recognition gate),
> [ADR-0040](0040-signal-tool-nodes-and-tree-edge-simplification.md) and
> [ADR-0054](0054-onboarding-safety-net-and-signal-wave.md) where they describe edges and aggregation. What
> they decided about **Safety Net**, **Guardrails**, **Signals** and **Onboarding** as concepts stays.
>
> Amends [ADR-0056](0056-agent-judged-fulfilment.md) and [ADR-0014](0014-tooling-tree-parser-ships-under-refactor-scan.md):
> the parser still computes graph logic only and ships with the data it reads, but the data are JSON Packs.

> Supersedes [ADR-0018](0018-psalm-becomes-a-tree-node.md) and [ADR-0035](0035-resolved-gate-cascades-through-rejected-required-ancestor.md).

> Supersedes in part [ADR-0005](0005-tooling-tree-not-baseline-skill.md) and [ADR-0021](0021-remaining-php-tooling-tree-nodes-extracted.md).

> Amends [ADR-0032](0032-psr-4-node-for-app-source-autoloading.md), [ADR-0044](0044-coverage-floor-node.md), [ADR-0045](0045-semgrep-owasp-top-ten-node.md) and [ADR-0074](0074-state-lives-in-the-tracker-found-by-search.md).

The suite could not be used on another language, and adding a tool was expensive. A node meant a row in
an edge table, a line in a diagram, a stub in a tree doc, a file of its own and sometimes a change in the
parser; Infection waited from August. Competing tools needed graph tricks: PHPStan or Psalm cost
`static-code-analyzer`, `psalm` as a recognition-only node, `phpstan-not-psalm` and two `required-any`
groups, and Pint had no model at all. The tree docs carried their own history, and a node's Track was
computed by the parser and written nowhere.

## Decision

**Roles, Tools, Stages, Packs.** A **Role** is what a tool is for (Static Analysis, Code Style). A **Tool**
plays one or more Roles and is *recommended* (proposed when its Role is empty) or *recognized* (counted when
present, never proposed). A **Stage** is one degree of a Tool — a PHPStan level, a Rector set — and the unit
a ticket is filed for; today's node is a Stage, so slugs and Names stay and the traces in targets stay. A
**Pack** is a set of Tools with an *Applies when* sentence the agent judges once per run; there is a
generic Pack, a PHP Pack, and a target may keep a Pack of its own. A **Ratchet** is how a Stage is raised
without letting the old violations back. Security is a Signal, not a Track; a Track stays a phase of work.

**The data are JSON with a schema**, one `pack.json` per Pack and one `roles.json`, written in one fixed
form. Prose stays in one Markdown file per Tool. The parser stays and reads the Packs with the standard
library only; a generator writes the Markdown tables and Mermaid diagrams for humans under `docs/`, which
the suite does not ship.

**Rules.**

- `requires` names a Stage, a Role (filled once the first Stage of one of its Tools is fulfilled), or an
  any-of list of Stages. `after` blocks until its Stages are decided and is released by a rejection.
- A rejection names a Role, a Tool or a Stage. **Choice** goes as a term: a Role filled by another Tool takes
  the place of the Tool that is not chosen (PHPStan is *out* on a target on Psalm) and needs no rejection.
- There are no aggregation nodes and no recognition-only nodes. The Safety Net is fulfilled when every
  Safety Net Stage is decided, in the Packs that apply and of the Tools in use; Guardrails Stages wait for it.
  The condition on Composer Audit (a real dependency) is the Stage's own *Applies when*; the empty
  baseline PHPStan's next level waits for is the Ratchet, part of the level's Fulfilment check.
- A Stage requires only Stages of its own Track or an earlier one.
- The runtime floor is handed in by the agent and compared by the parser as numbers, best effort; a value it
  cannot read blocks nothing, and every block names both values. Tool versions are not compared.
- `test-runner-if-missing` goes: the Role Testing with PHPUnit recommended does its job. A target's open
  ticket of that Name is closed with a note that Testing takes it over.
- The trace of a scan is kept per Stage, not per Track: a Stage with no ticket ever and no rejection is
  unknown and makes its Track's scan due, and the scan judges only unknown Stages.
- Tracks stay built on each other; an autonomous run with the Safety Net open ends as before.

## Considered Options

- **Change the format first, keep the meaning.** Aggregation nodes and `resolved` edges would be written
  into JSON and parser and data changed a second time. Rejected: two rewrites of one thing.
- **Keep nodes, add Tool and Role as labels.** Competing tools stay graph tricks. Rejected.
- **A Security Track.** Security tools sit in three Tracks today, answering *when*; a Track for a topic mixes
  phase and topic. Rejected; Signals already name the topic.
- **YAML or TOML for the data.** YAML needs a package in the target; TOML's `tomllib` needs Python 3.11.
  JSON needs nothing.
- **Tables as the source, read by a Markdown parser.** Lists in cells are convention, the parser reads
  Markdown, and the shape cannot be checked by a schema. Rejected; the table is generated.
- **Per-runtime version comparison schemes (ordered lists, calendar versions).** More than the check buys;
  a false positive is visible in the reason and a miss shows as a failing install.

## Consequences

**Pinned by an equivalence run.** The old parser (the base commit, in a throwaway worktree) and the new one
were given the same seeds and compared on tracks, nodes, backlog, withheld, closed, runtime blocks, reversals
and whether the Safety Net is fulfilled: 1,864 comparisons over four worlds. The seeds are the empty seed,
a walk that fulfils everything the old parser calls next, one rejection at every coherent point of the walk,
rejections with a blocker, and four runtime floors. The sample inputs are the repository's PHP fixtures; the
parser reads only the tracker file of a target, so a fixture enters through its onboarding and runtime.

- **PHP project with a real dependency** (665 comparisons): no difference.
- **PHP project without a real dependency** (675): `composer-audit` is absent everywhere instead of
  withheld — its own *Applies when* — and Guardrails count as fulfilled without it.
- **A target on Psalm** (488): the PHPStan Stages are absent instead of withheld, `rector-type-coverage` no
  longer waits forever for a PHPStan level that cannot come, and the Safety Net can be fulfilled where it
  never was.
- **Not a PHP project** (36, generic Stages): the PHP Stages are absent, the Safety Net is fulfilled once
  `ci-runner` and `editorconfig` are decided, and `secret-detection` is workable — the gap the recognition
  gate left.

Not a difference of behaviour but of shape: the nodes `structural-scan`, `php-safety-net`,
`is-php-project`, `static-code-analyzer`, `has-real-dependency`, `phpstan-not-psalm`, `phpstan-baseline-empty`
and `test-runner-if-missing` are gone; the keys `detected`, `next`, `withheld`, the top-level `backlog` and
`unblocked_by` are gone because no reference reads them; `php_floor_blocked` is `runtime_blocked`,
`tree.edges` is `tree.stages`, `safety_net_fulfilled` is new, and reason texts are worded for Stages.

**Delivered in parts.** First the model, the data and the parser beside the old one, with no run using
them; then the references switch, the old parser, its tests, the edge tables and the nodes that no longer exist
go, `CONTEXT.md` gets the terms, and the superseded ADRs get their banners. Then the files per Tool move into
the Packs and lose their history, the generator and the validator checks follow, then a target's own Pack,
then a new Pack as the acceptance case.

**What a target sees.** Rejections already on record keep their Stage names. A rejection of a Role or a Tool
is new, and a scan of an existing target proposes Stages it has not judged before (per-Stage trace).
