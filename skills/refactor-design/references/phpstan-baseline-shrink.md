# Planning a PHPStan baseline-shrink fix

`refactor-design` step 1's own case for a **PHPStan baseline-shrink candidate** —
`refactor-prioritize` already selected the group and filed it minimally, via its own Select mode
(`skills/refactor-prioritize/references/baseline-shrink-selection.md`, that file's own steps 1–2 —
resuming/reading/grouping no longer lives here). Run this before step 5.

## 3. Plan the fix

Read every file the chosen group touches (named on the issue `refactor-prioritize` filed). Design a
fix that removes the finding without changing behavior — same "provably behavior-preserving" bar any
other mechanical fix on this tree holds to. Reducing the group is enough; it doesn't have to empty in
one MR (`phpstan.neon`'s own "strictly reduce" wording already allows this for a level-bump MR — the
same principle applies here, one level earlier in the chain). Note in the plan which files this
pass's MR will actually touch if the group is large enough that not all of it fits comfortably in one
bounded MR.

Continue at `refactor-design/SKILL.md` step 5: the plan above goes on as a **comment** on the issue
`refactor-prioritize` already filed — not a fresh issue (dedupe doesn't apply here, `refactor-prioritize`
already handled it).
