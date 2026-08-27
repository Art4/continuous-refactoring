# Suite skill references (global)

Every reference from a suite skill to a **global** skill, and how its fallback behaves. Suite-internal references are exempt. Convention: `docs/adr/0003-external-skill-references-carry-a-fallback.md`.

| Skill | Global ref | Role | Fallback type | Self-contained in |
|---|---|---|---|---|
| `refactor-design` | `/codebase-design` | enrichment (vocab already inline) | crash-safe | 10 (ADR-0010) |
| `refactor-design` | `/grilling` (Z.8,18) | core (design loop) | self-sufficient | 02 ✓ shipped |
| `refactor-design` | `/domain-modeling` (Z.8,26) | enrichment (side effects) | crash-safe | 02 ✓ shipped |
| `refactor-implement` | `/tdd` | core (red→green rules) | self-sufficient | 03 ✓ shipped |
| `refactor-implement` | `mattpocock/skills` implement skill (`setup-matt-pocock-skills`) | core (review, embedded) | self-sufficient | 10 (ADR-0010) |
| `refactor-learn` | `/domain-modeling` | enrichment (ADR/CONTEXT.md side effects) | crash-safe | 10 (ADR-0010) |

Exempt (no global refs): `refactor-prioritize`, `refactor-scan` (moved its `/codebase-design` reference to `refactor-design`, ADR-0010 — the codebase walk for `structural-scan` candidates lives there now).

`refactor-review` retired as a standalone skill (ADR-0010); its two-axis logic and `/code-review` reference are now `refactor-implement`'s, folded in alongside `/tdd`. `continuous-refactoring`'s own `/domain-modeling` reference moved to `refactor-learn`, which now owns the learn step.

Keep this table in sync whenever a suite skill adds or drops a global reference — it is the audit ledger for the ADR-0003 convention.