# 1 — Audience-aware forge-facing text

**What to build:** A new shared reference,
`skills/continuous-refactoring/references/forge-facing-writing.md`, stating one rule for any text a
lifecycle skill posts onto the *target* repo's own forge — an issue comment, a closing note, a
human-readable `out-of-scope/<node>.md` entry, an MR/PR description or body. The reader has never
seen this suite's own repo and can't open its files. Two related leak patterns, one shared cause:

- **Internal file citations.** Don't cite this suite's own file paths (`skills/…`, `docs/adr/…` of
  *this* repo) as the reason for something — state the rule or finding itself, in plain words, instead
  of pointing at where it's written down. Triggered by
  [legacy-todo#250](https://github.com/Art4/legacy-todo/issues/250): a closing comment cited
  `skills/refactor-design/references/decision-gate.md` and
  `skills/continuous-refactoring/references/foundational-refactoring-rules.md` by path — meaningless
  in a repo that doesn't contain those files.
- **Internal jargon.** Don't use this suite's own controlled-vocabulary labels (`CONTEXT.md` terms
  scoped to this suite's bookkeeping — candidate, finding, tooling-tree node, gate, flagged candidate,
  pending candidate, resume-candidate, fulfilled node, and the like) as if the reader already knows
  them — describe the actual thing in plain terms instead. Doesn't apply to genuine external facts
  (a real tool/feature name such as "PHPStan Level 0", a target-repo file/line, the actual behavior
  found) — those stay exactly as concrete as they already are.

Both patterns share one self-check, stated positively rather than as a denylist: *read the draft back
as that stranger would, and say the substance in your own words rather than pointing at or borrowing
this suite's own vocabulary for it.* Not a ban on saying things — everything relevant still gets said;
only the suite-internal citation/label gets redirected into plain language.

Wire a pointer to this new reference from every site that instructs writing forge-facing text:

- `skills/refactor-learn/SKILL.md` — both rejection-writing spots (early-call "file a learned
  rejection under `out-of-scope/`", closing-call breaking-change bullet).
- `skills/refactor-design/references/decision-gate.md` — the flagged-candidate issue-comment
  instruction.
- `skills/continuous-refactoring/references/opening-a-merge-request.md` — MR/PR description content.
- `skills/refactor-learn/references/never-delete-without-record.md` — the abandonment closing note
  ("stating what was abandoned and why").

**Why:** The suite's own skill files necessarily talk to the *acting agent* via internal path
citations and controlled vocabulary — that's how one skill step points an agent at another. Without an
explicit audience switch, an agent drafting forge-facing prose echoes that same citation style
straight into text a stranger to this suite has to read, exactly as happened in legacy-todo#250. The
fix is a redirect, not a restriction — say everything relevant, just say it in words the actual reader
can use.

**Blocked by:** none.

**Priority:** low.

**Status:** ready-for-agent

Settled without a full `/grilling` session (narrow scope, no deep decision tree) — the user confirmed
each default below by not overriding it, except jargon leakage, which was explicitly added to scope:

- [x] **Scope widened to jargon, not just file paths.** User: "Bitte auch Jargon-Leckage fixen, wenn
  möglich" — the same audience principle covers both; one shared reference document, not two.
- [x] **Positive redirect, not a denylist.** Matches the user's own framing: "ich will ihnen nicht
  verbieten, Dinge zu sagen, sondern ich will sie dazu bringen, nur bestimmte relevante Dinge zu
  sagen." The instruction names the audience and asks for a self-check, not a list of forbidden
  strings.
- [x] **No automated enforcement.** `validate_skills.py` lints this suite's own skill prose, not text
  posted at runtime to a target repo's forge — there's no code-level check to add here; the guidance is
  necessarily prose, read and applied by the acting agent before it posts.
- [x] **The already-posted legacy-todo#250 comment is not retroactively edited.** One-off remnant from
  before this fix existed, not part of the suite's own state.
- [x] **Real external facts stay untouched.** A tooling-tree node's own Name, a target-repo file/line,
  the actual finding/behavior — none of that is "internal"; only this suite's own path structure and
  bookkeeping vocabulary are in scope.

**Parked, not part of this ticket:** none new; the earlier
`refactor-learn`-as-"bookkeeping" naming question stays parked from ticket 01 in
`design-decision-gate`, unrelated to this one.

## Comments

> **2026-09-13:** Filed after a short back-and-forth (German) triggered by
> [legacy-todo#250](https://github.com/Art4/legacy-todo/issues/250)'s closing comment citing this
> suite's own internal file paths. User asked whether a full `/grilling` session was needed;
> judged no — the design has one real idea (audience-aware redirect) and no deep branching, so this
> ticket states the plan directly with defaults the user can still override, rather than running a
> multi-round grilling tree. User expanded scope once, from file-citations only to also covering
> suite-internal jargon leakage, before confirming.

> **2026-09-13 (implement):** Added `skills/continuous-refactoring/references/forge-facing-writing.md`
> and wired a pointer from all four sites named above. Validator initially flagged the new file's own
> `skills/…`/`docs/adr/…` illustrations as broken local references (it treats backtick-wrapped paths as
> real); reworded to prose ("a path under this repo's own skill or ADR directories") to fix. 313/313
> tests green, validator clean (pre-existing size/duplication advisories only, none from this change).
> Changelog fragment filed (`83-audience-aware-forge-text.md`). Ready for review.
