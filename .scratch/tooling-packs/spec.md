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
  a Track. Follows from D1: a Track is a phase or function, not a topic.
- **File seams**, under `skills/continuous-refactoring/references/` (since D14 `pack.md` reads
  `pack.json` throughout this spec):

  ```
  tooling-model.md      rules: Role, Tool, Stage, Pack, Ratchet, dependencies, rejection levels,
                        Track thresholds, working it out without python3; git and onboarding-setup
                        as the suite's own prerequisites, in no Pack
  roles.json            Role | Name | Purpose | Signal (D16; was roles.md)
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

## Decisions from the grilling

**Round 1 (2026-10-18)**

- **D1 — A Track is a phase or function, not a topic.** A new Track comes only for a new kind of work,
  never for a topic; topics are **Signals**.
- **D2 — Tracks stay built on each other.** Guardrails need a fulfilled Safety Net, as today; the Tracks
  column changes the notation, not the dependency. (Correction to an earlier claim: `structural-scan`
  opens only Guardrails through required edges. Investigation always has something
  (`track-choice.md`); what holds it back is the recommendation to end the run while Safety Net is
  unfinished.)
- **D3 — A rejection hits a Role, a Tool or a Stage,** and names its subject's Name. Rejecting a Role
  closes its Tools and Stages; rejecting a Tool closes its Stages and leaves the Role open for another
  Tool. A Role filled by another Tool needs no rejection: a target on Psalm has Static Analysis filled,
  and PHPStan's Stages are not proposed because their Tool was not chosen. **Choice** goes as a term.
- **D4 — Trace per Stage.** A Stage with no ticket ever and no rejection is unknown and makes its Track's
  scan due; the scan judges only the unknown Stages, not the whole Track again.
- **D5 — `After` blocks until its predecessor is decided** (fulfilled or rejected), as today (ADR-0016's
  run: Rector output landed unstyled); a rejection releases the child.
- **D6 — Where the fields hang.** Role: Purpose, Signal. Tool: minimum runtime, Housekeeping line, Ratchet
  or not, recommended or only recognized. Stage: Name, slug, Fulfilment check, MR scope, Tracks,
  `Requires`, `After`.
- **D7 — The new terms live in this spec** until the ticket that brings the model; `CONTEXT.md` gets them
  in the same PR as the skills change.

**Round 2 (2026-10-18)**

- **D8 — `Requires` names a Stage or a Role.** A Stage when that Tool is meant (Rector: PHPUnit Set
  requires `phpunit`); a Role when any Tool will do (`rector-php-set` requires Static Analysis). A Role
  is filled once the first Stage of one of its Tools is fulfilled. `a | b` stays for the rest
  (`psalm-taint-analysis`: level 4 or Psalm). Role after Role (Code Style after `.editorconfig`) is an
  `After` on the first Stage; there is no separate Role-level dependency.
- **D9 — No aggregation nodes.** "Safety Net fulfilled" is a state the parser computes: every Stage with
  the Track Safety Net, in the Packs that apply and of the Tools chosen, is decided (fulfilled, rejected
  or closed by a rejection). Guardrails Stages need it (D2) without an edge. The threshold is the Safety
  Net mark on a Stage (PHPStan level 5, not 6); Psalm has one Stage and it carries Safety Net, so no
  mapping of PHPStan levels to Psalm's `errorLevel` is needed.
- **D10 — An autonomous run with Safety Net waiting is unchanged:** it ends with "Safety Net is waiting
  for merges". Not part of this series; a real run asking for more becomes a ticket of its own.
- **D11 — A Tool is *recommended* or *recognized*.** Recommended: proposed when its Role is empty.
  Recognized: counted when present, never proposed. One recommended Tool per Role and Pack. No Tech
  Radar rings. Choosing the Tool is no new decision point: the ticket names the recommended Tool, and
  whoever wants another rejects it (D3) or adopts their own.
- **D12 — A Tool may be a convention** (`Tool: none`, as `.editorconfig`, `psr-4`,
  `php-minimal-version` today), but every Stage belongs to a Tool and every Tool plays at least one Role.
  The Roles' names are settled with the ticket, not here.
- **D13 — *Applies when* is judged by the agent** from the sentence in the Pack, once per run, and handed
  to the parser as the list of Packs that apply — like the fulfilled Stages in the seed. The parser checks
  nothing itself.

**Round 3 (2026-10-18)**

- **D14 — Pack data is JSON** (`pack.json`), the single source for the graph. Prose — Fulfilment check,
  MR scope, Ratchet, longer purposes — stays in the Markdown file per Tool. A generator writes the
  Markdown tables and the Mermaid diagrams from it. JSON needs nothing beyond Python's standard library;
  YAML would need a package, TOML (`tomllib`) Python 3.11 in the target. Whether a generated table also
  lies beside the Pack: round 4.
- **D15 — The JSON has a fixed form,** written by the generator: fixed indentation, one object per
  Stage, Stages in table order, keys in a fixed order. The validator fails on any other form and on
  outdated generated files; one command fixes both. A schema: round 4.
- **D16 — The Roles are JSON too** (`roles.json`), so the validator can check that every Role a Pack
  names exists. A Role's Purpose stays one sentence.
- **D17 — A target's own Pack is the same JSON,** found through `## Refactoring operations` and checked by
  the same rules. Where its example lives is settled with the ticket.

