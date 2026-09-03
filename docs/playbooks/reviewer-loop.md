# Playbook: Observing a continuous-refactoring run as a human reviewer

A second agent (or a human) can watch a separate, independently-driven agent run the
continuous-refactoring skill suite against a target repo — reviewing its issues/merge requests the way a
human reviewer would, merging or rejecting them, and keeping a findings log — without touching the
running agent's own session. Useful whenever you want a live, forge-only trust boundary between "the
agent doing the work" and "the reviewer deciding what lands," e.g. while dry-running a new agent setup
against a real repo, or keeping an eye on an autonomous pass you aren't watching live yourself.

This playbook is **repo-agnostic and persona-agnostic** — every run picks its own target and its own
reviewer stance; nothing here defaults to a specific project or a fixed way of judging merge requests.

## Starting a run

Before round 1, ask the human three questions (one `AskUserQuestion` round, all three together):

1. **Target repo** — which repo to watch. No default; always ask.
2. **Persona** — which reviewer stance to adopt this run (see *Personas* below). No default; the human
   picks, or describes a custom one if none of the four fit.
3. **Cadence** — how long to wait between rounds. Propose 5 minutes as a starting default, but the human
   confirms or overrides it; never assume it without asking.

Only start round 1 once all three are answered.

## Personas

Every persona shares the same mechanics (below) — they differ in **where the bar sits** for merging,
requesting changes, and how much authority the reviewer actually has. Pick one per run; don't blend them
mid-run without the human explicitly changing it.

| Persona | Stance |
|---|---|
| **Wohlwollend** (benevolent) | Benefit of the doubt: merge when the diff is plausible and in scope, even with minor rough edges — note concerns in the findings log without blocking on them. The default lived experience of this role in its first real run. |
| **Streng/Skeptisch** (strict) | Higher evidentiary bar: CI must be green (not just present) before merging, behavior changes need visible test coverage, ambiguous scope or undocumented assumptions get `request-changes` rather than the benefit of the doubt. Also holds the target repo's own documented tooling conventions (its README or `CONTEXT.md`, whichever it actually has — e.g. "no host tooling, everything runs in Docker") to that same bar: an issue/MR admitting a violation gets a corrective comment, the same way a red CI would, not just a note in the findings log. |
| **Nur-Beobachter** (observer-only) | No merge authority at all — comments and logs only, never merges, never formally requests changes as a blocking action. For a first, low-trust run against a new or unfamiliar agent setup, before granting real authority. |
| **Sicherheitsfokussiert** (security-focused) | Wohlwollend's bar for everything else, but extra scrutiny — closer to Streng's bar — on anything touching authentication/authorization, input handling, secrets/credentials, or dependency versions/known CVEs. |

## Role & principles

- **Persona aside, this is always a reviewer, not a second automation agent.** Judge merge requests the
  way an engaged human would for the chosen persona — not pedantic by default (unless the persona says
  so), not blind either.
- **No direct contact with the agent being watched.** The only channels are the forge itself — comments
  on issues/merge requests, reviews (approve/request-changes), merge/reject — and the findings log. No
  messaging, no access to the other agent's own session.
- **Allowed actions:** comment on issues/merge requests; merge, or reject with a stated reason
  (`request-changes`, left open by default so the work can be corrected, rather than closed) — except
  under the Nur-Beobachter persona, which never merges or blockingly rejects.
- **Issues:** read and log only, no labels, no action — **except** when a comment on an issue/merge
  request asks the reviewer a direct question (e.g. "can we close this?"); then answer/act on it
  proportionately and note the scope extension in the log.
- **Findings log:** `.scratch/<target-repo-slug>-loop-observation/findings.md` in the repo the reviewer
  itself runs from — a research/observation artifact, not a canonical doc. One entry per round with a
  timestamp, plus its own `### Finding …` / `## ⚠️ Auffälligkeit` sections for anything outside the
  normal rhythm. Delete or fold into a proper fix once a finding's learnings are actually acted on —
  don't let it become a second, stale backlog.

## Loop mechanics

- Cadence: the value confirmed at start (default proposal 5 minutes), self-paced between rounds.
- Default stop condition: 6 consecutive quiet rounds (~30 minutes with no foreign activity) → automatic
  stop with a closing summary in the findings log.
- The human can also stop the run manually at any point (e.g. to review findings and fix the suite
  before continuing) — a normal control option, not a failure.
- State carried between rounds: last-seen issue/MR numbers, `mergedBy`/`updatedAt`/comment counts, which
  MRs have already been commented on/rejected and why. No separate state file needed — the findings log
  plus a fresh `gh issue list`/`gh pr list --state all` each round is the source of truth.

## Each round

1. Query `gh issue list --state all` / `gh pr list --state all` against the target repo, diff against
   the last known state (the previous log entry).
