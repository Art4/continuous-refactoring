# Playbook: `docs/agents/refactoring.md` in the target repo

The config file the orchestrator reads and writes. It's created lazily on the first pass (the orchestrator asks for the cadence; default: weekly).

## Structure

```markdown
# Refactoring Loop Config

**Cadence:** weekly
**Last run:** 2026-08-20
**Baseline:** done            <!-- or: pending -->
**Focus areas:** order intake, billing
```

## Fields

| Field | Meaning | Written by |
|---|---|---|
| `Cadence` | Turnus for periodic passes (`weekly`, `biweekly`, `monthly`, …) | Orchestrator on first pass; you can edit |
| `Last run` | Date of the last completed pass | Orchestrator after each pass |
| `Baseline` | `pending` / `done` — the tooling floor is in place | `refactor-baseline` on completion |
| `Focus areas` | Areas scans should target first | you, any time |

## Rules

- **Only the orchestrator and the baseline skill write it.** You edit by hand when you change cadence or focus — that's what it's for.
- The file travels with the repo. Loop state does not live in agent sessions but here (config, last-run), in the issue tracker (backlog), and in `.out-of-scope/` (learned rejections).
- If the file is missing, the orchestrator creates it — that's the marker from which a pass can run.