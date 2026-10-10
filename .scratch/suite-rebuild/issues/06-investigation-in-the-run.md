# 06: Investigation in the run

**What to build:** When the run reaches the Investigation Track, open tickets there are the worklist:
structural candidates the suite filed and tickets a human wrote. With none open, the run explores the
code, shows everything it found in order of signal, and recommends filing the three strongest.

Spec: `../spec.md` (sections *Track choice*, *Tickets as the worklist*). Written new with the
`writing-for-agents` skill as a reference of the entry skill; the signals catalogue and the structural
candidate search are carried over as content.

**Blocked by:** 04

**Status:** done

- [x] A ticket matching no tooling-tree node and not the Housekeeping ticket counts as Investigation
- [x] A ticket a human wrote is found through the **Candidate** hint or by being named in the call; the
      reference states this limit in one sentence
- [x] With open tickets, selection follows the signals, a **Priority** hint first
- [x] With none, the run explores; all findings are shown, the three strongest are the recommendation for
      filing, an autonomous run files those three; nothing else is stored
- [x] The project lines `Focus areas` and `Refactoring goal` shape the exploration and its order
- [x] No cap and no "one candidate per run" rule appears
- [x] No test is written or changed

## Comments

### Done — what exists now

Under `skills/continuous-refactoring/references/`:

- `investigation-track.md` — written new: the tickets, explore, file, select, hand over.
- `signals.md` — the signals catalogue, carried over, plus the section *Order of signal*.
- `structural-candidate-search.md` — the exploration, carried over: project lines, where to look, what
  qualifies, what a finding holds.
- `worklist.md` — one bullet changed: what counts when a whole listing of open tickets is read.
- `track-choice.md` — *Coming back here* names the Investigation Track next to steps 5 and 7.
- `design-point.md` — one pointer: the `Refactoring goal` line is read as the search reference says
  (`AGENTS.md`, else `CLAUDE.md`).

Not touched: the old skills (`refactor-scan/references/investigation-track.md`,
`refactor-prioritize/references/signals.md`, `structural-candidate-search.md`,
`baseline-shrink-selection.md`), the tree docs, `CONTEXT.md`. Not carried over:
`baseline-shrink-selection.md` — shrinking a baseline is a tooling ticket (`design-point.md`, *Planning a
baseline ticket*).

For ticket 08: the **Signal** fields of the tree docs (`secret-detection.md`, `phpmd.md`, `semgrep.md`,
`coverage-floor.md`, and the two tree files) still point to `refactor-prioritize/references/signals.md`
and speak of "Select mode"; they need the new path when the old skill goes.

### Decided here, not stated by the spec

**Finding the tickets**

- Nothing is added to the search for Investigation tickets: they are the tickets carrying the
  **Candidate** mark, the ticket the call names, and every ticket of a place the operations give to the
  suite alone (the Local Markdown folder). No search word, no fixed title.
- So that the suite finds its own structural tickets again on a tracker that also holds other work and
  has no **Candidate** operation, the filing decision point asks how they are marked — a label is
  recommended — and writes the answer as the **Candidate** bullet into the tracker file. The same move as
  the missing **Rejected** operation. With "no mark", the human is told that these tickets are worked
  when the call names them.
- A whole listing of open tickets read on a tracker with other work keeps only the tickets that match a
  node (`worklist.md`); before, every feature or bug ticket of a small tracker would have become an
  Investigation ticket.
- The limit is stated in step 1 of the reference, worded "on a tracker that also holds other work", and
  said to the human when the run explores because no open ticket was found — the moment they can still
  name one.

**When the run explores**

- With no open Investigation ticket, or when the call asked for a scan (the wording `SKILL.md` step 5
  already uses). With open tickets of which none is
  workable (in review, blocked, waiting) the recommendation is to return to Track choice; exploring for
  more is the other option. An autonomous run therefore does not file three new candidates on every call
  while earlier ones wait for review.
