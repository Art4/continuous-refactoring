# 01: Split continuous-refactoring into refactor-loop + per-Track orchestrator skills

**What to build:** `continuous-refactoring/SKILL.md` currently carries both the Track-selection
algorithm (step 0b) and the entire generic pass pipeline (steps 1–6), plus an awkward step 0c that
skips steps 1–5 whenever Housekeeping is selected. Split this into: a thin `continuous-refactoring`
that only selects a Track and dispatches; a new track-agnostic `refactor-loop` skill that runs one
pass for whichever Track it's given; four thin per-Track skills that each name their Track and
delegate to `refactor-loop` (three of them) or own their existing standalone process (Housekeeping).
No user-visible behavior changes — `/continuous-refactoring`, with or without a Track name, still
works exactly as documented in README today.

**Status:** ready-for-agent

- [x] New skill `refactor-loop`: runs one pass (today's steps 1–6 — scan, learn-early, prioritize,
      design, implement, learn-closing) for a Track given as a **mandatory** input. Aborts with a clear
      error instead of guessing when no valid Track is given — never infers or defaults one.
- [x] `refactor-loop` does no Track-name branching itself — it passes the Track straight through to
      `refactor-scan`/`refactor-learn`, which already branch internally per Track today (unchanged).
- [x] `refactor-loop` also owns the pass-describing sections currently inline in
      `continuous-refactoring/SKILL.md`: the "Opening a merge request" pointer, "Fallback", "Closing
      report", "Completion criterion".
- [x] New skill `continuous-safety-net`: Track = Safety Net, delegates to `refactor-loop`.
- [x] New skill `continuous-guardrails`: Track = Guardrails, delegates to `refactor-loop`.
- [x] New skill `continuous-investigation`: Track = Investigation, delegates to `refactor-loop`.
- [x] New skill `continuous-housekeeping`: owns Housekeeping's existing standalone process unchanged
      (does not use `refactor-loop` at all — it never did). Receives `housekeeping-track.md`,
      `housekeeping-cadence-interview.md`, `housekeeping-template-file-format.md`, moved out of
      `continuous-refactoring/references/` into its own `references/`.
- [x] `continuous-refactoring/SKILL.md` shrinks to: the track-scheduler algorithm
      (`track-scheduler.md`, unchanged content, stays under `continuous-refactoring/references/`) plus
      dispatch to the selected Track's skill. No inline pass-pipeline description left, no Housekeeping
      step-skip special case.
- [x] The six Track-independent reference files — `loop-config-interview.md`,
      `refactoring-bookkeeping.md`, `opening-a-merge-request.md`, `local-issue-tracker-template.md`,
      `forge-facing-writing.md`, `foundational-refactoring-rules.md` — stay under
      `continuous-refactoring/references/` unchanged. They predate the Track concept and aren't
      Track-selection logic; nothing about this split touches them.
