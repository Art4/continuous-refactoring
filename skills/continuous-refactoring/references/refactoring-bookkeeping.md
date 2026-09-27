# Reference: the bookkeeping document, the config file, and where they live

The suite's state is split in two, and both are written by the onboarding interview
(`onboarding-setup-interview.md`), which is why a fresh target has neither:

- the **bookkeeping document** (`bookkeeping.md`, below) — the loop's state: each Track's `Cadence`, `Last scan`,
  `Open` and `Out-of-scope`, `Pending candidates`, `Secret history scan`. Nothing personal.
- the **config file** (`.scratch/refactor/config.md`, *The config file*, below) — per person and machine: the
  **Bookkeeping pointer**, `Ticket-create-mode` and `MR-create-mode`.

`Focus areas` and `Refactoring goal` are in neither: they are lines in the instruction file (`AGENTS.md`, else
`CLAUDE.md`), written only by humans (*Project lines*, below).

The document is written last of everything onboarding produces, so its existence means "onboarding completed" — the
`onboarding-setup` node's Fulfilment check (`../../refactor-scan/references/tooling-tree.md`). A freshly
onboarded document holds only the title line; every other field and section below joins the first time something
needs it, and an absent field reads as unset (`Pending candidates` absent = `- none`).

The suite reads and writes the document as one local file, whichever of two places it really lives in:

- **File mode** — the pointer is a path. The file is the document: the suite writes it and never commits,
  branches or ignores anything; whether it goes into Git, and how it reaches another machine, is the developer's
  job, and this mode is meant for one person. Always the mode with the local Markdown tracker.
- **Issue mode** — the pointer is the URL of a tracker issue. The issue body is the document, and the local file
  is a copy the suite loads before a pass and saves after every write, so the state can be picked up from any
  machine without a commit (`issue-mode.md`).

Either way every skill and the parser read and write the same local files; only loading and saving differ.

## Where the Refactoring Notes live

The **Refactoring Notes** are the folder holding the loop's state — the bookkeeping document (`bookkeeping.md`,
this file), `merge-requests.md`, `out-of-scope/`. It is the folder the Bookkeeping pointer points into. The default
is `.scratch/refactor/`, next to the local Markdown tracker's own `issues/` folder.

**Resolution rule**, followed independently by every lifecycle skill (and by the deterministic parser,
`../../refactor-scan/references/tooling_tree.py`) wherever it needs the Refactoring Notes, the same way the suite
already resolves "does the tracker support native labels" from `docs/agents/issue-tracker.md` — not a value
threaded through the orchestrator's carried-data chain. The **Bookkeeping pointer** is, in this order:

1. the config file's `**Bookkeeping:**` field — the path of the bookkeeping document, or the URL of its issue;
2. else a `` Bookkeeping: `<path or URL>` `` line (backtick-quoted) in `AGENTS.md`, else `CLAUDE.md` — the shared
   fallback, for a team that wants one common document.

File mode: the Refactoring Notes are that path's folder. Issue mode: they are `.scratch/refactor/`, the working
copy (`issue-mode.md`). **No pointer anywhere means the target isn't onboarded** (*Not
onboarded yet*, below); the deterministic parser, which has no such notion, reads `.scratch/refactor/` then — which is also where it
reads the working copy in issue mode.

Every other skill in this suite refers to this folder by name — "the Refactoring Notes" — never by restating or
assuming the concrete path; this section is the one place the resolution rule itself is defined.

## The config file

`.scratch/refactor/config.md`, at this fixed path (so it needs no pointer of its own) and per person and machine.
Whether it goes into Git is the developer's decision, like the rest of `.scratch/`.

```markdown
# Refactoring Config

**Bookkeeping:** .scratch/refactor/bookkeeping.md

**Ticket-create-mode:** ask-each-time

**MR-create-mode:** human-opens
```

