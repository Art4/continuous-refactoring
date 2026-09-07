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

## 1. Read the baseline and group

Read `phpstan-baseline.neon`'s `ignoreErrors` entries for level N. Group by **root cause** — same
`message` pattern (with the file-specific token if the message parameterizes one, e.g. `$db` vs.
`$site_name` are different groups even under the same identifier) and `identifier`, not by file: a
group commonly spans several files, and that's the point — one fix approach usually covers the whole
group at once (e.g. every `might not be defined` finding for the same global, however many files
reference it).

## 2. Resume already-open groups, rank the rest

For each group: an issue titled `PHPStan Level N: baseline shrink — <group>` (same `N`) already open
→ resume it (skip to *File it* below's "already open" path) unless the group is now empty (a prior MR
already cleared it) — close it instead, drop it from consideration.

More than one fresh (not-yet-filed) group remains → don't discard the rest, same as a structural
search. Rank them by ordinary judgment (largest, most tractable, whatever makes for the most sensible
next MR — same reasoning Rank mode already applies elsewhere) to decide which one is this pass's
recommendation; the others still get filed, just not pursued this pass.

## 3. Admission tier per group

Each group's Signal (`skills/refactor-prioritize/references/signals.md`) is usually **tooling
pressure** — these are static-analysis residuals by definition — unless the group's actual nature
clearly names a sharper factor (a group of null-dereference findings on security-sensitive input is
**security**, not just tooling pressure; ordinary judgment, not a fixed rule).

- **Priority** (Signal is security or blast radius of inaction) → file regardless of backlog size.
- **Capped** (everything else, tooling pressure included) → file only while headroom remains: fewer
  than 5 open `refactor:candidate` issues not labelled `refactor:priority` → file it; 5 already open →
  stop filing capped groups this pass, queue the rest for a future exploration.

Mirrors `refactor-scan` step 1's own two-counter cap (`skills/refactor-scan/SKILL.md`) and
`structural-candidate-search.md`'s identical admission rule — same shape on both Select-mode paths.

## File it

Title: `PHPStan Level N: baseline shrink — <short group description>` (e.g. `PHPStan Level 1:
baseline shrink — $db might not be defined`), label `refactor:candidate` — plus `refactor:priority`
too, for a priority-tier group. Body: the group's messages and affected files — this is the minimal
payload; the planned fix (`refactor-design`'s job afterward, `phpstan-baseline-shrink.md` step 3) is
added as a comment only on the one group this pass actually pursues, including which files remain for
a future pass if that group is larger than one MR covers.

Continue at `refactor-prioritize/SKILL.md` step 4 for the rest (dedupe check already done above;
`Pending candidates` names only the single recommended group — the others sit as ordinary open issues
for a future pass).
