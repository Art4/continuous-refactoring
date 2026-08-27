# Playbook: `docs/refactoring/config.md` in the target repo

The config file the orchestrator reads and the suite writes. It doesn't exist on a fresh target repo: `refactor-scan` notices (the `loop-config` node, `docs/tooling-tree.md`, ADR-0008), files it as a single `refactor:candidate` issue, and `refactor-implement` creates the file when that candidate is implemented — the same path any other tooling-tree node takes.

## Structure

```markdown
# Refactoring Loop Config

**Last run:** 2026-08-21
**Create-mode:** autonomous
**Focus areas:** order intake, billing
```

## Fields

| Field | Meaning | Written by |
|---|---|---|
| `Last run` | Date of the last completed pass | Orchestrator after each pass |
| `Create-mode` | How the orchestrator opens merge requests: `autonomous`, `ask-each-time`, or `human-opens` | Orchestrator (first learn step) |
| `Focus areas` | Areas scans should target first | you, any time |

There is deliberately no `Cadence` field: the loop never triggers itself — "you kick it off whenever it's due" (`docs/playbooks/loop.md`), whether that's you running `/continuous-refactoring` by hand or a scheduler you set up outside the suite. Nothing here would read a stored cadence, so nothing stores one.

## Rules

- **`Last run` is orchestrator-written; `Create-mode` and `Focus areas` you can edit by hand any time** — that's what they're for.
- The file travels with the repo. Loop state does not live in agent sessions but here (last-run, create-mode, focus areas), in the issue tracker (backlog), in `docs/refactoring/merge-requests.md` (open suite merge requests), and in `docs/refactoring/out-of-scope/` (learned rejections).
- If the file is missing, that's the `loop-config` tooling-tree node — see above, not a special case.
