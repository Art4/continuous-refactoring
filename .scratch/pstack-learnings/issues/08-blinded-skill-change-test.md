# 08 — Test skill-text changes blinded before promoting them

Type: task
Status: done

Research only, scratch-only: a method for comparing skill-text variants blinded (see the skill-text-experiments memory). Do not edit real SKILL.md or ADR files from the experiment itself.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments

### 2026-10-16 — gap check against `skills/`: n/a

Nothing in `skills/`; stays scratch-only research per the memory note.

### 2026-10-17 — closed, replaced by real runs

The blinded test was not built. Instead, the changed skill texts were tried in real runs on a target: planning runs on comparable tickets before and after a text change, compared against criteria fixed beforehand (number of merge requests, size estimate, stated reason for a cut, questions asked, behaviour of the new rules). Those runs were not blind — the observer knew what was tested — and one run per variant cannot rule out chance. They were enough to keep the change. A blinded comparison stays possible as scratch-only research if a text change ever needs stronger evidence; nothing in `skills/` changes for it.
