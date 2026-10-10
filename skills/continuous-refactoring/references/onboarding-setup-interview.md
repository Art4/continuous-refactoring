# Reference: the onboarding interview

Asks where a target's tickets live and how the **Refactoring operations** work there, and writes the answer
as the `## Refactoring operations` section of the target's `docs/agents/issue-tracker.md`. That file is the
interview's only write. `refactoring-operations.md` names the operations, their fallbacks and the
templates; read it before step 1.

Run the interview inline, where the human can answer. Six steps, in order: Explore, Ask, Summarize, Write,
Verify, Report.

**Speaking to the human.** Call what is being set up the "skill suite" and one call of it a "run"; use the
forge's own word for a merge request (pull request on GitHub).

**On record.** An answer the target's files already state is on record: it is taken as it stands, shown in
the summary as "already recorded", and asked about only if the human wants it changed there.

## 1. Explore

Read-only. Note each of these as found or not found:

- **The tracker file.** `docs/agents/issue-tracker.md`: whether it exists, which tracker its title or text
  names, whether it has a `## Refactoring operations` section, and which bold operation names that section
  carries.
- **The forge.** `git remote get-url origin`: `github.com` → GitHub, `gitlab.com` → GitLab, another host or
  no `origin` → no match. On a match, run one reachability check (`gh repo view` / `glab repo view`); a
  failing check or a missing command-line tool softens the wording of the recommendation and changes
  nothing else.
- **Signs of another tracker**, when the tracker file is missing: `AGENTS.md`, `CLAUDE.md` or
  `CONTRIBUTING.md` naming one, or ticket numbers in commit messages that match no ticket on the forge.
- **Marks already in use** for **Candidate**, **Priority** and **Rejected**: labels on a reachable forge
  that plainly mark refactoring work or priority (`gh label list` / `glab label list`), a mark the tracker
  file or the repository's docs name for either, and an `.out-of-scope/` folder at the repository root.

Then name the case the rest of the interview follows:

| The tracker file | Case |
| --- | --- |
| has the section with **Search**, **Done** and **Merge requests** | **Complete** — tell the human the target is onboarded and end the interview here |
| has the section, a required operation is missing | **Incomplete** — the tracker and every bullet present are on record |
| has no section, or does not exist | **New** |

Step 1 is done when each of the four is noted and the case is named.

## 2. Ask

Open with one sentence saying what happens, for example "This repository is not set up for the skill suite
yet. I have a few questions about where your tickets live, then I write one file." — or, for
**Incomplete**, "The skill suite's section in your tracker file lacks **Search**. I'll add it."

Then say in plain prose what Explore found and which questions remain. Ask those one at a time: a title,
two to four concrete options, one recommendation drawn from Explore — a single-question `AskUserQuestion`
call where that tool exists, the same content as numbered prose otherwise — and wait for the answer before
the next. In an autonomous run each recommendation is taken as the answer, and a question that has none
stays open.

**Where do the tickets live?** On record in the **Incomplete** case, and when the tracker file's title is
`# Issue tracker: GitHub`, `GitLab` or `Local Markdown`.

- **GitHub** / **GitLab** — offered when Explore matched that forge.
- **<Name>, as `docs/agents/issue-tracker.md` describes it** — offered when the tracker file describes
  another tracker.
- **Another tracker, described here** — offered when there is no tracker file: the human names it and how
  an agent creates, reads, comments on and closes a ticket there.
- **Local Markdown** — always offered: tickets as files inside this repository. An existing tracker file
  stays as it is; only the skill suite's tickets are local.

Recommendation, first match: the described tracker; another tracker described here, when Explore found
signs of one; the matched forge, worded with the reachability finding; Local Markdown.

**Where do merge requests live?** On record when Explore matched a forge (that forge) or found no `origin`
(none). Asked only for another host: the human names the forge and the tool that reaches it, or chooses
"none — the prepared branch is handed to me".

