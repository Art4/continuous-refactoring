---
name: refactor-scan
description: Propose every currently-unblocked tooling-tree node from bookkeeping.md/tree state, and detect (never act on) remembered issues or merge requests that have since closed or merged.
---

# Refactor Scan

**Detect, never write.** Proposes what could be worked on next and notices what has already resolved itself since the last pass — never files an issue, never decides an outcome. `refactor-design` files issues for what gets chosen; `refactor-learn` acts on what this skill detects.

## Process

### 1. Check preconditions

- No git repository → stop the pass, report it, propose nothing.
- Five or more open `refactor:candidate` issues → stop, propose nothing new; let existing work clear first.

### 2. Resume pending work first

Read the Refactoring Notes' `bookkeeping.md`'s `Pending candidates` field (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`). If it names an issue, a prior pass's `refactor-design` filed it but was interrupted before a merge request followed. Propose exactly that issue and stop — finishing pending work comes before proposing fresh work.

### 3. Detect closed/merged remembered state

Get the remembered set — `docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab) → every open `refactor:candidate` issue, each resolved to its linked pull request via the tracker's own native issue↔closing-PR cross-reference (the `Closes #<n>` `refactor-implement` step 5 already puts on a delivering MR); an issue with no linked PR yet has nothing to reconcile this step. Otherwise → every entry in the Refactoring Notes' `merge-requests.md`. For each, check the external tracker/git: is the MR still open, is the issue still open?

