# 01: Split continuous-refactoring into refactor-loop + per-Track orchestrator skills

**What to build:** `continuous-refactoring/SKILL.md` currently carries both the Track-selection
algorithm (step 0b) and the entire generic pass pipeline (steps 1–6), plus an awkward step 0c that
skips steps 1–5 whenever Housekeeping is selected. Split this into: a thin `continuous-refactoring`
that only selects a Track and dispatches; a new track-agnostic `refactor-loop` skill that runs one
pass for whichever Track it's given; four thin per-Track skills that each name their Track and
delegate to `refactor-loop` (three of them) or own their existing standalone process (Housekeeping).
No user-visible behavior changes — `/continuous-refactoring`, with or without a Track name, still
works exactly as documented in README today.

**Status:** needs-triage

- [ ] New skill `refactor-loop`: runs one pass (today's steps 1–6 — scan, learn-early, prioritize,
      design, implement, learn-closing) for a Track given as a **mandatory** input. Aborts with a clear
      error instead of guessing when no valid Track is given — never infers or defaults one.
- [ ] `refactor-loop` does no Track-name branching itself — it passes the Track straight through to
      `refactor-scan`/`refactor-learn`, which already branch internally per Track today (unchanged).
- [ ] `refactor-loop` also owns the pass-describing sections currently inline in
      `continuous-refactoring/SKILL.md`: the "Opening a merge request" pointer, "Fallback", "Closing
      report", "Completion criterion".
- [ ] New skill `continuous-safety-net`: Track = Safety Net, delegates to `refactor-loop`.
- [ ] New skill `continuous-guardrails`: Track = Guardrails, delegates to `refactor-loop`.
- [ ] New skill `continuous-investigation`: Track = Investigation, delegates to `refactor-loop`.
- [ ] New skill `continuous-housekeeping`: owns Housekeeping's existing standalone process unchanged
      (does not use `refactor-loop` at all — it never did). Receives `housekeeping-track.md`,
      `housekeeping-cadence-interview.md`, `housekeeping-template-file-format.md`, moved out of
      `continuous-refactoring/references/` into its own `references/`.
- [ ] `continuous-refactoring/SKILL.md` shrinks to: the track-scheduler algorithm
      (`track-scheduler.md`, unchanged content, stays under `continuous-refactoring/references/`) plus
      dispatch to the selected Track's skill. No inline pass-pipeline description left, no Housekeeping
      step-skip special case.
- [ ] The six Track-independent reference files — `loop-config-interview.md`,
      `refactoring-bookkeeping.md`, `opening-a-merge-request.md`, `local-issue-tracker-template.md`,
      `forge-facing-writing.md`, `foundational-refactoring-rules.md` — stay under
      `continuous-refactoring/references/` unchanged. They predate the Track concept and aren't
      Track-selection logic; nothing about this split touches them.
- [ ] Only `continuous-refactoring` keeps `disable-model-invocation: true`. `refactor-loop` and the
      four `continuous-<track>` skills do **not** set it — mirrors how `refactor-scan`/`-prioritize`/
      `-design`/`-implement`/`-learn` already work today (invoked via the Skill tool from another
      skill's own prose, with no flag of their own). Setting the flag on a nested target breaks the
      call chain: verified against Claude Code's own docs and a reproduced GitHub issue — a
      `disable-model-invocation: true` skill invoked via the Skill tool (not literally typed first by
      the user this turn) is refused outright, not silently skipped.
- [ ] Residual auto-trigger risk from omitting the flag is mitigated, not eliminated: narrow,
      explicitly-internal `description:` fields on `refactor-loop` and the four `continuous-<track>`
      skills ("invoked by continuous-refactoring only, not a user entry point"); omitted from README's
      public skill table; fail-closed on missing/invalid required input.
- [ ] Direct invocation of a `continuous-<track>` skill — or `continuous-refactoring <trackname>` —
      is a full manual override: bypasses the Safety Net blockade and the one-time exception entirely,
      exactly like naming a Track already does today (`track-scheduler.md`'s Manual override section).
      No leaf skill ever reads another Track's state; each of the five new skills knows only its own
      Track, or none.
- [ ] Cross-references elsewhere in the suite naming `continuous-refactoring/SKILL.md` steps 1, 2, 5,
      or 6 get repointed to `refactor-loop`: `refactor-learn/SKILL.md`,
      `refactor-design/references/decision-gate.md`,
      `refactor-scan/references/track-open-processing.md`, `README.md`, `fixtures/README.md`, and the
      `fixtures/php/php-scheduler-*`/`php-track-open-hand-adopted` `expected/behavior.md` fixtures.
      References to steps 0b/0c stay pointing at `continuous-refactoring/SKILL.md` — those stay there.
      Historical ADRs (0050, 0051, 0053) and `.scratch/` ticket archives are **not** edited — this
      repo's convention treats them as an immutable record, amended by a new ADR, never rewritten.
- [ ] `CONTEXT.md` is unchanged. The Track vocabulary itself doesn't change, only the implementation's
      file organization — out of scope for the domain glossary.
- [ ] A new ADR amending ADR-0055 records this decision, including its "the scheduler lives in
      continuous-refactoring/SKILL.md, refactor-scan becomes Track-aware" framing and its
      Housekeeping-trigger-centralization framing, both superseded in part by this split.
- [ ] `skills-validation.yml`/`validate_skills.py` pass unchanged — every new `skills/*` folder gets a
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
