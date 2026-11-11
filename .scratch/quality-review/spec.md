# quality-review

**Status:** open — grilled and confirmed on 2026-11-06, tickets 01–10 filed

What came out of a critical review of the suite at 0.11.0 on 2026-11-06, gone through with the maintainer point by
point. Five strands of work stand; three points of the review were rejected (*Not in this plan*).

## Why

- **The skill texts are heavy.** About 51,000 words in 66 files under `skills/`. The run's `SKILL.md` plus every
  reference on the full path (scan → filing → design → implement → merge request, with the rules, the principles and
  the tooling model) is about 20,500 words, Pack docs not counted. The more text, the likelier a rule is overlooked.
- **The shipped suite has no glossary.** `skills/continuous-refactoring-run/references/tooling-model.md` names
  `CONTEXT.md` as the vocabulary the suite shares, but `CONTEXT.md` does not ship; in a target the pointer reaches the
  target's own `CONTEXT.md`. Several terms (Locality, Deepening, Hot spot, Part) have no definition under `skills/`.
- **Terms collide with the agent's own words.** Tool (the agent's tools), Plan (plan mode), Findings (review
  findings), Stage, Part, Role, Signal.
- **Many section jumps.** Roughly 1,000 italic section references under `skills/` (a rough count, plain emphasis
  included), and most references open with the same preamble on how a decision point is laid out.
- **CI checks structure, not behaviour.** The validator, the parser tests and the negative controls are static.
  Behaviour is backed by the scenarios in `docs/agents/evals/` (24 of them, `p`/`d`/`r`): hand-played by a fresh
  subagent, live on a fixture copy or as a walk-through, the result noted under `## Results` in each file. There is no
  runner and no CI step, so nothing guards them unless someone plays them.
- **Field results do not reach the repository.** The suite runs in the field on several projects, and much of it is
  proven there, Housekeeping included. But the field eval (`docs/agents/field-eval.md`) keeps its log in an ignored
  `.scratch/<owner>-<repo>-loop-observation/` folder, a fresh eval deletes it, and a finding is deleted once fixed.
  Only failures leave a trace (ticket, fix, ADR). What works leaves none, so a reader of the repository concludes
  "untested".
- **The generic core is unproven.** ADR-0002 promises a language-neutral core; only the `php`, `twig-php` and `generic`
  Packs exist.

## Decided

Grilled on 2026-11-06 (`/grilling`).

