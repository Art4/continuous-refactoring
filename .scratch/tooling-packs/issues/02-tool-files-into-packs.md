# 02 — Tool files into the Packs, and the new terms

Type: task
Status: ready-for-agent
Blocked by: 01

**What to build**

- The node files under `references/tooling-tree/` and `references/php-tooling-tree/` move to
  `references/packs/<pack>/`, one file per Tool (`../spec.md`, *File seams*). Each keeps Fulfilment check
  and MR scope per Stage, the Ratchet, the Housekeeping line; it loses the history prose ("used to be",
  "tried and dropped") — that lives in the ADRs and git.
- `php-cs-fixer.md` recognizes Pint and ECS (the Fulfilment check names only `friendsofphp/php-cs-fixer`
  today, against `CONTEXT.md`).
- `tooling-tree.md` and `php-tooling-tree.md` go, with the banner that says their edge prose is superseded;
  what remains of their prose moves to the Tool files, the paragraphs about edges, parents and children
  are dropped.
- `CONTEXT.md` got the terms in ticket 01, part 2; here **Stage** drops its note about the old word
  *node* once the Tool files no longer use it, and the validator's avoid-term list follows.
- Docs that still describe the tree before the model read true; a changelog fragment.

**Done when** the tests and the validator are green, `grep` finds no `tooling-tree/` or
`php-tooling-tree` path outside `docs/adr/` and `.scratch/`, and every Tool file is reachable from its
Pack.

## Decisions (grilled 2026-10-18)

- Files: `packs/<pack>/<tool>.md` beside `pack.json` (`details` points there); `git` and `onboarding-setup`
  under `prerequisites/`, named by `tooling-model.md`. Prose for a Pack as a whole in `packs/<pack>/README.md`
  (the PHP Pack's runtime floor and `require-dev` advisories).
- One form: a paragraph on the Tool (including a sentence **Why this order**, kept where the reason is
  still true), then per Stage Purpose (only beyond the Role's), Fulfilment check, Config, MR scope,
  Verification, Housekeeping. Name, Tool, Role, Track, Requires and After are in the JSON, not repeated.
  History prose and the words *node*, *edge*, *parent* are gone.
- Pint and ECS become recognized Tools of the Role Code Style (Psalm's pattern); PHP CS Fixer is out on a
  target that runs either; the "another tool serves the Purpose" rule in the scan names the Stage of the
  recognized Tool.
- The `Stage` entry of `CONTEXT.md` keeps `_Avoid_: node` (the parser's output keys still carry it) and
  loses the note about files not yet cleaned; the duplication allow-list for stubs goes.
- Two parts. Part 1: generic Pack, prerequisites, the smaller PHP Tools, Pint/ECS, the Pack README. Part 2:
  PHPStan, Psalm, Rector, the two tree documents and the old folders go, every path and word, CONTEXT.md,
  docs, validator.

## Comments
