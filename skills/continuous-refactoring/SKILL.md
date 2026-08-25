---
name: continuous-refactoring
description: Run one pass of the continuous refactoring loop — pick up remembered merge requests, scan, prioritise, design, implement, review, learn. Use to keep a codebase under continuous refactoring, on a cadence or on demand.
disable-model-invocation: true
---

# Continuous Refactoring

The **loop pass** — the stateful, repeatable sequence that keeps a project under continuous refactoring. Each pass does only the work due since the last pass, then records what it learned so the next pass starts from state, not from zero.

A completed candidate is delivered as a **merge request** remembered in the target repo; later passes react to that state (ADR-0006). Git is the only hard requirement — missing tools enter the language's **tooling tree** as small candidates instead of gating the loop (ADR-0005). A **required edge** gates a child until every required parent is fulfilled; a **recommended edge** only advises — the child stays proposable even when the recommended parent was rejected. `refactor-scan` checks git, the loop's own configuration, and backlog size itself before scanning anything else — the orchestrator does not duplicate those checks (ADR-0008).

Run this on demand whenever you're asked, or on the configured **cadence**.

## Loop state

State lives in the target repo, not in the conversation:

- **Config** — `docs/refactoring/config.md`: cadence, last-run date, focus areas, merge-request create-mode
- **Remembered merge requests** — `docs/refactoring/merge-requests.md`: every open suite merge request with its URL, candidate issue, and base branch
- **Backlog** — `refactor:*` issues on the issue tracker (see `docs/agents/issue-tracker.md`)
- **Learned rejections** — `docs/refactoring/out-of-scope/` entries from prior passes

Read all four at the start of every pass. `docs/refactoring/config.md` is no longer scaffolded here directly: `refactor-scan` checks for it itself (the `loop-config` node, `docs/tooling-tree.md`) and files the single candidate that creates it when it's missing (ADR-0008) — that candidate, once implemented, is the marker that a pass has real configuration to work from.

## The pass

Each numbered step runs the named lifecycle skill. Stop between steps where the skill itself stops for user input.

1. **Pick up remembered merge requests.** Work through `docs/refactoring/merge-requests.md`:
   - Review comments arrived → follow-up commits on that branch (atomic, in the repo's convention). A pass that pushed follow-ups starts no new candidate.
   - Merged → mark its candidate `done`, drop it from the remembered state.
   - Closed without merge → if the comments support a structural rejection, mark `wontfix` and file a learned rejection under `docs/refactoring/out-of-scope/`; otherwise ask the human.
   - Two merge requests still open → point the human at them; take no new candidate this pass beyond the responses above.

2. **Scan.** Run `/refactor-scan`. It checks its own preconditions first — git, loop configuration, backlog size — then files exactly one tooling-tree candidate, or a batch of structural candidates once the tree is resolved, never both in the same pass (ADR-0008). If it stops at a precondition, or reports the last scan is recent and nothing changed, stop this pass early.

3. **Prioritise.** Run `/refactor-prioritize`. It recommends an unblocked tooling-tree node when one exists; the user picks the next candidate.

4. **Design.** Run `/refactor-design` on the chosen candidate. If the candidate is tiny and the user wants to skip to implementation, that's their call — flag it, don't block.

5. **Implement.** Run `/refactor-implement`. One candidate, one branch; slices stay on that branch.

6. **Review.** Run `/refactor-review`. If findings come back, loop implement → review until clean.

7. **Learn.** Close the loop:
   - Deliver the completed candidate as a **merge request** — see `## Opening a merge request` below — remember its URL and candidate issue in `docs/refactoring/merge-requests.md`, and label the candidate `ready-for-human` (not done).
   - Record ADRs for decisions a future scan must not re-litigate (see `/domain-modeling`)
   - Update `CONTEXT.md` with any terms that crystallised
   - Stamp the last-run date in `docs/refactoring/config.md`

## Opening a merge request

The create-mode decides who opens the forge reviewable:

- Read the target repo's `AGENTS.md` / `CLAUDE.md` first. If either names a mode, follow it.
- Neither does → propose `autonomous` and record the chosen mode — `autonomous`, `ask-each-time`, or `human-opens` — in `docs/refactoring/config.md`.
- Skills always say **merge request**; conversation with the human uses the forge's native word (pull request on GitHub, merge request on GitLab).

While fewer than two suite merge requests are open, a pass may deliver one more. Stack it (base = the open branch) only when the new candidate is a tooling-tree child of what is in flight or the design depends on it; otherwise branch parallel off the default branch. After the parent merges, the next pass retargets or rebases the child.

The description is plain: link the candidate, what changed, which tests survive, what CI proves. No outlook, no type enum.

## Fallback

The suite must keep working in a target repo with none of the global skills installed. Per ADR-0003, each lifecycle skill self-contains its own step: its `## Fallback` section means "use the global skill if installed, else the inline fallback". Two fallback depths apply: **crash-safe** means skip the global skill with a note — the step's core is already inline; **self-sufficient** means the fallback inlines the part of the global skill the step uses. The orchestrator itself engages one global reference:

- **`/domain-modeling`** (learn step): if installed, use its discipline for the ADR and `CONTEXT.md` side effects. Otherwise skip with a note — the learn moves in step 7 (record the ADR, update `CONTEXT.md`, close the issue, stamp last-run) are inline and run regardless. Crash-safe.

Where each lifecycle skill's inline fallback engages, so a pass runs on the suite's own skills alone:

- **Scan** — `refactor-scan`: the candidate vocabulary is inline; a missing `codebase-design` is a crash-safe skip.
- **Design** — `refactor-design`: a missing `grilling` engages the inline grilling loop (self-sufficient); a missing `domain-modeling` is a crash-safe skip — the `CONTEXT.md`/ADR side effects run inline regardless.
- **Implement** — `refactor-implement`: a missing `tdd` engages the inline red → green rules and test-quality guidance (self-sufficient).
- **Review** — `refactor-review`: a missing `code-review` engages the inline two-axis rules and Fowler smell set (self-sufficient).

The authoritative inventory of every global reference and its fallback type lives in `docs/agents/skill-references.md` (ADR-0003) and is enforced by the Tier 1 validator (`scripts/validate_skills.py`).

## Completion criterion

One full pass completed and the loop state updated — remembered merge requests processed (comments answered, merges recorded or rejections learned), last-run stamped, and the pass's own outcome recorded: the delivered candidate sits `ready-for-human` with its merge request remembered, or the issue closed.
