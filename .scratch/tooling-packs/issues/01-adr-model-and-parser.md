# 01 — ADR, model and parser on Packs

Type: task
Status: in-progress

The tooling tree becomes Roles, Tools and Stages in Packs (`../spec.md`, D1–D24). This ticket brings the
meaning: after it, runs compute from JSON Packs, not from the tree docs' edge tables.

**What to build**

- An ADR for the model. It supersedes the parts of ADR-0007, 0008, 0016, 0017, 0040 and 0054 the spec
  names, says why the series is cut by meaning and not format first (D20), gives `test-runner-if-missing`
  a section (D24), and names every output difference the equivalence script shows.
- `references/tooling-model.md`: Role, Tool, Stage, Pack, Ratchet; `Requires` (Stage, Role, `a | b`) and
  `After` (blocks until decided); rejection levels and their cascade; "Safety Net fulfilled" as a computed
  state; Stage-level *Applies when*; recommended or recognized; the runtime in the seed and its best-effort
  comparison; working it out without `python3`; `git` and `onboarding-setup` as prerequisites.
- `pack.schema.json`, `roles.schema.json`; `roles.json`; `packs/generic/pack.json` and
  `packs/php/pack.json` with every node of today as a Stage, slugs and Names unchanged.
- `tooling_tree.py` rewritten to read the Packs: seed with fulfilled, rejected (with blockers), the Packs
  that apply and the runtime; output per Track as today, plus closed-by-rejection on all three levels;
  no aggregation nodes, no recognition-only nodes, no target files read. Tests ported to the new data.
- The references switched in the same ticket: `tooling-tree-parser.md` becomes `tooling-parser.md`;
  `worklist.md` (trace per Stage, D4), `selection.md`, `track-scan.md` (judge *Applies when*, unknown
  Stages only), `track-choice.md`, `rejection.md` (Role / Tool / Stage), `reconcile.md`,
  `implement-point.md`, `housekeeping-track.md`.

**Pin**

An equivalence script outside the tree: the old parser at the base commit and the new one get the same
seeds from the fixtures. Where D3, D4 and D9 leave the meaning alone the outputs match; every other
difference is listed in the ADR.

**Done when**

- `python3 -m unittest discover -s scripts -p 'test_*.py'` and `python3 scripts/validate_skills.py .` are
  green; the equivalence script's differences are all named in the ADR.
- No reference outside the tree docs points at `tooling-tree.md`, `php-tooling-tree.md` or
  `tooling-tree-parser.md` for graph logic.

**Cut**

Too big for one merge request; its plan cuts it into parts by `principles.md`, *A merge request a person
can review* — for instance data, schemas and parser first, then the references and the ADR's acceptance.

**Left to the plan:** how the eleven files of the spec's *Facts* point at the new references; the Roles'
names (D12).

## Comments

### 2026-10-18 — plan, decisions D25–D33 in the spec

Cut into two parts (D25). Part 1 (branch `tooling-packs-model-data-parser`): ADR, `tooling-model.md`, schemas,
`roles.json`, `packs/generic` and `packs/php`, `tooling_packs.py` with tests, proved by an equivalence run
(1,864 comparisons, differences listed in the ADR). Part 2: the references switch and the old goes.
