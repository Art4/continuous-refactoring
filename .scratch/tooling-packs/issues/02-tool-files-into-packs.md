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

## Comments