**How do the operations work there?** GitHub, GitLab and Local Markdown take their template, and this
question is answered. For any other tracker, go through **Search**, **Done**, **Linked merge request**,
**Claim** and **Blocked by**, in that order. An operation the tracker file or
the repository's own docs already answer is on record. Each remaining one is one question, its
recommendation drawn from what those files say about the tracker; for an optional operation "not
available" is an answer, and its bullet is left out.

**Which marks does the target already use?** Asked only when Explore found one, and only about those:

- a mark for refactoring work → proposed as **Candidate**; one for priority → as **Priority**;
- an `.out-of-scope/` folder → proposed as **Rejected**, in place of the template's bullet.

Recommendation: take what is in use. A mark Explore did not find is left out without a question, and so is
**Housekeeping**, which the Housekeeping Track writes when it sets its mechanism up.

Step 2 is done when every operation in the reference is in one of four states: answered, on record, taken
from a template, or left out with its fallback noted.

## 3. Summarize

A **decision point**. Lay out:

> Tracker: <GitHub | GitLab | Local Markdown | the name given>.
> <Pull requests | Merge requests>: <the forge and its tool | none — you land the prepared branch>.
> Operations: <one line per bullet, each with its source: template, read from `<file>`, your answer, or
> already recorded>.
> Left out: <each absent optional operation and what the skill suite does without it>.
> Removed: <**Bookkeeping**, **Filed date**, **Comment author and time** — only where an existing section carries them>.
> File: `docs/agents/issue-tracker.md`, <created | section appended | section completed>.

Options: **write it** (recommended), **change an answer** (back to that question, then this summary
again), **stop** (nothing is written).

- Autonomous run → the recommendation is taken when every required operation has an answer. A required
  operation without one ends the interview with a report naming the open question, and nothing is written.
- Nobody answers, here or at a question of step 2, and the run is not autonomous → the interview ends with
  this summary as its report, and nothing is written.

Step 3 is done when one of the three options is chosen, or the interview has ended.

## 4. Write

One file, `docs/agents/issue-tracker.md`; say one status line when it is written. In every case the
**Merge requests** bullet states the forge Explore read from the remote.

| Situation | What is written |
| --- | --- |
| No file, GitHub or GitLab | The title (`# Issue tracker: GitHub` / `GitLab`), one sentence naming the remote, and that template's section |
| No file, Local Markdown | The content of `local-issue-tracker-template.md` |
| No file, a tracker described here | The title (`# Issue tracker: <Name>`), a `## Conventions` list from what the human said about creating, reading, commenting on and closing a ticket, and the section built from the answers |
| File without the section | The section, appended; the rest of the file stays as it is |
| **Incomplete** | The missing required bullets, placed in the reference's order; the **Bookkeeping**, **Filed date** and **Comment author and time** bullets removed; every other bullet left as written |

Step 4 is done when the section carries **Search**, **Done** and **Merge requests**, and none of
**Bookkeeping**, **Filed date** and **Comment author and time**.

## 5. Verify

Run **Search** once, exactly as the section now states it, with any word. The tracker answering counts,
with zero hits too; on Local Markdown that includes `grep` ending without a match and a tickets folder
that does not exist yet. Where **Merge requests** names a tool, list one merge request with it
(`gh pr list --limit 1`, `glab mr list --per-page 1`).

A command that fails → show the human the error and ask for the corrected bullet, write it, and run this
step again. In an autonomous run the failure goes into the report as "not verified", and the section stays
as written.

Step 5 is done when each command got its answer, or each failure is carried into the report.

## 6. Report

Tell the human, in plain prose:

- **What was written** — the file, and whether it was created, extended or completed; what was already
  there and left alone.
- **Commit it.** The tracker file is shared like code. It is left uncommitted in the working tree for the
  human to commit.
- **What the skill suite does without** each operation that was left out, one line each.
- **Not verified** — each command of step 5 that failed, with its error.
- **Taken as recommended, not confirmed by you** — in an autonomous run, every answer that was a
  recommendation.

The interview ends with this report, and step 6 is done when every bullet that applies is in it. What the
run does next is the caller's.
