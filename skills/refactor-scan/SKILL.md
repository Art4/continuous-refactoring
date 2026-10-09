---
name: refactor-scan
description: Propose every currently-unblocked tooling-tree node from bookkeeping.md/tree state, and detect (never act on) remembered issues or merge requests that have since closed or merged.
---

# Refactor Scan

**Detect, never write.** Proposes what could be worked on next and notices what has already resolved itself since the last pass — never files an issue, never decides an outcome. `refactor-prioritize` drafts issues for the proposals, `refactor-loop` creates them and `refactor-design` writes the plan onto the chosen one; `refactor-learn` acts on what this skill detects.

## Process

### 1. Check preconditions

- No git repository → stop the pass, report it, propose nothing.
- Five or more open `refactor:candidate` issues without `refactor:priority` → stop, propose nothing new; let existing work clear first. Count separately from `refactor:priority` issues (`refactor-prioritize`'s Select mode: Security/Blast-Radius signal, `../refactor-prioritize/references/signals.md`) — those never count toward this cap, so priority admissions can't themselves choke off ordinary proposals.

Whenever a precondition above stops the pass, tell the human right away, in one or a few sentences, which one stopped it and why (e.g. "No git repository found — the loop needs one, so nothing was proposed this pass.") — before, and in addition to, `refactor-loop`'s closing report.

### 2. Resume pending work first

Read the `Open` of whichever Track the orchestrator's own Track-selection step selected this pass
(`../continuous-refactoring/references/track-scheduler.md`) from the Refactoring Notes'
`bookkeeping.md` (`../continuous-refactoring/references/refactoring-bookkeeping.md`) — the only state
this step reads, never another Track's: a non-empty Safety Net or Guardrails `Open` isn't resumed entry-by-entry
but walked, per `references/track-open-processing.md` (workability triage, the pick-up Fulfilment
re-check, exactly one node worked per pass, its issue filed only then, by `refactor-design`, never by
the walk), routed there by each Track's own reference file (`references/safety-net-track.md`,
`references/guardrails-track.md`); a non-empty **Investigation** `Open` is read entry-by-entry instead —
no Fulfilment-based workability triage, since every entry already carries a plan by construction — per
`references/investigation-track.md`, applying the per-entry logic below to whichever entry still has
design/implement work outstanding. Selected Track other than Investigation → its own `Open` is what's read here; `## Investigation`'s
`Open` is left untouched and unread, whatever it names — resuming an Investigation candidate is that
Track's own job, only when it's the one selected. If `## Investigation`'s own `Open` names an issue
(possibly several — apply what follows to each entry in turn), a prior pass got partway through before being interrupted — finishing pending work comes before
proposing fresh work. Read the issue for a plan (`refactor-design`'s output — a comment for most
candidate types, the issue body itself for a tooling-tree node) to see how far it got:

- **No plan yet** → straight to `refactor-design`, bypassing `refactor-prioritize` (re-running Select mode risks picking a different candidate — exactly what this entry prevents).
- **Plan present, `ready-for-agent` set** → straight to `refactor-implement`, bypassing `refactor-prioritize`/`refactor-design` both, same as a resume-candidate below. `refactor-design` itself keeps this label accurate in both directions once it finishes a candidate (`../refactor-design/references/decision-gate.md`), so presence alone is enough here — no separate flagged/unflagged tracking needed.
- **Plan present, `ready-for-agent` absent, `needs-info` present** → flagged and still waiting (an open question on the issue — `../refactor-design/references/decision-gate.md`) → not resumable this pass.
  - API access available (native-label tracker) → check the issue's most recent comment first: newer than `refactor-design`'s own flagging comment, and from a human, not the suite's own bot account → hand it forward straight to `refactor-design` instead (a human answered; `../refactor-design/references/decision-gate.md`'s "A flagged candidate's human answer arrives" judges it) — bypassing `refactor-prioritize` the same as the labeled cases above. No such comment (nobody's answered, or the suite's own nudge is already the newest entry) → step 3b below can rediscover this same issue on any future pass regardless of this entry. Leave the entry as-is and continue below exactly as if it weren't there — a human hasn't cleared it yet, and it must not block the rest of the backlog from being worked.
  - Git-only fallback → this entry is the *only* record this candidate exists at all; nothing can rediscover it otherwise — stop the pass here, reporting that the issue is still waiting on `ready-for-agent`.
