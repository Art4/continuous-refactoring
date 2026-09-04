# Picking a PHPStan baseline-shrink candidate

`refactor-design` step 1's own case for the **"PHPStan Level N — baseline shrink"** candidate
`refactor-scan` step 4b proposes generically (see that step: the signal is "level N fulfilled, its
baseline non-empty," nothing more specific yet — same shape as `structural-scan` itself, refined here
into one concrete candidate). Run this before step 5.

## Why this exists

`phpstan.md`'s own Stop conditions for the level chain: *"Baseline is non-empty → do not propose the
next level; the loop proposes shrinking work... until the baseline becomes empty."* Nothing shrinks
the baseline on its own — this is that shrinking work, made concrete.

## 1. Resume an already-open group first

Check open `refactor:candidate` issues titled `PHPStan Level N: baseline shrink — <group>` (same
`N` as the proposal). One already open → read `phpstan-baseline.neon` fresh: does that group (see
*Grouping* below — same message/identifier, ignoring path/line/count) still have entries? Yes → resume
that issue, skip straight to step 5's "already open, don't refile" path. No (a prior MR already
cleared it) → close it, then continue below as if none were open.

## 2. Read the baseline and group

Read `phpstan-baseline.neon`'s `ignoreErrors` entries for level N. Group by **root cause** — same
`message` pattern (with the file-specific token if the message parameterizes one, e.g. `$db` vs.
`$site_name` are different groups even under the same identifier) and `identifier`, not by file: a
group commonly spans several files, and that's the point — one fix approach usually covers the whole
group at once (e.g. every `might not be defined` finding for the same global, however many files
reference it).

More than one group exists → pick one by ordinary judgment (no fixed priority rule — largest, most
tractable, whatever makes for the most sensible next MR is fine, same reasoning `refactor-prioritize`
already applies elsewhere). One selection, one candidate, same as a structural pick.

## 3. Plan the fix

Read every file the chosen group touches. Design a fix that removes the finding without changing
behavior — same "provably behavior-preserving" bar any other mechanical fix on this tree holds to.
Reducing the group is enough; it doesn't have to empty in one MR (`phpstan.neon`'s own "strictly
reduce" wording already allows this for a level-bump MR — the same principle applies here, one level
earlier in the chain). Note in the plan which files this pass's MR will actually touch if the group is
large enough that not all of it fits comfortably in one bounded MR.

## 4. File it

Title: `PHPStan Level N: baseline shrink — <short group description>` (e.g. `PHPStan Level 1:
baseline shrink — $db might not be defined`), label `refactor:candidate`. Body: the group's messages
and affected files, the planned fix for this MR's slice of it, and — group larger than this MR covers
— which files remain for a future pass. Continue at `refactor-design/SKILL.md` step 5 for the rest
(dedupe check already done above; `Pending candidates` handling is the same as any other candidate,
no special case here).
