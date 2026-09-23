# Filing a ticket

Rules for creating a new issue on the target's tracker. Only two places create one: `refactor-loop` (for every loop Track) and the Housekeeping Track's own process (`continuous-housekeeping`), because they are the only places that can ask the human — a lifecycle skill runs in a subagent and can't. Every other skill **hands back a draft** and the loop creates it. `opening-a-merge-request.md` is the counterpart for merge requests.

Only *creating* moves here. A skill still comments on, updates the body of, and labels an issue that already exists.

**Ticket-create-mode.** Read the Refactoring Notes' `bookkeeping.md`'s `Ticket-create-mode` field: `autonomous` or `ask-each-time`. Absent → `autonomous` (nothing to migrate, nothing to ask). Decided once, during the dispatcher's onboarding step (`onboarding-setup-interview.md`), hand-editable afterwards. It never governs merge requests — that is `MR-create-mode`.

A draft is what a skill returns instead of creating: the title, the labels, the body, and — for the loop to recognise an issue that already exists — the title as the key (`Tooling tree: <Name>`, `PHPStan Level N: baseline shrink — <group>`), or Where/Problem for a structural candidate, which has no fixed title. A skill lists its drafts under its own output, next to the writes it made (`reporting-progress.md`).

**Creating one.** For every draft: look for an open issue that already carries that title (or the same Where) → that issue is the ticket, nothing is created and nobody is asked. Otherwise create it per `docs/agents/issue-tracker.md` (`gh`/`glab issue create`, or a new file on Local Markdown), report it as its own line, and hand its number to whoever needs it next — `refactor-design` for the chosen candidate, `refactor-learn`'s closing call for a Track `Open` entry's issue number.

**`autonomous`** → create every draft as it arrives.

**`ask-each-time`** → two kinds of question, both asked by the loop itself:
- **The up-front batch** — the drafts a step returns for candidates that were only *proposed* (every unblocked tooling-tree node's minimal issue; every candidate a Select-mode dispatch found; every secret-history finding). One question per batch: "Create issues for these N?", listing them by Name. **Yes** → create all of them. **No** → create none of them; the chosen candidate is still asked about, below.
- **The chosen candidate** — the ticket the pass is about to work on. Asked before it is created, unless a batch *yes* already created it.

**A refused ticket for the chosen candidate.** The pass ends there with a report — the node stays a proposal, nothing else was written, and the next pass proposes it again. Offer once, in the same message, to reject it for good instead: yes → hand a rejection to `refactor-learn`'s closing call (an `out-of-scope/` entry for a tooling-tree node; there is no issue to close), so it is not asked about every pass. A `Housekeeping` cycle refused the same way simply doesn't run this pass; its `Last scan` stays, so it is due again.

**No human present to ask** (an unattended run) with `ask-each-time`. Nothing is created. The pass ends with a report that it waits for a confirmation, and adds that `Ticket-create-mode` can be set to `autonomous` in the Refactoring Notes' `bookkeeping.md` if nobody will be there to answer. Never take a recommendation as an answer — an issue is visible to everyone watching the tracker and can be closed but not un-created.

**Secret-history findings.** `refactor-learn`'s early call returns them as drafts (`refactor:priority`, the secret's value redacted); the loop creates them per the mode. The `Secret history scan` field is written `done` only once every draft has a ticket (zero findings counts) — declined or unattended → it stays absent, and the next pass runs the scan again.
