# Grilling and domain-modeling fallback — inline mechanics

Backs `refactor-design`'s `## Fallback` section, for step 4 (grill toward the
seam) when the global skills it names aren't installed.

## `/grilling` loop, inline

Map the design as a **design tree** — every decision branches into the
decisions that hang off it — and work it in **rounds**. The **frontier** is
every decision whose prerequisites are already settled. Ask the whole
frontier in one round, numbering each question (`❓ **Q1** - **<title>**:
<body>`, multiple choices allowed) with your recommended answer (`➡️
<recommendation>`), then wait for the user. Their answers reshape the tree
and push the frontier outward — a question depending on one still open in
this round belongs to a later round. Facts are your job (dispatch a
sub-agent rather than asking the user), decisions are the user's. Done when
the frontier is empty: every branch visited, nothing silently assumed.

In this step the tree hangs off the five branches in step 4 of `## Process` —
the deepened module, the seam, the interface, locality, and the tests that
survive.

## `/domain-modeling` discipline, inline

Skip with a note if unavailable — the side effects this step performs are
already inline in step 4 of `## Process` and run regardless: add resolved
terms to `CONTEXT.md` (a glossary and nothing else — no implementation
details) as they crystallise, and offer an ADR under `docs/adr/` when the
user rejects a design with a load-bearing reason a future scan should not
re-suggest. The discipline's enrichment moves (challenging fuzzy terms,
probing edge-case scenarios, cross-referencing the code) are not part of
this step.