- Exploring is not held back by the tooling Tracks: the old gate (`structural-scan` proposable only once
  Safety Net is resolved) is not carried over. Track choice already keeps an autonomous run at an
  unfinished Safety Net, and a human who chooses Investigation earlier gets it.
- The exploration may run in a subagent (it reads and judges); the decision points stay in the
  conversation.
- The exploration's results are called proposals, as `CONTEXT.md` has it. Each is searched in the
  tracker before the filing decision point: an open ticket on the subject takes its place and joins the
  worklist, a declined subject drops it, a ticket closed as done is named in the new one.
- A tool named by a signal is read from its existing report, or run in a way that leaves the target's
  files alone: the exploration happens before a decision point and stays read-only.
- Where to look without a direction: the last few hundred commits, the ten places that come up most.
- After exploring and filing, the run selects when the worklist holds a workable Investigation ticket
  (new, found by the search, or there before); only without one is Investigation marked as tried.

**Filing**

- Investigation has its own filing decision point (step 3 of the reference), not the one of
  `filing-a-ticket.md`, whose recommendation is to file everything. Options: the three strongest, others
  the human names (any number), none. With fewer than three findings all are recommended.
- A structural ticket holds **Where**, **Problem** and **Signal** — the last in plain words with its
  evidence, not as a catalogue name — and a sentence that what the application does stays the same; its
  title says what gets done in the target's names.
- The suite sets the **Candidate** mark and never the **Priority** mark: priority is the human's hint.
  The old `refactor:priority` for security findings is replaced by the order of signal.
- The run goes on in the same call: after filing, selection takes the strongest of the new tickets.

**Order of signal** (`signals.md`)

- Security first, then Blast radius of inaction — the old "priority admission" tier, kept as order only,
  without the cap it bypassed. Then everything else by the four old ranking questions: heat, leverage,
  tooling pressure, low risk. The old fifth factor, age, went with **Filed date**.
- `Focus areas` moves an item up within its group; `Refactoring goal` breaks a tie, and during the
  exploration friction against the goal is evidence for the signal it falls under (the old text called it
  a signal of its own, which the catalogue has no entry for). `Focus areas` also decides where
  the exploration looks first, after a direction named in the call.
- The same order serves open tickets and exploration findings. A ticket that names no signal (a human's)
  gets one named from its text and the code it points to.
- The project lines are read from `AGENTS.md`, else `CLAUDE.md`, as plain lines; the heading they used to
  sit under is not required. `design-point.md` now points to that one place.

**Selection**

- A pick-up check of its own kind: the module or files the ticket names still exist and the friction is
  still there. A ticket whose subject is gone is proposed for closing with a note, like a tooling ticket
  fulfilled at pick-up.
- Handed to the design point: the ticket, the Track, the mode, the restriction (no node). A named ticket
  in review arrives with its merge request and the review's comments, as in `selection.md`.

**Catalogue**

- Tooling pressure no longer lists baseline residuals as evidence, and the search says that baseline
  entries are no finding: they belong to the baseline ticket of their level.
- Each signal says "generic" or "from a tool"; the tool evidence named per signal follows the tree docs'
  **Signal** fields (secret scanner, Psalm taint analysis, Semgrep, PHPMD, coverage floor).

### Red afterwards

No unit test is newly red (the same two). The validator has new errors; they are in a comment on
ticket 09.

### Changed after the review

The first draft found the suite's structural tickets by the word `refactoring`, which every such ticket
had to carry. Both review axes named it a fixed marker and a contradiction to the stated limit; it is
replaced by the proposal of a **Candidate** mark at filing (above). Also from the review: "proposals"
instead of "findings" for what the exploration returns; a proposal covered by an open ticket is no
longer offered for filing; a call that asked for a scan and files nothing still works the tickets that
were workable before.

Left as it is: `track-choice.md` says Investigation has something "always". With open tickets that are
all in review the Track is therefore recommended, lays out its one decision point and returns as tried.
