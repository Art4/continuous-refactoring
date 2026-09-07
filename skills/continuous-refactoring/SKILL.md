---
name: continuous-refactoring
description: Run one pass of the continuous refactoring loop — propose, prioritise, design, implement, learn. Use to keep a codebase under continuous refactoring, on demand or via your own recurring trigger.
disable-model-invocation: true
---

# Continuous Refactoring

One **loop pass**: does only the work due since the last pass, then records what it learned so the next pass starts from state, not from zero.

This skill is a thin data pipe: it calls each lifecycle skill in order and carries that skill's output forward as the next skill's input. It decides nothing a lifecycle skill could decide — `refactor-scan` detects, `refactor-prioritize`/`refactor-design` decide, `refactor-implement` executes, `refactor-learn` writes.

A completed candidate is delivered as a **merge request** remembered in the target repo. Git is the only hard requirement — missing tools enter the language **tooling tree** as small candidates instead of gating the loop. A **required edge** gates a child until every required parent is fulfilled; a **recommended edge** only advises — the child stays proposable even when the recommended parent was rejected.

Run this on demand, or via your own recurring trigger — the loop has no schedule of its own.

## Loop state

State lives in the target repo, not the conversation. Every lifecycle skill reads it directly; each writes only the field its own step produces (`refactor-prioritize`'s Select mode files a gate-shaped candidate's issue and sets `Pending candidates`; `refactor-design` does the same for a tooling-tree node, `loop-config`, or an externally-labeled candidate — the cases Select mode never runs for; `refactor-implement` sets `Create-mode` while delivering `loop-config`) — `refactor-learn` writes everything else, and is the suite's only *dedicated* bookkeeping writer:

- **Config** — the Refactoring Notes' `bookkeeping.md`: focus areas, merge-request create-mode (decided once, during `loop-config`'s own interview — see `## Opening a merge request`), `Pending candidates`, `Fulfilled nodes` cache, `Skip streak` (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`).
- **Remembered MRs** — every open `refactor:candidate` issue with a linked pull request (the tracker's native issue↔closing-PR cross-reference), when `docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab); otherwise the Refactoring Notes' `merge-requests.md`, a committed ledger with the same facts.
- **Backlog** — `refactor:*` issues on the tracker named by `docs/agents/issue-tracker.md` — scaffolded once, during `loop-config`'s own interview (`skills/continuous-refactoring/references/loop-config-interview.md`); every place that needs "does the tracker support native labels" reads this file rather than re-deriving it from `gh`/`glab`.
- **Learned rejections** — the Refactoring Notes' `out-of-scope/` entries.

The Refactoring Notes' `bookkeeping.md` isn't scaffolded here — it's `loop-config`, a tooling-tree node like any other except one thing: `refactor-scan` proposes it, but `refactor-design` runs a human interview instead of copying the tree doc's generic spec, and `refactor-implement` creates the file with `Create-mode` already set from that interview, not left for `refactor-learn` to fill in later.

## The pass

Each step runs the named lifecycle skill and carries its output to the next. Stop between steps where the skill itself stops for user input.

Prefer dispatching each step to a fresh subagent: hand it this pass's carried-forward input, bring back only its stated `## Output`. That keeps a skill's own reasoning inside its own context instead of leaking into the orchestrator's. No subagent mechanism available → run each step inline instead, same order.

0. **Housekeeping, only if already adopted.** `bookkeeping.md`'s `Housekeeping cadence` field set (the human has run `/continuous-housekeeping` at least once before, opting in) → run its own due-check (`skills/continuous-housekeeping/SKILL.md` steps 1–2); due → run it to completion (steps 3–7) before continuing below. Field unset → skip this step entirely, no interview triggered here — `continuous-housekeeping` only ever onboards itself when invoked directly, never implicitly from this orchestrator. Either way, this step is independent of everything below it: no ranking, no shared candidate slot, no effect on `Pending candidates` or `Skip streak` — one trigger covering two genuinely separate concerns, not housekeeping folded into this pipeline's own shape (which it doesn't fit — a checklist sweep isn't a single ranked-and-designed candidate).