- [x] Only `continuous-refactoring` keeps `disable-model-invocation: true`. `refactor-loop` and the
      four `continuous-<track>` skills do **not** set it — mirrors how `refactor-scan`/`-prioritize`/
      `-design`/`-implement`/`-learn` already work today (invoked via the Skill tool from another
      skill's own prose, with no flag of their own). Setting the flag on a nested target breaks the
      call chain: verified against Claude Code's own docs and a reproduced GitHub issue — a
      `disable-model-invocation: true` skill invoked via the Skill tool (not literally typed first by
      the user this turn) is refused outright, not silently skipped.
- [x] Residual auto-trigger risk from omitting the flag is mitigated, not eliminated: narrow,
      explicitly-internal `description:` fields on `refactor-loop` and the four `continuous-<track>`
      skills ("invoked by continuous-refactoring only, not a user entry point"); omitted from README's
      public skill table; fail-closed on missing/invalid required input.
- [x] Direct invocation of a `continuous-<track>` skill — or `continuous-refactoring <trackname>` —
      is a full manual override: bypasses the Safety Net blockade and the one-time exception entirely,
      exactly like naming a Track already does today (`track-scheduler.md`'s Manual override section).
      No leaf skill ever reads another Track's state; each of the five new skills knows only its own
      Track, or none.
- [x] Cross-references elsewhere in the suite naming `continuous-refactoring/SKILL.md` steps 1, 2, 5,
      or 6 get repointed to `refactor-loop`: `refactor-learn/SKILL.md`,
      `refactor-design/references/decision-gate.md`,
      `refactor-scan/references/track-open-processing.md`, `README.md`, `fixtures/README.md`, and the
      `fixtures/php/php-scheduler-*`/`php-track-open-hand-adopted` `expected/behavior.md` fixtures.
      References to steps 0b/0c stay pointing at `continuous-refactoring/SKILL.md` — those stay there.
      Historical ADRs (0050, 0051, 0053) and `.scratch/` ticket archives are **not** edited — this
      repo's convention treats them as an immutable record, amended by a new ADR, never rewritten.
- [x] `CONTEXT.md` is unchanged. The Track vocabulary itself doesn't change, only the implementation's
      file organization — out of scope for the domain glossary.
- [x] A new ADR amending ADR-0055 records this decision, including its "the scheduler lives in
      continuous-refactoring/SKILL.md, refactor-scan becomes Track-aware" framing and its
      Housekeeping-trigger-centralization framing, both superseded in part by this split. —
      [ADR-0057](../../../docs/adr/0057-refactor-loop-and-per-track-skills.md)
- [x] `skills-validation.yml`/`validate_skills.py` pass unchanged — every new `skills/*` folder gets a
      valid `SKILL.md` (frontmatter, `## Completion criterion`) per existing convention; nothing here
      needs a registry update, the validator scans `skills/**` generically.

## Comments

Distilled from a `/grill-with-docs` session (grilling + domain-modeling) settling nine open questions:
skill naming (`continuous-safety-net`, hyphenated; `refactor-loop` for the shared pass, not nested
under `refactor-scan`/`refactor-learn`), full manual-override semantics with zero cross-Track
knowledge in any leaf skill, doing the full split in one pass rather than staging it, moving
Housekeeping's own reference files into its own skill, keeping the six Track-independent reference
files where they are, and — after independently verifying against Claude Code's docs and a live
GitHub issue — dropping `disable-model-invocation` from every skill except `continuous-refactoring`
itself, since setting it on a nested target breaks skill-to-skill chaining outright.

---

**Spec** (via `/to-spec`):

## Problem Statement

`continuous-refactoring/SKILL.md` currently conflates two unrelated jobs: deciding *which* Track
this pass spends itself on, and running the *entire* generic pass (scan → prioritize → design →
implement → learn) for whichever Track won. A third thing is wedged in alongside them: Housekeeping,
whose own process isn't the generic pass at all, forcing an awkward step ("if Housekeeping was
selected, skip steps 1–5 entirely") into the same file. The result is a single skill that's hard to
read on its own terms, and that leaks Track-conditional branching into a file whose only real job
should be scheduling.

## Solution

Split `continuous-refactoring` into a thin dispatcher that only selects a Track and hands off, a new
track-agnostic `refactor-loop` skill that runs exactly one pass for whichever Track it's given, and
four thin per-Track skills (`continuous-safety-net`, `continuous-guardrails`,
`continuous-investigation`, `continuous-housekeeping`) that each name their own Track — three
delegate to `refactor-loop`, Housekeeping keeps its own already-distinct process. No user-visible
behavior changes: `/continuous-refactoring`, bare or with a Track name, works exactly as documented
in README today.

## User Stories

1. As a human operator, I want `/continuous-refactoring` to behave exactly as it does today (with or
   without a Track name), so that adopting this refactor requires no change to my own workflow.
2. As a human operator, I want to name a Track directly and have it behave as a full manual override,
   so that I can force a specific Track's work regardless of the scheduler's own staleness
   computation.
3. As a maintainer reading the suite, I want `continuous-refactoring/SKILL.md` to contain only
   Track-selection logic, so that I don't have to read pass-pipeline steps and a Housekeeping-only
   skip branch to understand what "select a Track" means.
4. As a maintainer, I want the generic pass description (scan → learn → prioritize → design →
   implement → learn) to live in exactly one file, so that Safety Net, Guardrails, and Investigation
   don't each duplicate it.
5. As a maintainer, I want `refactor-loop` to be visibly track-agnostic (it never branches by Track
   name itself), so that adding a fifth Track in future doesn't require touching `refactor-loop` at
   all.
6. As `refactor-loop`, I want a mandatory Track input, so that I abort clearly instead of guessing a
   Track when invoked incorrectly.
7. As a maintainer, I want each Track's own detection/judging/writing logic to stay exactly where it
   already lives (`refactor-scan`'s and `refactor-learn`'s own per-Track reference files), so that
   this split doesn't force a rewrite of logic that already works.
8. As `continuous-safety-net`, I want to know only my own Track and nothing about any other Track's
   state, so that no cross-Track coupling creeps back into a "thin" skill.
9. As `continuous-guardrails`, I want the same isolation, so that invoking me directly never silently
   reads Safety Net's blockade state.
10. As `continuous-investigation`, likewise.
11. As `continuous-housekeeping`, I want to keep my own already-distinct process untouched, only
    relocated into my own skill folder, so that Housekeeping's mechanism (unchanged since the
    now-retired standalone skill) isn't disturbed by this refactor.
12. As a maintainer, I want Housekeeping's own reference files to live under
    `continuous-housekeeping/references/` instead of `continuous-refactoring/references/`, so that
    `continuous-refactoring` no longer hosts content it doesn't itself use.
13. As a maintainer, I want the six genuinely suite-wide reference files to stay exactly where they
    are, so that files with no Track-selection relevance aren't needlessly moved.
14. As a maintainer, I want only `continuous-refactoring` to carry `disable-model-invocation: true`,
    so that Claude never spontaneously starts a whole refactoring loop pass unprompted, while still
    allowing `continuous-refactoring`'s own prose to successfully chain into the Track skills via the
    Skill tool.
15. As Claude (the agent following these skills), I want `refactor-loop` and the four
    `continuous-<track>` skills to carry no `disable-model-invocation` flag, so that a Skill-tool call
    chained from `continuous-refactoring`'s own instructions actually succeeds instead of being
    refused.
16. As a maintainer, I want those five skills' descriptions to read as clearly internal, so that
    Claude's own model-driven skill-matching is unlikely to pick them for an unrelated task even
    without a hard technical block.
17. As a human browsing README, I want only `continuous-refactoring` listed as the public entry
    point, so that I'm not confused about which of five new skill names I'm supposed to type.
18. As a power user, I want `/continuous-safety-net` to still work if I type it directly, identically
    to `/continuous-refactoring safety-net`, so that there's no artificial technical barrier, only a
    documentation one.
19. As CI (`skills-validation.yml` / `validate_skills.py`), I want every new skill folder to carry a
    syntactically valid `SKILL.md`, so that Tier 1 structural validation passes without the validator
    script itself needing changes.
20. As a maintainer, I want `refactor-loop` to use a `## Process` heading, not `## The pass`, so that
    the validator's existing orchestrator-only special case doesn't need extending for a second
    skill.
21. As a maintainer reading old ADRs (0050, 0051, 0053) or archived `.scratch/` tickets, I want their
    citations of `continuous-refactoring/SKILL.md` step numbers left untouched, so that the historical
    record stays an accurate snapshot of what was true when written.
22. As a maintainer reading currently-live docs, I want every citation of
    `continuous-refactoring/SKILL.md` steps 1, 2, 5, or 6 repointed to `refactor-loop`, so that the
    suite's own live cross-references stay accurate.
23. As a maintainer, I want citations of steps 0b/0c to keep pointing at
    `continuous-refactoring/SKILL.md`, so that the scheduler's own step numbering isn't disturbed by
    this split.
24. As the test harness, I want the scheduler fixtures' step citations updated to match the new file
    layout, so that they keep serving as an accurate regression check that Track-selection behavior
    is unchanged.
25. As a maintainer, I want `CONTEXT.md` left untouched, so that the Track glossary entries don't
    drift into naming skill files.
26. As a maintainer, I want a new ADR amending ADR-0055, so that a future reader understands why
    `continuous-refactoring` shrank, why `refactor-loop` exists as a separate skill rather than living
    inside `refactor-scan` or `refactor-learn`, and why four Track skills exist even though three have
    almost no unique content.
27. As any skill invoked with missing required input, I want to abort clearly rather than guess or
    default, so that a broken call chain fails loudly instead of silently doing the wrong thing.

## Implementation Decisions

- New skill `refactor-loop` houses today's `continuous-refactoring/SKILL.md` steps 1–6 (scan,
  learn-early, prioritize, design, implement, learn-closing) plus the "Opening a merge request"
  pointer, Fallback, Closing report, and Completion criterion sections. Takes a mandatory Track input;
  does no Track-name branching of its own — passes the Track straight to `refactor-scan`/
  `refactor-learn`, unchanged internally. Uses a `## Process` heading, not `## The pass`.