| # | Decision |
|---|---|
| Q1 | The field record is `docs/agents/field-results.md`, beside `field-eval.md`: a table of path, environment (kind of project, forge, agent), suite version, date, result; a row points to the scenario where one covers the path. Projects stay anonymous: no names, no ticket or merge request numbers |
| Q2 | The observing agent drafts the rows in a closing step of the field eval; the maintainer confirms them; they land through a PR |
| Q3 | A one-time backfill from the traces on the maintainer's targets, confirmed row by row by the maintainer |
| Q4 | A local runner, no CI (cost). Playing the affected scenarios before a merge is mandatory |
| Q5 | Superseded by Q23. The shipped glossary is generated from `CONTEXT.md` by a script; `--check` in the validator keeps it current, as `adr_index.py` does for the ADR index. Definitions that carry rules in place stay there |
| Q6 | The second language Pack is for a language with a real target |
| Q7 | That target is the frontend (JS) of a PHP application on GitLab already in field use; it also tests a language Pack beside `php` and `twig-php` in one target |
| Q8 | Each scenario gets a `Covers:` line naming the skill files it tests; a PR changing one of them plays the scenarios that cover it, notes the results at its head commit under `## Results`, and names them in its description. The validator checks only that every scenario has the line; the duty is written in `AGENTS.md` and becomes a check when broken twice |
| Q9 | The runner is a repository-local skill under `.claude/skills/` (not shipped), following *Playing one*; it plays walk-throughs and live scenarios as the table says, live ones on a fixture copy in a temporary folder |
| Q10 | A separate fresh judge subagent gets the player's record and the expected list and judges line by line; the result is pass, or the lines that failed, quoted |
| Q11 | The record's rows are drafted at both ends of a field eval (six quiet rounds, or the human's stop) before the log may be deleted; a new eval's start checks that the old log is recorded |
| Q13 | No Symfony Pack: a Symfony application already works with the `php` and `twig-php` Packs |
| Q14 | S6's Pack is `js`, ESLint first (adopt, raise rules, raise ecmaVersion); Stylelint later as a Tool of its own; HTML needs nothing (Twig templates are `twig-php`'s); an outdated frontend framework is Housekeeping's, not a Pack's |
| Q15 | The backfill rows are drafted outside the repository first; the maintainer reviews them before any PR. Ticket filing, Plan comments, closing fulfilled tickets in an external tracker, and the tracker file's Refactoring operations, are confirmed by the maintainer |
| Q16 | Order: S1 → S3 → S2 → S4/S5 → S6; S6 may run beside S4 |
| Q17 | Scenarios the traces do not show stay *not evidenced*; nothing is added from memory |
| Q18 | The PHP Pack applying to a repository whose only PHP file is a deploy script is a ticket of its own, outside this plan, and S1.4's first case |
| Q19 | The suite's website stays out of the record: its traces predate 0.5.0 |
| Q20 | Where rationale goes that a model needs is decided in S4; until then it stays where a scenario fails without it |
| Q21 | Every term ships, none is left out: all 55 occur under `skills/`, the rarest are the ones lacking a definition there. No marker |
| Q22 | Each of the three `SKILL.md` points to the glossary in one line; `tooling-model.md` and the two Pack files that named `CONTEXT.md` point to it too |
| Q23 | Supersedes Q5 and Q12: the shipped glossary is the single source. `CONTEXT.md`'s *Language* moves into `skills/continuous-refactoring-run/references/glossary.md` with its *Avoid* lines; `CONTEXT.md` keeps its head and points there. No generator, no `--check`; the validator's vocabulary checks read the glossary and leave it out of the text they count as use |
| Q24 | The pointer to the glossary says to look a term up only where the text does not make its meaning clear |
| Q25 | Ticket 08 cuts the glossary to the meaning at runtime, one to three sentences per entry, *Avoid* without history; ticket 07 measures the glossary's share on its own |
| Q26 | Supersedes part of Q8: the `Covers:` line is where the choice starts, not the whole list. A PR plays those covering scenarios whose expected lines bear on the behaviour it moves, and names the ones it left out with the reason; wording that moves no behaviour plays none. Why: the first full playing showed a one-sentence Driver change would replay all 14 d-scenarios, about 1.2M tokens |
| Q27 | A Stage a scan finds fulfilled with no ticket of its own, under its Tool's name or another, gets a ticket filed and closed at once as done, its text naming the evidence, so the Stage is known and the Track's trace holds. Why: a Stage in place left no record, so the scan was due again on every run with an empty result (r7 B) |
| Q28 | Where the tracker's **Search** does not reach comments, the worklist also reads the comments of a bounded set of tickets for an `Opener:` line, as `tooling-model.md`, *An Opener*, says; the Opener stays where design writes it. Why: r1 found an Opener in a `Plan` comment only through its merge request, which a target without one would not have |
| Q29 | r5's first line takes r3's wording: a `Plan`, or an open question where the design judges the fix a change of behaviour. r5 tests the Opener, not that boundary; the skill says nothing new about it until the field shows a need |
| Q30 | Ticket 08 leaves the glossary as it is: no play opened it since its pointer was reworded (ticket 07), so a cut saves almost nothing at runtime. Revisit when a play shows runs opening it again |
| Q31 | No sweep for rationale: the references hold little (about 40 "because"/"since"/"so that" in the 25 largest). A reason a model needs stays as a half-sentence in the text; any other moves to the ADR when its passage is touched anyway, as `CONTRIBUTING.md` says. Section pointers stay |
| Q32 | The decision-point preamble, copied into eleven references, becomes a one-line pointer to the run's `SKILL.md`, *Decision points*; played on r8 and r3 |
| Q33 | The word budget is one limit per file under `skills/`, its size plus a tenth when the check came in; a change that needs more raises the number in `WORD_BUDGET`, visibly in the diff |
| Q34 | The `js` Pack applies where the repository holds JavaScript of its own: a `package.json`, or a `*.js`/`*.mjs`/`*.cjs` file outside `node_modules/` and `vendor/`; minified files and build output are not its own |
| Q35 | TypeScript stays out of the first `js` Pack |
| Q36 | Every ESLint Stage is Guardrails: a frontend without a linter never holds the Safety Net back |
| Q37 | Three ESLint Stages: adoption with `js.configs.recommended` and bulk suppressions, clearing the suppressions, and a rollout of `no-var`, `prefer-const`, `object-shorthand`; no `ecmaVersion` Stage, its concern is the rollout's browser question |
| Q38 | The Pack, fixtures and scenarios go in one PR; the field test follows on the maintainer's real target, its row in a small PR of its own; ticket 10 stays open until then |
| Q39 | A language Pack follows, after `generic`, the Packs of the languages it builds on (`js` and `twig-php` after `php`), through a field in `pack.json`; its name (`after` or `recommends`) is settled in that PR, a small one after the `js` Pack |
| Q40 | The field test of the `js` Pack runs on the suite's website; the maintainer's session prepares its merge request for the skill links |
| Q41 | Its second session is interactive: `/continuous-refactoring-run Guardrails, only the ESLint Stages` |
| Q42 | The maintainer reviews the merge request as any reviewer; the evaluation against the expectation follows once |
| Q43 | The field for Q39 is named `follows`: `after` was the Stages' old name for `waits_for`, `recommends` was rejected in ADR-0086 |
| Q44 | `follows` only orders; a Pack it names that does not apply is passed over; an unknown name and a cycle are refused by the parser |
| Q45 | The rollout's gap for browsers without ES2015 goes in a small PR of its own, not with Q39 |
| Q46 | PHP that only builds or deploys a site counts for the `php` Pack: its `applies_when` stays; a tool not wanted there is rejected |
| Q47 | Guardrails keep waiting for the whole Safety Net, the PHP one included; a known limitation says to name the Track to lint a frontend sooner. Taken up again if the field shows it more often |
| Q48 | A PHP file that only configures a tool (a Deployer recipe), with no `composer.json` beside it, makes no PHP project; code of the project's own, a build script included, still does (Q46) |
| Q49 | A fixture `static-site-deploy-script` and a scenario r11; played with r9 as the counter-check |
| Q50 | A scan that is due because a Stage is not known judges only the Stages not known; known ones go into the seed as the seed from the trace takes them. A scan the call asks for, and the Housekeeping re-check, judge all |
| Q51 | Filing's search keeps only hits that match the Stage as the worklist's rule says, so a sibling's ticket is no hit. Unique markers in ticket text are weighed separately |
| Q52 | Without ES2015, the run whose worklist reads the answer closes the rollout's ticket, quoting it; where the adoption wrote `Not yet:` entries, the ticket removes them first |
| Q53 | The scenarios' slips (no ticket open beside Housekeeping, closed tickets for on-request Stages, fixtures without a tracker file) are fixed in a PR of their own, with no play |
| Q54 | The unclear places named once, that forced no wrong decision, stay in the log as left as is |
| Q12 | Superseded by Q23. A term ships in the glossary when `CONTEXT.md` marks it explicitly; the glossary is `skills/continuous-refactoring-run/references/glossary.md`; the pointer in `tooling-model.md` aims at it; the Driver and Housekeeping reach it through `../continuous-refactoring-run/` |

