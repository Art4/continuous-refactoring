# Suite skill references (global)

Every reference from a suite skill to a **global** skill, and how its fallback behaves. References between the suite's own two skills are exempt.

There is none: neither `continuous-refactoring` nor `continuous-housekeeping` names a global skill. At the design point and the implement point a run looks at the skills on offer in the conversation and at the target's `AGENTS.md`, recommends what fits, and falls back to the suite's own procedure (`design-point.md`, `implement-point.md`, `reviewing-a-change.md`), which is complete without any other skill.

List it here whenever a suite skill starts naming a global skill: the skill, the reference, its role, and how its fallback behaves.
