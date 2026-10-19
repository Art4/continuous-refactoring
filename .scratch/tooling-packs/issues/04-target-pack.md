# 04 — The target's own Pack

Type: task
Status: done
Blocked by: 01

**What to build**

- A target may keep a Pack of its own in the format of `pack.json`, with `"$schema"` pointing at the
  suite's schema; `## Refactoring operations` names where it lives (`refactoring-operations.md`).
- It may add Tools, Stages and Roles, never redefine or remove the suite's (D21); a collision ends the
  parser with exit code 2, and the run names it.
- The scan and the parser read it beside the suite's Packs; its *Applies when* is judged like theirs.
- An example of a target's Pack, and the onboarding or Housekeeping text that offers it — where the
  example lives is this ticket's decision (D17).
- Docs: `README.md` or a playbook section on adding a tool of one's own; FAQ; a changelog fragment.

**Done when** a fixture target with its own Pack gets its Stages in the parser's output, a fixture whose
Pack reuses a suite slug ends with exit code 2, and tests and validator are green.

## Decisions (grilled 2026-10-19)

- The Pack is found through a new optional operation **Tooling Pack** (a directory; recommended place a
  folder `tooling-pack` beside the tracker file). The onboarding does not ask; its "Left out" line names it.
- The Pack's Roles go in an optional `roles.json` beside `pack.json` (same schema); the Pack format gets no
  Roles field.
- Parser: `--own-pack <dir>`; the Pack is loaded after the suite's; `details` is named relative to the
  directory of each `pack.json` (suite Packs too, as a separate commit).
- Slug, Role and Pack-name collisions end the parser with exit code 2 and name both places.
- `"$schema"` points at the schema in the target's installed skills; the generator stays this repo's tool.
- The example is two fixtures (`php-own-pack`, `php-own-pack-clash`) read by tests, and
  `docs/playbooks/own-tool.md`; no copy in the shipped references.
- Added while grilling: **a Pack names a scope** and a Role is filled per scope, so Tools for different
  languages do not take each other's place (ADR-0080). It also lets a Pack of a project stand beside the
  suite's Tools for the same language.

## Comments
