# 03 — Tools on request; Composer Audit to Housekeeping

Type: task
Status: ready-for-agent
Blocked by: 02

**What to build** (ADR-0086)

- **The status.** `pack.schema.json` allows `"on-request"`; `tooling_tree.py`: a Stage of an on-request Tool is ticketable
  only once it has a ticket; without one it is not *unknown* (makes no scan due) and is not in its Track's backlog. It
  fills its Role when present, like any Tool. Tests for each rule. `tooling-model.md`, `tooling-parser.md`.
- **Asking for it.** `track-scan.md`: a call naming an on-request Tool or Stage scans that Tool alone and offers its Stages;
  a scan asked for "including on-request Tools" judges them all; every scan report ends with one line naming the
  on-request Tools available. `docs/playbooks/run.md` (how to ask), `docs/playbooks/tracks.md`.
- **Semgrep and Psalm Taint Analysis** become on request (`packs/php/pack.json`, `semgrep.md`, `psalm.md`; the "Why it is a
  Guardrails Stage" text keeps its point about Track).
- **Composer Audit.** Remove the Tool, its Stage, `composer-audit.md` and the Role `dependency-audit`; fix the mentions in
  `ci-runner.md`, `secret-detection.md`, `semgrep.md`, `packs/php/README.md` (the `require-dev` section names it),
  `track-scan.md`. Add a standard task to the first template in `housekeeping-setup.md`, worded for any package manager:
  audit the dependencies with the package manager's own audit (`composer audit`, `npm audit`, …) and attempt a fix for
  every advisory with a patched version. A target that has the template already gets the task as a *new line*
  (`housekeeping-track.md`, step 4) — check that path covers it or add it. An open `composer-audit` ticket is closed with a
  note that Housekeeping takes it over; an existing CI job is not touched.
- `CONTEXT.md`, **Tool** — after *Recognized*:

  > *On request*: counted when present, proposed only when a human asks for it (Semgrep, Psalm Taint Analysis); its
  > Stages make no scan due and count towards their Track only once one of them has a ticket.

  **Track** — in the scan sentence, after "of its Tool or of its Role": "; a Stage of an *on request* **Tool** never
  counts as not known". **Housekeeping**: add the dependency audit to the list of sweeps.
- Docs: `README.md` (Guardrails row: "dependency audit, … taint analysis"), `docs/playbooks/tracks.md`,
  `docs/architecture.md`, `docs/FAQ.md` (why are Semgrep and taint analysis not proposed?), `docs/playbooks/housekeeping.md`.
  Regenerate `docs/tooling/`.

**Done when** a fixture target with no Semgrep trace gets no Guardrails scan for it, a target with a Semgrep ticket works
it, the first template carries the audit task, and tests and validator are green.

## Comments

> **2026-10-24 (from 01):** `php-minimal-version` was dropped without handling an open ticket of it on a target: with a **Candidate** operation it would be listed and sorted into Investigation (`worklist.md`, step 2). Solve the open-ticket case for a dropped Stage generically here, for `composer-audit` and `php-minimal-version` alike.