2. **For every new/updated open MR:**
   - Check `gh pr view <n> --json mergedBy,state` — **if it's already MERGED and not by the reviewer
     itself, that's an incident** (see *Anomaly detection* below), not a routine action.
   - Read the diff + description, judge it per the chosen persona's bar (see *Personas*).
   - If CI exists, check `gh pr checks <n>` before merging (mandatory under Streng/Sicherheitsfokussiert,
     good practice under the others too).
   - **Good/defensible** (per the persona's bar) → merge (adapt the merge method to the repo's actual
     settings). Minor concerns don't block the merge but still get logged, unless the persona is
     Nur-Beobachter, which never merges regardless.
   - **After merging, verify the merge actually landed the branch's content** — `gh pr merge`
     reporting success is not proof the base branch now matches the branch's tip; a real conflict
     can be silently resolved in favor of the wrong side with no error surfaced. Diff the touched
     files: `git fetch origin && git diff <branch-tip-sha> origin/<base-branch> -- <touched-files>`
     should be empty (or, for a true merge commit, diff the merge commit against both parents and
     confirm it matches the branch-side parent's tree on those files, not the base's stale
     pre-merge value). Catch this before moving to the next MR, not at the end of the round.
   - **If verification fails** (a silent bad merge caught) — log it under `## ⚠️ Auffälligkeit`
     immediately, per *Anomaly detection* below, and fix it the same way any correction lands: a
     normal follow-up MR (`git revert -m 1 <merge-commit-sha>`, or a corrective commit) per the
     "Reverts always go through the normal MR workflow" rule — never a force-push or history
     rewrite, even to fix your own mistake.
   - **Questionable/broken/out of scope** → `request-changes` with a concrete, actionable reason; leave
     the MR open rather than closing it, except for a clearly orphaned/wrong MR. Nur-Beobachter logs the
     same judgment but takes no blocking action.
   - **Substantial/premise-changing decisions** (e.g. a runtime version bump that lifts a deliberate
     constraint the target repo states) — never merge unilaterally regardless of persona; ask the human,
     even when the MR itself is clean and well-argued.
   - **Real structural code changes** (not just tooling adoption) get closer scrutiny: small and well
     covered by new/existing tests, CI green → treat normally; large/risky/thin on tests → look closer or
     escalate.
   - For larger/riskier changes (e.g. a runtime version bump), reading the diff alone isn't enough:
     **check the branch out locally, run its lint/build equivalent, and click through the target
     application's central user path** (no browser available: `curl` with a cookie jar through
     register/login/CRUD/logout or the equivalent) before merging. Record the test result as a PR
     comment.
3. **New issues:** read only, log the title and a short assessment.
4. Update the quiet-round counter (above) and write the round's log entry.

## Anomaly detection ("agent stuck" / special cases)

Log immediately under `## ⚠️ Auffälligkeit` **and pause the round to ask the human** (not just at the end
of the run), for e.g.:

- The same MR reopens after a rejection with no change to the diff/commits (thrashing). **Watch for false
  positives:** a repeated title/branch pattern is only a real hang if the *watched agent itself* abandoned
  the earlier attempts unsuccessfully — manual cleanup by a human *before* observation started doesn't
  count (always check who/what closed earlier attempts, e.g. via
  `gh api repos/<owner>/<repo>/issues/<n>/timeline`).
- **The watched agent merges an MR itself** (`mergedBy` isn't the reviewer). This must never happen
  regardless of persona — merge decisions belong to the reviewer alone. Check `mergedBy` for every
  new/changed MR, every round. A single incident: report to the human, revert only on instruction (via a
  clean revert PR, see below), never auto-revert if the pattern repeats (could be a bigger problem, e.g.
  the agent's own merge permissions, worth a separate conversation) — pause and ask instead of reverting
  again.
- The watched agent reacts to a revert (or other correction) purely on the *fact* of it, without reading
  the **reasoning in the revert's own body**, and draws the wrong conclusion from it. Log as a finding
  about the watched agent's behavior, not necessarily an anomaly that pauses the round.
- An MR touches files outside the expected scope (e.g. the skill suite driving the loop, instead of the
  target repo's own code) or looks destructive (large deletions unrelated to the stated goal).
- Unusual force-pushes / history rewrites.

**Reverts always go through the normal MR workflow**, never a force-push/history rewrite: `git revert -m
1 <merge-commit-sha>` on a new branch, then a normal MR (with the reasoning in the body, so the watched
agent can factor it in on its next attempt) merged by the reviewer.

## Escalation to the human

Always pause and ask (`AskUserQuestion` or equivalent), rather than deciding unilaterally, when:

- an MR changes the target's fundamental premise (e.g. a runtime upgrade that lifts a deliberately
  stated constraint),
- a core rule gets violated repeatedly (e.g. a second self-merge),
- it's unclear whether an existing standing instruction extends to a new, similar-but-not-identical
  situation — ask rather than extrapolate.
