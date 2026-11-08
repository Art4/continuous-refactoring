# Field results

What the suite has done on real targets, path by path. The [scenarios](evals/README.md) test the skill text in a
made-up situation; this record says where a path has held, or failed, in the field. A path nobody has seen in the
field is missing here, and is a candidate for a scenario.

A maintainer's record: it does not ship. Rows come from the closing step of a [field eval](field-eval.md), or from a
maintainer who saw the path run.

## Writing a row

- **Path** — a step or situation of the suite as a reader of the skills would name it: onboarding, a Track, a Stage
  or a group of Stages, the design point's plan, rework after a request for changes, a base update, Housekeeping
  set up or worked, the Driver's review, a scenario's situation.
- **Environment** — described, never named: the kind of project (application or library, language, framework), the
  forge, where the tickets live, the agent. The same environment keeps one short label (E1, E2, …) across rows, kept
  in the list under *Environments*.
- **Version** — the suite release the run used, or a range.
- **Dates** — when it ran, as a date or a range.
- **Result** — **confirmed**, **in progress**, **rejected** (the human declined it, and the rejection was recorded),
  or **miss** (the suite went wrong; the row says how, and names the ticket's subject, not its number).
- **Scenario** — the scenario that covers the path, where one does.
- **Source** — *trace* when it shows on the forge or tracker, *maintainer* when a maintainer confirms what no trace
  shows.

No row names a project, a repository, a person, or a ticket or merge request number.

## Environments

| Label | Environment |
|---|---|
| E1 | PHP application, Symfony, PHP 8.2; GitLab merge requests, tickets in an external tracker; Claude Code |
| E2 | PHP library, PHP 8.2; GitHub; Claude Code |
| E3 | PHP application without a framework, PHP 8.2, migrated from 5.6; GitHub; Claude Code, later OpenCode |
| E4 | Static website: plain JavaScript loaded by a `<script>` tag, PHP as build tooling only; GitLab; Claude Code |

## Results

| Path | Environment | Version | Dates | Result | Scenario | Source |
|---|---|---|---|---|---|---|
| Onboarding | E1, E2, E3 | 0.5–0.9 | 2026-09-26 – 2026-10-25 | confirmed | — | trace |
| BC promise set at onboarding | E2 | 0.9 | 2026-10-25 | confirmed | — | trace |
| Housekeeping set up | E1, E3 | 0.5–0.6 | 2026-09-26 – 2026-10-17 | confirmed | — | trace |
| Housekeeping worked, next ticket filed | E1, E2, E3 | 0.10 | 2026-11-01 – 2026-11-04 | confirmed | — | trace |
| Housekeeping re-check files tooling tickets | E3 | 0.10 | 2026-11-01 | confirmed | — | trace |
| Housekeeping template follow-up | E1 | 0.11 | 2026-11-06 | confirmed | — | trace |
| Safety Net / Guardrails: Rector sets, PHPStan levels with baseline and deprecation rules, PHPMD rule by rule, Psalm taint analysis, Twig-CS-Fixer, PER-CS, EditorConfig | E1 | 0.6–0.11 | 2026-10-07 – 2026-11-06 | confirmed | — | trace |
| Guardrails: Roave BC check, Rector PHP set, PHPStan level 10, PHPMD, PHPUnit coverage metadata | E2 | 0.9–0.10 | 2026-10-25 – 2026-10-30 | confirmed | — | trace |
| Safety Net / Guardrails: PHP CS Fixer, CI gate for code style, Rector PHP set | E3 | 0.5–0.10 | 2026-09-26 – 2026-11-02 | confirmed | — | trace |
| Coverage floor | E1 | 0.11 | 2026-11-06 | in progress | — | trace |
| Secret Detection proposed, rejected by the human, rejection recorded | E1 | 0.10–0.11 | 2026-11-05 | rejected | — | trace |
| A rejection respected later: the plan names it and how it differs | E3 | 0.5 | 2026-09-27 | confirmed | — | trace |
| Investigation Track: structural scan → tickets → merge requests | E1, E2, E3 | 0.5–0.11 | 2026-09-27 – 2026-11-06 | confirmed | — | trace |
| Plan comment at the design point | E2, E3 | 0.5–0.10 | 2026-09-27 – 2026-11-04 | confirmed | — | trace |
| Plan comment at the design point | E1 | 0.6–0.11 | — | confirmed | — | maintainer |
| Open question on a ticket, answered by the human, the run goes on | E3 | 0.5 | 2026-09-27 – 2026-09-28 | confirmed | — | trace |
| Ticket filing | E2, E3 | 0.5–0.10 | 2026-09-27 – 2026-11-04 | confirmed | — | trace |
| Ticket filing; closing a ticket found fulfilled | E1 | 0.6–0.11 | — | confirmed | — | maintainer |
| Refactoring operations in the tracker file | E3 | 0.10 | 2026-11-01 | confirmed | — | trace |
| Refactoring operations in the tracker file | E1 | 0.6–0.11 | — | confirmed | — | maintainer |
| Ticket delivered in parts | E1, E2, E3 | 0.5–0.11 | 2026-09-27 – 2026-11-06 | confirmed | — | trace |
| Driver review with a verdict, merge left to the human | E1, E3 | 0.10–0.11 | 2026-11-01 – 2026-11-06 | confirmed | — | trace |
| Rework after a human's request for changes | E1, E3 | 0.10 | 2026-11-02 – 2026-11-05 | confirmed | d11 | trace |
| Driver review called a flawed merge request mergeable; the human found the flaw (coverage counted the tests themselves) | E3 | 0.10 | 2026-11-02 | miss | d11 | trace |
| Base update after a conflict the human's merge caused | E1 | 0.10–0.11 | 2026-11-05 – 2026-11-06 | confirmed | d12 | trace |
| Draft set to ready by the review | E1 | 0.11 | 2026-11-06 | confirmed | — | trace |
| End after N rounds, timer stopped | E3 | 0.10 | 2026-11-02 | confirmed | — | trace |
| Guardrails: ESLint adopted fresh, its suppressions and remaining rules filed, the browser question asked at filing | E4 | after 0.11 | 2026-11-08 | confirmed | r9 | trace |

## Not evidenced

Seen in no trace and confirmed by no maintainer, as of 2026-11-06 — candidates for scenarios or a field eval:

- Scenarios: d1–d10, d13, d14, p1–p3, r1–r7.
- Paths: `merge` mode; a draft left behind; a conflict the suite cannot resolve; a project without PHP on 0.5 or
  later; interactive against autonomous mode, which traces do not show.
- The miss above has no ticket and no scenario of its own yet: whether the Driver's review now catches it is open.