| Field | Meaning | Written by |
|---|---|---|
| `Bookkeeping` | The Bookkeeping pointer — the path of the bookkeeping document, or the URL of the issue that holds it | the dispatcher's onboarding step, once — hand-editable after that |
| `Ticket-create-mode` | How new tickets (issues) get created: `autonomous` or `ask-each-time`. Read by `refactor-loop` and the Housekeeping Track (`filing-a-ticket.md`) | the dispatcher's onboarding step, once — hand-editable after that |
| `MR-create-mode` | How merge requests get opened: `autonomous`, `ask-each-time`, or `human-opens`. Read by `refactor-implement` and the Housekeeping Track (`opening-a-merge-request.md`) | the dispatcher's onboarding step, once — hand-editable after that |

**A create-mode the file doesn't state — or no config file at all — reads as the safe value:**
`Ticket-create-mode: ask-each-time`, `MR-create-mode: human-opens`. A fresh machine without a config file must not
create tickets or open merge requests on its own; whichever pass runs on those defaults says so in its closing
report. No skill writes this file after onboarding.

## Project lines

`Focus areas` (areas scans should target first) and `Refactoring goal` (a freeform description of the *shape*
structural work should converge toward — not *where* to look, that's `Focus areas`, but what the result should
become, e.g. "convert legacy procedural code to OOP") are lines in the instruction file's `## Continuous-refactoring
suite` section:

```markdown
Focus areas: order intake, billing

Refactoring goal: convert legacy procedural code to OOP
```

Only humans write them, any time; the suite never does. Both are optional — absent reads as unset. `Focus areas`
is a hint for where scans should look first; `Refactoring goal` is read only by `refactor-prioritize`'s Select mode, picking a
`structural-scan` candidate (`../../refactor-prioritize/references/structural-candidate-search.md`) — never by a
tooling-tree node's Fulfilment check, and never by Rank mode. Omitted → no bias on candidate search.

## Structure

```markdown
# Refactoring Bookkeeping

**Secret history scan:** done (2026-09-12)

**Pending candidates:**
- none

## Safety Net

**Cadence:** 90 days

**Last scan:** 2026-09-14

