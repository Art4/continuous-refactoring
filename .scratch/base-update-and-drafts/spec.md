# base-update-and-drafts

The suite notices when one of its merge requests can no longer merge, brings it onto the current default branch
itself, and marks a merge request as a draft for as long as it is being worked on. Grilled on 2026-11-05
(`/grill-me`). Two new ADRs: the base update (ticket 01) and the draft lifecycle (ticket 02).

## Why

- **Conflicts go unnoticed.** A merge request that merged cleanly when it was opened conflicts once another one
  lands. The Driver's *Ready* picks up an open merge request only when the human has answered or asked for changes;
  the review reads checks, not the forge's merge state; a run sees the ticket as *in review* and skips it. The human
  has to point it out.
- **The docs say it is the human's job.** `docs/known-limitations.md` (*Parallel merge requests may conflict*),
  `docs/FAQ.md` (*Why is there no limit on open merge requests?*) and `docs/playbooks/run.md` leave resolving to the
  human. That changes.
- **A merge request looks finished while it is not.** It opens ready for review before the Driver's review, and stays
  ready through a request for changes. A human or a reviewer cannot tell "the suite is still on it" from "the suite
  thinks this can merge".

## pstack's babysit

Looked at (`cursor/plugins`, `pstack/skills/poteto-mode/playbooks/babysit.md`, at `2776ddd`) and not adopted: it is a
playbook of `poteto-mode`, tied to a GitHub-only TypeScript watcher, Bugbot and Origin; it *reports* a conflict and
never rebases; pstack opens every PR ready, never as a draft. Taken from it:

- Conflicts come before review threads, and those before CI.
- The forge's merge verdict counts, not a list of green checks.
- A CI failure in code the diff does not touch points to a stale base, not a flake (`git merge-base --is-ancestor`).
- After an update with no textual conflict the checks still run: the default branch may have grown callers of code
  the branch moves (drift).
- Force-push only the suite's own branch, with `--force-with-lease`; a push the suite did not make → stop.
- Update only when needed: every update restarts CI.

ADR-0031 had drafts once (draft until the fold-in lands); ADR-0064 dropped it. Its lesson stays: an interrupted run
leaves a draft nothing picks up again, unless something looks for it.

## Decided

