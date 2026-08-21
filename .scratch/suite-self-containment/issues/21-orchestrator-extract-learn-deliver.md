# 21 — Orchestrator: extract refactor-learn and refactor-deliver

**Type:** build

**What to build:** Decompose the 81-line orchestrator (`skills/continuous-refactoring/SKILL.md`) into a pure scheduler by extracting two self-contained lifecycle skills:

- **`refactor-learn`** — the learn step's side effects: record ADRs for decisions a future scan must not re-litigate, update `CONTEXT.md` with crystallised terms, close the candidate issue, stamp the last-run date in config. Crash-safe fallback: the side effects are already inline and run regardless of whether `/domain-modeling` is installed.
- **`refactor-deliver`** — the MR-opening protocol: read `AGENTS.md`/`CLAUDE.md` for create-mode, propose `autonomous` if neither says, remember the mode, open the merge request with plain description (candidate link, what changed, surviving tests, CI), manage stacking rules (tooling-tree child or design dependency → stack; else parallel), cap at two open suite merge requests. Self-contained: no global skill for the forge.

After extraction, the orchestrator reads as ~35 lines of pure delegation: step N = run skill X, step N+1 = run skill Y. Each extracted skill has its own `## Fallback`, `## Completion criterion`, and frontmatter.

**Blocked by:** 12 — Deliver each candidate as a remembered merge request (ADR-0006 must land first; the deliver logic lives there currently).

**Status:** ready-for-agent

- [ ] `skills/refactor-learn/SKILL.md` written with frontmatter, process, fallback, completion criterion
- [ ] `skills/refactor-deliver/SKILL.md` written with frontmatter, process, fallback, completion criterion
- [ ] Orchestrator rewritten as pure scheduler (~35 lines)
- [ ] Both new skills reference ADR-0004 foundational rules where applicable
- [ ] `docs/agents/skill-references.md` updated (no new global refs — both are suite-internal)
- [ ] Tier 1 validator passes clean on all skills
- [ ] `refactor-learn` can be invoked standalone (e.g. "learn from this decision" without full loop)

## Comments

> **2026-08-21:** Created from architecture review candidate 1 (Worth exploring). The orchestrator is the most-edited file in the repo (6 touches in 30 commits). Extracting learn + deliver reduces coupling and makes each step independently testable. Blocked by 12 because ADR-0006's MR-opening protocol must stabilize before extraction.

> **2026-08-21:** Ticket hygiene — #12 is done (commit `2c4bb31`). This ticket is now unblocked.
