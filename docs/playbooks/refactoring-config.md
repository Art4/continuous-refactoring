# Playbook: `docs/refactoring/config.md` in the target repo

The config file the orchestrator reads and writes. It's created lazily on the first pass (the orchestrator asks for the cadence; default: weekly).

## Structure

```markdown
# Refactoring Loop Config

**Cadence:** weekly
**Last run:** 2026-08-21
**Create-mode:** autonomous
**Focus areas:** order intake, billing
```

## Fields

| Field | Meaning | Written by |
|---|---|---|
| `Cadence` | Turnus for periodic passes (`weekly`, `biweekly`, `monthly`, …) | Orchestrator on first pass; you can edit |
| `Last run` | Date of the last completed pass | Orchestrator after each pass |
| `Create-mode` | How the orchestrator opens merge requests: `autonomous`, `ask-each-time`, or `human-opens` | Orchestrator (first learn step) |
| `Focus areas` | Areas scans should target first | you, any time |

## Rules

- **Only the orchestrator writes it.** You edit by hand when you change cadence, focus areas, or create-mode — that's what it's for.
- The file travels with the repo. Loop state does not live in agent sessions but here (config, last-run), in the issue tracker (backlog), in `docs/refactoring/merge-requests.md` (open suite merge requests), and in `docs/refactoring/out-of-scope/` (learned rejections).
- If the file is missing, the orchestrator scaffolds the `docs/refactoring/` directory — that's the marker from which a pass can run.
