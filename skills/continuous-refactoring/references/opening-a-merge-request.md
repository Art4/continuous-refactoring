# Opening a merge request

Rules for any suite skill opening or basing a merge request (MR): `refactor-implement` for a candidate, and the Housekeeping Track's own process for its cycle.

**MR-create-mode.** Read the `MR-create-mode` field of the config file (`.scratch/refactor/config.md`, `refactoring-bookkeeping.md`'s *The config file*) and follow it — `autonomous`, `ask-each-time`, or `human-opens`. Decided exactly once, per person and machine, during the dispatcher's onboarding step (`onboarding-setup-interview.md`) — not inferred fresh per merge request. A field the file doesn't state, or no config file at all, reads as `human-opens`: the loop prepares the branch and the human opens it, and the closing report says the default applied. The separate `Ticket-create-mode` (how issues get created, `filing-a-ticket.md`) never governs merge requests.

**Vocabulary.** Skills always say **merge request**; talking to the human, use the forge's own word (pull request on GitHub, merge request on GitLab).

**Basing.** While fewer than two suite MRs are open, a pass may deliver one more — always branch it directly off the default branch, never off another still-open suite branch. Holds regardless of whether the new candidate is a tooling-tree child of what's in flight, and regardless of whether the branch it might otherwise base on carries the same candidate's own earlier step or a genuinely different one — no case stacks. Branches dependent on each other's merge order would be exposed to a forge silently auto-closing one of them the moment its base branch gets deleted.

**Description.** Opens with one or two plain sentences for a human who doesn't know the suite's vocabulary — what this unlocks for the project, not which tree node it fulfils. Then the plain facts: link the candidate, what changed, which tests survive, what CI proves. Same audience rule throughout the description, not just its opening sentence — `forge-facing-writing.md`.

**Housekeeping mention.** This MR's own tooling-tree node names a `Housekeeping` field, contributed to `docs/refactoring/housekeeping-template.md` per that node's own entry → say so, one line, in the same plain-facts block: what got registered — the Housekeeping Track (`../../continuous-housekeeping/references/housekeeping-track.md`) picks it up automatically on its own cadence, no separate opt-in step needed. If this MR is the first thing to ever create that file on this target, say that too — the first housekeeping check on this repo is worth a human noticing, not just a diff they might skim past.

**No forge/remote available.** `git remote -v` (or equivalent) shows nothing, or the configured remote can't be reached — there is nowhere to push to, in any MR-create-mode. This is not the same situation `git-only-reconciliation.md` covers (that's "a remote exists, only the API is unavailable") — here there's no remote at all. Don't invent a substitute: no local-only "merge request," no direct commit to the default branch. Stop at this step and hand the branch to the human with both options named:

- **They commit it themselves** — merge or cherry-pick the branch into the default branch by hand, skipping review. Reasonable for a low-stakes change.
- **They push and open the merge request themselves**, once forge access exists — the branch and its commits stay exactly as prepared, nothing about them changes.

Name the branch and what it contains in the closing report. Leave the candidate's own state exactly as if its merge request were still open (label, `Pending candidates`) — a later pass detects it delivered once the human's own action lands it, via `git-only-reconciliation.md`'s no-remote variant, the same as any merge request closing outside the loop's own action.
