# 02 — Backfill the field record

Type: task
Status: open
Blocked by: 01

**What to build** (spec S1.3; Q3, Q15, Q17, Q19)

- Rows for what the suite already did in the field since 0.5.0, drafted from the traces on the maintainer's targets
  (merge requests, tickets, comments), outside the repository first. The maintainer reviews every row before a PR.
- Paths the maintainer confirms from an external tracker (ticket filing, Plan comments, closing a fulfilled ticket,
  the tracker file's Refactoring operations) are marked as confirmed by the maintainer.
- What the traces do not show and nobody can confirm stays out as *not evidenced*; list those paths and scenario ids
  under the table as candidates for scenarios.
- Traces from before 0.5.0 stay out.
- Every environment described neutrally; no name, no number.

**Done when** the maintainer has reviewed the rows, they are in `docs/agents/field-results.md`, and tests and
validator are green.
