# r5 — The tool is in place

Played as a walk-through.

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

- [ ] The run works the ticket and posts a `Plan` comment.
- [ ] Under `Decisions` there is no Opener line: not for `psalm-taint-analysis`, which is in place, and not for
      `semgrep`, since the injection is the taint analysis's.

## Results
