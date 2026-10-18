# tooling-packs

Rebuild the **tooling tree** as **Roles**, **Tools** and **Stages**, delivered in **Packs** of tables.
Collected in discussion on 2026-10-14 and 2026-10-17; nothing is decided beyond the section *Decided so
far*. Open points are grilled next (`/grill-with-docs`), and the tickets of this series are cut from the
answers.

## Why

- **The suite cannot be used on other languages.** JS, Node or Python repositories would need a tree of
  their own, and building one — or adding a node to the PHP tree — is too hard today.
- **Many good tools stay out.** The PHP tools worth knowing (Twig tools among them) and security tools that
  help every repository (the secret scan over the Git history) are expensive to add: a node today touches
  the edge table, the diagram, the stub in the tree doc, its own file and sometimes the parser. Infection
  (`.scratch/php-tooling-tree/issues/09`) has waited since August.
- **Competing tools need graph tricks.** PHPStan or Psalm costs `static-code-analyzer`, `psalm` as a
  recognition-only node, `phpstan-not-psalm`, two `required-any` groups and an *Equivalents* section.
  PHP CS Fixer or Pint has no model at all: `CONTEXT.md` says Pint fulfils `php-cs-fixer`, but that
  node's Fulfilment check names only `friendsofphp/php-cs-fixer`.
- **The tree docs carry their history.** `php-tooling-tree.md` has 492 lines; node files tell what an edge
  used to be and what was tried and dropped. A node's Track is computed by the parser and written
  nowhere.

## Facts

- Outside the tree docs and the parser the suite is almost language-neutral. PHP-specific are the PHP
  floor (`_LEAF_MIN_PHP_VERSION`, `php_floor_precheck()` in `tooling_tree.py`) and the aggregation node
  `php-safety-net`.
- The parser detects nothing since ADR-0056; it computes graph logic only — per Track the nodes, backlog,
  withheld and next nodes; the rejection cascade; the aggregation nodes' state; the PHP floor and its
  reversals. Six references call it (`worklist.md`, `selection.md`, `track-scan.md`, `track-choice.md`,
  `rejection.md`, `reconcile.md`); `test_tooling_tree.py` holds its rules in 106 tests. Without
  `python3` the same answers are worked out by hand (`tooling-tree-parser.md`).
- The node files already group per tool: `rector.md` holds five nodes, `phpstan.md` the level chain,
  `psalm.md` two nodes.
- Eleven files outside the tree docs name them: `README.md`, `docs/architecture.md`,
  `docs/playbooks/tracks.md`, `housekeeping-track.md`, `implement-point.md`, `reconcile.md`,
  `rejection.md`, `selection.md`, `track-choice.md`, `track-scan.md`, `worklist.md`.
- Security tools sit in three Tracks today: `psalm-taint-analysis` in Safety Net; `composer-audit`,
  `secret-detection`, `semgrep` in Guardrails; the secret scan over the history in Housekeeping.
  `CONTEXT.md` calls the Security signal and Safety Net membership orthogonal.

## Terms

