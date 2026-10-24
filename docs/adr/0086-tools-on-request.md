# Tools on request

> Amended by [ADR-0089](0089-secret-detection-on-request.md): Secret Detection is on request too.

> Amends [ADR-0079](0079-tooling-model-roles-tools-stages-in-packs.md): a Tool has a third status, and `after` is
> renamed `waits_for`. Amends [ADR-0082](0082-psalm-taint-analysis-is-a-guardrails-stage.md): Semgrep no longer
> covers the Security Signal unasked.

> Supersedes in part [ADR-0005](0005-tooling-tree-not-baseline-skill.md).

> Amends [ADR-0019](0019-static-analyzer-mutual-exclusion-and-taint-analysis-node.md), [ADR-0045](0045-semgrep-owasp-top-ten-node.md), [ADR-0074](0074-state-lives-in-the-tracker-found-by-search.md) and [ADR-0084](0084-phpstan-levels-wait-for-rector-and-the-phpunit-set-is-guardrails.md).

Every recommended Tool is proposed to every target its Pack applies to. For some that is noise. Semgrep was close to
useless on young projects that already had their guardrails: it finds little in code written under them, and pays off
in old code that grew without them. Mutation testing is expensive and worth it only once a good test suite exists.
Neither belongs in every target's Guardrails backlog, yet both should be available when a human wants them.

## Decision

**A Tool may be *on request*.** Beside *recommended* (proposed when its Role is empty) and *recognized* (counted when
present, never proposed), an *on-request* Tool is counted when present and proposed only when a human asks for it.

- Its Stages keep their Track, `requires` and `waits_for`. A Stage without a ticket and without a rejection is not
  *unknown*: it makes no scan due and does not count towards its Track having something. Once one of its Stages has a
  ticket, the Stage is an ordinary backlog Stage.
- A human asks in three ways: by naming the Tool or a Stage in the call (the run scans that Tool alone and offers its
  Stages like any proposal); by asking for a scan *including on-request Tools*; and every scan report ends with one line
  naming the on-request Tools available, without filing anything.
- **Semgrep and Psalm Taint Analysis are on request.** Infection, when it is added, is on request too.

**Composer Audit leaves the tooling tree.** Its value is in repetition: a CI gate fails only on advisories known at the
time of a change and never on one published later against an unchanged lockfile, and Composer audits on `update` by
itself. The first Housekeeping template gets a standard task instead, worded for any package manager: audit the
dependencies with the package manager's own audit and attempt a fix for every advisory with a patched version. The
Stage `composer-audit` and the Role Dependency Audit go. On a target that has it, a CI job stays untouched; an open
`composer-audit` ticket is closed with a note that Housekeeping takes it over.

**`after` is renamed `waits_for`.** "B waits for A" reads as what it does: B is held until A is decided, and a rejection
of A releases it. `recommends` was weighed and rejected: it collides with the status *recommended*, and ADR-0016
showed that a "recommended" edge is read as advice that blocks nothing.

## Considered Options

- **A Track for extras.** A Track is a phase of work (ADR-0079); an on-request Tool still has one — Infection comes after
  the Safety Net, Semgrep waits for CI. A Track for "extras" would be neither phase nor topic, and its Stages would need
  `requires` across Tracks. Rejected; the status answers *whether* a Stage is proposed, the Track *when*.
- **An *Applies when* on Semgrep for older code.** Judged anew on every run from fuzzy evidence ("code grown without
  guardrails"); the proposal would come and go. Rejected.
- **Composer Audit on request.** Keeps a Stage whose Fulfilment check (a CI job is present) says little about what it
  is for. Rejected for the Housekeeping task.
- **Secret Detection on request too.** Not decided here: Housekeeping's scan over the Git history reads the scanner this
  Stage sets up, so moving it touches Housekeeping. Left open.

## Consequences

- Targets that never asked get no Semgrep or taint analysis ticket. The Security Signal is then read by the generic
  method (`signals.md`) unless a Security tool is present.
- Tickets and rejections already on record for Semgrep or Psalm Taint Analysis keep counting: a filed ticket is worked,
  a rejection stays.
- The parser learns the status; the pack schema, the generated pages, the scan, the Housekeeping setup and the docs
  that list Guardrails tools change with it.