**Round 4 (2026-10-18)**

- **D18 — Generated tables live only under `docs/`,** never beside the Pack: two sources at run time
  would cost context and invite reading the wrong one. Someone in a target reads `pack.json`. Missing the
  table there in practice becomes a ticket of its own.
- **D19 — JSON Schemas ship beside the data** (`pack.schema.json`, `roles.schema.json`); every file
  points at its schema with `"$schema"`, so editors check and complete it, a target's Pack included. The
  schema holds structure (keys, types, allowed values such as Track names and recommended/recognized).
  This repo's validator checks against it in CI with `jsonschema` as a development-only dependency (as
  `pyyaml` is today), plus what a schema cannot: every Role and Stage named in `Requires` and `After`
  exists, every required parent carries its child's Tracks, one recommended Tool per Role and Pack. The
  parser in the target stays on the standard library, checks the few rules it computes with, and exits 2
  on a broken Pack, as on a broken seed.
- **D20 — The series is cut by meaning, not format first.** Format-only would map today's aggregation
  nodes and `resolved` edges into JSON and then change data and parser a second time. See *Order*.

**Round 5 (2026-10-18)**

- **D21 — A target's Pack may add Tools, Stages and Roles,** never redefine or remove the suite's; a
  suite Tool it does not want is rejected (D3). Slugs and Role names are unique across all Packs; a
  collision ends the parser with exit code 2.
- **D22 — The runtime comes in the seed, the parser compares best-effort.** The agent hands the target's
  lowest allowed runtime as a string (`"runtime": {"php": "7.4"}`), read from the target's constraint; the
  parser reads no target files any more. It compares by numbers, best-effort as today; a value it cannot
  read blocks nothing. No schema restriction on version strings, and no comparison schemes per runtime
  (too complex for what it buys). Every block names both values; the scan checks a block before it
  proposes the rejection, and a wrong comparison is a finding in the closing report. A block missed
  shows as a red check at the implement point. A miscomparison seen twice gets a parser test for that
  form. Tool versions are not compared: a Stage's minimum tool version (`phpstan-level-10` needs
  PHPStan 2) stays in its prose.
- **D23 — No recognition-only nodes remain.** A Stage may carry its own *Applies when*, judged like the
  Pack's (D13): `composer-audit` applies when the repository has a real dependency, which retires
  `has-real-dependency`. The empty-baseline condition is PHPStan's Ratchet: level N+1 requires level N,
  and level N is fulfilled only with an empty baseline (its Fulfilment check), which retires
  `phpstan-baseline-empty`. `phpstan-not-psalm` and `static-code-analyzer` go by D3 and D8. The draft
  table's `Ticket` column goes.
- **D24 — `test-runner-if-missing` goes;** the Role Testing with PHPUnit recommended does its job. Ticket 1
  gives it a section in the ADR and a step that closes an open ticket of that Name with a note that the
  Role Testing takes it over. Before that is written, check the targets for such tickets.

Side finding: `php_floor_precheck`'s docstring says a blocked leaf is not a rejection, while
`tooling-tree-parser.md` and `php-tooling-tree.md` have the scan propose one with a blocker; the
docstring is outdated and goes with the function in ticket 1.

## Open points

In the order they depend on each other.

1. ~~What a Track is, and whether Tracks stay built on each other~~ → D1, D2.
2. ~~What a rejection hits~~ → D3.
3. ~~Dependencies on three levels~~ → D8.
4. ~~Does `After` block or only sort?~~ → D5.
5. ~~Track threshold per Tool~~ → D9.
6. ~~Trace per node instead of per Track~~ → D4.
7. ~~Recommended or only recognized~~ → D11.
8. ~~An autonomous run with Safety Net unfinished~~ → D10.
9. ~~Where the fields hang~~ → D6.

Smaller: ~~whether the Track thresholds live in `pack.md`~~ (D9: a mark on the Stage). Left to ticket 1's
plan: how the eleven files above point at the new references; whether targets hold open tickets of
`test-runner-if-missing` (D24; youthweb's Redmine needs credentials this session does not have).

## Constraints

- Slugs and Names stay stable, or targets' existing tickets lose their trace.
- Supersedes parts of ADR-0007, 0008, 0016, 0017, 0040 and 0054; the change needs an ADR of its own.

## Order (D20)

1. **ADR and model.** The ADR, `tooling-model.md`, the schemas, the Packs as JSON (generic and PHP, every
   node of today as a Stage), the new parser with its tests, and the references switched to it in the
   same ticket — otherwise the new parser lies unused. The pin is an equivalence script: old and new
   parser get the same seeds from the fixtures; where D3, D4 and D9 leave the meaning alone the output
   is the same, and where they change it the ADR names each difference. Its plan cuts it into parts,
   for instance data and parser first, then the references.
2. **The files per Tool** move to `packs/`, lose their history prose; `CONTEXT.md` gets the new terms
   (D7).
3. **Generator and docs:** tables and Mermaid under `docs/`, and the validator's checks.
4. **The target's own Pack**, with an example.
5. **Acceptance case:** Twig or Infection, whichever is the smaller new Pack.

Each step is cut by `principles.md`, *A merge request a person can review*.
