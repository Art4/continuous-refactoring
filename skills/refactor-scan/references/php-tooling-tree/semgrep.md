# `semgrep`

Node on the PHP **tooling tree** (`../php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**, **signal**, **Signal wave**).

- **Name:** Semgrep (OWASP Top 10)
- **Tool:** Semgrep — a standalone binary/Python/Docker tool, not a Composer dependency (unlike most
  of this tree's other nodes).
- **Purpose:** broad OWASP Top 10 static-analysis coverage for `refactor-prioritize`'s Select mode — a
  Signal-producing node, not a Safety Net one (no `resolved` edge anywhere). Complements
  `psalm-taint-analysis` rather than duplicating it: Psalm's taint analysis follows tainted data flow
  (strongest for injection-class bugs, A03/A01/A10), while Semgrep's OWASP-Top-10 registry ruleset
  additionally catches pattern-matchable categories taint analysis doesn't reach on its own — crypto
  misuse (A02), misconfiguration (A05), logging gaps (A09). Also a **Signal wave** node — the one
  node among the nodes reclassified alongside it where full replacement, not addition, was correct.
- **Required parent:** `php-safety-net` alone — fully replaces the old `composer` required parent
  (dropped, not kept alongside). Unlike every other node this ADR moved into the Signal wave, this
  replacement loses nothing: this node's own doc already states Semgrep needs no Composer at all, so the
  `composer` edge was purely an incidental rejection-cascade-closure technicality (added so a rejected
  `composer` could still close this node automatically, since it otherwise had no `required`/`required-
  any` chain back to `composer` at all) — made redundant now that `php-safety-net` is the gate: a
  rejected `php-safety-net` leaf still counts as resolved, but `php-safety-net` itself only ever resolves
  once `composer` (transitively, via its own nine leaves) is decided one way or another, so the same
  closure guarantee holds through the new edge instead.
- **Recommended parent:** `ci-runner` — downgraded from having no edge at all to this node before, the
  same "audit-style node" shape `composer-audit` now uses (`composer-audit.md`), with the same
  Housekeeping-line fulfilment fallback below. The old `psalm-taint-analysis` recommended parent is
  dropped entirely, not merely downgraded — it's redundant now that `psalm-taint-analysis` is one of
  `php-safety-net`'s own nine leaves, so it's always already decided (fulfilled or rejected) by the time
  `php-safety-net` — this node's own required parent — resolves; withholding on it separately would never
  actually delay anything.
- **Fulfilment check:** a CI job invokes `semgrep`, with an OWASP-Top-10 ruleset reference (the
  registry config `p/owasp-top-ten`, inline in the CI invocation or inside a committed
  `.semgrep.yml`/`.semgrep.yaml`) — presence of the invocation, not proof it actually fails the
  pipeline on a finding, the same conservative approximation `composer-audit`'s own CI-gate check
  already uses — **or** a line naming this node is already committed to the Refactoring Notes'
  `housekeeping-template.md` (`../../../continuous-housekeeping/references/housekeeping-template-file-format.md`), no
  proof of a completed run required, the same fallback `composer-audit.md` documents in full.
- **MR scope:** Semgrep wired into CI (however it installs — pip, Docker, or a marketplace CI action;
  never a `composer.json` entry) with the OWASP Top 10 registry ruleset, plus one initial scan pass
  (fix or explicitly baseline what it reports — a target's own judgement call at adoption time, the
  same note `phpmd`'s and `secret-detection`'s own MR scopes already carry). No separate "security
  checklist" document — the tool's own deterministic CI findings are the check; a parallel manual
  checklist covering the same ground would be duplicate upkeep for no real additional coverage. Also
  contribute this node's `Housekeeping` line (below) to `docs/refactoring/housekeeping-template.md`,
  creating that file fresh if it doesn't exist yet
  (`../../../continuous-housekeeping/references/housekeeping-template-file-format.md`).
- **Housekeeping:** re-run Semgrep's OWASP Top 10 ruleset periodically and review new findings — a
  point-in-time scan whose value is in repetition, the same reasoning `composer-audit`'s own
  Housekeeping entry already states for CVE advisories.
- **Signal:** Security (`../../../refactor-prioritize/references/signals.md`) — once fulfilled, Select
  mode prefers this node's real findings, alongside `psalm-taint-analysis`'s, over the generic
  (reading-the-code) recognition method for this factor.
