# r5 — The tool is in place

Played as a walk-through.

Covers: `skills/continuous-refactoring-run/references/design-point.md`, `skills/continuous-refactoring-run/references/packs/php/psalm.md`, `skills/continuous-refactoring-run/references/packs/php/semgrep.md`

## Situation

An onboarded PHP project on GitHub, `acme/shop`. Its Safety Net is fulfilled, and so are PHPStan Level 5 and Psalm
Taint Analysis: a CI job runs `vendor/bin/psalm --taint-analysis`. Semgrep is not in place, has no ticket and no
rejection. Housekeeping is set up, and its ticket is not due. No ADRs, no glossary.

The open Investigation ticket #33, signal Security, filed from the taint analysis's output: "`ReportController`
writes `$_GET['title']` into the HTML of the report page unescaped (Psalm `TaintedHtml`)." The ticket names the
finding's line in the CI log.

## Call

`/continuous-refactoring-run autonomous`

## Expected

- [ ] The run works the ticket and posts a `Plan` comment, or, where it judges the fix a change of behaviour, an
      open question.
- [ ] In whichever it posts, there is no Opener line: not for `psalm-taint-analysis`, which is in place, and not for
      `semgrep`, since the injection is the taint analysis's.

## Results

2026-11-03, skill commit 9654c4b: pass, every line, as a walk-through.

2026-11-06, on a3c2d7a with the worklist's judging step (safety-net-gate, ticket 02): pass, every line, as a walk-through.

2026-11-07, on 0e29b63, the first playing of every scenario with the runner and a separate judge: fails "The run works the ticket and posts a `Plan` comment." The design judged the fix a change of behaviour and posted an open question, as r3 allows; no Opener line, which holds, as a walk-through.

2026-11-08, with the first line widened to an open question: by the verdict of 2026-11-07, which shows an open question and no Opener line, every line holds; not played again.
