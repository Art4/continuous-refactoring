---
name: refactor-scan
description: Propose every currently-unblocked tooling-tree node from bookkeeping.md/tree state, and detect (never act on) remembered issues or merge requests that have since closed or merged.
---

# Refactor Scan

**Detect, never write.** Proposes what could be worked on next and notices what has already resolved itself since the last pass — never files an issue, never decides an outcome. `refactor-prioritize`/`refactor-design` file issues for what gets chosen; `refactor-learn` acts on what this skill detects.

## Process

### 1. Check preconditions

- No git repository → stop the pass, report it, propose nothing.
- Five or more open `refactor:candidate` issues without `refactor:priority` → stop, propose nothing new; let existing work clear first. Count separately from `refactor:priority` issues (`refactor-prioritize`'s Select mode: Security/Blast-Radius signal, `skills/refactor-prioritize/references/signals.md`) — those never count toward this cap, so priority admissions can't themselves choke off ordinary proposals.
- No Refactoring Notes' `bookkeeping.md` yet (`loop-config` unfulfilled) → skip steps 2 through 4c entirely and hand forward `loop-config` as the pass's only proposal (the shape step 4's Output section already describes). No `tooling_tree.py` run, no tree-doc reading needed to reach this: steps 2/3/3b all read state that only exists once `loop-config`'s own interview has scaffolded it (`Pending candidates`, the remembered set, `docs/agents/issue-tracker.md`), and no other node can be unblocked either (every one requires `loop-config` as a parent) — a target's very first pass costs one conclusion, not a walk of the whole tree.

### 2. Resume pending work first

Read the Refactoring Notes' `bookkeeping.md`'s `Pending candidates` field (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`), **and** the `Open` list of whichever Track the orchestrator's own Track-selection step selected this pass (`skills/continuous-refactoring/references/track-scheduler.md`) — a Safety Net or Guardrails Track candidate resumes the same way, just tracked separately (`skills/refactor-scan/references/safety-net-track.md`, `skills/refactor-scan/references/guardrails-track.md`). A structural (Investigation Track) candidate has no `Open` list to check here at all — it resumes purely through `Pending candidates` above, exactly as before this Track existed (`skills/refactor-scan/references/investigation-track.md`). Only the selected Track's own `Open` list is ever relevant here in practice: a Guardrails node is never unblocked until the Safety Net has fully resolved, so the two Tracks' `Open` lists can't both be non-empty at once anyway (`guardrails-track.md`'s own Scope section) — `track-scheduler.md`'s fixed tie-break order exists for when Housekeeping, which carries no such gating relationship, eventually joins (Investigation, now wired, never carries `Open` at all, so it can never be one of the Tracks competing for this particular tie-break either). If any names an issue, a prior pass got partway through this candidate before being interrupted — finishing pending work comes before proposing fresh work. Read the issue for a plan (`refactor-design`'s output — a comment for most candidate types, the issue body itself for a tooling-tree node/`loop-config`) to see how far it got:

- **No plan yet** → straight to `refactor-design`, bypassing `refactor-prioritize` (re-running Select mode risks picking a different candidate — exactly what this field prevents).
- **Plan present, `ready-for-agent` set** → straight to `refactor-implement`, bypassing `refactor-prioritize`/`refactor-design` both, same as a resume-candidate below. `refactor-design` itself keeps this label accurate in both directions once it finishes a candidate (`skills/refactor-design/references/decision-gate.md`), so presence alone is enough here — no separate flagged/unflagged tracking needed.
- **Plan present, `ready-for-agent` absent, `needs-info` present** → flagged and still waiting (an open question on the issue — `skills/refactor-design/references/decision-gate.md`) → not resumable this pass.
  - API access available (native-label tracker) → step 3b below can rediscover this same issue on any future pass regardless of `Pending candidates`. Leave the field as-is and continue below exactly as if it named nothing — a human hasn't cleared it yet, and it must not block the rest of the backlog from being worked.
  - Git-only fallback → `Pending candidates` is the *only* record this candidate exists at all; nothing can rediscover it otherwise. Don't let anything overwrite that field this pass — stop the pass here instead, reporting that the issue is still waiting on `ready-for-agent`.
- **Plan present, neither label set** → design wrote the plan but was interrupted before its own final labeling step (`refactor-design/SKILL.md` step 5's "Set `ready-for-agent`, last") — not a human waiting, a step design itself never finished. Straight to `refactor-design` again; its own idempotent checks (same step) mean it won't redo the plan itself, only complete what's missing.

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

### 3b. Detect issue-backed candidates

API access available (not the git-only fallback) → also query open `refactor:candidate` issues that aren't already accounted for: not step 2's `Pending candidates` entry, not step 3's remembered set (an issue with a linked pull request is already in flight). What's left is every candidate that already has an issue but no plan yet — a human (or another process) labeled one directly, or an earlier pass's own `refactor-prioritize` pre-filed a tooling-tree proposal (step 4 below) that hasn't won a ranking yet; nothing extra is needed to tell those apart, both are handled identically from here. Alongside each: its creation date (native tracker: `created_at`; Local Markdown: its `Filed:` line, `local-issue-tracker-template.md`) and whether it carries `refactor:priority` — `refactor-prioritize`'s own Age factor and priority override (step 2) read both directly off what's handed forward here, no second round-trip to the tracker. Hand each forward as a **proposal**, the same list step 4's tooling-tree proposals join — `refactor-prioritize` ranks it alongside everything else on its usual factors; it competes on its own merits, never jumps the queue just for existing. No API access (git-only fallback) → skip this step entirely, git alone can't enumerate issues by label.

Also among those same not-yet-accounted-for issues: one that already carries a plan (a comment, or —
for a tooling-tree node/`loop-config` — the issue body itself), not a proposal to rank.
`ready-for-agent` present → hand it forward the same way step 2 hands forward a plan-present pending
candidate: straight to `refactor-implement`, bypassing `refactor-prioritize`/`refactor-design`.
Absent, `needs-info` present → flagged and still waiting (`skills/refactor-design/references/decision-gate.md`);
no finding, no proposal; skip it silently this pass, same as an untouched open MR above — a human
hasn't gotten to it yet. Neither label present → design's own final labeling step never completed;
hand it forward straight to `refactor-design` to finish (its idempotent checks mean it won't redo the
plan itself, only complete what's missing).

### 4. Propose tooling-tree nodes

Skip if step 2 already proposed a pending candidate.

Run `python3 references/tooling_tree.py <target-repo>` — that path is relative to wherever this skill's own files are actually installed (this repo when working in the suite itself; a target repo's `.claude/skills/refactor-scan/` or `.agents/skills/refactor-scan/` once installed there), never assumed relative to the suite's own repo as the current working directory; the script resolves its own sibling tree docs the same self-relative way — and read the JSON's `next` field — the real, currently-unblocked set, rejected nodes (an existing entry in the Refactoring Notes' `out-of-scope/<node>.md`) already excluded, take as-is however many entries it holds. **Not** `roadmap` (a forward simulation, not real options today). Also read `withheld`: nodes that would otherwise be in `next` but wait on an undecided recommended parent — each entry names which parent(s). No `python3`, or not permitted → dispatch a sub-agent with `skills/refactor-scan/references/tree-walk-prompt.md`'s prompt (`{N}=all`) — it walks the same tree docs by hand (reads the Refactoring Notes' `bookkeeping.md`'s `Fulfilled nodes` first to skip re-deriving cached state, skips any node with an out-of-scope entry); no sub-agent mechanism → run its steps yourself inline.

- **Safety Net Track nodes — judged, not matched.** Reached only when the orchestrator's own Track-selection step handed this Track down as the one to run this pass (`skills/continuous-refactoring/references/track-scheduler.md`, `skills/continuous-refactoring/SKILL.md` step 0b). Before proposing (or accepting the parser's `fulfilled: false` for) any node in the Safety Net Track's own scope, follow `skills/refactor-scan/references/safety-net-track.md` first — it confirms this Track was actually selected (an `Open` entry already in flight bypasses this whole step, per step 2 above), and, when it was, judges each in-scope node's own Fulfilment check against its Purpose statement rather than trusting the parser's raw dependency-name match alone. The `psr-4` exception below is this same discipline's original, narrower instance — generalized here to every Safety Net Track node instead of one field.
- **Guardrails Track nodes — the same discipline, a second node set.** Reached only when Track selection handed this Track down instead. Follow `skills/refactor-scan/references/guardrails-track.md` the same way: it confirms this Track was selected, and judges each in-scope node (`composer-audit`, `phpmd`, `coverage-floor`, `php-minimal-version`, `phpstan-level-6` and above, `phpstan-deprecation-rules`, `semgrep` for PHP) against its own Purpose statement, unblocked only once `php-safety-net` itself is resolved.
- **Investigation Track node — gated the same way, no judgement involved.** Reached only when Track selection handed the Investigation Track down instead. Follow `skills/refactor-scan/references/investigation-track.md`: it confirms this Track was selected, then proposes `structural-scan` exactly as the bullet below always did — no Purpose-based judgement applies here at all (`structural-scan`'s own Fulfilment check was never a dependency-name match to begin with, spec's own "Out of Scope"). This Track wasn't selected → `structural-scan` is **not** proposed this pass, even once its own resolved-edge parents clear.
- **`psr-4` exception — don't take `fulfilled: false` at face value.** `detected["psr-4"]["details"]["unwired_entry_points"]` (non-empty) is a deliberately blunt, over-reporting-prone raw fact, not a verified conclusion — `php-tooling-tree/psr-4.md`'s own *"Reading a non-empty `unwired_entry_points` result"* section says the judgement call is this skill's job, not the script's. Before accepting `psr-4` as still open (in `next`, or blocking a downstream node from `next`/`withheld`) because of a non-empty `unwired_entry_points`, look at each file it names: one that never references the target's own PSR-4 root namespace and is self-evidently a dev/CI/build utility is exempt — skip it. If every named file is exempt this way, treat `psr-4` as fulfilled after all (same as if `unwired_entry_points` had come back empty); otherwise the remaining, non-exempt files are real unwired work, proposed as usual.

- **Ordinary tooling nodes** (`loop-config`, and language-specialization nodes, e.g. `skills/refactor-scan/references/php-tooling-tree.md`) — proposed by their **Name** (never the raw slug); each is already fully specified in its tree doc. Already forwarded this pass via step 3b (a prior pass's own pre-filing, `refactor-prioritize/SKILL.md` step 2, already turned it into an issue) → don't propose it again by bare Name here, it's already in the list as that issue.
- **`structural-scan`** — the Investigation Track's own node (bullet above): proposed once every node with a `resolved` edge into it is resolved (fulfilled, or explicitly rejected under the Refactoring Notes' `out-of-scope/`): `editorconfig` at the generic root, plus the active language specialization's own aggregation node (PHP: `php-safety-net`), itself resolved once every one of its own resolved-parents is resolved (`skills/refactor-scan/references/tooling-tree.md`). Only `structural-scan` is ever proposed this way — `php-safety-net` is pure plumbing, never a candidate. Proposing it is just naming it; the codebase walk happens in `refactor-prioritize`'s Select mode, only once this node actually wins ranking. **Gated on Investigation Track selection** (above) — unlike an ordinary tooling node, this is never proposed just because its own resolved-edge parents happen to clear; the orchestrator's own Track-selection step has to have handed Investigation down this pass first.
- **No language tree recognized**: `structural-scan` still waits on `editorconfig`, the generic-root leaf — not immediately proposable just because no language-specific tree applies.

### 4b. Detect baseline-shrink candidates

PHP tree only, for now (`skills/refactor-scan/references/php-tooling-tree/phpstan.md`'s Stop
conditions for the level chain: *"Baseline is non-empty → do not propose the next level; the loop
proposes shrinking work... until the baseline becomes empty"* — this step is that promise, kept). Read
`detected` from step 4's own `tooling_tree.py` run (no second invocation) — find the highest `N` where
`phpstan-level-N` is `fulfilled`. Its `details.baseline_empty` is `false` → propose **"PHPStan Level
N — baseline shrink"** alongside step 4's other proposals, same generic shape as how `structural-scan`
itself gets proposed (naming the gate, not yet a specific plan — `refactor-prioritize`'s Select mode
does the baseline read and picks a concrete group, only once this proposal actually wins ranking). No `phpstan-level-N` node
ever fulfilled yet, or the fulfilled one's baseline is already empty → nothing to propose here.

### 4c. Detect a still-owed secret history scan

Language-neutral, not scoped to any one tree — `secret-detection` itself lives at the generic root and
reads git history/file contents directly, no language-specific tooling involved
(`skills/refactor-scan/references/tooling-tree.md`'s own `secret-detection` node). Read `detected`
from step 4's own `tooling_tree.py` run (no second invocation) — `secret-detection`'s own `fulfilled`
is `true`, and the
Refactoring Notes' `bookkeeping.md`'s `Secret history scan` field is absent (never yet run, see
`skills/continuous-refactoring/references/refactoring-bookkeeping.md`) → run a full git-history scan
now, using whichever scanner `secret-detection`'s own `details.scanner` already names (the same
`tooling_tree.py` run from step 4 — no CI config re-reading needed) against the target's complete
history, reusing that scanner's own baseline mechanism
(gitleaks `--baseline-path`, detect-secrets `.secrets.baseline`, or the equivalent) so a finding
already known — filed earlier, or explicitly accepted — never resurfaces. Every new finding becomes
its own finding, handed to `refactor-learn` alongside step 3's: file/line and the scanner's own
rule/finding id, **the secret's value redacted**. `secret-detection` unfulfilled, or `Secret
history scan` already `done` → nothing to detect here — this scan runs at most once per target.

## Output

Handed onward by the orchestrator, plainly:

- Which precondition stopped the pass, if one did — nothing below applies this pass.
- **Findings** (possibly empty) → `refactor-learn`.
- **A resume-candidate**, if one was detected → straight to `refactor-implement`, bypassing `refactor-prioritize`/`refactor-design`.
- **A pending candidate**, if one was detected and resumable (step 2) → straight to `refactor-design` (no plan yet, or a plan present but neither label set — design has more to finish either way) or straight to `refactor-implement` (plan present, `ready-for-agent` set), bypassing `refactor-prioritize` either way. Found but still flagged and waiting (`needs-info` present) → not handed forward at all this pass; treated as absent.
- **A flagged candidate now carrying `ready-for-agent`** (step 3b), if one was detected → straight to `refactor-implement`, same as a pending candidate whose plan is already present.
- **Proposals** — every currently-unblocked node, by Name (never slugs) or, once pre-filed, by its issue (step 3b), never capped, plus any other issue-backed candidate from step 3b and any baseline-shrink candidate from step 4b, or none → `refactor-prioritize`. Every node currently unblocked (required parents fulfilled, not rejected, every recommended parent already decided) — never a priority-truncated subset. Alongside it, name every `withheld` node and which parent(s) it's waiting on (e.g. "Rector: Type Coverage Set — waiting on: PHP CS Fixer").

## Completion criterion

Findings (if any) handed to `refactor-learn`, a resume-candidate or a pending candidate (if any) handed straight to `refactor-implement`/`refactor-design` per above, proposals (if any) handed to `refactor-prioritize` — or a precondition stopped the pass and the report says which. Never a node together with entries past `structural-scan` in the same list. A flagged candidate still waiting on `ready-for-agent` (`needs-info` present instead), found via step 3b on a native tracker, is neither a finding nor a proposal nor handed anywhere this pass — silently skipped, same as an untouched open MR. Found instead as step 2's own `Pending candidates` entry on a git-only tracker → the pass stops here, same as any other precondition failure — nothing can rediscover this candidate later if something else overwrites that field.
