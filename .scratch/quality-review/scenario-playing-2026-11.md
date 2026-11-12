# Playing every scenario once (ticket 05)

The first full playing with the runner `.claude/skills/play-scenarios/`, on the skills of `main` at c982762 and
later (no change to `skills/` since). Records, briefs and verdicts live in the session's scratchpad, not here.

## Plan

Played one block at a time, on the maintainer's go, so the cost stays visible. Variants of one scenario share one
player; plays of different scenarios never do. Judges take several records each.

| Block | Plays | State |
|---|---|---|
| 1 | judges for d1, d2, d3, d4, d5-a, d5-b, d6, d7, d8, d10 (records played 2026-11-07) | done |
| 2 | d11, d12: play and judge | done |
| 3 | d13, d14 | done; d13 replayed with the fixed brief |
| 4 | p3 (walk-through), p1 and p2 (live, on fixture copies) | done |
| 5 | r1, r2 | done |
| 6 | r3, cases A–C in one player | done |
| 7 | r4, r5, r6 | done; r6 replayed with both calls |
| 8 | r7 and r8, each scenario's variants in one player | done |
| — | d9 needs a real top-level session: for the maintainer | open |

## Cost

- A player: about 50k–115k tokens, most of it reading the skill texts (block 2: d11 85k, d12 81k).
- Block 3: d13 63k, d14 64k, judge about 50k.
- Replays: d13 83k, r6 89k, judge about 55k.
- In all, about 2.2M tokens for the blocks and replays, besides the aborted first attempt.
- Block 8: r7 (A and B) 102k, r8 (A and B) 118k, judge about 60k.
- Block 7: r4 107k, r5 111k, r6 72k, judge about 55k.
- Block 6: r3, three cases in one player, 119k (three players would have cost about 300k); judge 53k.
- Block 5: r1 115k, r2 118k, judge 58k.
- Block 4: p3 63k, p1 live 96k, p2 live 77k, judge (with the live folders) 69k.
- A judge: about 13k tokens per record of ~2,000 words (block 1: two judges of five records, 64k and 68k).
- The first attempt started all plays at once and hit the limit of 20 concurrent subagents; it was stopped on the
  maintainer's word. Ten records survived and were judged in block 1.

## Results

| Scenario | Result |
|---|---|
| d1, d2, d3, d4 | pass |
| d5, both calls | pass |
| d6, d7 | pass |
| d8 | pass; one line only loosely: the comment leaves the correction to the human, without naming a normal merge request as the way |
| d11, d12 | pass |
| d14 | pass |
| r2 | pass |
| r3, cases A–C | pass |
| r4 | pass |
| r7, r8, both variants each | pass |
| r5 | **fail, the scenario against the design**: "The run works the ticket and posts a `Plan` comment." The design judged escaping the output a change of behaviour and posted an open question instead, as r3 allows ("or, where it judges the fix a change of behaviour, in an open question"); the Opener line holds — none |
| r6 | **fail** on the replay, one line: "One comment on !40 … asks which order to keep" — the comment says what each side changes, but asks where the voucher step belongs, with three options. The second-call line, missed by the first play, now holds |
| r1 | **fail**: "The worklist finds the Opener through **Search**" — the player took the tracker's search to cover a ticket's title and text only, so **Search** missed the line in #14's `Plan` comment; it found the Opener through the merge request search instead, and the scan was due as expected |
| p1, p2 (live), p3 | pass; the judge checked the live folders' branches and commits too |
| d13 | pass on the replay. The first play failed from the brief: it showed round 2's run only by its outcome |
| d10 | **fail**: "It ends the timer explicitly before its closing message, with the call the environment has for that." The player made no call and relied on setting no new wake-up |

