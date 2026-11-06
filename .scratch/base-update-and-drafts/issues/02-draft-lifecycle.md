# 02 — The draft lifecycle

Type: task
Status: done
Blocked by: 01

**What to build** (spec Q7, Q12–Q15, Q25; a new ADR)

- **Opening.** `opening-a-merge-request.md` step 3: every merge request opens as a draft (`gh pr create --draft`,
  `glab mr create --draft`); a forge without drafts or **Merge requests** `none` skips this. Step 4: a run alone and
  Housekeeping mark it ready once CI is green (Q7); under the Driver it stays a draft. A target whose CI does not run
  on drafts → mark it ready so CI runs, say so in the closing report and a comment (Q14). The run needs to know
  whether the Driver called it: the Driver's prompt says so.
- **The Driver.** `skills/continuous-refactoring/SKILL.md`, step 4: ready only after the verdict mergeable; request
  changes, a handover after the reworks ran out, an unresolvable conflict and "ask the human" keep or make it a
  draft, the comment says why (Q12). *Ready*: a draft of the suite with no comment of the Driver since its last
  commit is reviewed, or reworked where it is incomplete (Q13).
- **The hold.** A draft the human set, read from the forge's timeline (spec, *Facts*), is a hold for the Driver and
  a run: no review, no rework, no base update, until the human marks it ready or comments (Q15, Q25). `worklist.md`:
  such a ticket stays in review, not workable.
- **The base update.** `updating-the-base.md` (ticket 01): a draft during the update, afterwards the state before
  restored — ready where it was ready and CI is green, a draft where the suite had handed it over (Q25).
- Docs: `docs/playbooks/driver.md` (what a draft of the suite means, and the human's hold; the table of what waits
  for the human), `docs/playbooks/run.md`, `docs/FAQ.md` (why drafts), `docs/known-limitations.md` (CI that skips
  drafts), `README.md` and `docs/architecture.md` where they describe an opened merge request.
- **Scenarios.** `docs/agents/evals/d13-a-draft-left-behind.md` (an interrupted run left a draft with green CI and
  no verdict → *Ready* reviews it and marks it ready) and `d14-the-human-holds-a-draft.md` (the human made a ready
  merge request a draft and it now conflicts → the Driver leaves it alone and lists it as waiting). Both in the
  README's table.
- A changelog fragment.

**Done when** d13 and d14 pass as walk-throughs, d12 and r6 still pass, and tests and validator are green.

## Comments

> **2026-11-06:** Done. *Draft and ready* in `opening-a-merge-request.md` holds the commands and whose draft a
> draft is; ADR-0095. The human chose (spec Q26) to tell the suite's drafts by its own steps rather than the
> timeline's actor, since the suite often shares the human's account; so a base update no longer toggles the draft
> state (Q25 changed). A run alone also marks ready when CI is still running or unreadable at its end, otherwise its
> draft would wait for nobody. The Driver's call says `under the Driver`. d13 and d14 pass, d12 and r6 still do.

> **2026-11-06 (field):** On a test target two of three merge requests were reviewed mergeable and stayed drafts. The
> Driver's verdict said only "mark it ready", without a command, and its *Done when* asked for the verdict, not the
> forge's state. Fixed: the commands are in the verdict, and the round ends only once the forge shows it ready. d13
> checks it.

> **2026-11-06 (field):** Merge requests did not open as drafts every time. Step 3 named the draft in a clause
> without a command, its *Done when* did not check it, and a merge request the implementing skill had opened stayed
> ready unless new commits were pushed. Fixed: the commands in step 3, the draft read back from the forge in its
> *Done when*, and step 1 makes any open one that is not a draft a draft, with its comment.