- `continuous-refactoring/SKILL.md` shrinks to the Track-selection algorithm (`track-scheduler.md`,
  content unchanged, stays under its `references/`) plus a dispatch step naming the winning Track's
  skill. Retains `disable-model-invocation: true` — the only skill in this set that does.
- Four new skills: `continuous-safety-net`, `continuous-guardrails`, `continuous-investigation` each
  hard-name their own Track and delegate unconditionally to `refactor-loop`. `continuous-housekeeping`
  owns Housekeeping's existing standalone process (reconcile/checklist/quality-gate/deliver, mechanism
  unchanged), never calls `refactor-loop`. None of the four sets `disable-model-invocation`.
- Housekeeping's three reference files move from `continuous-refactoring/references/` to
  `continuous-housekeeping/references/`: `housekeeping-track.md`, `housekeeping-cadence-interview.md`,
  `housekeeping-template-file-format.md`. Every cross-reference to them (in `refactor-scan`'s
  php-tooling-tree node docs, `refactor-learn/SKILL.md`, `refactor-learn/references/
  housekeeping-write.md`) gets repointed to the new path.
- Six files stay under `continuous-refactoring/references/` unchanged: `loop-config-interview.md`,
  `refactoring-bookkeeping.md`, `opening-a-merge-request.md`, `local-issue-tracker-template.md`,
  `forge-facing-writing.md`, `foundational-refactoring-rules.md`, plus `track-scheduler.md` itself.
