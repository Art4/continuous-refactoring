---
name: refactor-loop
description: Runs one refactoring pass — scan, prioritise, design, implement, learn — for a Track handed in by the caller. Internal — invoked by the continuous-<track> skills only, not a user entry point; aborts without a valid Track or an onboarded target.
---

# Refactor Loop

One **loop pass** for one **Track** (`CONTEXT.md`): does only the work due since the last pass, then records what it learned so the next pass starts from state, not from zero.

This skill is a thin data pipe: it calls each lifecycle skill in order and carries that skill's output forward as the next skill's input. It decides nothing a lifecycle skill could decide — `refactor-scan` detects, `refactor-prioritize`/`refactor-design` decide, `refactor-implement` executes, `refactor-learn` writes. It is also **Track-agnostic**: it never branches on a Track's name — the Track goes straight through to `refactor-scan`/`refactor-learn`, which branch per Track internally.

A completed candidate is delivered as a **merge request** remembered in the target repo. Git is the only hard requirement — missing tools enter the language **tooling tree** as small candidates instead of gating the loop. A **required edge** gates a child until every required parent is fulfilled; a **recommended edge** only advises — the child stays proposable even when the recommended parent was rejected.

Not a user entry point: which Track runs is decided by `continuous-refactoring` (or named by a human directly), and one of the `continuous-<track>` skills hands it down. Invoked by them only.

## Input

**Track** — mandatory. One of `safety-net`, `guardrails`, `investigation`, passed by the invoking `continuous-<track>` skill. The Housekeeping Track is not valid input here: it has its own process (`continuous-housekeeping`) and never runs the pass below.

Track missing, empty, or anything else → **abort now**: nothing runs, not even step 6. Report "refactor-loop needs a Track (`safety-net`, `guardrails`, or `investigation`) and was given none / <what it was given> — invoke `/continuous-refactoring`, or the matching `continuous-<track>` skill, instead." Never infer, default, or guess a Track from repo state.

**Onboarded target** — the Refactoring Notes' `bookkeeping.md` must exist (`skills/continuous-refactoring/references/refactoring-bookkeeping.md` says where the Refactoring Notes live). Missing → abort now, same as a missing Track: nothing runs, not even step 6. Report it as `refactoring-bookkeeping.md`'s *Not onboarded yet* section says.

This skill never runs Track selection and never reads another Track's bookkeeping state — the caller already settled which Track runs.

## Loop state

State lives in the target repo, not the conversation. Every lifecycle skill reads it directly; each writes only the field its own step produces (`refactor-prioritize`'s Select mode files a gate-shaped candidate's issue and sets `Pending candidates`; `refactor-design` does the same for a tooling-tree node or an externally-labeled candidate — the cases Select mode never runs for) — `refactor-learn` writes everything else, and is the suite's only *dedicated* bookkeeping writer:

