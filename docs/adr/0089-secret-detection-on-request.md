# Secret Detection on request, the history scan on its own

> Amends [ADR-0086](0086-tools-on-request.md), which left Secret Detection open.

> Amends [ADR-0043](0043-secret-history-scan-as-process-step.md): the history scan no longer needs the target's
> scanner.

> Amends [ADR-0040](0040-signal-tool-nodes-and-tree-edge-simplification.md): `secret-detection` feeds no Signal.

Secret Detection was a recommended Guardrails Stage in the generic Pack, its Role Secret Scanning carried the Signal
Security, and Housekeeping's scan over the Git history ran the scanner the Stage set up. Four things did not fit:

- **The Track.** Guardrails means "after the Safety Net". A secret scanner collides with no structural work; it sat
  there only because every Stage with a Signal did. A cheap protection waited behind PHPStan, Rector and PHP CS Fixer.
- **The Signal.** `signals.md` read the scanner's findings as evidence for the Security signal of a structural
  candidate, while Housekeeping files each finding as an ordinary ticket, "no refactoring". A committed secret is
  fixed by rotating it, not by restructuring code.
- **The history scan waited for the gate.** Secrets already in the history are the larger risk, yet the scan ran only
  once the CI gate existed — after the Safety Net — and was ticked `not run` until then.
- **The gate warns late.** A CI job sees a secret once it is pushed, when it has to be rotated anyway; a forge's push
  protection keeps it out. With the history scan in every Housekeeping cycle, the CI gate reports a leak at most one
  rhythm earlier.

## Decision

**The history scan stands on its own.** Housekeeping runs the scanner the target already uses, with its file of known
findings. A target without one gets a secret scanner the run can execute without adding it to the project — a binary
or a Docker image, gitleaks for instance; nothing is written to the target for it, no baseline either. The range keeps
findings from coming back: after the first full scan, each cycle scans only the commits added since. Where no scanner
can run, the task is ticked `not run: no secret scanner available`, the closing report says what is missing, and the
next cycle tries again.

**Secret Detection is on request.** It stays a Guardrails Stage and now waits for `ci-runner`, as Semgrep does.

**Its Role carries no Signal.** The Security signal is read from code, and from Psalm Taint Analysis and Semgrep where
they are in place.

**Push protection fulfils it.** The Stage is fulfilled by a CI job running a secret scanner, or by the forge's push
protection, where the run can read it through the forge's API. Unreadable counts as absent, and the findings say so. A
pre-commit hook alone does not fulfil it: nobody has to run it.

## Considered Options

- **Safety Net.** Earlier, but a secret scanner collides with no structural work, and the Stage would hold the Safety
  Net until decided. Rejected.
- **Out of the tree, like Composer Audit.** Unlike an audit gate, a secret gate does catch something on each change, and
  a human who wants one should get it set up. Rejected for on request.
- **The suite writes a baseline file into the target.** A write the target did not ask for; the range already keeps
  findings from repeating. Rejected.

## Consequences

- A target without Housekeeping gets no secret scan; Track choice already counts missing Housekeeping as due.
- Tickets and rejections on record for `secret-detection` keep counting (ADR-0086). A CI job already in place is the
  scanner the history scan runs.
- The generic Pack has no Guardrails Stage proposed unasked.