**Tally:** 29 plays, 25 pass, 4 fail — d10 (a gap in the Driver's text), r1 (possibly a gap: **Search** and
comments), r5 (the scenario against the design, see *r5 against r3*), r6 (the comment's question, see below).

The `## Results` lines go into the scenarios on the maintainer's go.

## Findings for later

**Confirmed gap (d10).** The Driver's *Stops* asks it to end the timer explicitly "with the call its environment
has for that", but names that call for no environment; *Between rounds* names `ScheduleWakeup` for setting it. Players
of d5-b, d7, d8 and d10 each stumbled on it independently; d10 failed. It makes a required step fall away, so it is
worth a fix: name the Claude Code call (`ScheduleWakeup` with `stop: true`), in a PR of its own, not in ticket 05.

**Unclear places several players named** (to weigh; none forced a wrong decision on its own):

- The Driver has no Status/Next closing lines of its own; players borrowed the run's (d1, d2, d7, d10).
- *Stops* has no row for ending without a timer (d7) or after the onboarding (d6), so their closing form is open.
- Notifications: which tool in Claude Code, whether one goes out when nothing waits, and whether step 5's and the
  stop's are one message or two (d1, d2, d4, d5-b, d8).
- "Ending a timer that was never set, or whose one wake-up has already fired" (d1, d2, d4, d5-a, d5-b, d7, d8, d10):
  the same gap as above, seen from the other side.
- Base updates "once more" before a stop, when step 1 of the same round just found nothing blocked (d1, d4, d5-b,
  d10).
- "The merge requests of this Driver" against "open merge requests of the suite's tickets" (d1, d4).
- "More than three" lets a fourth merge request open, so the ceiling is four (d4): as designed, but worth a word.
- The Log is "a line in the Log" every round, yet off by default (d5-a, d5-b).
- d8: a forge that deletes the head branch on merge removes it before the child is retargeted; nothing says to look
  for children before merging.
- d6: which call text the onboarding run gets from the Driver; step 2 hands over before step 3 reads `AGENTS.md`.
- d3: no third rework is only implied (glossary *Round*), not stated in step 4.

**From block 2** (d11, d12; none forced a wrong decision):

- The Driver's run prompt has no slot for the ticket a rework or base update names (d3, d11).
- A human's request for changes on a merge request the review marked ready: who sets it back to draft, and when
  (d11); `under the Driver` keeps it a draft, the base update keeps draft or ready as it was — which wins (d12).
- After a rework, whether the merge request's description is updated, and whether the review checks that the
  human's request was met (d11).
- A base update by rebase: which side is "the default branch's", how a tool's rerun replaces a commit mid-rebase,
  and what happens to commits that depend on it, such as a PHPStan baseline (d12).
- The suite's commits and the human's cannot be told apart by author when both use one account (d3, d12).
- Reconcile's "In review" line: a finding that needs a decision point or not (d11, and r7/r8 earlier).

**About the runner's brief (d13).** The Driver's plays were told "a subagent you would start, you describe
instead, with what it returns as the situation implies" — wording of this playing's prompts, not of the runner
skill. d13's player therefore reported round 2's run only by its outcome, and the lines about how the run opens and
reads back the draft could not be judged. The brief now says to play a subagent's steps too, in a section of their
own. The Driver plays that passed did not hinge on a run's inside; d13 is replayed.

**From block 3** (d13, d14): the closing has two Status lines, the run's and the Driver's, and only the Driver's
names a held draft (d14); a round with no run, only a review, is counted towards the End by the player's own choice
(d13).

**From block 4** (p1–p3; none forced a wrong decision):

- p1: the own Pack's `"$schema"` points at `.agents/skills/…`, which a target without installed skills does not
  have; the Tool's facts (package, command) come from the agent's own knowledge; whether a details file needs a
  Housekeeping line is open.
- p2: the rename went into the build commit, not a correction commit of its own; the player reformatted the human's
  existing `pack.json` unasked; the branch stays checked out at the end.
- p3: "the Pack is still to come" could promise a Pack the next run finds unneeded, where the tool is one the suite
  knows.

**Possible gap (r1).** An Opener is written in a `Plan` comment or an open question, but **Search** may not reach
comments: the player, assuming GitLab, took issue search to cover title and description only. The merge request
search found it here because !15 carried the same line. Where **Merge requests** is `none`, or the plan's merge
request never opened, the Opener would be missed. To check: which trackers' search covers comments, and whether
`tooling-model.md`, *An Opener*, should say how to reach a comment. r1's brief also names no forge.

**From block 5** (r1, r2): the parser exits 2 on a Tool only the scenario knows (`example-policy`), so players worked
the seed by hand; which step owns the Opener search, the worklist or Track choice, is read two ways (r1, r2); which
record uses an Opener up, the closed ticket or the rejection (r2).

**From block 6** (r3; none forced a wrong decision): a Security fix changes behaviour, so the design ends in an
open question, yet the Tool files' *Opener* speaks only of "a plan"; the behaviour-change question has no default,
and *An answer arrived* has no row for "becomes feature work" — nor a third way such as a bug fix now; a ticket
filed by an exploration enters the worklist only through a **Candidate** operation, which the player had to assume;
Semgrep's "injection only where taint analysis cannot run" has to be pieced together from two files.

**r5 against r3.** r3 accepts a design that ends in an open question where the fix changes behaviour; r5 expects a
`Plan` comment for an unescaped HTML output, which the design judged a behaviour change. Either r5's line gets r3's
"or an open question" wording, or the skill says when a Security fix counts as no change of behaviour. A decision
for the maintainer.

**From block 7** (r4–r6): r4's pin is a comparison script never committed, at the callers' seam, which the player
itself names as at odds with "first commit is a Pinning Test"; r4 and r5 reach Investigation only by assuming both
tooling Tracks have a trace; r6's hand-over comment carries no searchable mark, so how a second call tells the base
update was handed over is not backed.

**Possible gap (r7 B).** A Stage the scan finds already in place under another name gets no ticket and no
rejection, so it never becomes *known*: the Track has no trace again on the next run, and the scan runs again,
with an empty result, every time. Nothing says how that loop ends. To check against `worklist.md`, *A Track's
trace*, and the scan's report.

**From block 8** (r7, r8): `worklist.md` says the due scan judges the Stages not known, `track-scan.md` every Stage
in scope, and a Guardrails scan re-judges Safety Net Stages the trace counted (`tooling-parser.md`: "judged once");
whether a PHP CS Fixer rollout ticket counts as a baseline ticket; a Housekeeping ticket not due is "workable" in the
worklist and "nothing" in Track choice; `coverage-metadata-strict`'s *Applies when* has no fallback when the PHPUnit
version cannot be read; fresh rollout and metadata proposals have no prescribed title.

**r6's comment.** The branch only moves the discount rules, while `main` changes the voucher's order; the
scenario says both sides changed the order, and the player's own analysis contradicts its comment on that. The
comment then asks where the voucher step belongs instead of which order to keep. Either the scenario's premise is
tightened (what !40 itself changes), or the line accepts a question that leads to the same decision. One play, so
by the rule on single misses no skill change follows from it alone.

**About the scenarios themselves:** d3's brief names no forge; d4's "mergeable" can be read as the forge's state
or the Driver's verdict; d5-a's player played both calls in one path.

## After the playing (2026-11-08)

Decided in Q27–Q29 and played: r7 both variants (player 120k, judge 51k) and r1 both variants (player 115k, judge
about 50k), all pass. Unclear places named on the way, for later:

- The scan judges "the Stages not known" (`worklist.md`) or "every Stage in scope" (`track-scan.md`): named again in
  r7 and r1.
- Filing's search for an in-place ticket or an Opener's Tool hits sibling tickets (Rector's) or the ticket the Opener
  came from (#14); the rule for dropping such hits lives only in `worklist.md`.
- No command for "the ten tickets closed last" or for reading comments; GitLab lists by update, not by close. On
  GitHub, a query for `Opener: <tool>` may read the colon as a qualifier.
- `track-scan.md`, *Tools on request*: "a ticket exists → requested" against the parser's exception for a ticket
  still waiting on the Opener's yes.
- The scan report has no form for a Role left unfilled by design.

**From the plays for ticket 08** (r8 137k, r3 109k, judge for both; all pass): a workable ticket keeps unfiled
Guardrails Stages from a scan, and nothing tells the human (r8 B); filing a whole chain at once, PHPStan Levels 7–10
blocked behind 6 in review, may be more than a human expects; whether a Tool closed by a rejection of what it requires
counts as rejected (r3); whether closing an injection is a change of behaviour has no rule (r3, as in r5).

**From the field test of the JavaScript Pack:** on a site whose `composer.json` serves the build alone, the `php` Pack
applies and its Safety Net (14 Stages) holds the ESLint Stages back; only a call naming Guardrails reached them.
Decided in Q46 and Q47: `php` still applies, and the wait stays; a known limitation says how to go sooner.

**From the plays of the JavaScript Pack and the deploy recipe** (r9 four times, r11 once; all pass; none forced a
wrong decision):

- The browser question has no recommended default, and nothing says whether the adoption waits for the answer or
  goes on with "current browsers"; the players went on.
- An answer given on the rollout's ticket reaches the adoption's plan only through the worklist's judging; the
  design point reads the selected ticket alone. No step says when the rollout's ticket is closed, nor with what
  reason ("not planned" reads as a rejection, "completed" as fulfilled).
- Whether `prefer-const` gets a `Not yet: 0` entry or none is open; partial ES2015 support (Internet Explorer 11 has
  `let` and `const`) is not counted anywhere.
- The Node.js version is read from a lock file the plan only proposes to write; where in the run Node.js is checked,
  and what a ticket's state is without it, is not said.
- `eslint.md` asks for a commit "before the changelog entry" that no reference asks for; whether Composer's
  `vendor/` is among the ignores, and which config extension to write, is left open.
- The rollout's *Applies when* lives in prose only; the parser's seed knows "applies" or `not_applicable`, not "not
  known, ask".
- `eslint-adoption`'s one search word "ESLint" also finds the two sibling tickets.
- CI Runner's MR scope does not say what the first job holds where no check applies yet.
- "Available on request: BC promise" is listed for a static site too.
- `track-scan.md` does not say outright that the Stages of a Pack that does not apply go unjudged.
- About the scenarios: "no ticket is open" against Housekeeping set up, which keeps one open (r9, r11); "every Stage
  has a closed ticket" read literally takes in the on-request ones (r9, r10); the fixtures have no tracker file, so
  players hand the parser a stand-in.

**Sorted on 2026-11-11** (Q50–Q54): the scan's judging of known Stages (Q50), filing's sibling hits (Q51) and the
closing of the rollout's ticket (Q52) are fixed; the scenarios' own slips get a PR of their own (Q53). Everything
else above, named once and forcing no wrong decision, is left as is (Q54) and becomes a ticket if it comes back.

**From the plays for tickets 11 and 12** (r7 127k, r8 129k, judge 70k; both pass): the trace's sentence was hard to
parse and its search did not say that a hit must match the Stage (fixed before merge). Named again, so tickets under
Q54: design step 1's route for a baseline ticket without a plan (ticket 13); whether reconcile's "In review" line is a
finding (ticket 14); a scan files whole chains at once, with the title of a rollout Stage before its adoption
(ticket 15). Named once and left as is: a single-part rule
creates no rollout file, "nothing typed by hand" beside a config change, CI for a new rollout file, the Status count
of a pull request the run did not touch.

**Probe p1 on 2026-11-12** (r7's situation, a call naming the target's planning skill, autonomous and interactive;
player 93k, judge 47k; pass): the run let the named skill plan in both modes, reading the call as the human's answer
to *Who plans*, against step 2's literal "plans by itself" and "a decision point, every time". Named once, left as is
(Q61). Also named once: a target skill's plan may lack the `Plan` line; who adds `Opener:` lines to it; step 5's choice
is skipped when the target's skill posts the plan; Track choice's five options against a question tool that takes four;
the Stage Name "PHP CS Fixer Rollout" against its ticket title; `selection.md`'s pick-up check worded for PHPStan's
baseline alone.

**From the plays for ticket 14** (r7 A 105k, d11 84k, judge for both; both pass). Named a second time, so candidates
for tickets under Q54: CI for a part that creates the first rollout file, against the one commit with nothing typed by
hand (r7 on 2026-11-11, r7 A now); a rollout ticket's title against its Stage Name and `planning-a-baseline-ticket.md`'s
paragraph keyed to "take in the remaining rules" (p1, r7 A). Named once: optional operations the brief leaves out;
`roave-bc-check` not applicable may read as BC guarded; whether a ticket in review that delivered a part counts for the
trace; #52 named twice, in reconcile and Track choice; selection lays out a decision point for one workable ticket; the
PHPStan level checks use while Level 6 is unmerged. d11: which round a human's request counts in; the Driver leaves a
ready merge request ready during the rework; the subagent prompt has no slot for the ticket; reply and push unordered;
the description after a rework; GitLab's unresolved threads; a run naming a ticket hides the blocked one from the
Driver's pause list; the review does not check the human's request was met.

**From the plays for ticket 13** (r7 A 114k, probe p1 B 91k, judge 55k; both pass). Named a second time, so
candidates for tickets under Q54: when a PHP CS Fixer part's earlier plan still stands, which only PHPStan's paragraph
says (r7 A, p1 B); selection lays out a decision point for one workable ticket with nothing to close (r7 A on
2026-11-12, p1 B); whether a merge request in review the run did not touch counts among what waits for the human (r8
on 2026-11-11, r7 A); a rule whose first part is its last creates no rollout file, said only by inference (r7 on
2026-11-11, r7 A). Filed: the plan that stands and the single-part rule on ticket 16, selection as 17, the Status count
as 18, and a fixture for r7 and r8 as 19. Already in tickets: CI and the cache entry for a rollout file (16); the
ticket's three names (15).
Named once: a target's skill the human picks for a baseline ticket loses the cut (decided so in Q60); when the suite
writes a changelog entry; selection's seed; the clean-tree check not a step of its own. About the scenarios: the
briefs leave the tracker file's operations unsaid, and no fixture matches r7, so the parser holds Guardrails back on
the stand-in.
