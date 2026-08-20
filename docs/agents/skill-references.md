# Suite skill references (global)

Every reference from a suite skill to a **global** skill, and how its fallback behaves. Suite-internal references are exempt. Convention: `docs/adr/0003-external-skill-references-carry-a-fallback.md`.

| Skill | Global ref | Role | Fallback type | Self-contained in |
|---|---|---|---|---|
| `refactor-scan` | `/codebase-design` (Z.31) | enrichment (vocab already inline) | crash-safe | 01 ✓ shipped |
| `refactor-design` | `/grilling` (Z.8,18) | core (design loop) | self-sufficient | 02 ✓ shipped |
| `refactor-design` | `/domain-modeling` (Z.8,26) | enrichment (side effects) | crash-safe | 02 ✓ shipped |
| `refactor-implement` | `/tdd` (Z.10) | core (red→green rules) | self-sufficient | 03 ✓ shipped |
| `refactor-review` | `/code-review` (Z.23) | core (smell baseline) | self-sufficient | 04 (planned) |
| `continuous-refactoring` | `/domain-modeling` (Z.41) | enrichment (learn step) | crash-safe | 05 (planned) |

Exempt (no global refs): `refactor-baseline`, `refactor-prioritize`.

Keep this table in sync whenever a suite skill adds or drops a global reference — it is the audit ledger for the ADR-0003 convention.