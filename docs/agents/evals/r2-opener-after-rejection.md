# r2 — An Opener after a rejection

Played as a walk-through.

## Situation

The project of r1, a week later. The human answered the open question on the *Example Policy* ticket with "No, we
do not want one", and the suite recorded a rejection of the Tool `example-policy`; the ticket is closed. Since then,
the plan of Investigation ticket #21 has met the Opener again, and its `Decisions` carry
`Opener: example-policy — kept a deprecated constant, because no policy says whether addons read it.` No tooling
ticket is open.

## Call

`/continuous-refactoring-run autonomous`

## Expected

- [ ] The rejection is found, and it uses the Opener up: no scan is due for it.
- [ ] Nothing is filed for `example-policy`, and no question is posted.

## Results
