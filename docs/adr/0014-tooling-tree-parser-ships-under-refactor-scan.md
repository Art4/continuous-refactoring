# The tooling-tree parser and its two tree docs ship together under `skills/refactor-scan/references/`

> Extends [ADR-0013](0013-skill-reference-docs-live-under-skills.md): the same "if a `SKILL.md` instructs the agent to consult it, it lives under `skills/<owning-skill>/references/`" rule, now applied to an executable script and the data it loads at runtime, not just a markdown reference doc.

The same manual testing that found ADR-0013's gap surfaced a second, worse instance: `refactor-scan` and `continuous-refactoring` shell out to `scripts/lib/tooling_tree.py` by its suite-repo path, and `refactor-prioritize`/`refactor-design` separately cite `docs/tooling-tree.md`/`docs/php-tooling-tree.md` as material to read — none of which ships. Worse than a plain doc citation: the script itself loaded its two tree docs relative to the suite's own repo root (`Path(__file__).resolve().parents[2]`), so even copying the script alone into a skill's directory wouldn't have worked — its dependency on the two docs was invisible until traced.

All three files are one unit: the script cannot answer without its docs, and the docs are pointless to a skill without the script reading them the same way a human would. They move together.

## Considered Options

- **Symlink a bridge file under `skills/refactor-scan/references/` back to `scripts/lib/tooling_tree.py`.** Rejected: `README.md` documents "or copy" as a valid alternative to symlink install. A copy install would copy the bridge symlink itself, which then dangles — the real file it points at was never installed. Silent breakage under one of two documented install paths is worse than the extra move.
- **Duplicate the script into `skills/refactor-scan/references/`, keep the original in `scripts/lib/` for the suite's own tests.** Rejected for the same single-source-of-truth reason ADR-0013 rejected duplicating `refactoring-config.md`: one parser, two copies to keep in sync.
- **Move all three files for real, and make the script resolve its two docs as siblings of itself** (`Path(__file__).resolve().parent`) instead of via the suite's repo root. Accepted: works identically under symlink or copy install, and the script no longer has any hidden dependency on the suite checkout's layout for anything it needs to ship.

## Consequences

`scripts/lib/tooling_tree.py` → `skills/refactor-scan/references/tooling_tree.py`; `docs/tooling-tree.md` → `skills/refactor-scan/references/tooling-tree.md`; `docs/php-tooling-tree.md` → `skills/refactor-scan/references/php-tooling-tree.md`. `refactor-scan` owns them — proposing tooling-tree nodes is its job. The script keeps a `REPO_ROOT` constant only for `roadmap()`'s dev/test-only fixtures fallback (`fixtures/php/<name>/expected/`), never reached outside the suite's own test harness — no target repo ships a `fixtures/` tree, so this is not a shipping concern.

The deterministic parser is a convenience layer over what the tree docs already say in prose — each node's Fulfilment check is written there for a reader, script or not. So a second gap closes at the same time: `refactor-scan` and the orchestrator's outlook step had no path forward if `python3` isn't installed or running it isn't permitted in the executing harness. Both now dispatch a sub-agent with `skills/refactor-scan/references/tree-walk-prompt.md`'s prompt instead, which walks the same tree docs by hand — required edges gate, recommended edges don't, `structural-scan`'s resolved edges clear on fulfilment or an out-of-scope record, table order decides which nodes come back. With no sub-agent mechanism, the calling skill runs those same steps inline.

As with ADR-0013, no skill cites this ADR by number — the rule is a plain pointer to the reference files, nothing more.