No `gh`/`glab` (or other forge API/token) available → fall back to git-only reconciliation instead of skipping this step (never attempt to install `gh`/`glab` here either — treat their absence as exactly this fallback's trigger): `skills/refactor-scan/references/git-only-reconciliation.md`. No remote at all (`git remote -v` empty) → the same file's local-only variant — a remembered candidate may have been merged or rejected by a human working purely locally, per `opening-a-merge-request.md`'s "No forge/remote available".

- **Merged** → a finding: delivered.
- **Closed without merge** → a finding: declined — note whether closing comments give a maintainer's structural reason (out-of-scope material) or not.
- **Still open, with reviewer activity (a review or comment) newer than the branch's last commit** → a **resume-candidate**, not a finding — nobody has decided anything yet, it just needs another look. Checked first, regardless of the MR's draft status below (a human can comment on a draft too, and that comment still takes priority over the mechanical draft check). API access available → also read the actual review state alongside the timestamp (`gh pr view <n> --json reviews,reviewDecision` or equivalent) — don't stop at "something changed":
  - **`CHANGES_REQUESTED`, unaddressed** (no newer commit than the review) → still a resume-candidate, but hand forward the review's own comments/body along with it, not just the branch — `refactor-implement` step 1 reads and addresses that specific feedback, not just re-examines the branch from scratch.
  - **A comment, or an `APPROVED` review with no blocking feedback** → the existing generic resume-candidate handling; nothing else to attach.

  Hand it forward the same way step 2 hands forward a `Pending candidates` entry: straight to `refactor-implement`, skipping `refactor-prioritize`/`refactor-design` (it already has a design and an open MR; only the fix loop applies — `refactor-implement` step 1 already supports resuming an existing branch). No API access (git-only fallback) → review state stays unavailable exactly as `git-only-reconciliation.md` already documents; this refinement doesn't apply there.
- **Still open, no reviewer activity, still marked draft** (`opening-a-merge-request.md`'s *Draft candidate MRs*) → a finding: fold-in still owed — an earlier pass opened this candidate's MR as a draft and never reached the fold-in commit that would have marked it ready. `refactor-learn`'s early call checks out that branch and performs the same fold-in writes its closing call would have, then marks it ready. API access available → `isDraft` comes back on the same `gh pr view`/`glab mr view` call already used for state and review data above, no extra round trip. No API access (git-only fallback) → draft status is unreadable the same way review state is; this case doesn't apply there.
- **Still open, no reviewer activity, not draft (or draft status unreadable)** → no finding.

Also check every entry in the Refactoring Notes' `out-of-scope/<node>.md` naming a `**Blocked by:** PHP >= X.Y` condition (`tooling_tree.py`'s `detect_nodes()` reports this directly when run; by hand, compare against the target's current `composer.json` `require.php`/`config.platform.php`) — if the target's current PHP version now satisfies it, a finding: this rejection is reversed. No `Blocked by:` field, or condition still unmet → never a finding.

Hand every finding to `refactor-learn` — this skill only notices; it never marks anything `done`/`wontfix` and never writes to the Refactoring Notes' `out-of-scope/` itself.

### 3b. Detect externally-labeled candidates

API access available (not the git-only fallback) → also query open `refactor:candidate` issues that aren't already accounted for: not step 2's `Pending candidates` entry, not step 3's remembered set (an issue with a linked pull request is already in flight). What's left is a candidate a human (or another process) labeled directly, that this loop has never designed or implemented — in normal operation the suite's own candidates are always covered by one of those two, so nothing extra is needed to tell "ours" from "someone else's." Hand each forward as a **proposal**, the same list step 4's tooling-tree proposals join — `refactor-prioritize` ranks it alongside everything else on its usual factors; it competes on its own merits, never jumps the queue just for existing. No API access (git-only fallback) → skip this step entirely, git alone can't enumerate issues by label.

### 4. Propose tooling-tree nodes

Skip if step 2 already proposed a pending candidate.

Run `python3 skills/refactor-scan/references/tooling_tree.py <target-repo>` and read the JSON's `next` field — the real, currently-unblocked set, rejected nodes (an existing entry in the Refactoring Notes' `out-of-scope/<node>.md`) already excluded, take as-is however many entries it holds. **Not** `roadmap` (a forward simulation, not real options today). Also read `withheld`: nodes that would otherwise be in `next` but wait on an undecided recommended parent — each entry names which parent(s). No `python3`, or not permitted → dispatch a sub-agent with `skills/refactor-scan/references/tree-walk-prompt.md`'s prompt (`{N}=all`) — it walks the same tree docs by hand (reads the Refactoring Notes' `bookkeeping.md`'s `Fulfilled nodes` first to skip re-deriving cached state, skips any node with an out-of-scope entry); no sub-agent mechanism → run its steps yourself inline.

- **Ordinary tooling nodes** (`loop-config`, and language-specialization nodes, e.g. `skills/refactor-scan/references/php-tooling-tree.md`) — proposed by their **Name** (never the raw slug); each is already fully specified in its tree doc.
- **`structural-scan`** — proposed once every node with a `resolved` edge into it is resolved (fulfilled, or explicitly rejected under the Refactoring Notes' `out-of-scope/`): `editorconfig` at the generic root, plus the active language specialization's own aggregation node (PHP: `php-structural-scan`), itself resolved once every one of its own resolved-parents is resolved (`skills/refactor-scan/references/tooling-tree.md`). Only `structural-scan` is ever proposed this way — `php-structural-scan` is pure plumbing, never a candidate. Proposing it is just naming it; the codebase walk happens in `refactor-design`, only for the node actually chosen.
- **No language tree recognized**: `structural-scan` still waits on `editorconfig`, the generic-root leaf — not immediately proposable just because no language-specific tree applies.

### 4b. Detect baseline-shrink candidates

PHP tree only, for now (`skills/refactor-scan/references/php-tooling-tree/phpstan.md`'s Stop
conditions for the level chain: *"Baseline is non-empty → do not propose the next level; the loop
proposes shrinking work... until the baseline becomes empty"* — this step is that promise, kept). Read
`detected` from step 4's own `tooling_tree.py` run (no second invocation) — find the highest `N` where
`phpstan-level-N` is `fulfilled`. Its `details.baseline_empty` is `false` → propose **"PHPStan Level
N — baseline shrink"** alongside step 4's other proposals, same generic shape as how `structural-scan`
itself gets proposed (naming the gate, not yet a specific plan — `refactor-design` does the baseline
read and picks a concrete group only for the candidate actually chosen). No `phpstan-level-N` node
ever fulfilled yet, or the fulfilled one's baseline is already empty → nothing to propose here.

## Output

Handed onward by the orchestrator, plainly:

- Which precondition stopped the pass, if one did — nothing below applies this pass.
- **Findings** (possibly empty) → `refactor-learn`.
- **A resume-candidate**, if one was detected → straight to `refactor-implement`, bypassing `refactor-prioritize`/`refactor-design`.
- **Proposals** — the pending candidate alone, or every currently-unblocked node's Name (never slugs, never capped) plus any externally-labeled candidate from step 3b and any baseline-shrink candidate from step 4b, or none → `refactor-prioritize`. Every node currently unblocked (required parents fulfilled, not rejected, every recommended parent already decided) — never a priority-truncated subset. Alongside it, name every `withheld` node and which parent(s) it's waiting on (e.g. "Rector: Type Coverage Set — waiting on: PHP CS Fixer").

## Completion criterion

Findings (if any) handed to `refactor-learn`, a resume-candidate (if any) handed straight to `refactor-implement`, proposals (if any) handed to `refactor-prioritize` — or a precondition stopped the pass and the report says which. Never a node together with entries past `structural-scan` in the same list.