- Direct invocation of any `continuous-<track>` skill (or naming a Track via
  `continuous-refactoring <trackname>`) is a full manual override — bypasses the Safety Net blockade
  and the one-time bootstrap exception entirely, matching `track-scheduler.md`'s existing Manual
  override semantics. No leaf skill, `refactor-loop` included, ever reads another Track's bookkeeping
  state.
- Mitigating the loss of a hard invocation gate (verified against Claude Code's own docs plus a
  reproduced GitHub issue: a `disable-model-invocation: true` skill invoked via the Skill tool, rather
  than literally typed first by the user this turn, is refused outright, not silently skipped): each
  new skill's `description:` states plainly it's invoked by `continuous-refactoring` only; README's
  skill table lists only `continuous-refactoring`; `refactor-loop` fails closed on missing or invalid
  required input rather than guessing.
- Cross-reference migration: every live citation of `continuous-refactoring/SKILL.md` step 1, 2, 5, or
  6 is repointed to `refactor-loop` (`refactor-learn/SKILL.md`, `refactor-design/references/
  decision-gate.md`, `refactor-scan/references/track-open-processing.md`, `README.md`,
  `fixtures/README.md`, the `php-scheduler-*`/`php-track-open-hand-adopted` fixture
  `expected/behavior.md` files). Citations of steps 0b/0c stay pointing at
  `continuous-refactoring/SKILL.md`. Historical ADRs (0050, 0051, 0053) and archived `.scratch/`
  tickets are never edited, per this repo's existing convention of treating them as an immutable
  record.
