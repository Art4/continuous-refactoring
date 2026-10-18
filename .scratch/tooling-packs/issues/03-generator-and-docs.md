# 03 — Generator, docs and validator checks

Type: task
Status: ready-for-agent
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

## Comments
