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
- `tooling-tree.md` and `php-tooling-tree.md` go; their remaining prose moves to `tooling-model.md` or the
  Tool files.
- `CONTEXT.md` gets Role, Tool, Stage, Pack, Ratchet and the changed Track, Safety Net, Guardrails,
  Fulfilment check entries; Choice, aggregation node, recognition-only gate node, required-any and
  resolved edge go (D7).
- Docs that describe the tree read true: `README.md`, `docs/architecture.md`, `docs/playbooks/tracks.md`,
  `docs/FAQ.md`, `docs/known-limitations.md`; a changelog fragment.

**Done when** the tests and the validator are green, `grep` finds no `tooling-tree/` or
`php-tooling-tree` path outside `docs/adr/` and `.scratch/`, and every Tool file is reachable from its
Pack.

## Comments
