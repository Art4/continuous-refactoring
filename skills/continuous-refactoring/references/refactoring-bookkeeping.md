# Reference: `bookkeeping.md`, in the target repo's Refactoring Notes

The config file the suite reads and writes. It doesn't exist on a fresh target repo: `refactor-scan` proposes it (the `loop-config` node, `skills/refactor-scan/references/tooling-tree.md`), `refactor-design` runs a human interview instead of copying the tree doc's generic spec (`skills/continuous-refactoring/references/loop-config-interview.md`) and files the recorded decisions as a single `refactor:candidate` issue, and `refactor-implement` creates the file when that candidate is implemented — the same path any other tooling-tree node takes.

## Where the Refactoring Notes live

The **Refactoring Notes** are the target repo's own folder holding the loop's state — `bookkeeping.md` (this file), `merge-requests.md`, `out-of-scope/`. Default `docs/refactoring/`; overridable per target, decided once during `loop-config`'s own interview (`skills/continuous-refactoring/references/loop-config-interview.md`, Q3) and recorded, by that name, in the target's `AGENTS.md`/`CLAUDE.md`.

**Resolution rule**, followed independently by every lifecycle skill (and by the deterministic parser, `skills/refactor-scan/references/tooling_tree.py`) wherever it needs the Refactoring Notes, the same way the suite already resolves "does the tracker support native labels" from `docs/agents/issue-tracker.md` — not a value threaded through the orchestrator's carried-data chain: read the target's `AGENTS.md`, and if that doesn't exist or doesn't name one, `CLAUDE.md` — whichever names a line matching `` Refactoring Notes: `<path>` `` (path backtick-quoted, trailing slash optional) wins. Neither names one → the Refactoring Notes default to `docs/refactoring/`.

Every other skill in this suite refers to this folder by name — "the Refactoring Notes" — never by restating or assuming the concrete path; this section is the one place the resolution rule itself is defined.

## Structure

```markdown
# Refactoring Loop Config

**Create-mode:** autonomous

**Focus areas:** order intake, billing

**Refactoring goal:** convert legacy procedural code to OOP

**Secret history scan:** done (2026-09-12)

**Pending candidates:**
- none

## Safety Net

**Cadence:** 90

**Last scan:** 2026-09-14

**Open:**
- php-cs-fixer (#82)

**Out-of-scope:**
- phpmd — out-of-scope/phpmd.md

## Guardrails

**Cadence:** 60

**Last scan:** 2026-09-01

**Open:**
- composer-audit (#90)

**Out-of-scope:**
- none

## Housekeeping

**Cadence:** 7

**Last scan:** 2026-09-15

## Investigation

**Cadence:** continuous

**Last scan:** 2026-09-10

**Fulfilled nodes:**
- loop-config
- composer (#77)
- ci-runner (#78)
```

`Fulfilled nodes` sorts last, not alphabetically or by write-frequency — it's the field most likely to grow long as the tree gets worked through, and the only-ever-growing one; keeping it below every other top-level field means `Create-mode`, `Focus areas`, `Refactoring goal`, `Secret history scan`, and `Pending candidates` stay visible together without scrolling past it. The `## Safety Net`, `## Guardrails`, `## Housekeeping`, and `## Investigation` sections (below) sit between `Pending candidates` and `Fulfilled nodes`, in that order — the same Safety Net > Guardrails > Housekeeping > Investigation priority the scheduling algorithm uses elsewhere (`CONTEXT.md`'s **Track** entry) — each is its own heading, not a top-level field, so none competes with that ordering rule.

## Fields