**Open:**
- php-cs-fixer (#82)

**Out-of-scope:**
- phpmd — out-of-scope/phpmd.md

## Guardrails

**Cadence:** 60 days

**Last scan:** 2026-09-01

**Open:**
- composer-audit (#90)

**Out-of-scope:**
- none

## Housekeeping

**Cadence:** 7 days

**Last scan:** 2026-09-15

## Investigation

**Cadence:** continuous

**Last scan:** 2026-09-10

**Open:**
- Shallow UserService (#101)
```

`Pending candidates` sorts last, not alphabetically or by write-frequency. The `## Safety Net`, `## Guardrails`, `## Housekeeping`, and `## Investigation` sections (below) sit between `Pending candidates` and the end of the file, in that order — the same Safety Net > Guardrails > Housekeeping > Investigation priority the scheduling algorithm uses elsewhere (`CONTEXT.md`'s **Track** entry) — each is its own heading, not a top-level field, so none competes with that ordering rule.

## Cadence values

Every Track's `Cadence` (except Investigation's literal `continuous`, below) is one of these forms — a number *with its unit*, or a monthly calendar anchor. Written out in full, singular or plural (`1 month`, `2 months`); case-insensitive. This is the only place the forms are defined; `track-scheduler.md`, the `*-write.md` files and the docs point here.

| Form | Example | Interval used for `overdue_ratio` |
|---|---|---|
| `<n> hours` | `12 hours` | `n / 24` days |
| `<n> days` | `90 days` | `n` days |
| `<n> weeks` | `2 weeks` | `7n` days |
| `<n> months` | `1 month` | `30n` days — a deliberate approximation, not calendar-exact |
| `monthly on the <N>th` (`N` = 1–28) | `monthly on the 1st` | a 30-day period; due by calendar, not by elapsed time (below) |
| `continuous` | Investigation only | no interval — always due, contributes no ratio |

- **Interval forms** — `overdue_ratio = (today − Last scan, in days) / interval in days`; due at `>= 1`. `Last scan` is a plain date, so an `hours` cadence is only as precise as a calendar day: a Track last scanned today is not due again today, one last scanned yesterday is due for any `hours` value up to `24`.
- **Calendar anchor** — due as soon as at least one `<N>`th of a month falls after `Last scan` and on or before `today` (`Last scan` itself excluded, `today` included). Then `overdue_ratio = max(1, (today − Last scan, in days) / 30)`; not due, `(today − Last scan, in days) / 30` (always `< 1`). So "due ⇔ `overdue_ratio >= 1`" and the Housekeeping preemption rule (`track-scheduler.md`) hold unchanged for anchored Tracks too.
- **A bare number** (`90`, from a file written before units existed) is read as days. No migration; the next hand-edit or interview may add the unit.
- **A value that matches none of the forms** is never guessed at: the Track's own default (`90 days` / `60 days` / `7 days`) is used for this pass and the closing report names the unreadable value.
- **Section absent** (never run) is unchanged: maximally overdue, always due.
- **Written defaults carry the unit** — `refactor-learn` writes `90 days`, `60 days`, `7 days` on first creation.

## Fields

| Field | Meaning | Written by |
|---|---|---|
| `Secret history scan` | Whether the one-time full git-history secret scan (`refactor-scan/SKILL.md` step 4c) has already run — absent until it has, `done (YYYY-MM-DD)` (the date the scan ran, purely for human-readable audit trail — nothing reads or compares it) once every finding from that run is filed. Read only by that step, to decide whether to run at all; gated on the `secret-detection` node itself being fulfilled first, so it's meaningless (and never written) on a target that hasn't adopted that node yet. | `refactor-learn`, early call, once, the pass the scan actually runs — never hand-edited (a target that genuinely wants the scan to run again removes the field by hand instead, the same escape hatch an `out-of-scope/` rejection uses) |
| `Pending candidates` | A one-item list (a bullet under the header, `- none` when empty) holding the issue most recently filed for a **tooling-tree node's own first-ever proposal**, before its Track's own `## Safety Net`/`## Guardrails` section exists yet — the one pass where that node isn't already tracked by the Track's own `Open` (below). Narrow and short-lived: from the Track's next scan on, every node in its scope is tracked in that Track's own `Open` instead, and this field goes back to `none`. **Non-native tracker only** — on a native tracker this write is skipped entirely (stays `none`): a future pass's `refactor-scan` step 3 rediscovers the same still-open issue on its own. | `refactor-design` sets it for that narrow case only (non-native tracker); `refactor-learn` clears it once the merge request is remembered (`merge-requests.md`) or the Track's own `Open` takes over |

`Pending candidates` exists so a pass interrupted mid-candidate doesn't get re-proposed as fresh work by the next `refactor-scan` — scan reads this field before walking the tree, and if it names an issue, that pending issue is the only thing it proposes this pass, resuming at whichever step is actually next (no plan comment on the issue yet → `refactor-design`; plan comment present → `refactor-implement` — `refactor-scan/SKILL.md` step 2). **Never written for a Safety Net or Guardrails Track candidate** once that Track's own section exists (below) — that candidate's in-flight issue lives in the relevant Track's own `Open` list instead, which can hold more than the one entry this field is limited to. **Never written for a structural, baseline-shrink, or externally-labeled candidate either** — those are `## Investigation`'s own business, tracked in its own `Open` (below), not here.

## `Safety Net` section

Replaces the global `Pending candidates` for every node the **Safety Net Track** (`CONTEXT.md`)
works through — every tooling-tree node reachable before `structural-scan` opens, `git`/`onboarding-setup`/the
language specialization's own recognition gate excepted (those stay outside every Track — `onboarding-setup`
is fulfilled by the dispatcher's onboarding step and never proposed, `CONTEXT.md`'s **Onboarding** entry). Full read/write mechanics:
`../../refactor-scan/references/safety-net-track.md` (`refactor-scan`'s own scan step),
`../../refactor-learn/references/safety-net-write.md` (`refactor-learn`'s own write step),
`track-scheduler.md` (the orchestrator's own Track-selection
step — reads this section's `Cadence`/`Last scan`/`Open` to decide whether this Track even runs this
pass, competing against every other currently-wired Track; this section's `Open` field is also what that
file's own "One-time exception" reads to decide whether Investigation/Guardrails/Housekeeping each still
owe their one turn — `Open` currently empty is that check's entire precondition). While Safety Net `Open`
is non-empty, it is selected and nothing else runs, even if no node is currently workable; the scheduler
reports the wait.

```markdown
## Safety Net

**Cadence:** 90 days

**Last scan:** 2026-09-14

**Open:**
- php-cs-fixer (#82)

**Out-of-scope:**
- phpmd — out-of-scope/phpmd.md
```

- **`Cadence`** — interval between scans (forms: *Cadence values*, above), `90 days` unless hand-edited. Never read to decide whether to scan when `Open` is non-empty (below).
- **`Last scan`** — the date (`YYYY-MM-DD`) the Track's scan last completed, written even when it found nothing to do. **The whole section is absent until the Track's first scan completes** — absence means "never run," never "nothing found"; a Track with no section is always due, the same as one whose `Last scan` is more than `Cadence` days old.
- **`Open`** — the complete, ordered backlog for this Track: every node of the Track's scope that is neither fulfilled nor out-of-scope, in script order, hand-reorderable, blocked ones included. One per bulleted line, `- <slug> (#<issue>)` (issue # only while the node is being worked, omitted otherwise). `- none` when empty. **`Open` empty means the Track is done.** Non-empty `Open` means the Track is never rescanned this pass — its existing entries are worked through the ordinary propose → design → implement → learn pipeline first, the same "resume before propose fresh" discipline `Pending candidates` already applies, just scoped to this Track and able to hold more than one entry at a time. A scan runs only for a selected Track whose `Open` is empty (due by cadence, or named manually — naming a Track never forces a scan while `Open` has entries). Existing files under the old meaning (where `Open` listed only nodes with filed issues) are not migrated: such an `Open` is walked like any other, and the scan that runs once it empties records the complete backlog.
- **`Out-of-scope`** — every Safety Net node rejected via this Track, one per bulleted line, `- <slug> — out-of-scope/<slug>.md` (the pointer, not a restatement — the entry's own reasoning lives in that file, format unchanged from every other `out-of-scope/` entry). Never removed except by the ordinary reversal path (the `out-of-scope/<slug>.md` file deleted by hand or by a PHP-version-reversal finding, `refactor-scan/SKILL.md` step 3) — this bulleted pointer and the file are added/removed together.
- A slug **never appears in both `Open` and `Out-of-scope` at once** — the mutual-exclusion invariant, enforced within this section for a Safety Net Track node.

## `Guardrails` section

Replaces the global `Pending candidates` for every node the **Guardrails Track** (`CONTEXT.md`)
works through — the nodes required on `structural-scan`/`php-safety-net` themselves, proposed only once
the Safety Net has closed (PHP: `composer-audit`, `phpmd`, `coverage-floor`, `php-minimal-version`,
`phpstan-level-6` and above, `phpstan-deprecation-rules`, `semgrep`). Same shape as `## Safety Net`
above, independent of it — a slug lives in at most one Track's section, never both. Full read/write
mechanics: `../../refactor-scan/references/guardrails-track.md` (`refactor-scan`'s own scan step),
`../../refactor-learn/references/guardrails-write.md` (`refactor-learn`'s own write step),
`track-scheduler.md` (the orchestrator's own Track-selection
step — reads this section's `Cadence`/`Last scan`/`Open` the same way it reads `## Safety Net`'s own). With at least one workable `Open` node, Guardrails is selected ahead of Investigation; with nothing workable, it yields.

```markdown
## Guardrails

**Cadence:** 60 days

**Last scan:** 2026-09-14

**Open:**
- composer-audit (#90)

**Out-of-scope:**
- none
```

- **`Cadence`** — interval between scans (forms: *Cadence values*, above), `60 days` unless hand-edited (shorter than Safety Net's default 90 —
  Guardrails nodes are mostly point-in-time audits whose value is in repetition, `php-tooling-tree/
  composer-audit.md`'s own Housekeeping entry). Never read to decide whether to scan when `Open` is
  non-empty (below).
- **`Last scan`** — same meaning as `## Safety Net`'s own field: the date the Track's scan last
  completed, written even when it found nothing to do. **The whole section is absent until the Track's
  first scan completes** — absence means "never run," never "nothing found."
- **`Open`** — the complete, ordered backlog for this Track: every node of the Track's scope that is neither fulfilled nor out-of-scope, in script order, hand-reorderable, blocked ones included. One per bulleted line, `- <slug> (#<issue>)`. `- none` when empty. **`Open` empty means the Track is done.** Non-empty `Open` means the Track is never rescanned this pass — same resume-before-propose discipline `## Safety Net`'s own `Open` already follows.
- **`Out-of-scope`** — every Guardrails node rejected via this Track, one per bulleted line, `-
  <slug> — out-of-scope/<slug>.md`. Same reversal path, same pointer-and-file-together discipline as
  `## Safety Net`'s own `Out-of-scope`.
- A slug **never appears in both `Open` and `Out-of-scope` at once** — and
  never in `## Safety Net`'s own `Open`/`Out-of-scope` either — the two Tracks' node sets are disjoint
  by construction (Scope, `../../refactor-scan/references/guardrails-track.md`).

## `Housekeeping` section

A hybrid of the two shapes above and `## Investigation`'s own: only `Cadence`/`Last scan`, like
`## Investigation` — no `Open`/`Out-of-scope`, since a maintenance cycle isn't a tooling-tree node
adoption — but a real, unit-carrying `Cadence` that competes in ratio comparison exactly like `## Safety
Net`'s/`## Guardrails`' own, unlike `## Investigation`'s permanent literal `continuous`. Replaces the
old, now-retired top-level `Housekeeping cadence` field the standalone `continuous-housekeeping` skill
used to own; the swept checklist content itself stays in `housekeeping-template.md`, entirely unrelated
to this section and unchanged by any of this. Full read/write mechanics:
`../../continuous-housekeeping/references/housekeeping-track.md` (`continuous-housekeeping`'s process, run
directly rather than through `refactor-scan` — this Track isn't a tooling-tree scan),
`../../refactor-learn/references/housekeeping-write.md` (`refactor-learn`'s own write step),
`track-scheduler.md` (the orchestrator's own Track-selection
step — reads this section's `Cadence`/`Last scan` the same way it reads `## Safety Net`'s/`##
Guardrails`'s own).

```markdown
## Housekeeping

**Cadence:** 7 days

**Last scan:** 2026-09-15
```

- **`Cadence`** — interval between scans (forms: *Cadence values*, above), `7 days` unless hand-edited — the same default the old
  `continuous-housekeeping` skill's own setup interview always recommended (`weekly`), applied silently
  on this Track's first-ever scheduler-driven run instead of asked
  (`../../continuous-housekeeping/references/housekeeping-track.md`'s own *First-run cadence* section).
  Hand-editable any time, same as `## Safety Net`'s/`## Guardrails`' own — directly, or via the optional,
  human-run `../../continuous-housekeeping/references/housekeeping-cadence-interview.md`. Never read to
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

Carries what the Track scheduler needs to compete **Investigation** (`CONTEXT.md`) against the other
Tracks, plus its own `Open` — a single-entry counterpart to `## Safety Net`'s/`## Guardrails`' own,
holding the one candidate the Track is actively working (structural, PHPStan baseline-shrink, or an
externally-labeled issue — everything `refactor-scan/SKILL.md` step 3b now routes to an Investigation
pass only). No `Out-of-scope`: Investigation doesn't reject a fixed set of candidates the way the tree
does, and every *other* open candidate — one Select mode drafted but didn't pick this pass, or a human's
own untouched `refactor:candidate` issue — stays exactly what it already is, an ordinary open issue, not
a tracked backlog entry: the tracker itself already shows it, cheaply and live, `refactor-scan` step 3b
re-discovers it fresh every Investigation pass, and there's no un-filed-node concept here the way there
is for the tree (a tree node can sit unblocked for passes with no issue at all; an Investigation
candidate is always already an issue the moment it exists). Full read/write mechanics:
`../../refactor-scan/references/investigation-track.md` (`refactor-scan`'s own scan step),
`../../refactor-learn/references/investigation-write.md` (`refactor-learn`'s own write step),
`track-scheduler.md` (the orchestrator's own Track-selection
step — reads this section's `Cadence`/`Last scan`/`Open` the same way it reads `## Safety Net`'s/`##
Guardrails`'s own, with one difference, next; that file's own "One-time exception" also reads whether
this section exists at all, and, once it does, whether its own `Open` still names an issue — the
load-bearing signal for "Investigation's one candidate from that exception hasn't been fully delivered
yet," since this section's own `Last scan` gets written on that turn's very first pass, well before
design/implement/learn actually finish it).

```markdown
## Investigation

**Cadence:** continuous

**Last scan:** 2026-09-14

**Open:**
- none
```

- **`Cadence`** — always the literal `continuous`, never an interval and never hand-edited (unlike
  `## Safety Net`'s/`## Guardrails`' own `Cadence`, above). Investigation carries no fixed interval
  (`CONTEXT.md`'s **Track** entry; spec's Scheduling algorithm decision) — it's the scheduler's
  permanent fallback, not a Track that becomes overdue on its own timer. `track-scheduler.md` treats a
  Track whose `Cadence` carries no interval as always due, contributing no `overdue_ratio` to compare
  numerically — the same "no ratio to compare" case that file already defines for a never-run Track,
  except this one holds permanently for Investigation, every pass, not only before its first scan.
- **`Last scan`** — the date the Track's scan (`investigation-track.md`) last actually ran, written even
  when it proposed nothing (`structural-scan` still gated by its own unchanged resolved-edge parents,
  `../../refactor-scan/references/tooling-tree/structural-scan.md`) — same "the first/every run records
  that it happened" discipline `## Safety Net`/`## Guardrails` already follow. **The whole section is
  absent until the Track's first scan completes** — absence means "never run," not "nothing found," same
  as either other section — but unlike those two, this never changes whether Investigation is due: with
  no `Cadence` to divide by, Investigation stays always due and always eligible regardless of `Last
  scan`'s own value; the field is a pure audit trail here ("did Investigation's scan run, and when"), not
  an input to its own due-check.
- **`Open`** — at most one entry, `- <issue title> (#<issue>)`, `- none` when empty (unlike `## Safety
  Net`'s/`## Guardrails`' own multi-entry backlog — see *Why single-entry*, above). Written on **every**
  tracker, native-label ones included — unlike a tooling-tree node's top-level `Pending candidates`
  (above), which native trackers skip: an Investigation candidate needs `refactor-scan` to resume
  *exactly* this issue next pass rather than treat it as a fresh candidate and possibly pick a different
  one via step 3b's ranking, regardless of whether the tracker also shows the issue open. `refactor-scan`
  resumes it only when **Investigation is the Track selected this pass** (`track-scheduler.md`) — the
  same "read this Track's own `Open` only when this Track runs" discipline `## Safety Net`/`##
  Guardrails` already follow; a Guardrails or Safety Net pass never touches it. `refactor-learn` clears
  it to `- none` once the candidate is merged, rejected, or closed as a design-time breaking-change
  finding.
- Investigation never blocks its own re-selection on `Open`'s own emptiness the way Guardrails/Safety Net
  do (no "`Open` must be empty before a fresh scan" precondition): `structural-scan`'s own resolved-edge
  gate (unchanged — every node with a `resolved` edge into it must itself be resolved, fulfilled or
  explicitly rejected) already decides whether there's anything fresh to propose once this Track is
  selected and its own `Open` is empty.

**Why single-entry.** `refactor-prioritize`'s Select mode can draft more than one structural candidate's
issue in a single pass, but only one is ever chosen to be designed and implemented this pass — the suite
tracks exactly one thing in flight at a time, the same discipline the retired global `Pending candidates`
field already held to. The others sit as ordinary open issues for a future pass
(`../../refactor-prioritize/references/structural-candidate-search.md`) — `refactor-scan` step 3b
re-discovers and re-ranks them fresh every Investigation pass, the same as any other candidate; nothing
here privileges or queues them ahead of time.

There is deliberately no `Cadence` field for the continuous-refactoring loop itself: it never triggers itself — you kick it off whenever it's due, whether that's you running `/continuous-refactoring` by hand or a scheduler you set up outside the suite. `## Housekeeping`'s own `Cadence` (above) doesn't contradict this — it belongs to one Track among the four this loop schedules internally once it does run, not to the loop's own outer trigger.

## Rules

- **`Pending candidates` is `refactor-learn`-written — never by hand.** The config file and the project lines
  (above) are the hand-edited part; this document is the suite's. `Secret history scan` is `refactor-learn`-written too (to
  `done (YYYY-MM-DD)`, once) — the one exception you *can* hand-edit, but only to remove it outright, on
  the rare target that genuinely wants the one-time scan to run again. The `## Safety Net`, `## Guardrails`,
  and `## Housekeeping` sections are the same: `refactor-learn`-written, never by hand, except each
  section's own `Cadence` — hand-editable any time (directly, or, for `## Housekeeping`, via the optional
  `housekeeping-cadence-interview.md`). `## Investigation` is the same too — `refactor-design` sets its
  `Open` entry, `refactor-learn` clears it and writes `Last scan` — but unlike those three, *nothing* in
  it is hand-editable — its `Cadence` is always the literal `continuous` (above), never a number to tune.
- The suite never commits this document, in either mode. Loop state does not live in the agent's own conversation but here (pending candidates, the Safety Net, Guardrails, Housekeeping, and Investigation sections), in the issue tracker (backlog), in the Refactoring Notes' `merge-requests.md` (open suite merge requests — only when `docs/agents/issue-tracker.md` names no native-label tracker; otherwise that state lives directly on the tracker, as every open `refactor:candidate` issue's own native link to its delivering pull request), and in the Refactoring Notes' `out-of-scope/` (learned rejections). A branch can therefore only see the state of the working tree it runs in.
- If the Bookkeeping pointer is missing, or names a file that doesn't exist, the target isn't onboarded yet (an issue URL that can't be read is a different case — `issue-mode.md`, *Load*: the pass stops, and nothing is created in its place): the dispatcher's onboarding step runs before anything else, and every other skill that needs the document aborts (*Not onboarded yet*, below) rather than creating it.

## Not onboarded yet

When `refactor-loop` or `continuous-housekeeping` finds no Bookkeeping pointer, or no `bookkeeping.md` where it points, it aborts before doing anything — nothing runs, nothing is announced, and it never creates the file or the issue. Report: "This repo isn't onboarded yet — there is no bookkeeping document. Run `/continuous-refactoring` first; its onboarding step sets the repo up, then rerun." This is the one place that text lives; both skills point here.
- **Old-schema repos need no migration.** A `bookkeeping.md` predating any of these sections (no `## Safety Net`/`## Guardrails`/`## Housekeeping`/`## Investigation` heading at all) is read exactly like any other repo whose Track has never run — absence means "never run," not an error; nothing about the old `Pending candidates`/`Housekeeping cadence` fields already on the file blocks this — that last one is the standalone `continuous-housekeeping` skill's own now-retired field, superseded by `## Housekeeping`'s own `Cadence`, never read or migrated into it — and none of them needs to be understood, migrated, or removed for any Track's own first scan to proceed normally (`../../refactor-scan/references/safety-net-track.md`, `../../refactor-scan/references/guardrails-track.md`, `../../continuous-housekeeping/references/housekeeping-track.md`, `../../refactor-scan/references/investigation-track.md`). The four sections migrate independently, too — a target that's already run its first Safety Net Track scan (so `## Safety Net` exists) but never its first Guardrails Track scan (so `## Guardrails` doesn't yet) is an entirely ordinary, expected state, not a partial or inconsistent one; `## Housekeeping`/`## Investigation` join the same way, each on its own first scan, independent of the others.
