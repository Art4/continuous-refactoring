`refactor-learn` now requires a genuine event (a finding, a freshly opened merge request, or a
design-time breaking-change finding) before it writes anything — a call with nothing to react to
stops immediately instead of opening a bookkeeping merge request that only refreshed the `Fulfilled
nodes` cache. `refactor-design` now reads existing issue comments, not just the body, everywhere it
grounds itself in a candidate, and posts a **Decision trail** comment recording any grilling question
that met the ADR bar, separate from the (still unchanged) decision gate. A tooling-tree candidate's
"what this unlocks next" note moves off the merge request description and onto the candidate's own
issue. `Secret history scan: done` now carries the date it ran.

Also fixed: `refactor-learn`'s new precondition checks only what a call was actually handed, instead
of independently investigating (reading open merge requests, re-analyzing `bookkeeping.md`) to see
whether a reason to act might exist. And `refactor-scan` now resolves `tooling_tree.py` relative to
wherever the suite's skills are actually installed, rather than assuming the suite's own repo is the
current working directory — running the suite from a target repo via a symlinked or copied install no
longer needs a sub-agent dispatch just to locate it, noticeably speeding up every pass.
