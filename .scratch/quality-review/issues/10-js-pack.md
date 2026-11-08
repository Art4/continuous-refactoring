# 10 — A Pack for JavaScript

Type: task
Status: done
Blocked by: 05

**What to build** (spec S6; Q6, Q7, Q14)

- A Pack `js` under `skills/continuous-refactoring-run/references/packs/`, with ESLint as its first Tool: Stages to
  adopt it, to raise its rules, and to raise its `ecmaVersion`. When the Pack applies is decided here (a
  `package.json`, JavaScript sources outside `node_modules/`, …). Stylelint stays for later, as a Tool of its own;
  HTML needs nothing, Twig templates are `twig-php`'s; an outdated frontend framework is Housekeeping's.
- The Pack applies beside `php` and `twig-php` in one target; check that the parser, the Track choice and the scan
  hold three Packs at once.
- Fixtures under `fixtures/`, anonymous: a PHP application with a JavaScript frontend linted by ESLint, and one with
  no ESLint yet. Scenarios for both, with `Covers:` lines.
- Field test on a PHP application already in field use whose frontend is linted with ESLint; its rows go into the
  field record. Neither the target nor anything from it is named in this repository, its tickets, merge requests or
  code.
- Docs: `docs/playbooks/tracks.md`, `docs/architecture.md`, `README.md` where they list the Packs. A changelog
  fragment.

**Done when** the Pack, its fixtures and scenarios are in, the scenarios pass, the field test has a row in the record,
and tests and validator are green.

## Comments

**2026-11-08 — Pack, fixtures and scenarios in.** Decided in Q34–Q39 (spec). r9 and r10 pass at b36de5e (players
117k and 110k, judge for both). The field test on the maintainer's target is still to come; this ticket stays open
until its row is in the field record. The order of language Packs (Q39) follows in a PR of its own.

**2026-11-08 — Field test.** A static website (E4 in the field record), call "Guardrails, only the ESLint Stages":
three tickets filed, the browser question asked at filing and answered, the adoption's merge request with
`package.json`, flat config (`sourceType: "script"`, browser globals, vendored copy ignored), two suppressed findings
and a CI job; green. It confirms the fresh-adoption path; "already linted" stays covered by r10 alone. Three fixes to
`eslint.md` followed: the Node.js version is read from the installed release's `engines` (the run had copied
"ESLint 9 needs 18.18" into a ticket while installing ESLint 10), a rule that finds nothing is on from the adoption
and `prefer-const` is counted again after `no-var`, and current browsers keep the default `ecmaVersion`.
