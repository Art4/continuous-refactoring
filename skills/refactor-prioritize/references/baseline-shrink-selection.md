# Selecting a PHPStan baseline-shrink candidate

`refactor-prioritize`'s own Select mode, run only when Rank mode recommended a **"PHPStan Level N —
baseline shrink"** proposal (`refactor-scan` step 4b) — a gate named generically ("level N fulfilled,
its baseline non-empty"), not yet a concrete candidate. This is a fresh dispatch, separate from Rank
mode's own (see `refactor-prioritize/SKILL.md` step 4). Planning the actual fix
(`skills/refactor-design/references/phpstan-baseline-shrink.md`, that file's own step 3) is
`refactor-design`'s job afterward — not run here.

## Why this exists

`phpstan.md`'s own Stop conditions for the level chain: *"Baseline is non-empty → do not propose the
next level; the loop proposes shrinking work... until the baseline becomes empty."* Nothing shrinks
the baseline on its own — this is that shrinking work, made concrete.

## 1. Resume an already-open group first

Check open `refactor:candidate` issues titled `PHPStan Level N: baseline shrink — <group>` (same
`N` as the proposal). One already open → read `phpstan-baseline.neon` fresh: does that group (see
*Grouping* below — same message/identifier, ignoring path/line/count) still have entries? Yes → resume
that issue, skip straight to "File it" below's "already open, don't refile" path. No (a prior MR already
cleared it) → close it, then continue below as if none were open.

## 2. Read the baseline and group

Read `phpstan-baseline.neon`'s `ignoreErrors` entries for level N. Group by **root cause** — same
`message` pattern (with the file-specific token if the message parameterizes one, e.g. `$db` vs.
`$site_name` are different groups even under the same identifier) and `identifier`, not by file: a
group commonly spans several files, and that's the point — one fix approach usually covers the whole
group at once (e.g. every `might not be defined` finding for the same global, however many files
reference it).

More than one group exists → pick one by ordinary judgment (no fixed priority rule — largest, most
tractable, whatever makes for the most sensible next MR is fine, same reasoning Rank mode already
applies elsewhere). One selection, one candidate, same as a structural pick.

## File it

Title: `PHPStan Level N: baseline shrink — <short group description>` (e.g. `PHPStan Level 1:
baseline shrink — $db might not be defined`), label `refactor:candidate`. Body: the group's messages
and affected files — this is the minimal payload; the planned fix (`refactor-design`'s job
afterward, `phpstan-baseline-shrink.md` step 3) is added as a comment on this same issue, including
which files remain for a future pass if the group is larger than one MR covers.

Continue at `refactor-prioritize/SKILL.md` step 4 for the rest (dedupe check already done above;
`Pending candidates` handling is the same as any other candidate, no special case here).
