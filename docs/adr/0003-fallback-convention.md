# External skill references carry a fallback

Every suite skill that references a **global** skill (`/grilling`, `/tdd`, `/code-review`, `/codebase-design`, `/domain-modeling`) carries a `## Fallback` section. Suite-internal references are exempt — those skills ship together. The `/X` reference stays and means "use X if installed, else the inline fallback".

Two fallback depths, chosen by the skill's role:
- **Self-sufficient** (core procedure — the loop step cannot run without it): the fallback inlines the *contract* — the subset of the referenced skill that this step actually uses.
- **Crash-safe** (enrichment — the step's core is already inline): the fallback says *skip with a note* when the global skill is missing.

Fallbacks are written inline in the skill file itself (no shared suite file — each skill must work standalone). Before invoking `/X`, check it is available in the environment; if not, follow the fallback. The complete reference inventory lives in `docs/agents/skill-references.md`.

Chosen so the suite keeps working in a target repo with none of the global skills installed, while still preferring the richer global skills when present. A shared fallback file would recreate the dependency problem it solves; reproducing the whole global skill would bloat every skill with unused surface.