| # | Decision |
|---|---|
| Q1 | Two tickets, each with an ADR and a PR of its own; 01 (base update) first, 02 (drafts) builds on its check in *Ready* |
| Q2 | The Driver checks every open merge request of the suite; a run, the one of the ticket it works on — widened by Q17/Q23 |
| Q3 | Rebase or merge by the target's convention, read from its history (linear → rebase, merge commits → merge). Rebase only when the branch holds the suite's commits alone, pushed with `--force-with-lease`; a foreign commit makes it a merge |
| Q4 | A base update counts as no rework and has no limit: a new conflict needs someone to merge, so it cannot loop |
| Q5 | Graded: a conflict resolved by running the tool again (PHP CS Fixer, Rector) needs green checks; an update with no textual conflict needs the pin and the checks (drift); a conflict resolved by hand needs a new review by the Driver |
| Q6 | A conflict that cannot be resolved safely (intents contradict, both sides changed the same logic): the branch stays as it was, a comment on the merge request names the files and both sides, it goes to the human. No half-done rebase is pushed |
| Q7 | A run alone (no Driver) and Housekeeping open a draft and mark it ready themselves once CI is green — their own review ran before opening. Under the Driver it stays a draft until the Driver's verdict |
| Q8 | The base update happens in the Driver's *Ready*, before the round's run: one subagent run per blocked merge request, naming its ticket. It is no round and has no cadence before it |
| Q9 | Before a stop **done**, **ended** or **paused**, the Driver updates every blocked merge request first, so the human comes back to mergeable ones. Not before **broken** |
| Q10 | No extra check in `merging.md`: the next *Ready*, or the stop (Q9), finds it |
| Q11 | Order: merge requests whose ticket blocks others (**Blocked by**) first, then the oldest; after each update the others' merge state is read again |
| Q12 | Ready only after the verdict mergeable (a run alone: green CI, Q7). Request changes, a running base update, a handover after the reworks ran out, an unresolvable conflict and "ask the human" keep or make it a draft; the comment says why. A draft means "the suite does not think this can merge" |
| Q13 | A draft of the suite with no comment of the Driver since its last commit (an interrupted run): the Driver reviews it in *Ready*, or starts a rework run where it is incomplete (CI red, checks missing) |
| Q14 | A target whose CI does not run on drafts (no pipeline for the push, while earlier merge requests had one): the run marks it ready so CI runs, and says so in the closing report and a comment. The verdict still needs green CI |
| Q15 | A draft the human set (read from the forge's timeline) is a hold: the suite leaves the merge request alone, a conflict too, until the human marks it ready or comments. A human who marks a draft ready before the verdict changes nothing: the Driver reviews as usual |
| Q16 | What triggers an update: the forge reports a conflict (GitHub `mergeable: CONFLICTING` / `mergeStateStatus: DIRTY`, GitLab `detailed_merge_status: conflict` / `has_conflicts`); the forge blocks the merge because the branch is behind (GitHub `BEHIND` with "require up to date", GitLab `need_rebase` with fast-forward only); CI red from a stale base. Behind with no block → no update. `UNKNOWN` while the forge computes → read again shortly |
| Q17 | The Driver detects and names the ticket with the reason; the procedure is a new reference `skills/continuous-refactoring-run/references/updating-the-base.md` (Q3, Q5, Q6), read from `implement-point.md` step 2. A run detects the blocker too, not only the Driver (Q23) |
| Q18 | A clean update gets no comment, the push shows it. A resolved conflict gets one: the files, which merge request or commit on the default branch it collided with, and how it was resolved (tool run again, or by hand) |
| Q19 | No forge (**Merge requests** `none`): the Driver detects nothing on local branches; a run that works the branch anyway checks with `git merge-tree` and updates. Into `known-limitations.md` |
| Q20 | A merge request the suite handed to the human (reworks ran out, a question) still gets base updates; its question stays open. Only a draft the human set (Q15) is left alone |
| Q21 | `CONTEXT.md` gets **Base update**: bringing the branch of an open merge request of the suite onto the current default branch, by rebase or merge, conflicts resolved; neither a rework nor a round. Draft and ready stay the forge's words, no entry; what they mean to the suite (Q12) is in the Driver's docs |
| Q22 | Four scenarios under `docs/agents/evals/` (Q22 names them in the tickets) |
| Q23 | `worklist.md` gets the state **needs base update**: a ticket in review whose merge request is blocked (Q16). It is workable and comes before every Track choice; the run updates and ends with that merge request (one run, one merge request). Several → Q11's order. Under the Driver, *Ready* has cleared them, so its run finds none (Q8 holds) |
| Q24 | In an interactive run it is a decision point: findings (the merge request, the trigger, the colliding files); options update (the recommendation), skip it and go on as usual, stop. An autonomous run takes the recommendation |
| Q25 | The human's draft hold (Q15) holds for a run too: the ticket stays in review, not workable. During the update the run makes the merge request a draft and afterwards restores its state: ready where it was ready and CI is green, a draft where the suite had handed it over (Q12) |

## Facts

- GitHub: `gh pr view <n> --json mergeable,mergeStateStatus,isDraft`; `gh pr create --draft`, `gh pr ready <n>`,
  `gh pr ready <n> --undo`. Who changed the draft state: the issue timeline's `convert_to_draft` /
  `ready_for_review` events with their actor (`gh api repos/{owner}/{repo}/issues/<n>/timeline`).
- GitLab: `glab mr view <n> -F json` → `detailed_merge_status`, `has_conflicts`, `draft`; `glab mr create --draft`,
  `glab mr update <n> --ready` / `--draft`. Who changed it: the system notes ("marked this merge request as draft /
  ready") with their author.
- The packs already say a conflict of tool output is resolved by running the tool again (`packs/php/php-cs-fixer.md`,
  `packs/php/rector.md`).
- `docs/agents/field-eval.md` skips drafts as someone's work in progress; with Q12 the reviewer sees a merge request
  of the suite once the Driver's verdict made it ready. It stays as it is.

## Tickets

- `issues/01-base-update.md`
- `issues/02-draft-lifecycle.md` (blocked by 01)