- **Plan present, neither label set** → design wrote the plan but was interrupted before its own final labeling step (`refactor-design/SKILL.md` step 5's "Set `ready-for-agent`, last") — not a human waiting, a step design itself never finished. Straight to `refactor-design` again; its own idempotent checks (same step) mean it won't redo the plan itself, only complete what's missing.

### 3. Detect closed/merged remembered state

Get the remembered set — `docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab) → every open `refactor:candidate` issue, each resolved to its linked pull request via the tracker's own native issue↔closing-PR cross-reference (the `Closes #<n>` `refactor-implement` step 5 already puts on a delivering MR); an issue with no linked PR yet has nothing to reconcile this step. Otherwise → every entry in the Refactoring Notes' `merge-requests.md`. For each, check the external tracker/git: is the MR still open, is the issue still open?

No `gh`/`glab` (or other forge API/token) available → fall back to git-only reconciliation instead of skipping this step (never attempt to install `gh`/`glab` here either — treat their absence as exactly this fallback's trigger): `references/git-only-reconciliation.md`. No remote at all (`git remote -v` empty) → the same file's local-only variant — a remembered candidate may have been merged or rejected by a human working purely locally, per `opening-a-merge-request.md`'s "No forge/remote available".

- **Merged** → a finding: delivered.
- **Closed without merge** → a finding: declined — note whether closing comments give a maintainer's structural reason (out-of-scope material) or not.
- **Still open, with reviewer activity (a review or comment) newer than the branch's last commit** → a **resume-candidate**, not a finding — nobody has decided anything yet, it just needs another look. Checked first, regardless of the MR's draft status below (a human can comment on a draft too, and that comment still takes priority over the mechanical draft check). API access available → also read the actual review state alongside the timestamp (`gh pr view <n> --json reviews,reviewDecision` or equivalent) — don't stop at "something changed":
  - **`CHANGES_REQUESTED`, unaddressed** (no newer commit than the review) → still a resume-candidate, but hand forward the review's own comments/body along with it, not just the branch — `refactor-implement` step 1 reads and addresses that specific feedback, not just re-examines the branch from scratch.
  - **A comment, or an `APPROVED` review with no blocking feedback** → the existing generic resume-candidate handling; nothing else to attach.

  Hand it forward the same way step 2 hands forward a plan-present `Open` entry: straight to `refactor-implement`, skipping `refactor-prioritize`/`refactor-design` (it already has a design and an open MR; only the fix loop applies — `refactor-implement` step 1 already supports resuming an existing branch). No API access (git-only fallback) → review state stays unavailable exactly as `git-only-reconciliation.md` already documents; this refinement doesn't apply there.
- **Still open, no reviewer activity** → no finding.

Also check every entry in the Refactoring Notes' `out-of-scope/<node>.md` naming a `**Blocked by:** PHP >= X.Y` condition (`tooling_tree.py`'s `reversals` output — `php_version_reversal_findings()` — reports this directly when run; by hand, compare against the target's current `composer.json` `require.php`/`config.platform.php`) — if the target's current PHP version now satisfies it, a finding: this rejection is reversed. No `Blocked by:` field, or condition still unmet → never a finding.

Hand every finding to `refactor-learn` — this skill only notices; it never marks anything `done`/`wontfix` and never writes to the Refactoring Notes' `out-of-scope/` itself.

### 3b. Detect issue-backed candidates

**Track-scoped.** A candidate that is *not* a tooling-tree node's — its issue isn't titled `Tooling tree: <Name>`: a structural candidate an earlier Investigation pass filed, or a human's own `refactor:candidate` — belongs to the Investigation Track. It is picked up only when Investigation is the Track selected this pass (`../continuous-refactoring/references/track-scheduler.md`), never in a Safety Net or Guardrails pass, so a Track with nothing left to do doesn't fill its pass with another Track's work. In those passes skip it silently (no proposal, no resume, not even a plan-present one below) and report only how many such candidates are waiting for an Investigation pass. One thing stays open to every pass: a candidate carrying `refactor:priority` (a human set it on purpose — it never waits behind a Track order). A tooling-tree node's own issue is handled as before, in any pass.

API access available (not the git-only fallback) → also query open `refactor:candidate` issues that aren't already accounted for: not an entry of the `Open` step 2 read, not step 3's remembered set (an issue with a linked pull request is already in flight). What's left is every candidate that already has an issue but no plan yet — a human (or another process) labeled one directly, or an earlier pass's own `refactor-prioritize` pre-filed a tooling-tree proposal (step 4 below) that hasn't won a ranking yet; nothing extra is needed to tell those apart, both are handled identically from here. Alongside each: its creation date (native tracker: `created_at`; Local Markdown: its `Filed:` line, `local-issue-tracker-template.md`) and whether it carries `refactor:priority` — `refactor-prioritize`'s own Age factor and priority override (step 2) read both directly off what's handed forward here, no second round-trip to the tracker. Hand each forward as a **proposal**, the same list step 4's tooling-tree proposals join — `refactor-prioritize` ranks it alongside everything else on its usual factors; it competes on its own merits, never jumps the queue just for existing. No API access (git-only fallback) → skip this step entirely, git alone can't enumerate issues by label.

Also among those same not-yet-accounted-for issues: one that already carries a plan (a comment, or —
for a tooling-tree node — the issue body itself), not a proposal to rank.
`ready-for-agent` present → hand it forward the same way step 2 hands forward a plan-present `Open`
entry: straight to `refactor-implement`, bypassing `refactor-prioritize`/`refactor-design`.
Absent, `needs-info` present → flagged and still waiting (`../refactor-design/references/decision-gate.md`).
Check its most recent comment: newer than the flagging comment, from a human, not the suite's own bot
account → a human answered; hand it forward straight to `refactor-design` instead (its "A flagged
candidate's human answer arrives" judges it) — no finding, no proposal, but not silently
skipped either. No such comment → no finding, no proposal; skip it silently this pass, same as an
untouched open MR above — a human hasn't gotten to it yet. Neither label present → design's own final labeling step never completed;
hand it forward straight to `refactor-design` to finish (its idempotent checks mean it won't redo the
plan itself, only complete what's missing).

### 4. Propose tooling-tree nodes

Skip if step 2 already handed an `Open` entry forward.

`references/tooling_tree.py` holds only the tree's graph logic: which nodes are fulfilled is handed to it, and it answers what that state unblocks. Its path is relative to wherever this skill's own files are installed (this repo when working in the suite itself; a target repo's `.claude/skills/refactor-scan/` or `.agents/skills/refactor-scan/` once installed there), and it resolves its sibling tree docs the same self-relative way.

**Safety Net or Guardrails scan** — the agent judges, the script orders:

1. **Judge** the Fulfilment check of every node in the selected Track's scope, gate nodes included, per that Track's own file (bullets below).
2. **Write the seed**: a JSON file `{"<slug>": true|false}` in a temporary location outside the target repo. A node left out counts as not fulfilled.
   - A node in the selected Track's scope, or outside every Track (`is-php-project`, `onboarding-setup`) → your judgement from 1.
   - A node in the other Track's scope → `true` when that Track's `bookkeeping.md` section exists and lists the node under neither `Open` nor `Out-of-scope`; otherwise `false` — a missing section means that Track never ran.
3. **Run** `python3 references/tooling_tree.py --seed <seed-file> <target-repo>` — a seed it cannot read ends in an error, never in an answer from some other state: fix the file and rerun — and read from its JSON:
   - `next` — the currently-unblocked set, rejected nodes (an entry in the Refactoring Notes' `out-of-scope/<node>.md`) already excluded; take it as-is, however many entries it holds.
   - `withheld` — nodes that would be in `next` but wait on an undecided recommended parent; each entry names which parent(s).
   - `backlog` — every unresolved node in tree order, blocked ones included. Its entries inside the selected Track's scope, order kept, are that Track's new `Open` (`## Output`).

**Investigation pass** — nothing to judge, no seed: run `python3 references/tooling_tree.py <target-repo>`. The script then reads the fulfilled set from `bookkeeping.md`'s Track sections by the rule in 2's second bullet, applied to both Tracks.

No `python3`, or not permitted → dispatch a sub-agent with `references/tree-walk-prompt.md`'s prompt (`{N}=all`) — it walks the same tree docs by hand (skips any node with an out-of-scope entry); no sub-agent mechanism → run its steps yourself inline.

- **Safety Net Track nodes — judged, not matched.** Reached only when the orchestrator's own Track-selection step handed this Track down as the one to run this pass (`../continuous-refactoring/references/track-scheduler.md`, `../continuous-refactoring/SKILL.md` step 1). Before judging any node in the Safety Net Track's own scope, follow `references/safety-net-track.md` first — it confirms this Track was actually selected (an `Open` entry already in flight bypasses this whole step, per step 2 above), and, when it was, judges each in-scope node's own Fulfilment check against its Purpose statement rather than by a raw dependency-name match alone. The `psr-4` exception below is this same discipline's original, narrower instance — generalized here to every Safety Net Track node instead of one field.
- **Guardrails Track nodes — the same discipline, a second node set.** Reached only when Track selection handed this Track down instead. Follow `references/guardrails-track.md` the same way: it confirms this Track was selected, and judges each in-scope node (`composer-audit`, `phpmd`, `coverage-floor`, `php-minimal-version`, `phpstan-level-6` and above, `phpstan-deprecation-rules`, `semgrep` for PHP) against its own Purpose statement, unblocked only once `php-safety-net` itself is resolved.
- **Investigation Track node — gated the same way, no judgement involved.** Reached only when Track selection handed the Investigation Track down instead. Follow `references/investigation-track.md`: it confirms this Track was selected, then proposes `structural-scan` exactly as the bullet below always did — no Purpose-based judgement applies here at all (`structural-scan`'s own Fulfilment check was never a dependency-name match to begin with, spec's own "Out of Scope"). This Track wasn't selected → `structural-scan` is **not** proposed this pass, even once its own resolved-edge parents clear.
- **`psr-4` exception — the entry-point walk over-reports; judge each file it flags.** Judging `psr-4`'s Fulfilment check (its criterion-2 entry-point walk, `php-tooling-tree/psr-4.md`'s own *"Reading a non-empty `unwired_entry_points` result"* section) yields a deliberately blunt, over-reporting-prone raw fact — every candidate file the walk flags as unwired — not a verified conclusion; the judgement call is this skill's job. Before judging `psr-4` unfulfilled because of a flagged file, look at each one: a file that never references the target's own PSR-4 root namespace and is self-evidently a dev/CI/build utility is exempt — skip it. If every flagged file is exempt this way, treat `psr-4` as fulfilled after all; otherwise the remaining, non-exempt files are real unwired work, proposed as usual.

- **Ordinary tooling nodes** (generic-root and language-specialization nodes, e.g. `references/php-tooling-tree.md`) — proposed by their **Name** (never the raw slug); each is already fully specified in its tree doc. Already forwarded this pass via step 3b (a prior pass's own pre-filing, `refactor-prioritize/SKILL.md` step 2, already turned it into an issue) → don't propose it again by bare Name here, it's already in the list as that issue.
- **`structural-scan`** — the Investigation Track's own node (bullet above): proposed once every node with a `resolved` edge into it is resolved (fulfilled, or explicitly rejected under the Refactoring Notes' `out-of-scope/`): `editorconfig` at the generic root, plus the active language specialization's own aggregation node (PHP: `php-safety-net`), itself resolved once every one of its own resolved-parents is resolved (`references/tooling-tree.md`). Only `structural-scan` is ever proposed this way — `php-safety-net` is pure plumbing, never a candidate. Proposing it is just naming it; the codebase walk happens in `refactor-prioritize`'s Select mode, only once this node actually wins ranking. **Gated on Investigation Track selection** (above) — unlike an ordinary tooling node, this is never proposed just because its own resolved-edge parents happen to clear; the orchestrator's own Track-selection step has to have handed Investigation down this pass first.
- **No language tree recognized**: `structural-scan` still waits on `editorconfig`, the generic-root leaf — not immediately proposable just because no language-specific tree applies.

### 4b. Detect baseline-shrink candidates

PHP tree only, for now (`references/php-tooling-tree/phpstan.md`'s Stop
conditions for the level chain: *"Baseline is non-empty → do not propose the next level; the loop
proposes shrinking work... until the baseline becomes empty"* — this step is that promise, kept). In
the fulfilled set step 4 worked with — the seed in a Safety Net or Guardrails scan, `bookkeeping.md`'s
Track sections read by step 4's rule otherwise — find the highest `N` where `phpstan-level-N` is
fulfilled. Check that level's baseline yourself, per `phpstan.md`'s
own *Empty baseline* operational definition (`phpstan-baseline.neon` absent at the repo root, or
present with an empty `parameters.ignoreErrors`): non-empty → propose **"PHPStan Level
N — baseline shrink"** alongside step 4's other proposals, same generic shape as how `structural-scan`
itself gets proposed (naming the gate, not yet a specific plan — `refactor-prioritize`'s Select mode
does the baseline read and picks a concrete group, only once this proposal actually wins ranking). No `phpstan-level-N` node
ever fulfilled yet, or the fulfilled one's baseline is already empty → nothing to propose here.

### 4c. Detect a still-owed secret history scan

Language-neutral, not scoped to any one tree — `secret-detection` itself lives at the generic root and
reads git history/file contents directly, no language-specific tooling involved
(`references/tooling-tree.md`'s own `secret-detection` node). `secret-detection` is fulfilled in the
fulfilled set step 4 worked with (the seed in a Safety Net or Guardrails scan, `bookkeeping.md`'s
Track sections read by step 4's rule otherwise), and the Refactoring Notes' `bookkeeping.md`'s `Secret history scan` field is
absent (never yet run, see
`../continuous-refactoring/references/refactoring-bookkeeping.md`) → run a full git-history scan
now, using whichever scanner the target's own committed secret-scanning setup invokes — the same CI
job/config the fulfilment judgement for this node just read (`secret-detection.md`'s own Fulfilment
check names the recognized scanners) — against
the target's complete
history, reusing that scanner's own baseline mechanism
(gitleaks `--baseline-path`, detect-secrets `.secrets.baseline`, or the equivalent) so a finding
already known — filed earlier, or explicitly accepted — never resurfaces. Every new finding becomes
its own finding, handed to `refactor-learn` alongside step 3's (which returns its drafts to `refactor-loop`, `filing-a-ticket.md`): file/line and the scanner's own
rule/finding id, **the secret's value redacted**. `secret-detection` unfulfilled, or `Secret
history scan` already `done` → nothing to detect here — this scan runs at most once per target.

## Output

Handed onward by `refactor-loop`, plainly — this skill writes nothing, so it has no writes to name:

- Which precondition stopped the pass, if one did — nothing below applies this pass.
- **Findings** (possibly empty) → `refactor-learn`.
- **A resume-candidate**, if one was detected → straight to `refactor-implement`, bypassing `refactor-prioritize`/`refactor-design`.
- **An in-flight `Open` entry**, if one was detected and resumable (step 2) → straight to `refactor-design` (no plan yet, or a plan present but neither label set — design has more to finish either way) or straight to `refactor-implement` (plan present, `ready-for-agent` set), bypassing `refactor-prioritize` either way. Found but still flagged and waiting (`needs-info` present, no newer human comment) → not handed forward at all this pass; treated as absent.
- **Candidates left for an Investigation pass** (step 3b, a Safety Net or Guardrails pass) → only their count, for the closing report; nothing is handed forward for them.
- **A flagged candidate now carrying `ready-for-agent`** (step 3b), if one was detected → straight to `refactor-implement`, same as an `Open` entry whose plan is already present.
- **A flagged candidate with a newer human comment** (step 2 or step 3b, native tracker only) → straight to `refactor-design` for judgment (`../refactor-design/references/decision-gate.md`'s "A flagged candidate's human answer arrives"), bypassing `refactor-prioritize`, whether or not it self-confirms.
- **A walked Track `Open` outcome** (Safety Net or Guardrails, `Open` non-empty — `references/track-open-processing.md`) → the one workable node the walk selected (with a draft of its issue, unless it already has one — `refactor-loop` creates it before design runs, `../continuous-refactoring/references/filing-a-ticket.md`), straight to `refactor-design` (or straight to `refactor-implement` if it already carries a plan with `ready-for-agent`), bypassing `refactor-prioritize`; any **fulfilled at pick-up** findings (nodes the walk's re-check found already adopted) go with the other findings to `refactor-learn`; non-workable nodes are reported with their reasons for the closing report. Nothing workable → the walk reports exactly that.
- **A scanned Track's new `Open`** (a Safety Net or Guardrails scan, step 4) → the `backlog` entries inside that Track's scope, in the script's order, blocked ones included — possibly none — to `refactor-learn`'s closing call, which writes them (`../refactor-learn/references/safety-net-write.md` / `guardrails-write.md`).
- **Proposals** — every currently-unblocked node, by Name (never slugs) or, once pre-filed, by its issue (step 3b), never capped, plus any other issue-backed candidate from step 3b and any baseline-shrink candidate from step 4b, or none → `refactor-prioritize`. Every node currently unblocked (required parents fulfilled, not rejected, every recommended parent already decided) — never a priority-truncated subset. Alongside it, name every `withheld` node and which parent(s) it's waiting on (e.g. "Rector: Type Coverage Set — waiting on: PHP CS Fixer").

## Completion criterion

Findings (if any) handed to `refactor-learn`, a resume-candidate or an in-flight `Open` entry (if any) handed straight to `refactor-implement`/`refactor-design` per above, proposals (if any) handed to `refactor-prioritize` — or a precondition stopped the pass and the report says which. Never a node together with entries past `structural-scan` in the same list. A flagged candidate still waiting on `ready-for-agent` (`needs-info` present instead), found via step 3b on a native tracker, with no newer human comment on its issue, is neither a finding nor a proposal nor handed anywhere this pass — silently skipped, same as an untouched open MR. The same candidate *with* a newer human comment is handed to `refactor-design` instead (above) — reaching this step at all is what counts as a completed check, whether design self-confirms it or nudges and leaves it flagged. Found instead as one of step 2's own `Open` entries on a git-only tracker → the pass stops here, same as any other precondition failure — nothing else can rediscover this candidate.
