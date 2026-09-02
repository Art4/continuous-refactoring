# Foundational refactoring rules

Binding in `refactor-design` (the plan) and `refactor-implement` (every slice) — one shared definition instead of each skill restating it.

- **No breaking changes.** A refactor preserves observable behavior; a behavior change routes to the normal feature/bug path instead, never shipped under the refactor label.
- **Strangler Fig for wide migrations.** Large/legacy migrations replace the old piece by piece, old and new working side by side until the swap is complete — never a big-bang rewrite.
- **Kent Beck's technique vocabulary.** The small, behavior-preserving transformations (extract method/class, move method, rename, introduce parameter object, replace conditional with polymorphism, …) are the standard moves; a plan decomposes into them.
- **Deterministic tools over agents.** Where a deterministic tool can do the move, the tool does it — never hand-applied. A violation a tool both reports and fixes (Rector, php-cs-fixer, …) is fixed by that tool; a violation a tool can only report (PHPStan, …) is fixed by the agent, following the tool's diagnosis.
- **Own refactor branch.** Every refactor works on its own branch, never the default branch, unless the human or the plan explicitly says otherwise.