- `CONTEXT.md` unchanged — no domain-vocabulary change, purely an implementation reorganization.
- A new ADR amends ADR-0055: the scheduler now lives in a slimmer `continuous-refactoring/SKILL.md`
  unchanged in substance; the pass pipeline moved into its own `refactor-loop` skill rather than
  nesting under any single lifecycle skill; Housekeeping regains a dedicated skill identity (echoing
  the pre-ADR-0055 standalone `continuous-housekeeping`) while its trigger stays centrally scheduled;
  and the `disable-model-invocation` placement decision, with rationale.

## Testing Decisions

- Primary, automated seam: `scripts/validate_skills.py` Tier 1, already wired into CI via
  `.github/workflows/skills-validation.yml`. Every new `skills/*/SKILL.md` must satisfy its structural
  checks (frontmatter incl. `name` matching the directory, `description`, `## Completion criterion`,
  `## Process` on `refactor-loop` and the four Track skills — none of them is "the orchestrator," so
  none uses `## The pass`), and every relocated reference file must resolve from its new location
  with no orphaned references left behind under `continuous-refactoring/references/`.
- `docs/agents/skill-references.md` is unaffected — confirmed it tracks only references to skills
  *outside* the suite; none of the new skills add one.
- Regression seam: the existing `fixtures/php/php-scheduler-*` and `php-track-open-hand-adopted`
  behavior fixtures. The scheduler algorithm itself (`track-scheduler.md`) is untouched, so
  Track-selection outcomes in these fixtures shouldn't change — only their literal citations of
  `continuous-refactoring/SKILL.md` steps 1/2/5/6 need updating to `refactor-loop`, which doubles as a
  review checklist for "did every cross-reference actually get repointed."
- No new fixture or test mechanism is introduced — this is a documentation/skill-file reorganization
  with a behavior-preservation goal, so the bar is "existing tests keep passing, updated only where
  they cite a path/step that moved," not new coverage.

## Out of Scope

- Any change to Track-selection semantics itself (staleness ratio, one-time exception, Safety Net
  blockade, Housekeeping preemption) — `track-scheduler.md`'s algorithm is carried over unchanged.
- Any change to a Track's own detection/judgment/writing logic inside `refactor-scan`/`refactor-learn`
  — untouched, only the identity of their caller changes.
- Hardening the existing five lifecycle skills with explicit "abort on missing required input"
  documentation — raised during grilling as a good general principle, but out of scope here; a
  separate ticket if wanted.
- A technical (as opposed to documentation-only) barrier against directly invoking a
  `continuous-<track>` skill — no such mechanism currently exists in Claude Code without breaking the
  internal dispatch chain; direct invocation is accepted as functionally equivalent to naming the
  Track via `continuous-refactoring`.
- Changes to `docs/agents/skill-references.md`'s ledger — confirmed not applicable, no new
  external-skill references are introduced.
- Any change to README's description of user-facing behavior beyond reflecting that only
  `continuous-refactoring` is documented as an entry point.

## Further Notes

- Distilled from a full `/grill-with-docs` session (grilling + domain-modeling), covering nine
  numbered decision points plus a live-verified correction about `disable-model-invocation`'s actual
  scope (confirmed against Claude Code's own docs and a reproduced GitHub issue, not assumed).
- This is a behavior-preserving refactor from the human operator's perspective — all observable
  change is in the suite's own file organization.
- Recommended sequencing even though this spec covers the full end state in one ticket: land the new
  skill files and the cross-reference migration together (they're interdependent — `validate_skills.py`
  would flag orphaned references if done partially), then land the ADR in the same or an immediately
  following change.
