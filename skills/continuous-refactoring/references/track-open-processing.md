# Track Open processing

How the orchestrator (`skills/continuous-refactoring/SKILL.md` step 1) walks a selected Track's
`Open` list (Safety Net or Guardrails) when the Track has existing entries. Replaces the earlier
"resume the top entry" behavior for Track nodes — `Pending candidates` still resumes the same way
as before, tracked separately.

## Workability

A node in `Open` is **workable** when all three hold:

1. **Unblocked per the graph** — every required parent is fulfilled (or rejected, which releases the
   child via `CONTEXT.md`'s **Required edge** semantics), and every recommended parent is decided
   (fulfilled or rejected). A node blocked by an unfulfilled required parent is not workable.
2. **Not flagged `needs-info`** — the node's own candidate issue (if already filed) does not carry
   the `needs-info` label (`docs/agents/triage-labels.md`). A flagged decision still carries the
   issue forward, but the pass holds it back until a human confirms or overrides.
3. **Not held back by the PHP floor** — the node is not `php-minimal-version` or another node whose
   own fulfilment depends on the codebase's declared PHP floor being correct, when that floor has
   not yet been verified. Concretely: if `rector-php-set` has fully applied a PHP-version rule set
   but `php-minimal-version`'s floor correction has not yet landed, `php-minimal-version` is not
   workable until the floor is verified.

## Walk algorithm

When a Track (Safety Net or Guardrails) is selected and its `Open` is non-empty:

1. Start at the top of `Open` (the first entry).
2. Check workability (above).
3. If not workable → collect the node with its reason (blocked by: `<parent>`, `needs-info`, or
   `PHP floor unverified`) for the pass report. Move to the next entry.
4. If workable → re-run that one node's Fulfilment check (`skills/refactor-scan/references/
   safety-net-track.md` "Judging fulfilment", `skills/refactor-scan/references/guardrails-track.md`
   "Judging fulfilment"):
   - **Now fulfilled** → remove the node from `Open` (no merge request, no issue created). The
     pass moves on to the next entry — loop back to step 2.
   - **Not fulfilled** → this is the one node worked this pass. Create its issue (if not already
     filed), and continue to `refactor-design` / `refactor-implement` as usual. **Continue walking
     the remaining entries** to collect any non-workable nodes (step 3) for the pass report, but
     do not work a second node — exactly one node is worked per pass.
5. All entries exhausted → the walk is complete. If at least one workable, unfulfilled node was
   found, it has been worked. If none was found, report that the Track has no workable `Open`
   entries this pass (all skipped or fulfilled), and continue to step 6.

## Pass report

Non-workable nodes collected during the walk appear in the closing report's **Status** line with
their reason. Example:

```
Status: Safety Net Track walked — 2 skipped (phpstan-level-6: blocked by phpstan-level-5;
coverage-floor: needs-info), php-cs-fixer worked (MR #12 open). Next: review and merge #12.
```

Nodes found fulfilled during the walk (step 4, "now fulfilled") are removed from `Open` and do not appear in
the pass report — they left silently, same as a hand-adopted node leaving without a merge request.

## Relationship to `refactor-scan` and `refactor-prioritize`

This walk runs inside `refactor-scan`'s Track-specific process (`safety-net-track.md` /
`guardrails-track.md`), not as a separate orchestrator step. `refactor-scan` hands the walk's
outcome (one workable node with its issue, or "nothing workable") to the orchestrator as its
output. `refactor-prioritize` Rank mode is not involved — Track nodes are no longer ranked or
pre-filed; only the single walk's winner reaches `refactor-design`.