## Strands

### S1 — Field results back into the suite

1. **The field record**, `docs/agents/field-results.md` (Q1): one row per path and environment, anonymous.
2. **A closing step in `field-eval.md`** (Q2, Q11): at both ends of an eval the observing agent drafts the rows, the
   maintainer confirms them, a PR lands them; a new eval's start checks the old log is recorded.
3. **The backfill** (Q3, Q15, Q17): rows drafted from the traces on the maintainer's targets, reviewed by the
   maintainer before any PR. What nobody can confirm stays *not evidenced* and is a candidate for a scenario.
4. **A field case becomes a scenario**: a miss found in the field becomes a ticket *and* a scenario; a newly
   confirmed path becomes one where it is cheap to rebuild. First case: the PHP Pack applying to a repository whose
   only PHP file is a deploy script (Q18).

### S2 — Scenarios played repeatably

1. **A `Covers:` line** in every scenario, naming the skill files it tests; the validator checks it is there (Q8).
2. **A runner**, a repository-local skill under `.claude/skills/`, following *Playing one*, walk-throughs and live
   scenarios alike (Q9); no CI (Q4).
3. **A separate judge** subagent per scenario, line by line (Q10).
4. **The duty** in `AGENTS.md`: a PR that changes a covered skill file plays those scenarios, notes the results at
   its head commit, names them in its description (Q8).

