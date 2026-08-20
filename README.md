# Continuous Refactoring

A portable agent-skill suite that keeps a software project under **continuous refactoring** — as a stateful, repeatable loop instead of a one-shot action.

```
scan → prioritise → design (grill) → implement (tdd) → review (2 axes)
   └────────────────────────────── learn (ADR / CONTEXT.md / issue status) ←──────┘
```

The core is language-neutral; the first specialization is a **general PHP project** (code style, Rector, PHPStan as the baseline).

## Skills

| Skill | Purpose |
|---|---|
| `continuous-refactoring` | Orchestrator — runs a loop pass (cadence or on-demand) |
| `refactor-baseline` | Establish the tooling floor once (PHP: php-cs-fixer, Rector, PHPStan, CI enforcement) |
| `refactor-scan` | Find candidates, file them as `refactor:candidate` issues |
| `refactor-prioritize` | Rank the backlog, recommend the next candidate |
| `refactor-design` | Grill a candidate → plan (module, seam, interface, surviving tests) |
| `refactor-implement` | Execute the plan test-first, in slices |
| `refactor-review` | Verify — two-axis review (standards / spec) |

## Installing in a target project

The suite makes no assumptions about the target repo beyond the issue-tracker convention. Install via symlink:

```bash
ln -s /path/to/continuous-refactoring/skills/* <target>/.agents/skills/
```

Or copy. To make the suite globally available (e.g. in `~/.config/opencode/skills/`), a symlink on the `skills/` directories there is enough.

The target project needs the engineering-skills baseline (`setup-matt-pocock-skills`: issue-tracker config, triage labels, domain docs). If it's missing, the orchestrator points that out.

## Quick start

1. **Establish the baseline:** `/refactor-baseline` — tooling floor incl. CI, once.
2. **Start the loop:** `/continuous-refactoring` — the orchestrator creates `docs/agents/refactoring.md` (cadence, default weekly) and runs the first pass.

## Loop state

- **Config + last run:** `docs/agents/refactoring.md` in the target repo
- **Backlog:** `refactor:*` issues on the issue tracker
- **Learned rejections:** `.out-of-scope/`
- **Domain language:** `CONTEXT.md` · decisions: `docs/adr/`

See [Playbooks](docs/playbooks/loop.md) for steering the loop as a human and [docs/playbooks/refactoring-config.md](docs/playbooks/refactoring-config.md) for the config file.