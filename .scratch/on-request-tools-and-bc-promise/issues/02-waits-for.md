# 02 — `after` is renamed `waits_for`

Type: task
Status: ready-for-agent
Blocked by: —

**What to build** (ADR-0086)

- Rename the Stage key `after` to `waits_for` in `pack.schema.json`, every `pack.json` (suite Packs and test fixtures),
  `tooling_tree.py`, `scripts/tooling_docs.py` (generated column header "Waits for") and the tests.
- A target's own Pack written before the rename still says `after`: the parser either reads both or ends with a message
  naming the rename — decide in the PR and say which.
- Prose: `tooling-model.md`, `tooling-parser.md`, `track-scan.md`, `rejection.md`, `docs/playbooks/own-tool.md` and any
  other hit of `` `after` `` outside `docs/adr/`. "B waits for A" is the reading.
- Regenerate `docs/tooling/`.

**Done when** no Pack, schema, script or reference outside `docs/adr/` uses `after` as a Stage key, and tests and
validator are green.

## Comments
