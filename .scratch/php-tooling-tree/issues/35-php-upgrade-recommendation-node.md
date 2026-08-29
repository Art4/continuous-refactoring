# 35 — Should the tree ever *recommend* a PHP-runtime upgrade without executing it?

**What to build:** Not yet spec'd — this is an open design question the user flagged as worth thinking about, not a firm ask. Record it here so it survives rather than getting lost, and pick it up properly in a future session.

**Why:** Observed on the `Art4/legacy-todo` run: the target stayed pinned to PHP 5.6 throughout, and adopting PHPStan/Rector (both require PHP 7.2+/8.0+) was solved by running them in a second, parallel Docker container (PHP 8.3) rather than by proposing a PHP-runtime bump for the target itself — even though this same target repo has precedent for exactly that kind of candidate: an earlier, unrelated run's merged `PR #45 "Tool/Build: bump PHP runtime floor to 7.2"`. Maintaining two permanently-parallel PHP versions (one for the app, one for its own dev tooling) is a plausible interim state, but not obviously the suite's intended steady state, and nothing in the tree today ever raises "you now have two PHP versions in play" as a thing worth surfacing.

**Priority:** (none — this is a research/design question, not a firm high-priority ask; don't spec it blind)

**Status:** needs-triage

Open questions to resolve in a design session, not to answer here:

- [ ] Should there be a dedicated `php-upgrade` tree node at all, or is this better handled as an ad hoc observation some other node's outlook surfaces (e.g. `phpstan-level-0-baseline`'s MR outlook could note "this required a second PHP 8 container; consider a runtime upgrade" without a new formal node)?
- [ ] If a dedicated node: how does the suite reconcile "the tree normally files and implements a candidate autonomously by default" with "a PHP-runtime upgrade must never happen without an explicit human go-ahead"? Would this be the tree's first node whose MR scope is deliberately "advisory only, no automatic candidate filed" — and if so, what does `refactor-design`/`refactor-implement` even do with a node like that (neither of them currently has a concept of "propose but never build")?
- [ ] Where would such a node sit in the edge table — a sibling of `composer` under `loop-config`? A node with no required parents that's just always eligible to *suggest* (not propose as a normal candidate) once some trigger condition is met (e.g. two parallel PHP versions detected)?
- [ ] Is this PHP-specific, or does the same shape (recommend-only, human-gated runtime bump) belong in the generic tree so other language specializations can reuse it later?

## Comments

> **2026-08-29:** Filed from the legacy-todo reviewer-loop findings log
> (`.scratch/legacy-todo-loop-observation/findings.md`, "Finding — PHPStan läuft jetzt korrekt in
> separatem Docker/PHP-8.3-Container, aber kein PHP-Upgrade-Vorschlag") after the user asked for it to be
> turned into a ticket, explicitly framed as "we need to think about this" rather than a ready spec —
> kept as `needs-triage` rather than `ready-for-agent`/`ready-for-human` for that reason.
