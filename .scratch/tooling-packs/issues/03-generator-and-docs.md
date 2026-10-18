# 03 — Generator, docs and validator checks

Type: task
Status: done
Blocked by: 01

**What to build**

- The parser, or one script beside it sharing its reader, writes from the Packs and `roles.json`:
  the JSON in its fixed form (D15), and per Pack a Markdown table and a Mermaid diagram under `docs/`
  (D14, D18). Nothing generated ships with the skills.
- `validate_skills.py`: every `pack.json` and `roles.json` matches its schema (`jsonschema` as a
  development-only dependency, installed in CI like `pyyaml`); every Role and Stage named in `Requires`
  and `After` exists; every required parent carries its child's Tracks; one recommended Tool per Role and
  Pack; slugs and Role names unique; the JSON is in its fixed form; the generated docs are current. Each
  check with a unit test.
- `CONTRIBUTING.md`: the one command that regenerates; a changelog fragment.

**Done when** the tests and the validator are green, and changing a Stage in a Pack without regenerating
fails the validator.

## Decisions (grilled 2026-10-18)

- The generator is `scripts/tooling_docs.py`, a development tool that imports `load_model`; the parser
  gets no writing code. One command writes the fixed JSON form and the docs; `--check` writes nothing and
  lists every difference, and the validator runs the same check.
- The fixed form: the file is read and written back canonically (2-space indent, objects one key per line,
  lists of plain values on one line, keys in schema order); `roles.json` is expanded too, one key per line.
- Docs: `docs/tooling/README.md` (Roles with their Tools, the Packs) and `docs/tooling/packs/<pack>.md`
  (Tools, Stages, diagram). The Pack pages live in a subfolder so no Pack can collide with the index.
- Diagram: one per Pack, a subgraph per Track, `requires` solid, `after` dashed, an any-of as a decision
  node ("one of"), a Role as a stadium node fed by the first Stage of its Tools, other Packs' Stages at the
  edge. Node ids carry a prefix per kind (`s_`, `r_`, `x_`, `a_`, `t_`), so equal slugs never meet.
- The validator calls `load_model` and repeats none of its checks; it adds the schemas, the fixed form,
  one recommended Tool per Role and Pack, the existence of each `details` file and the current docs.
  A missing `jsonschema` is an error, not a skip; CI pins it; it is a development dependency only.
- A check that each `details` file has a section per Stage waits for the ticket that moves those files.

## Comments
