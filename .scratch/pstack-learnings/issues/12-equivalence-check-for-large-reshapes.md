# 12 — Equivalence check for large reshapes

Type: task
Status: open

Split out of ticket 01. pstack asks, for larger reshapes, for a script that runs old and new code on the
real artifact and diffs the outputs (back-to-back / differential testing), on top of the pin. Decide what
"large" means (files touched? seams crossed? a plan flag?), where the plan names the check, and how the
merge request reports it. Builds on the `Pin` item of the plan.

See `../spec.md`.

## Comments
