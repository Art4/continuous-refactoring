# Continuous Refactoring

A portable agent-skill suite that keeps a software project under **continuous refactoring** — as a stateful, repeatable loop instead of a one-shot action.

```
scan (propose nodes, detect closed MRs) → prioritise → design (grill, file the issue) → implement (tdd + review)
   └────────────────────────────────── learn (ledger / ADR / CONTEXT.md / issue status) ←──────┘
```

The orchestrator carries each skill's output to the next skill's input (ADR-0010) — no skill re-derives its own context from shared state.

The core is language-neutral; the first specialization is a **general PHP project** (code style, Rector, PHPStan via the tooling tree).

## Skills

| Skill | Purpose |
|---|---|
| `continuous-refactoring` | Orchestrator — runs a loop pass (cadence or on-demand), passes each skill's output to the next |
| `refactor-scan` | Propose every currently-unblocked tooling-tree node from `config.md`; detect (never file) closed/merged issues and MRs |
| `refactor-prioritize` | Rank the proposals, recommend the next one |
| `refactor-design` | Grill/search the chosen node → plan, files it as an issue |
| `refactor-implement` | Execute the plan test-first, in slices, review included |
| `refactor-learn` | The suite's only writer — ledger, ADR/CONTEXT.md, issue status |

## Installing in a target project

The suite makes no assumptions about the target repo beyond the issue-tracker convention. Install via symlink:

```bash
ln -s /path/to/continuous-refactoring/skills/* <target>/.agents/skills/
```

Or copy. To make the suite globally available (e.g. in `~/.config/opencode/skills/`), a symlink on the `skills/` directories there is enough.

The target project needs the engineering-skills setup (`setup-matt-pocock-skills`: issue-tracker config, triage labels, domain docs). If it's missing, the orchestrator points that out.

## Quick start

1. **Start the loop:** `/continuous-refactoring` — the orchestrator scaffolds `docs/refactoring/` (cadence, default weekly) and runs the first pass.

## Loop state

- **Config + last run:** `docs/refactoring/config.md` in the target repo
- **Remembered merge requests:** `docs/refactoring/merge-requests.md`
- **Backlog:** `refactor:*` issues on the issue tracker
- **Learned rejections:** `docs/refactoring/out-of-scope/`
- **Domain language:** `CONTEXT.md` · decisions: `docs/adr/`

See [Playbooks](docs/playbooks/loop.md) for steering the loop as a human and [skills/continuous-refactoring/references/refactoring-config.md](skills/continuous-refactoring/references/refactoring-config.md) for the config file.