# Track Open processing

How `refactor-scan` walks a selected Track's `Open` list (Safety Net or Guardrails) when the Track
has existing entries — dispatched from `refactor-loop`'s scan step
(`../../refactor-loop/SKILL.md` step 1), which hands the selected Track down as input and
routes the walk's outcome onward, but never walks or judges itself: `refactor-loop` is a thin data
pipe, and the walk is scan's own work — `refactor-scan` is the skill that reads the tree and judges
fulfilment. Replaces the earlier "resume the top entry" behavior for Track nodes — `Pending
candidates` still resumes the same way as before, tracked separately.

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
4. If workable → re-run that one node's Fulfilment check (`safety-net-track.md` /
   `guardrails-track.md`, each file's own "Judging fulfilment" section — the same judgement
   discipline that file already documents, never a parser verdict):
   - **Now fulfilled** → report a **fulfilled at pick-up** finding — the node was adopted,
     typically by hand, since the last scan, and the re-check this walk exists to perform caught
     it — and hand it to `refactor-learn`'s early call, which removes the node from `Open`
     (`../../refactor-learn/references/safety-net-write.md` /
     `../../refactor-learn/references/guardrails-write.md`): no merge request, no issue created.
     The pass moves on to the next entry — loop back to step 2. This skill never writes: the
     removal is `refactor-learn`'s write, the same detect-never-write split every other finding
     already follows.
   - **Not fulfilled** → this is the one node worked this pass. Hand it forward to `refactor-design` /
     `refactor-implement` as usual, **marked self-tracking** — `refactor-design/SKILL.md` step 5
     already skips `Pending candidates` for a candidate marked this way, without needing to know why;
     this `Open` entry is this node's own resume marker instead, so the two must never both point at
     the same candidate. The walk creates no issue itself (`refactor-scan` detects, never
     writes): unless the node already has one, it returns a draft for it — title `Tooling tree: <Name>`, label
     `refactor:candidate`, body = the node's Purpose line — and `refactor-loop` creates it before design runs
     (`../../continuous-refactoring/references/filing-a-ticket.md`); `refactor-design` then writes the full plan onto it.
     This pass's pick, and the issue it ends up with, is this walk's own `## Output`
     (below), which is what authorizes `refactor-learn`'s closing call to write that issue's number
     onto this `Open` entry (`safety-net-write.md`/`guardrails-write.md`), whether or not
     `refactor-implement` also got as far as opening a merge request this same pass. **Continue walking
     the remaining entries** to collect any non-workable nodes (step 3) for the pass report, but
     do not work a second node — exactly one node is worked per pass.
5. All entries exhausted → the walk is complete. If at least one workable, unfulfilled node was
   found, it has been worked. If none was found, report that the Track has no workable `Open`
   entries this pass (all skipped or fulfilled) — `refactor-loop`'s own step routing (its
   `SKILL.md` steps 2 and 6) carries the outcome from there.

## Pass report

Non-workable nodes collected during the walk appear in the closing report's `Status` line with
their reason. Example:

```
Status: Safety Net Track walked — 2 skipped (phpstan-level-6: blocked by phpstan-level-5;
coverage-floor: needs-info), php-cs-fixer worked (MR #12 open). Next: review and merge #12.
```

Nodes found fulfilled during the walk (step 4, "now fulfilled") don't appear in the pass report —
nothing was skipped or worked for them. Their leaving `Open` is `refactor-learn`'s early call's own
write, performed on the finding above; the walk's only trace of them is the finding itself.

## Relationship to `refactor-loop`, `refactor-learn`, and `refactor-prioritize`

The walk is `refactor-scan`'s own — part of its Track-specific process (`safety-net-track.md` /
`guardrails-track.md`, each file's non-empty-`Open` section routes here), never a `refactor-loop`
step. `refactor-scan` hands the walk's outcome to `refactor-loop` as its own `## Output`: the one
workable node it selected (its issue, if one already exists), any fulfilled-at-pick-up findings (for `refactor-learn`'s
early call), or "nothing workable". `refactor-learn` performs every write those findings imply —
the `Open` removals above. `refactor-prioritize` Rank mode is not involved — Track nodes are no
longer ranked or pre-filed; only the single walk's winner reaches `refactor-design`.

`refactor-loop` carries this same `## Output` — which node this pass's walk picked — forward past
`refactor-design`/`refactor-implement` to `refactor-learn`'s closing call, the way it already carries
a freshly opened MR or a design-time breaking-change finding: this is that call's own precondition
(`../../refactor-learn/SKILL.md`), authorizing it to write the picked node's now-known issue number
onto its `Open` entry (`safety-net-write.md`/`guardrails-write.md`) even on a pass where
`refactor-implement` never got as far as opening a merge request.
