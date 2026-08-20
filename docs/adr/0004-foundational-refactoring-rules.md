# Foundational refactoring rules

The loop's ground rules, binding in `refactor-design` and `refactor-implement` — every plan and every slice follows them:

- **No breaking changes.** A refactor preserves observable behavior; behavior change is not a refactor — it routes to the normal feature/bug path. The loop never ships a breaking change under the refactor label.
- **Strangler Fig for wide migrations.** Large/legacy migrations replace the old piece by piece, keeping old and new working side by side until the swap is complete — never a big-bang rewrite.
- **Kent Beck's technique vocabulary.** The small, behavior-preserving transformations (extract method/class, move method, rename, introduce parameter object, replace conditional with polymorphism, …) are the standard moves; a plan decomposes into them.
- **Deterministic tools over agents.** Where a deterministic tool can do the move, the tool does it — an agent never hand-applies what a tool could do. Code-style fixes go through the existing formatter with the repo's ruleset (php-cs-fixer, …), never by hand; violations a tool reports (Rector, PHPStan, …) are fixed by that tool, not manually rewritten by the agent.
- **Own refactor branch.** Every refactor works on its own branch, never on the default branch — unless the human or the plan explicitly says otherwise.

Written down so every pass and every MR shares one definition of a refactor (behavior-preserving), one migration strategy (Strangler Fig), one move vocabulary (Kent Beck), one division of labor with tools (deterministic tools over agents), and one delivery discipline (own branch). The rules live here so the skills reference them once instead of each restating them — the loop never relitigates what a refactor is per candidate.