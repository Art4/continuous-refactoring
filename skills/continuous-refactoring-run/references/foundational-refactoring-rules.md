# Foundational refactoring rules

Binding on every plan and every slice of a run, whoever writes them: the suite or a skill of the target.

- **No breaking changes.** A refactor preserves observable behavior; a behavior change routes to the normal feature/bug path instead, never shipped under the refactor label.
- **Deterministic tools over agents.** Where a deterministic tool can do the move, the tool does it — never hand-applied. A violation a tool both reports and fixes (Rector, php-cs-fixer, …) is fixed by that tool; a violation a tool can only report (PHPStan, …) is fixed by the agent, following the tool's diagnosis.
- **Own refactor branch.** Every refactor works on its own branch, started from the default branch.
- **Pin before structure moves.** A structural ticket's first commit is a Pinning Test: it holds the current behaviour at the seam and passes on the code as it stands, before any commit moves structure. A type check or a linter is no pin. It does not apply to a tooling or baseline ticket, where a tool changes the code and the target's existing suite is what notices.
- **A check is never weakened.** A red check is fixed by changing the code, not the check: no test deleted or bent to fit, no ignore rule, no lowered threshold. This holds for the pin and the reader-load review too. Only the human may allow it; a baseline ignore needs exactly that. A test of code the plan deletes goes with it, and the plan names it among the tests that survive.

What helps judgement without binding — reader load, the Strangler Fig, the technique vocabulary — is in `principles.md`.
