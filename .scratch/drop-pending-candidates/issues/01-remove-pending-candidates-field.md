# 01: Remove the top-level `Pending candidates` field

**What to build:** Delete the bookkeeping document's top-level `Pending candidates` field from the
suite entirely — every read, every write, every mention — and with it the **Self-tracking** hand-off
marker, whose only job is to suppress that write. Record the decision in a new ADR (ADR-0064 and
ADR-0065 both say the field "stays for now"; this is the later change they deferred).

**Why:** The field has no remaining writer under today's rules, so it is pure reading cost in six
skills:

- Every proposable tooling-tree node belongs to a Track. Safety Net and Guardrails cover all of them,
  `structural-scan` is a gate handled through `## Investigation`'s own `Open`, and `git`,
  `onboarding-setup` and `is-php-project` are never proposed.
- A Track's scan designs nothing: it only fills `Open` (no issue, no design). The case the field is
  still documented for — "a tooling-tree node's first-ever proposal, before its Track's section
  exists" (`refactoring-bookkeeping.md`) — therefore never occurs.
- A Track node reaches `refactor-design` only through the `Open` walk, which always marks it
  self-tracking; `refactor-prioritize` excludes Track nodes from its pool.
- No fixture seeds a set value: every fixture `bookkeeping.md` carries `- none`.
- `Art4/legacy-todo`'s live bookkeeping issue (#273) carries `- none` too (checked 2026-10-03).

Two sentences still claim a wider scope ("on every tracker, native-label ones included" in
`refactor-prioritize/SKILL.md`'s Select mode, "for a gate-shaped one on every tracker" in
`refactor-loop/SKILL.md`). Both predate Investigation's own `Open` and contradict
`refactor-design/SKILL.md` and the bookkeeping table; they go with the field.

**Blocked by:** none.

**Priority:** low — internal simplification, no user-facing bug.

**Status:** done — PR #136

## Decisions (confirmed by the maintainer, 2026-10-03)

1. **Old bookkeeping documents are left alone.** A document that still carries the field is neither
   read for it nor rewritten to drop it — no migration, the same rule every other old-schema field
   already follows. The old-schema fixtures keep asserting exactly that.
2. **The Self-tracking marker goes too**, including its `CONTEXT.md` entry and the "marked
   self-tracking" wording in `track-open-processing.md`, `safety-net-write.md` and
   `guardrails-write.md`.
3. **The one residual path re-ranks instead of resuming.** An already-existing issue titled
   `Tooling tree: <Name>` (pre-filed by an older suite version, or created by hand) can reach
   `refactor-design` through `refactor-scan` step 3b without the marker; on a non-native tracker
   design would set the field today. Without the field, a pass interrupted between design and
   implement leaves that issue to be rediscovered by step 3b on the next pass and ranked again —
   what a native tracker already does. Nothing is lost: every non-native tracker uses the Local
   Markdown mechanics (onboarding's "something else" falls through to them), which step 3b can list.

## Scope

- **`refactor-scan`** — step 2 reads only the selected Track's `Open`; the field's read and its
  "always one entry" wording go. Steps 3, 3b, 4 and `## Output` lose their "pending candidate" references (the per-entry resume
  logic itself stays, for Investigation's `Open`). `track-open-processing.md`, `safety-net-track.md`.
- **`refactor-design`** — the three-way paragraph (native tracker / self-tracking / write the field)
  and the field's mention under the reported writes.
- **`refactor-learn`** — clearing the field on a fresh merge request and on a rejection; the
  precondition's and completion criterion's mentions; the "Never touches `Pending candidates`" and
  old-schema paragraphs in `safety-net-write.md`, `guardrails-write.md`, `investigation-write.md`.
- **`refactor-loop`, `refactor-prioritize`, `refactor-implement`** — the state description, step 1's
  pending-candidate routing, Select mode's stale sentence, `baseline-shrink-selection.md`, the
  self-assign note.
- **`continuous-refactoring/references`** — `refactoring-bookkeeping.md` (intro, structure example,
  field table, purpose paragraph, the Track sections' "Replaces the global…" lead-ins, rules,
  old-schema note), `issue-mode.md`, `onboarding-setup-interview.md`, `opening-a-merge-request.md`,
  `forge-facing-writing.md`.
- **Docs** — `CONTEXT.md` (**Bookkeeping**, **Self-tracking**), `docs/architecture.md`,
  `docs/known-limitations.md`; a new ADR; a `.changelog.d/` fragment.
- **Tests and fixtures** — drop the `- none` line from the current-schema fixture `bookkeeping.md`
  files and the matching `expected/behavior.md` lines; keep it in the old-schema fixtures and their
  `fixtures/harness/run.sh` checks; `fixtures/README.md`, `fixtures/harness/rubric.md`,
  `scripts/test_tooling_tree.py`.

## Acceptance

- `grep -rn "Pending candidates"` over `skills/`, `CONTEXT.md`, `README.md` and `docs/` (outside
  `docs/adr/`) finds only the old-schema note saying the field is ignored.
- `grep -rni "self-tracking"` over the same paths finds nothing.
- `python3 -m unittest discover -s scripts -p 'test_*.py'`, `python3 scripts/validate_skills.py .`
  and the relevant `fixtures/harness/run.sh` tier pass.

## Comments

> **2026-10-03:** Filed from an analysis of whether the field can go, prompted by the note left
> during the bookkeeping-in-issues design discussion (2026-09-26). The analysis read every read and
> write site in the six loop skills, the Track references, ADR-0029/0060/0064/0065 and the fixtures.
> No grilling session: the three decisions above were the only open points and were confirmed as
> recommended.

> **2026-10-03 (implement):** Landed on the same branch (PR #136), ADR-0069. Two points turned out
> differently from the scope as first filed. (1) The git-only "stop the pass, this is the only
> record" branch in `refactor-scan` step 2 stays, reworded: it also covers a flagged
> `## Investigation` `Open` entry, which still needs it. (2) `refactor-learn/SKILL.md` still said a
> freshly opened merge request clears Investigation's `Open` entry, contradicting
> `investigation-write.md` and ADR-0068 (the entry leaves only on merge or rejection); the lines had
> to be rewritten anyway and now follow the reference. The same file's "clear it to
> `- none`" wording for a merged or rejected Investigation candidate, which predates the multi-entry
> `Open`, was fixed in the same PR afterwards (remove exactly that entry). Old-schema fixtures, their harness checks and
> `OldSchemaPassThroughTests` keep the field on purpose; 30 current-schema fixture documents lost
> their `- none` line. 235 unit tests, `validate_skills.py` (same 12 advisories as `main`) and
> harness `tier2 php-project-with-candidates` pass; the agent-judged Track tiers (`--opencode`,
> local-only, advisory) were not run.
