`refactor-learn` now requires a genuine event (a finding, a freshly opened merge request, or a
design-time breaking-change finding) before it writes anything — a call with nothing to react to
stops immediately instead of opening a bookkeeping merge request that only refreshed the `Fulfilled
nodes` cache. `refactor-design` now reads existing issue comments, not just the body, everywhere it
grounds itself in a candidate, and posts a **Decision trail** comment recording any grilling question
that met the ADR bar, separate from the (still unchanged) decision gate. A tooling-tree candidate's
"what this unlocks next" note moves off the merge request description and onto the candidate's own
issue. `Secret history scan: done` now carries the date it ran.
