# r1 — A plan met an Opener

Played as a walk-through.

## Situation

An onboarded PHP project; its Safety Net is fulfilled, and no tooling ticket is open. The generic Pack has a Tool on
request, *Example Policy* (`example-policy`), one Safety Net Stage, whose file names this Opener: "a plan that takes
the careful way only because the project's policy is not written down". It is not in place, has no ticket and no
rejection.

The last run worked Investigation ticket #14. Its `Plan` comment lists under `Decisions`:
`Opener: example-policy — kept the old method beside the new one, because no policy says whether code outside the
repository calls it.` Its merge request !15 carries the same line and was merged. Ticket #14 is closed.

## Call

`/continuous-refactoring-run autonomous`

## Expected

- [ ] The worklist finds the Opener through **Search** and holds the Safety Net's trace as not complete: its
      scan is due.
- [ ] The scan judges `example-policy` and proposes it as a question, "Set up Example Policy?", with the Opener's
      line and a link to #14's plan. It does not put the Stage into `requested`.
- [ ] Filing creates one ticket and posts the question on it as an open question; the recommendation does not
      answer it, although the run is autonomous.
- [ ] The new ticket is waiting. The run neither plans nor implements it, and opens no merge request for it.
- [ ] The Safety Net still counts as fulfilled: the parser's seed has no `requested` for `example-policy`.

## Results

2026-11-02, skill commit 43b505b: pass, every line, as a walk-through. The play before it named two gaps that were
closed in that commit: the ticket's text carries the Opener's line and the link to its `Plan` comment.
