# `semgrep`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **recommended edge**, **signal**).

- **Name:** Semgrep (OWASP Top 10)
- **Tool:** Semgrep — a standalone binary/Python/Docker tool, not a Composer dependency (unlike most
  of this tree's other nodes).
- **Purpose:** broad OWASP Top 10 static-analysis coverage for `refactor-prioritize`'s Select mode — a
  Signal-producing node, not a Safety Net one (no `resolved` edge anywhere). Complements
  `psalm-taint-analysis` rather than duplicating it: Psalm's taint analysis follows tainted data flow
  (strongest for injection-class bugs, A03/A01/A10), while Semgrep's OWASP-Top-10 registry ruleset
  additionally catches pattern-matchable categories taint analysis doesn't reach on its own — crypto
  misuse (A02), misconfiguration (A05), logging gaps (A09).
- **Required parent:** `composer` — this node was the one other place in the tree (besides
  `rector-type-coverage`) with no `required`/`required-any` chain back to `composer` at all, so a
  rejected `composer` could never automatically close it; it would have had to be manually filed and
  rejected by hand the first time `psalm-taint-analysis` cascaded to effectively-rejected on such a
  target. Added *alongside* the `recommended` edge below, not replacing it (unlike the flat,
  `composer`-only shape `phpmd` uses) — inert whenever `composer` is genuinely adopted, since
  `psalm-taint-analysis` itself already requires `composer` transitively by the time it's ever decided;
  the edge only ever binds when `composer` itself is rejected.
- **Recommended parent:** `psalm-taint-analysis` (`psalm.md`) — this node stays withheld from proposal
  until `psalm-taint-analysis` is *decided* (fulfilled or rejected), so Psalm's own taint-flow baseline
  settles first; a rejected `psalm-taint-analysis` still releases this node, it just goes in without
  that baseline. The `composer` required edge above doesn't disturb this ordering — Semgrep still can't
  be proposed before `psalm-taint-analysis` is decided, `composer` fulfilled or not; it only adds a
  second, independent way for this node to close for good, the same "settle Psalm's own scope first"
  reasoning `editorconfig → php-cs-fixer` already applies to formatting-before-style.
- **Fulfilment check:** a CI job invokes `semgrep`, with an OWASP-Top-10 ruleset reference (the
  registry config `p/owasp-top-ten`, inline in the CI invocation or inside a committed
  `.semgrep.yml`/`.semgrep.yaml`) — presence of the invocation, not proof it actually fails the
  pipeline on a finding, the same conservative approximation `composer-audit`'s own CI-gate check
  already uses.
- **MR scope:** Semgrep wired into CI (however it installs — pip, Docker, or a marketplace CI action;
  never a `composer.json` entry) with the OWASP Top 10 registry ruleset, plus one initial scan pass
  (fix or explicitly baseline what it reports — a target's own judgement call at adoption time, the
  same note `phpmd`'s and `secret-detection`'s own MR scopes already carry). No separate "security
  checklist" document — the tool's own deterministic CI findings are the check; a parallel manual
  checklist covering the same ground would be duplicate upkeep for no real additional coverage.
- **Signal:** Security (`skills/refactor-prioritize/references/signals.md`) — once fulfilled, Select
  mode prefers this node's real findings, alongside `psalm-taint-analysis`'s, over the generic
  (reading-the-code) recognition method for this factor.
