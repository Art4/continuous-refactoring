# 01 — The tracker file may live elsewhere, named in `AGENTS.md`

Type: task
Status: done

Grilled 2026-10-29; decided in ADR-0091. Until now the suite reads `docs/agents/issue-tracker.md` only; a target
describing its tracker elsewhere cannot say so.

**What to build**

- Parser: `--tracker-file <path>` on `tooling_tree.py`, relative to the target, default `docs/agents/issue-tracker.md`;
  `TRACKER_FILE` becomes that default. Tests in `scripts/test_tooling_tree.py`: another path, a missing file at the
  given path.
- The rule, stated once in `refactoring-operations.md`: `AGENTS.md`'s pointer (prose, as for the domain docs), else
  `CLAUDE.md`'s, else the default. Contradiction between the two → finding at Ready, run goes on. Pointer wins over an
  existing default file. Pointer to a missing file → onboarding writes there. Pointer outside the repository (URL,
  outside path) → the run ends naming it. Paths in the section stay relative to the repository root.
- Skill text uses *the tracker file* and cites the rule: `SKILL.md` (Ready step resolves the path and hands it to the
  parser), `onboarding-setup-interview.md` (Explore, summary, Write), `prerequisites/onboarding-setup.md`,
  `local-issue-tracker-template.md`, `tooling-parser.md` (the flag), `continuous-housekeeping`'s
  `housekeeping-setup.md`.
- Onboarding writes no pointer into `AGENTS.md`.
- Docs: `CONTEXT.md` (term *tracker file*), `README.md`, `docs/architecture.md`, `docs/FAQ.md` (how to put the file
  elsewhere, why a pointer in `AGENTS.md`), `docs/known-limitations.md` (pointer outside the repository ends the run),
  `docs/playbooks/run.md`, `driver.md`, `own-tool.md`; changelog fragment.

**Done when** a target whose `AGENTS.md` names another tracker file gets its section read and written there, a target
without a pointer behaves as before, and tests and validator are green.
