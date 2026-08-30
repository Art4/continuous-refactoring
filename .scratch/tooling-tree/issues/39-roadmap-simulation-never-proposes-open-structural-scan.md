# 39 — `roadmap()`'s 10-step simulation never proposes `structural-scan` once its gate is already open

**What to build:** `tooling_tree.py`'s `next_candidates()` already special-cases `structural-scan`
(checked on its own terms *before* the generic "already fulfilled, skip" check — see its own code
comment: `detect_nodes()` marks this node "fulfilled" the instant its gate opens, but that's the gate
*opening*, not the node being delivered and done). `roadmap()`'s simulation loop never got the matching
fix: it checks `if sim_fulfilled.get(node, False): continue` *before* reaching its own
`if node == "structural-scan":` branch, so once every PHP-tree leaf is resolved (fulfilled or rejected),
`roadmap()`'s 10-step lookahead skips `structural-scan` entirely and falls through to the meaningless
`phpstan-level-N` "open chain" filler instead — for every step, forever, on any repo whose tree is fully
resolved.

**Why:** Found while building `fixtures/php/php-clean/` for ticket 27's Tier 4 "clean repo" negative
control. `next_candidates(php-clean)` correctly returns `[structural-scan]` and nothing else — the real,
already-fixed API `refactor-scan`'s `SKILL.md` tells the skill to read. But
`skills/refactor-scan/references/tooling_tree.py <php-clean> --steps 10`'s `roadmap` field lists
`phpstan-level-4` through `phpstan-level-13`, never `structural-scan`, even though `next` in the same
output is correct. `fixtures/php/php-clean/expected/roadmap.json` currently records this buggy-but-real
behavior honestly (see `fixtures/README.md`'s `php-clean` entry) rather than asserting a wished-for
result — this ticket is to fix the parser, not the fixture.

Low real-world impact today: `refactor-scan`'s own `SKILL.md` already tells the skill to use `next`, "not
`roadmap`" — "`roadmap` simulates forward … so entries past the first are a future lookahead, not real
options today" — precisely because of this class of drift between the two functions. But `roadmap()` is
still what a human skimming `fixtures/harness/run.sh roadmap --verbose`'s "Next 10 MRs" output sees, and
any future consumer that *does* trust `roadmap()`'s forward simulation past this point would silently
never see the loop's actual endpoint (opening structural work) — it would look like the tree just keeps
generating phantom PHPStan levels forever.

**Blocked by:** none — self-contained fix in `skills/refactor-scan/references/tooling_tree.py`'s
`roadmap()`.

**Status:** needs-triage

- [ ] Give `roadmap()`'s simulation loop the same before-the-generic-skip special case
  `next_candidates()` already has for `structural-scan` (move/duplicate the `node == "structural-scan"`
  branch ahead of the `if sim_fulfilled.get(node, False): continue` check, mirroring `next_candidates()`'s
  ordering and its own explanatory comment)
- [ ] Regenerate `fixtures/php/php-clean/expected/roadmap.json` (and re-check the other 6 fixtures'
  `expected/roadmap.json` for the same drift — none of them reach a fully-resolved tree today, so none are
  expected to change, but confirm)
- [ ] Add a `test_tooling_tree.py` case: a tree state with every `structural-scan` leaf resolved must have
  `roadmap(steps=1)[0]["node"] == "structural-scan"`

## Comments

> **2026-08-30:** Filed while building `fixtures/php/php-clean/` for ticket 27 (Tier 4 negative controls) —
> not fixed there to keep that ticket's diff scoped to the test harness, not the tooling-tree parser. See
> `fixtures/php/php-clean/expected/roadmap.json` for the currently-real (buggy) recorded output.