### S3 — A shipped glossary (weakness 2, part A)

The glossary moves from `CONTEXT.md` into `skills/continuous-refactoring-run/references/glossary.md`, every term with
its *Avoid* line; `CONTEXT.md` points there. Every `SKILL.md` names it; the validator's vocabulary checks read it
(Q21–Q23).

### S4 — Lighter skill texts (weakness 1, and part C of weakness 2) — after S2

1. Measure what real runs read, from the runner's transcripts.
2. Move rarely taken branches into files read only when their table row applies — for example the design point's
   *Planning a baseline ticket* and *Open questions*. Wording unchanged.
3. Drop rationale from runtime text and replace repeated preambles with a pointer, every cut played against the
   affected scenarios. Rule of thumb until S4 decides otherwise (Q20): rationale stays where a scenario fails without
   it; otherwise it belongs in the ADR.
4. Last, a validator word budget per reference, with targets taken from steps 1–3.

### S5 — Colliding terms (weakness 2, part B) — after S2

Rename a colliding term (Tool, Plan, Findings, Stage, Part, Role, Signal) only where a scenario shows it causes a
wrong decision.

### S6 — A second language Pack

The Pack `js`, ESLint first, on the frontend of a PHP application on GitLab already in field use (Q6, Q7, Q14).
Bears on 1.0, which comes at the earliest when the Pack system is established, tested and stable.

## Order

S1 → S3 → S2 → S4/S5 → S6; S6 may run beside S4 (Q16). S1 and S3 can start now.

## Tickets

| # | Ticket | Strand | Blocked by |
|---|---|---|---|
| 01 | The field record and the field eval's closing step | S1.1, S1.2, S1.4 | — |
| 02 | Backfill the field record | S1.3 | 01 |
| 03 | A shipped glossary | S3 | — |
| 04 | Every scenario names what it covers | S2.1 | — |
| 05 | A scenario runner with a separate judge | S2.2, S2.3 | 04 |
| 06 | Playing the affected scenarios before a merge | S2.4 | 05 |
| 07 | Measure what runs read, and move rare branches out | S4.1, S4.2 | 05 |
| 08 | Cut rationale and repeated preambles, then a word budget | S4.3, S4.4 | 07 |
| 09 | Colliding terms | S5 | 05 |
| 10 | A Pack for JavaScript | S6 | 05 |

The PHP Pack's false positive is `.scratch/php-pack-false-positive/issues/01-deploy-script-is-no-php-code.md`.

## Not in this plan

- **Design churn.** 0.x means heavy development by design; `scripts/adr_index.py` already keeps the ADRs' status in
  `docs/adr/README.md`. Not a weakness.
- **Rules fitted to one target.** Observations come from several projects, they are only not named.
- **A heavy process.** With AI help the process works very well and carries structural rebuilds; a strength.
- **A Symfony Pack** (Q13): a Symfony application already works with `php` and `twig-php`.
- **The PHP Pack's false positive** (Q18): its own ticket, outside this plan; how the rule should read is decided
  there. It is S1.4's first case.
- **The suite's website** (Q19): its traces predate 0.5.0 and stay out of the record; its installed skills are the old
  set, a matter of installation.