1. **Scan.** Run `/refactor-scan` — checks preconditions (git, backlog size) and resumes `Pending candidates` before proposing anything fresh.
   - No git repository → pass ends now, nothing else runs (not even step 6).
   - Backlog full → skip to step 5 with scan's findings, no new candidate.
   - Resume-candidate (an open MR with reviewer activity newer than its last commit) → skip straight to step 5 with it; steps 2–4 don't run.
   - Pending candidate → skip straight to step 4 (no plan comment yet) or step 5 (plan comment present, same as a resume-candidate); steps in between don't run.
   - Otherwise → **findings** (possibly empty) go to step 2, **proposals** (every unblocked node's Name, never slugs) go to step 3.

2. **Learn, early call — only if step 1 found something.** Run `/refactor-learn` on the findings before prioritising: step 3 reads the ledger, and a finding this pass just resolved (an MR merged or closed) must land there first. No findings → skip this call entirely.

3. **Prioritise.** Run `/refactor-prioritize` (Rank mode) on scan's proposals against the now-current ledger. Stops the pass (skip to step 5) if two suite MRs are already open, or every proposal is already in flight. Otherwise hands forward one chosen node with its rationale — a gate (`structural-scan`, a PHPStan baseline-shrink family) → run `/refactor-prioritize` again (Select mode, a fresh dispatch) to pick and minimally file the concrete candidate within it before continuing to step 4. Already concrete (tooling-tree node, externally-labeled candidate) → straight to step 4, Select mode doesn't run.

4. **Design.** Run `/refactor-design` on what step 3 handed forward — files (or updates) the issue itself for a tooling-tree node, `loop-config`, or an externally-labeled candidate, same as always; grounds and grills a gate-shaped candidate Select mode already filed, then adds the plan as a comment on that same issue instead. Carries the issue/plan to step 5.

5. **Implement.** Run `/refactor-implement` — one candidate, one branch, created here. Reviews its own diff (standards + spec) until clean, looping back to its own earlier steps on findings, before opening the merge request. Carries the opened MR to step 6.

6. **Learn, closing call — always**, even when nothing past step 3 ran (a pass that only did step 2 is still complete). Run `/refactor-learn` with the freshly opened MR, if any. Records it (its `Closes #<n>` link on a native tracker, or the ledger), clears `Pending candidates`, captures ADR/`CONTEXT.md` updates, writes `Fulfilled nodes` last.

## Opening a merge request

Followed by `refactor-implement` when it opens the reviewable, and by `refactor-learn` for its bookkeeping MR. Full rules — create-mode (decided once, via `loop-config`'s own interview), stacking, description, outlook — in `skills/continuous-refactoring/references/opening-a-merge-request.md`.

## Fallback

The suite must keep working in a target repo with none of the global skills installed. Each lifecycle skill's own `## Fallback` covers its step: **crash-safe** (skip the global skill with a note — the step's core is already inline) or **self-sufficient** (the fallback inlines the part of the global skill the step uses). The orchestrator engages no global skill itself.

## Closing report

Wherever the pass ends, close with exactly two lines to the human — a lifecycle skill's own `## Output` is handoff data for the *next skill*, separate from this. Name any tooling-tree node by its Name, never its slug.

Every claim in **Status** must reflect state freshly confirmed this pass, not an earlier step's stated intent — if `refactor-implement` reported CI green, that means a check run *this* pass, not a memory of what an earlier round meant to fix. When state can't be freshly confirmed (no forge/remote, or CI status unreadable via API), say so explicitly rather than reporting an assumed outcome.

- **Status:** one line, what happened this pass — mention step 0 too if it ran ("Status: housekeeping sweep delivered (MR #7); ...").
- **Next:** one line, what the human can or should do now.

**Unused housekeeping nudge.** `bookkeeping.md`'s `Housekeeping cadence` unset (step 0 never engaged, the target never opted in), and at least one `Fulfilled nodes` entry's own tree-doc names a `Housekeeping` field → append one clause to **Next** naming how many ("... also: 2 adopted tools have registered housekeeping checks nobody's using yet — run `/continuous-housekeeping` once to opt in"). Checking this reuses the same per-slug tree-doc lookup `continuous-housekeeping`'s own reconciliation step already does (`skills/continuous-housekeeping/SKILL.md` step 3) against whatever `Fulfilled nodes` this same pass's `refactor-learn` call just settled — no extra tree walk. Repeats every pass while the condition holds; stops the moment `Housekeeping cadence` is set, no tracking field needed to avoid repeating it.

Examples: "Status: no git repository found — the loop can't run here. Next: initialize git, then rerun." / "Status: 2 merge requests already open (links). Next: review/merge one; nothing else to do until then." / "Status: delivered PHPStan Level 0 — merge request #12 open. Next: review and merge; the following pass proposes PHPStan Level 1 once this lands." / "Status: Refactoring Config prepared on local branch `refactor/loop-config` — no forge/remote here, so nothing was pushed. Next: commit it yourself, or push it and open the merge request once you have forge access."

## Completion criterion

One full pass completed and loop state updated: `refactor-learn` ran at least once, `Fulfilled nodes` is written, and the pass's outcome is recorded — a delivered candidate's MR carries `Closes #<n>`, discoverable via the tracker's native linkage (or remembered in the ledger, on a local tracker), the issue closed once merged, nothing was actionable and that's reported, or (no forge/remote available) the candidate sits prepared on its own branch, handed to the human, per `opening-a-merge-request.md`.