| Field | Meaning | Written by |
|---|---|---|
| `Create-mode` | How merge requests get opened: `autonomous`, `ask-each-time`, or `human-opens` | `refactor-implement`, once, during `loop-config`'s own interview (`skills/continuous-refactoring/references/loop-config-interview.md`) — hand-editable after that, same as `Focus areas` |
| `Focus areas` | Areas scans should target first | you, any time |
| `Refactoring goal` | Freeform description of the *shape* structural work should converge toward — not *where* to look (that's `Focus areas`), but what the result should become (e.g. "convert legacy procedural code to OOP"). Read only by `refactor-prioritize`'s Select mode, picking a `structural-scan` candidate (`skills/refactor-prioritize/references/structural-candidate-search.md`) — never by a tooling-tree node's own Fulfilment check, and never by Rank mode. Omitted → today's behaviour, unchanged: no bias on candidate search. | you, any time |
| `Secret history scan` | Whether the one-time full git-history secret scan (`refactor-scan/SKILL.md` step 4c) has already run — absent until it has, `done (YYYY-MM-DD)` (the date the scan ran, purely for human-readable audit trail — nothing reads or compares it) once every finding from that run is filed. Read only by that step, to decide whether to run at all; gated on the `secret-detection` node itself being fulfilled first, so it's meaningless (and never written) on a target that hasn't adopted that node yet. | `refactor-learn`, early call, once, the pass the scan actually runs — never hand-edited (a target that genuinely wants the scan to run again removes the field by hand instead, the same escape hatch an `out-of-scope/` rejection uses) |
| `Pending candidates` | A one-item list (a bullet under the header, `- none` when empty) holding the issue most recently filed for this candidate, not yet delivered as a merge request. Written as a list purely for formatting consistency with `Fulfilled nodes` and easier diffing — it still holds at most one entry; the suite tracks exactly one thing in flight at a time (`refactor-scan`/`refactor-prioritize`), this is not a multi-pending queue. **No native-label tracker only** — on a native tracker, filing a tooling-tree node/`loop-config`/externally-labeled candidate skips this write entirely (stays `none` there in the ordinary case); a structural/baseline-shrink candidate's early filing (`refactor-prioritize`'s Select mode) writes it *even on a native tracker* — a narrow, deliberate exception, see below. | `refactor-design` sets it when it files a tooling-tree node/`loop-config`/externally-labeled candidate (non-native tracker only); `refactor-prioritize`'s Select mode sets it when it files a structural/baseline-shrink candidate (always, native tracker included); `refactor-learn` clears it once the merge request is remembered (`merge-requests.md`) or the candidate is resolved another way |
| `Fulfilled nodes` | Tooling-tree node **slugs** (never Names — internal bookkeeping stays keyed by the slug) already confirmed fulfilled, one per bulleted line, each carrying the delivering issue # (`- <slug> (#<issue>)`) when known — see *Fulfilled nodes* below. Sorts last — see the note above the table. **Never written for a Safety Net or Guardrails Track node** (below) — those live in the `## Safety Net`/`## Guardrails` sections instead. | `refactor-learn`, closing call, only when that call has a genuine delivery or rejection to record this pass — never written by itself as the sole reason for a bookkeeping branch — see *Fulfilled nodes* below |

`Pending candidates` exists so a pass interrupted mid-candidate doesn't get re-proposed as fresh work by the next `refactor-scan` — scan reads this field before walking the tree, and if it names an issue, that pending issue is the only thing it proposes this pass, resuming at whichever step is actually next (no plan comment on the issue yet → `refactor-design`; plan comment present → `refactor-implement` — `refactor-scan/SKILL.md` step 2). The native-tracker exception for a structural/baseline-shrink candidate's early filing exists for the same reason one level earlier: without it, a future pass's `refactor-scan` step 3b would rediscover the minimally-filed issue as an *externally-labeled* candidate and re-run candidate search on it from scratch — possibly picking a different one, exactly what this field prevents at the design→implement handoff already. **Never written for a Safety Net or Guardrails Track candidate** (below) — that candidate's in-flight issue lives in the relevant Track's own `Open` list instead, which can hold more than the one entry this field is limited to.

## `Safety Net` section