- **Config** — the Refactoring Notes' `bookkeeping.md`: focus areas, merge-request create-mode (decided once, during the dispatcher's onboarding step — see `## Opening a merge request`), `Pending candidates`, and every currently-wired **Track**'s (`CONTEXT.md`) own bookkeeping section — `## Safety Net`, `## Guardrails`, `## Housekeeping`, `## Investigation` (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`).
- **Remembered MRs** — every open `refactor:candidate` issue with a linked pull request (the tracker's native issue↔closing-PR cross-reference), when `docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab); otherwise the Refactoring Notes' `merge-requests.md`, a committed ledger with the same facts.
- **Backlog** — `refactor:*` issues on the tracker named by `docs/agents/issue-tracker.md` — scaffolded once, during the dispatcher's onboarding step (`skills/continuous-refactoring/references/onboarding-setup-interview.md`); every place that needs "does the tracker support native labels" reads this file rather than re-deriving it from `gh`/`glab`.
- **Learned rejections** — the Refactoring Notes' `out-of-scope/` entries.

The Refactoring Notes' `bookkeeping.md` isn't scaffolded here — `continuous-refactoring`'s onboarding step writes it (the `onboarding-setup` node, fulfilled before any Track runs), with `Create-mode` already set from its interview. This skill only checks that it exists (`## Input`).

## Process

Before step 1, tell the human in one sentence that a loop pass is starting now, naming the Track (e.g. "Starting a refactoring loop pass for the Guardrails Track."). Only after the Track input and the onboarded-target check pass — an aborted invocation announces nothing.

Each step runs the named lifecycle skill and carries its output to the next. Stop between steps where the skill itself stops for user input.

Whenever a step stops the pass early — a precondition, a full backlog, two MRs already open, a breaking-change finding — tell the human at once, in one or a few sentences, what stopped it and why, before the closing report. Never end a pass silently.

Prefer dispatching each step to a fresh subagent: hand it this pass's carried-forward input, bring back only its stated `## Output`. That keeps a skill's own reasoning inside its own context instead of leaking into this one's. No subagent mechanism available → run each step inline instead, same order.

1. **Scan.** Tell the human in one sentence what is starting in a subagent — walking through the Track's open items when its own `Open` list is non-empty (e.g. "Walking through the open items in a subagent."), otherwise a fresh scan (e.g. "Starting a fresh scan in a subagent.") — then run `/refactor-scan` in a fresh subagent — for this step always, not merely preferred — told this pass's Track (the required input above). No subagent mechanism available → run it inline and say so in that one sentence instead. Checks preconditions (git, backlog size) and resumes `Pending candidates` before proposing anything fresh. A Track's own `Open` list, when it carries one, is walked by `refactor-scan` itself (`skills/refactor-scan/references/track-open-processing.md`) — `refactor-scan` doesn't decide for itself which Track is due; this skill's caller already did, and this skill hands the answer down as input.
   - No git repository → pass ends now, nothing else runs (not even step 6).
   - Backlog full → skip to step 5 with scan's findings, no new candidate.
   - Resume-candidate (an open MR with reviewer activity newer than its last commit) → skip straight to step 5 with it; steps 2–4 don't run.
   - Pending candidate, resumable → skip straight to step 4 (no plan yet, or a plan present but neither label set — `refactor-design` has more to finish either way) or step 5 (plan present, `ready-for-agent` set); steps in between don't run. Pending candidate found but still flagged and waiting (`needs-info` present, `skills/refactor-design/references/decision-gate.md`) → native tracker → treated as though none was found, continue below; git-only fallback → the pass ends here instead (`refactor-scan/SKILL.md` step 2) — `Pending candidates` is the only record of it, so nothing else may file over that field this pass.
   - **Track `Open` walk** (a Track that carries an `Open` list) → scan walks the Track's `Open` list itself (`skills/refactor-scan/references/track-open-processing.md`) and hands its outcome forward: the one workable node it worked, any **fulfilled at pick-up** findings — nodes its re-check found already adopted, which step 2's `refactor-learn` call removes from `Open` — and any non-workable nodes with their reasons, for the closing report (step 6).
   - A flagged candidate found already carrying `ready-for-agent` (`refactor-scan` step 3b) → skip straight to step 5, same as a resume-candidate; steps 2–4 don't run.
   - Otherwise → **findings** (possibly empty) go to step 2, **proposals** (every unblocked node's Name, never slugs) go to step 3.

2. **Learn, early call — only if step 1 found something.** Run `/refactor-learn` on the findings before prioritising: step 3 reads the ledger, and a finding this pass just resolved (an MR merged or closed, or a Track `Open` node found fulfilled at pick-up) must land there first. No findings → skip this call entirely.

3. **Prioritise.** Run `/refactor-prioritize` (Rank mode) on scan's proposals against the now-current ledger. Stops the pass (skip to step 5) if every proposal is already in flight. Otherwise hands forward one chosen node with its rationale — a gate (`structural-scan`, a PHPStan baseline-shrink family) → run `/refactor-prioritize` again (Select mode, a fresh dispatch) to pick and minimally file the concrete candidate within it before continuing to step 4. Already concrete (tooling-tree node, externally-labeled candidate) → straight to step 4, Select mode doesn't run.

4. **Design.** Run `/refactor-design` on what step 3 handed forward — files (or updates) the issue itself for a tooling-tree node or an externally-labeled candidate, same as always; grounds and grills a gate-shaped candidate Select mode already filed, then adds the plan as a comment on that same issue instead. Carries the issue/plan to step 5. Grounding/grilling (or planning a PHPStan baseline-shrink fix) may instead apply the decision gate (`skills/refactor-design/references/decision-gate.md`): a flagged decision still carries the issue/plan forward, but step 5's own precondition then holds it back; a genuine breaking change carries a finding forward to step 6 instead, and step 5 doesn't run at all this pass for this candidate.

5. **Implement.** Skip entirely when step 4 didn't produce a confirmed, implementable plan this pass — a flagged candidate still missing `ready-for-agent`, or a breaking-change finding handed to step 6 instead; continue at step 6 either way. **Cap gate — new MRs only.** If this step would open a *new* merge request, count the in-flight suite MRs first — the same remembered set `refactor-prioritize` step 1 reads (against this pass's now-reconciled ledger); two or more open → don't run `/refactor-implement`: the candidate keeps its plan and stays pending for a later pass, tell the human which MRs are waiting and that the pass ends without new work, then continue at step 6. Applies on every path into this step — a Track `Open` walk and a `Pending candidates` resume never pass through `refactor-prioritize`. Continuing an already-open MR (a resume-candidate with reviewer activity) opens no new MR and isn't gated. Otherwise: tell the human in one sentence that implementation is starting in a subagent (e.g. "Starting the implementation in a subagent."), then run `/refactor-implement` in a fresh subagent — always, not merely preferred; no subagent mechanism → inline, and say so in that sentence instead — one candidate, one branch, created here. Reviews its own diff (standards + spec) until clean, looping back to its own earlier steps on findings, before opening the merge request. Carries the opened MR to step 6.

   A subagent can't ask the human or reliably reach the forge, so it hands back instead of stalling: its output names the branch and commits, plus whatever it couldn't do — seams the plan doesn't record as confirmed (nothing written yet), a create-mode that asks the human (`ask-each-time`, `human-opens`), or a failed push, MR creation, or CI-status read. This skill then finishes that part itself, in its own context: confirms the seams with the human and re-dispatches, or pushes and opens the MR per `skills/continuous-refactoring/references/opening-a-merge-request.md` (draft or not as that reference says), and reads the CI status. Never treat a hand-back as a finished step 5 until the MR is open, or no forge/remote is available at all.

6. **Learn, closing call — always**, even when nothing past step 3 ran (a pass that only did step 2 is still complete). Run `/refactor-learn` with the freshly opened MR, if any, or the design-time breaking-change finding step 4 produced instead (`decision-gate.md`) — that finding gets the same rejection treatment (`wontfix`, closing note or `out-of-scope/`) a load-bearing MR-review rejection already gets. Records a delivered candidate (its `Closes #<n>` link on a native tracker, or the ledger), clears `Pending candidates`, captures ADR/`CONTEXT.md` updates — and, when the pass's Track carries its own bookkeeping section, updates that section instead of (or as well as) the ledger, per the Track's own write file under `skills/refactor-learn/references/` (`safety-net-write.md`, `guardrails-write.md`, `investigation-write.md`) — this skill never branches on which Track it is.

## Opening a merge request

Followed by `refactor-implement` when it opens the reviewable, and by `refactor-learn` for its bookkeeping MR. Full rules — create-mode (decided once, during the dispatcher's onboarding step), basing, description — in `skills/continuous-refactoring/references/opening-a-merge-request.md`. The tooling-tree candidate's own outlook comment (what it unlocks next) lives on the issue instead — `skills/refactor-implement/references/outlook-comment.md`.

## Fallback

The suite must keep working in a target repo with none of the global skills installed. Each lifecycle skill's own `## Fallback` covers its step: **crash-safe** (skip the global skill with a note — the step's core is already inline) or **self-sufficient** (the fallback inlines the part of the global skill the step uses). This skill engages no global skill itself.

## Closing report

Wherever the pass ends, close with exactly two lines to the human — a lifecycle skill's own `## Output` is handoff data for the *next skill*, separate from this. Name any tooling-tree node by its Name, never its slug.

Every claim in **Status** must reflect state freshly confirmed this pass, not an earlier step's stated intent — if `refactor-implement` reported CI green, that means a check run *this* pass, not a memory of what an earlier round meant to fix. When state can't be freshly confirmed (no forge/remote, or CI status unreadable via API), say so explicitly rather than reporting an assumed outcome.

- **Status:** one line, what happened this pass. When a Track's `Open` was walked this pass, include any skipped non-workable nodes with their reason (e.g. "Skipped: phpstan-level-6 (blocked by phpstan-level-5), coverage-floor (needs-info)").
- **Next:** one line, what the human can or should do now.

Examples: "Status: design flagged issue #12 for confirmation before implementing — ready-for-agent needed. Next: review the open question on issue #12 and add ready-for-agent once satisfied." / "Status: no git repository found — the loop can't run here. Next: initialize git, then rerun." / "Status: 2 merge requests already open (links). Next: review/merge one; nothing else to do until then." / "Status: delivered PHPStan Level 0 — merge request #12 open. Next: review and merge; the following pass proposes PHPStan Level 1 once this lands."

## Completion criterion

One full pass completed for the given Track and loop state updated: `refactor-learn` ran at least once, and the pass's outcome is recorded — a delivered candidate's MR carries `Closes #<n>`, discoverable via the tracker's native linkage (or remembered in the ledger, on a local tracker), the issue closed once merged, nothing was actionable and that's reported, or (no forge/remote available) the candidate sits prepared on its own branch, handed to the human, per `opening-a-merge-request.md`.
