# r1 — A plan met an Opener

Played as a walk-through, once per variant.

Covers: `skills/continuous-refactoring-run/references/worklist.md`, `skills/continuous-refactoring-run/references/track-scan.md`, `skills/continuous-refactoring-run/references/filing-a-ticket.md`, `skills/continuous-refactoring-run/references/tooling-model.md`

## Situation

An onboarded PHP project; its Safety Net is fulfilled, and no tooling ticket is open. The generic Pack has a Tool on
request, *Example Policy* (`example-policy`), one Safety Net Stage, whose file names this Opener: "a plan that takes
the careful way only because the project's policy is not written down". It is not in place, has no ticket and no
rejection.

The last run worked Investigation ticket #14. Its `Plan` comment lists under `Decisions`:
`Opener: example-policy — kept the old method beside the new one, because no policy says whether code outside the
repository calls it.` Its merge request !15 carries the same line and was merged. Ticket #14 is closed.

**Variant A.** The target is on GitHub; the tracker file is the GitHub default.

**Variant B.** The target's tickets live on GitLab, under the GitLab default, but its tracker file names **Merge
requests** `none`: #14's change went in by hand, and no merge request exists.

## Call

`/continuous-refactoring-run autonomous`

## Expected

- [ ] Variant A: the worklist finds the Opener through **Search**. Variant B: it reads the comments of the open
      tickets and of the ten closed last, and finds the line in #14's `Plan`.
- [ ] The worklist holds the Safety Net's trace as not complete: its scan is due.
- [ ] The scan judges `example-policy` and proposes it as a question, "Set up Example Policy?", with the Opener's
      line and a link to #14's plan. It does not put the Stage into `requested`.
- [ ] Filing creates one ticket and posts the question on it as an open question; the recommendation does not
      answer it, although the run is autonomous.
- [ ] The new ticket is waiting. The run neither plans nor implements it, and opens no merge request for it.
- [ ] The Safety Net still counts as fulfilled: the parser's seed has no `requested` for `example-policy`.

## Results

2026-11-02, skill commit 43b505b: pass, every line, as a walk-through. The play named one gap, closed in that commit:
the ticket's text carries the Opener's line and the link to its `Plan` comment.

2026-11-06, on a3c2d7a with the worklist's judging step (safety-net-gate, ticket 02): pass, every line, as a walk-through.

2026-11-07, on 0e29b63, the first playing of every scenario with the runner and a separate judge: fails "The worklist finds the Opener through **Search**": taking the tracker's search to miss comments, the player found the Opener through the merge request search instead; the scan was due, and the other lines hold, as a walk-through.

2026-11-08, on c8d3e1e with the reading of recent comments where the tracker's search misses them: pass, every line, both variants, as a walk-through, by one player.