Replaces `Fulfilled nodes`/`Pending candidates` for every node the **Safety Net Track** (`CONTEXT.md`)
works through — every tooling-tree node reachable before `structural-scan` opens, `git`/`loop-config`/the
language specialization's own recognition gate excepted (those stay outside every Track — `loop-config`
remains its own mandatory human interview, `CONTEXT.md`'s **Onboarding** entry). Full read/write mechanics:
`skills/refactor-scan/references/safety-net-track.md` (`refactor-scan`'s own scan step),
`skills/refactor-learn/references/safety-net-write.md` (`refactor-learn`'s own write step),
`skills/continuous-refactoring/references/track-scheduler.md` (the orchestrator's own Track-selection
step — reads this section's `Cadence`/`Last scan`/`Open` to decide whether this Track even runs this
pass, competing against every other currently-wired Track; this section's `Open` field is also what that
file's own "One-time exception" reads to decide whether Investigation/Guardrails/Housekeeping each still
owe their one turn — `Open` currently empty is that check's entire precondition).

```markdown
## Safety Net

**Cadence:** 90

**Last scan:** 2026-09-14

**Open:**
- php-cs-fixer (#82)

**Out-of-scope:**
- phpmd — out-of-scope/phpmd.md
```

- **`Cadence`** — days between scans, `90` unless hand-edited. Never read to decide whether to scan when `Open` is non-empty (below).
- **`Last scan`** — the date (`YYYY-MM-DD`) the Track's scan last completed, written even when it found nothing to do. **The whole section is absent until the Track's first scan completes** — absence means "never run," never "nothing found"; a Track with no section is always due, the same as one whose `Last scan` is more than `Cadence` days old.
- **`Open`** — every Safety Net node currently proposed but not yet delivered or rejected, one per bulleted line, `- <slug> (#<issue>)` (issue # once filed, omitted before that — same convention as `Fulfilled nodes`' own `(#<issue>)`). `- none` when empty. **Non-empty `Open` means the Track is never rescanned this pass** — its existing entries are worked through the ordinary propose → design → implement → learn pipeline first, the same "resume before propose fresh" discipline `Pending candidates` already applies, just scoped to this Track and able to hold more than one entry at a time.
- **`Out-of-scope`** — every Safety Net node rejected via this Track, one per bulleted line, `- <slug> — out-of-scope/<slug>.md` (the pointer, not a restatement — the entry's own reasoning lives in that file, format unchanged from every other `out-of-scope/` entry). Never removed except by the ordinary reversal path (the `out-of-scope/<slug>.md` file deleted by hand or by a PHP-version-reversal finding, `refactor-scan/SKILL.md` step 3) — this bulleted pointer and the file are added/removed together.
- A slug **never appears in both `Open` and `Out-of-scope` at once**, and never in `Fulfilled nodes` either — the same mutual-exclusion invariant `Fulfilled nodes`/`out-of-scope/` already hold for every other node, just enforced within this section for a Safety Net Track node instead.

## `Guardrails` section

Replaces `Fulfilled nodes`/`Pending candidates` for every node the **Guardrails Track** (`CONTEXT.md`)
works through — the nodes required on `structural-scan`/`php-safety-net` themselves, proposed only once
the Safety Net has closed (PHP: `composer-audit`, `phpmd`, `coverage-floor`, `php-minimal-version`,
`phpstan-level-6` and above, `phpstan-deprecation-rules`, `semgrep`). Same shape as `## Safety Net`
above, independent of it — a slug lives in at most one Track's section, never both. Full read/write
mechanics: `skills/refactor-scan/references/guardrails-track.md` (`refactor-scan`'s own scan step),
`skills/refactor-learn/references/guardrails-write.md` (`refactor-learn`'s own write step),
`skills/continuous-refactoring/references/track-scheduler.md` (the orchestrator's own Track-selection
step — reads this section's `Cadence`/`Last scan`/`Open` the same way it reads `## Safety Net`'s own).

```markdown
## Guardrails

**Cadence:** 60

**Last scan:** 2026-09-14

**Open:**
- composer-audit (#90)

**Out-of-scope:**
- none
```

- **`Cadence`** — days between scans, `60` unless hand-edited (shorter than Safety Net's default 90 —
  Guardrails nodes are mostly point-in-time audits whose value is in repetition, `php-tooling-tree/
  composer-audit.md`'s own Housekeeping entry). Never read to decide whether to scan when `Open` is
  non-empty (below).
- **`Last scan`** — same meaning as `## Safety Net`'s own field: the date the Track's scan last
  completed, written even when it found nothing to do. **The whole section is absent until the Track's
  first scan completes** — absence means "never run," never "nothing found."
- **`Open`** — every Guardrails node currently proposed but not yet delivered or rejected, one per
  bulleted line, `- <slug> (#<issue>)`. `- none` when empty. **Non-empty `Open` means the Track is
  never rescanned this pass** — same resume-before-propose discipline `## Safety Net`'s own `Open`
  already follows.
- **`Out-of-scope`** — every Guardrails node rejected via this Track, one per bulleted line, `-
  <slug> — out-of-scope/<slug>.md`. Same reversal path, same pointer-and-file-together discipline as
  `## Safety Net`'s own `Out-of-scope`.
- A slug **never appears in both `Open` and `Out-of-scope` at once**, never in `Fulfilled nodes`, and
  never in `## Safety Net`'s own `Open`/`Out-of-scope` either — the two Tracks' node sets are disjoint
  by construction (Scope, `skills/refactor-scan/references/guardrails-track.md`).

## `Housekeeping` section

A hybrid of the two shapes above and `## Investigation`'s own: only `Cadence`/`Last scan`, like
`## Investigation` — no `Open`/`Out-of-scope`, since a maintenance cycle isn't a tooling-tree node
adoption — but a real numeric `Cadence` that competes in ratio comparison exactly like `## Safety
Net`'s/`## Guardrails`' own, unlike `## Investigation`'s permanent literal `continuous`. Replaces the
old, now-retired top-level `Housekeeping cadence` field the standalone `continuous-housekeeping` skill
used to own; the swept checklist content itself stays in `housekeeping-template.md`, entirely unrelated
to this section and unchanged by any of this. Full read/write mechanics:
`skills/continuous-refactoring/references/housekeeping-track.md` (the orchestrator's own step 0c, run
directly rather than through `refactor-scan` — this Track isn't a tooling-tree scan),
`skills/refactor-learn/references/housekeeping-write.md` (`refactor-learn`'s own write step),
`skills/continuous-refactoring/references/track-scheduler.md` (the orchestrator's own Track-selection
step — reads this section's `Cadence`/`Last scan` the same way it reads `## Safety Net`'s/`##
Guardrails`'s own).

```markdown
## Housekeeping

**Cadence:** 7

**Last scan:** 2026-09-15
```

- **`Cadence`** — days between scans, `7` unless hand-edited — the same default the old
  `continuous-housekeeping` skill's own setup interview always recommended (`weekly`), applied silently
  on this Track's first-ever scheduler-driven run instead of asked
  (`skills/continuous-refactoring/references/housekeeping-track.md`'s own *First-run cadence* section).
  Hand-editable any time, same as `## Safety Net`'s/`## Guardrails`' own — directly, or via the optional,
  human-run `skills/continuous-refactoring/references/housekeeping-cadence-interview.md`. Never read to
  decide whether to scan when an in-progress cycle exists (below).
- **`Last scan`** — the date the Track's process (`housekeeping-track.md`) last ran, written even when it
  found nothing registered to check. **The whole section is absent until the Track's first scan
  completes** — absence means "never run," never "nothing found," same as every other Track's own
  section.
- **No `Open`/`Out-of-scope`** — a Housekeeping cycle's own in-flight state (an open, not-yet-delivered
  `Housekeeping — <date>` issue) is never tracked here: `housekeeping-track.md`'s own *Resuming an
  in-progress cycle* section reads the tracker's history directly instead, the same "detect, never
  duplicate" discipline the suite's remembered-MR tracking already uses. This is also why Housekeeping
  never gates its own re-selection on an `Open`-non-empty precondition the way Safety Net/Guardrails do
  (`track-scheduler.md`'s own Eligibility section) — there's nothing in this section for that rule to
  read.

## `Investigation` section

Carries only what the Track scheduler needs to compete **Investigation** (`CONTEXT.md`) against the
other Tracks — nothing else. Replaces nothing: Investigation never had a `Fulfilled nodes`/`Pending
candidates` entry of its own to begin with, and doesn't gain an `Open`/`Out-of-scope` list either —
unlike `## Safety Net`/`## Guardrails` above, a structural candidate's own open/done/rejected state
stays on the issue tracker / the Refactoring Notes' `merge-requests.md` exactly as today (`Pending
candidates`, above, still tracks the one in-flight structural/baseline-shrink candidate exactly as it
already did before this section existed). Full read/write mechanics:
`skills/refactor-scan/references/investigation-track.md` (`refactor-scan`'s own scan step),
`skills/refactor-learn/references/investigation-write.md` (`refactor-learn`'s own write step),
`skills/continuous-refactoring/references/track-scheduler.md` (the orchestrator's own Track-selection
step — reads this section's `Cadence`/`Last scan` the same way it reads `## Safety Net`'s/`##
Guardrails`'s own, with one difference, next; that file's own "One-time exception" also reads whether
this section exists at all, and, once it does, whether the top-level `Pending candidates` field still
names an issue — the load-bearing signal for "Investigation's one candidate from that exception hasn't
been fully delivered yet," since this section's own `Last scan` gets written on that turn's very first
pass, well before design/implement/learn actually finish it).

```markdown
## Investigation

**Cadence:** continuous

**Last scan:** 2026-09-14
```

- **`Cadence`** — always the literal `continuous`, never a day count and never hand-edited (unlike
  `## Safety Net`'s/`## Guardrails`' own `Cadence`, above). Investigation carries no fixed interval
  (`CONTEXT.md`'s **Track** entry; spec's Scheduling algorithm decision) — it's the scheduler's
  permanent fallback, not a Track that becomes overdue on its own timer. `track-scheduler.md` treats a
  Track whose `Cadence` carries no day-count as always due, contributing no `overdue_ratio` to compare
  numerically — the same "no ratio to compare" case that file already defines for a never-run Track,
  except this one holds permanently for Investigation, every pass, not only before its first scan.
- **`Last scan`** — the date the Track's scan (`investigation-track.md`) last actually ran, written even
  when it proposed nothing (`structural-scan` still gated by its own unchanged resolved-edge parents,
  `skills/refactor-scan/references/tooling-tree/structural-scan.md`) — same "the first/every run records
  that it happened" discipline `## Safety Net`/`## Guardrails` already follow. **The whole section is
  absent until the Track's first scan completes** — absence means "never run," not "nothing found," same
  as either other section — but unlike those two, this never changes whether Investigation is due: with
  no `Cadence` to divide by, Investigation stays always due and always eligible regardless of `Last
  scan`'s own value; the field is a pure audit trail here ("did Investigation's scan run, and when"), not
  an input to its own due-check.
- **No `Open`/`Out-of-scope`** — Investigation never blocks its own re-selection on in-flight work (no
  "`Open` must be empty" precondition, unlike Safety Net/Guardrails): `structural-scan`'s own
  resolved-edge gate (unchanged — every node with a `resolved` edge into it must itself be resolved,
  fulfilled or explicitly rejected) already decides whether there's anything to propose once this
  Track is selected, and any concrete structural candidate it does produce is an ordinary issue from
  there — `Pending candidates` (above) tracks it in flight the same way it always has, unaffected by any
  of this.

## `Fulfilled nodes`

A cache, not a second source of truth — it exists purely to let a pass skip re-deriving what earlier
passes already established, and only matters to the **manual/LLM tree-walk fallback**
(`skills/refactor-scan/references/tree-walk-prompt.md`), which otherwise re-evaluates every node's
Fulfilment check by hand, in tree order, on every single pass. The deterministic parser
(`skills/refactor-scan/references/tooling_tree.py`) never reads this field — plain filesystem detection
is already cheap and always correct there, so there's nothing to gain and a staleness risk to avoid.
**Never covers a Safety Net or Guardrails Track node** — see `## Safety Net section`/`## Guardrails
section` above.

- **Read:** only by the tree-walk-fallback prompt — a listed slug is skipped without re-checking its
  Fulfilment check.
- **Write:** `refactor-learn`, closing call, per its own `## Process` — but only when that call has a
  genuine delivery or rejection to record this pass; never opened as a branch's sole reason. When it
  does write and this pass ran the
  deterministic parser (`python3` was available), it **overwrites the entire field** with the parser's
  complete current fulfilled-set — cheap ground truth, and this is what makes the cache self-healing:
  any staleness from an out-of-band change (a human revert, a manual edit) gets wiped out the next time
  a pass has parser access, whenever that is. Reads the file as currently committed first, so the
  overwrite carries forward every already-known `(#N)` annotation, keyed by slug — the parser itself
  never produces issue numbers, only slugs. When this pass ran the fallback instead, `refactor-learn`
  only adds newly-confirmed slugs from this pass's own walk, each with this pass's delivering issue #
  if one exists — it does not attempt to verify or prune entries it didn't itself just check.
- **Per-entry metadata: only the delivering issue #**, `- <slug> (#<issue>)` — omitted for an entry
  that predates this convention or whose delivering issue is otherwise unknown (never invented). No
  other per-entry metadata (no timestamp, no "as of which pass") — that kind of field in a versioned,
  repeatedly-rewritten file invites merge conflicts for no operational benefit; an issue # is worth
  the small conflict surface because it answers a real question ("which change delivered this node")
  a timestamp doesn't.
- A node **never appears in `Fulfilled nodes` and the Refactoring Notes' `out-of-scope/` at the same
  time** — fulfilled and rejected are different, mutually exclusive states for a node; rejection state
  lives entirely in `out-of-scope/` (one file per rejected node), never duplicated here. A node moves from
  rejected to fulfilled only through the normal reversal path (an out-of-scope entry removed, then the
  node adopted for real) — see `skills/refactor-scan/references/php-tooling-tree.md`'s Nodes intro and
  `skills/refactor-learn/SKILL.md`.

**`loop-config` exception:** for the `loop-config` candidate itself, this file doesn't exist yet when `refactor-design` would normally write `Pending candidates` — `refactor-implement` sets it directly when it creates the file instead, alongside `Create-mode` (already decided by the interview `refactor-design` ran for this candidate) — leaving only the first `Fulfilled nodes` entry (`loop-config (#<its own issue>)`, at minimum) for `refactor-learn`'s own follow-up commit. Because the file only exists on that candidate's own (not yet merged) branch, `refactor-learn`'s writes land there too, the one time bookkeeping doesn't go straight to the default branch. Every pass after that, once the file is on the default branch, all of this is as described in the table above.

There is deliberately no `Cadence` field for the continuous-refactoring loop itself: it never triggers itself — you kick it off whenever it's due, whether that's you running `/continuous-refactoring` by hand or a scheduler you set up outside the suite. `## Housekeeping`'s own `Cadence` (above) doesn't contradict this — it belongs to one Track among the four this loop schedules internally once it does run, not to the loop's own outer trigger.

## Rules

- **`Pending candidates` and `Fulfilled nodes` are `refactor-learn`-written — never by hand.** `Create-mode`, `Focus areas`, and `Refactoring goal` you can edit by hand any time — that's what they're for. Nobody is expected to hand-edit `Fulfilled nodes`; if it drifts wrong, the next pass with parser access re-derives it. `Secret history scan` is `refactor-learn`-written too (to `done (YYYY-MM-DD)`, once) — the one exception you *can* hand-edit, but only to remove it outright, on the rare target that genuinely wants the one-time scan to run again. The `## Safety Net`, `## Guardrails`, and `## Housekeeping` sections are the same: `refactor-learn`-written, never by hand, except each section's own `Cadence` — hand-editable any time (directly, or, for `## Housekeeping`, via the optional `housekeeping-cadence-interview.md`). `## Investigation` is `refactor-learn`-written too, but unlike those three, *nothing* in it is hand-editable — its `Cadence` is always the literal `continuous` (above), never a number to tune.
- The file travels with the repo. Loop state does not live in the agent's own conversation but here (create-mode, focus areas, refactoring goal, pending candidates, fulfilled nodes, the Safety Net, Guardrails, Housekeeping, and Investigation sections), in the issue tracker (backlog), in the Refactoring Notes' `merge-requests.md` (open suite merge requests — only when `docs/agents/issue-tracker.md` names no native-label tracker; otherwise that state lives directly on the tracker, as every open `refactor:candidate` issue's own native link to its delivering pull request), and in the Refactoring Notes' `out-of-scope/` (learned rejections).
- If the file is missing, that's the `loop-config` tooling-tree node — see above. Ordinary in every way except who writes which field and which branch it lands on for that one candidate — see the `loop-config` exception above.
- **Old-schema repos need no migration.** A `bookkeeping.md` predating any of these sections (no `## Safety Net`/`## Guardrails`/`## Housekeeping`/`## Investigation` heading at all) is read exactly like any other repo whose Track has never run — absence means "never run," not an error; nothing about the old `Fulfilled nodes`/`Pending candidates`/`Housekeeping cadence` fields already on the file blocks this — that last one is the standalone `continuous-housekeeping` skill's own now-retired field, superseded by `## Housekeeping`'s own `Cadence`, never read or migrated into it — and none of them needs to be understood, migrated, or removed for any Track's own first scan to proceed normally (`skills/refactor-scan/references/safety-net-track.md`, `skills/refactor-scan/references/guardrails-track.md`, `skills/continuous-refactoring/references/housekeeping-track.md`, `skills/refactor-scan/references/investigation-track.md`). The four sections migrate independently, too — a target that's already run its first Safety Net Track scan (so `## Safety Net` exists) but never its first Guardrails Track scan (so `## Guardrails` doesn't yet) is an entirely ordinary, expected state, not a partial or inconsistent one; `## Housekeeping`/`## Investigation` join the same way, each on its own first scan, independent of the others.
