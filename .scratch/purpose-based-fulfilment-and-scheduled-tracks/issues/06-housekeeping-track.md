# 06: Housekeeping Track — retire the standalone `continuous-housekeeping` skill

**What to build:** `continuous-housekeeping`'s existing process (due-check, reconciliation against
fulfilled nodes, checklist assembly, quality gate, deliver) becomes the Housekeeping Track's own content,
unchanged, triggered by the shared Track scheduler instead of its own standalone due-check. Its
`references/` (cadence interview, template-file-format doc) move under `continuous-refactoring`. Manual
invocation of the Housekeeping Track directly stays possible, generalized to the same
Track-name-as-argument pattern the other three Tracks use.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] The existing housekeeping process runs with unchanged content, triggered by the shared scheduler.
- [ ] `continuous-housekeeping`'s `references/` move under `continuous-refactoring`.
- [ ] `bookkeeping.md` gains a `Housekeeping` section (`Cadence`, `Last scan`); default cadence stays 7
      days (weekly), unchanged from today's default.
- [ ] Manual invocation of the Housekeeping Track directly remains possible.
- [ ] No standalone `continuous-housekeeping` entry point remains as its own top-level skill.
