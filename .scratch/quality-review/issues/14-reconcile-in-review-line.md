# 14 — Is reconcile's "In review" line a finding?

Type: task
Status: open
Blocked by: —

**What the plays showed** (d11, then r7 and r8 on 2026-11-11; named three times, so a ticket under Q54).
`reconcile.md` step 1 *In review* names the tickets whose merge request is still open "in one line, with their
merge requests; nothing follows for them". Step 2 says "No finding → say so in one sentence and go on; this is no
decision point", otherwise one decision point for all findings. It is not said whether the "In review" line is a
finding. Read as one, a reconcile with only tickets in review becomes a decision point with nothing to decide, and
an autonomous run reports a recommendation that does nothing. Every player so far took it as no finding and named
the tickets in the sentence of step 2.

**To decide**

- Whether the "In review" line is information only, said in step 2's sentence and never a finding; and whether the
  two cases that do lead somewhere (a review that asks for changes, a base update) are findings or remain notes for
  Track choice.

**Done when** `reconcile.md` says it in its own text, the scenarios that cover reconcile pass, and tests and
validator are green.

## Comments

**2026-11-12 — Decided** (Q62). The "In review" line, a review asking for changes and a base update included, is
information, never a finding; step 2's sentence for no finding names it.