| Term | Means | Examples |
|---|---|---|
| **Role** | what a tool is for; a tool plays one or more Roles, a Role can be empty (from role modelling: Reenskaug's OOram, Riehle, DCI) | Static Analysis, Code Style, Testing, Taint Analysis, Secret Detection |
| **Tool** | the concrete tool | PHPStan, Psalm, PHP CS Fixer, Pint |
| **Stage** | one degree of a tool; today's **node** is a Stage, so slugs and the targets' traces stay | PHPStan Level 0 … 10, Rector: Dead Code Set |
| **Track** | as today; carried by the Stage | Level 5 is Safety Net, Level 6 Guardrails |
| **Pack** | Tools with an *Applies when* condition; replaces recognition gates such as `is-php-project` | PHP, Twig, a target's own |
| **Ratchet** | the pattern for raising a Stage: no new violations, old ones shrink, one direction only. A property of a Tool, not a level of its own | PHPStan baseline, coverage floor |

Rejected names: **Practice** (for Role; the user dislikes it), **Capability** (collides with the tracker
operations' "capability"), **Level** (a PHPStan word), **Step** (in general use in `CONTEXT.md`). Slot and
Port/Adapter were the runners-up for Role.

## Decided so far

- **Everything stays in this repository.** Packs are not moved out.
- **Security is no Track.** A Track says when and what for (secure before structural work, hold quality
  after it, maintain regularly, investigate); Security says which topic. It stays a **Signal**; the
  security tools are the Roles that carry it. Working only on security would be a filter in the call, not
  a Track. Follows from: a Track stays a phase or function, not a topic — to be confirmed in the grilling.
- **File seams**, under `skills/continuous-refactoring/references/`:

  ```
  tooling-model.md      rules: Role, Tool, Stage, Pack, Ratchet, dependencies, rejection levels,
                        Track thresholds, working it out without python3; git and onboarding-setup
                        as the suite's own prerequisites, in no Pack
  roles.md              one table: Role | Name | Purpose | Signal
  tooling-parser.md     call, seed, output (today tooling-tree-parser.md)
  tooling_tree.py       reads every packs/*/pack.md
  packs/
    generic/pack.md     Applies when: always · editorconfig, ci-runner, secret-detection
    php/pack.md         Applies when: PHP code in the repository · one file per Tool beside it
    twig/pack.md        Applies when: .twig templates in the repository
  ```

  - Rules, catalogue and data are apart: the model changes rarely, the Packs whenever a tool is added.
  - `pack.md` is the only table the parser reads; a new Pack is a new directory, no parser change. A
    scan loads only the Packs whose *Applies when* holds.
  - One file per Tool, not per Stage: Fulfilment check and MR scope per Stage, the Ratchet, the minimum
    runtime and the Housekeeping line change together.
  - Twig is a Pack of its own (another condition); its Stages may require Tools of the PHP Pack.
  - A target's own Pack has the format of `pack.md`, lives in the target and is found through
    `## Refactoring operations`.
- **The parser stays, smaller.** One reader of the `pack.md` tables serves the run (order, blocking,
  rejection cascade), the validator (every reference exists, every required parent carries its child's
  Tracks) and the Mermaid generator. Dropping it would leave the cascade rules as untested prose.
- **The Mermaid diagram is for humans only.** It is generated from the Packs into `docs/`, never shipped,
  and the validator checks it is current. A target's own Pack has no diagram unless someone runs the
  generator there.

## Draft table

One row per Stage; `a | b` is any-of. A sketch with today's nodes, not a decision:

| Node | Name | Role | Tracks | Requires | After | Ticket | Details |
|---|---|---|---|---|---|---|---|
| `composer` | Composer | Package Manager | Safety Net, Guardrails | – | – | yes | `composer.md` |
| `phpunit` | PHPUnit | Testing | Safety Net, Guardrails | `composer` | – | yes | `phpunit.md` |
| `coverage-floor` | Coverage Floor | Testing | Guardrails | `phpunit` | – | yes | `coverage-floor.md` |
| `phpstan-level-0` | PHPStan Level 0 | Static Analysis | Safety Net | `composer` | – | yes | `phpstan.md` |
| `rector-php-set` | Rector: PHP Set | Automated Refactoring | Safety Net | Static Analysis | `php-cs-fixer` | yes | `rector.md` |

Per Pack, the Tools per Role:

| Role | Recommended | Also recognized |
|---|---|---|
| Code Style | PHP CS Fixer | Pint, ECS |
| Static Analysis | PHPStan | Psalm |
| Testing | PHPUnit | Pest |

## Open points

In the order they depend on each other.

1. **What a Track is, and whether Tracks stay built on each other.** Today `structural-scan` opens
   Guardrails and Investigation only after Safety Net. The earlier idea was independent Tracks; no run is
   known that needed it. Decides what takes `structural-scan`'s place, and point 8.
2. **What a rejection hits:** the Role ("no static analysis"), the Tool ("not PHPStan, we use Psalm") or
   the Stage ("not above level 6"). Today only the Stage, plus the **Choice** convention. Decides the
   parser's cascade and how a rejection is recorded in the target.
3. **Dependencies on three levels:** Role → Role (Code Style after `.editorconfig`), Stage → Stage of the
   same Tool (level 1 before level 2), Stage → a specific Tool (Rector: PHPUnit Set needs PHPUnit, not any
   test runner). Do `Requires`, `After` and `a | b` carry all three?
4. **Does `After` block or only sort?** The lessons behind today's blocking recommended edges speak for
   blocking; asking the human only for preferences speaks for sorting.
5. **Track threshold per Tool.** Safety Net counts PHPStan from level 5 today; which Psalm Stage matches is
   unresearched. Likely a mark on the Stage in `pack.md`.
6. **Trace per node instead of per Track.** A node with no ticket ever and no rejection is "unknown" and
   makes its Track's scan due. Also fixes new suite nodes never being proposed in targets that already
   have a trace.
7. **Recommended or only recognized.** Psalm is never proposed today, only recognized. Becomes a property
   of the Tool in the Pack (Tech Radar rings — Adopt / Trial / Assess / Hold — as an idea). Is the choice
   of Tool a decision point in an interactive run?
8. **An autonomous run with Safety Net unfinished:** end, or go on to Guardrails? Hangs on point 1.
9. **Where the fields hang:** Purpose and probably Signal on the Role; minimum runtime and Housekeeping
   line on the Tool; Fulfilment check, MR scope and Track on the Stage. Mostly clear, to be confirmed.

Smaller: whether the Track thresholds live in `pack.md`; how the eleven files above point at the new
references.

## Constraints

- Slugs and Names stay stable, or targets' existing tickets lose their trace.
- Supersedes parts of ADR-0007, 0008, 0016, 0017, 0040 and 0054; the change needs an ADR of its own.

## Suggested order, not decided

1. Format only, with today's meaning.
2. The new model, with its ADR.
3. Packs, the target's own Pack among them.
4. An acceptance case: Infection, or a second language.

Each step is cut by `principles.md`, *A merge request a person can review*.
