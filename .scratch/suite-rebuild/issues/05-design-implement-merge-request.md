# 05: Design, implement, merge request

**What to build:** A selected ticket gets a plan and an implementation, and the run ends with an open
merge request. Where the target has its own skills for planning and implementing, the suite recommends
those; otherwise it uses its own fallback references. A decision worth recording travels in the same
merge request.

Spec: `../spec.md` (sections *Design and implementation*, *The run*). The fallback references are written
new with the `writing-for-agents` skill, carrying over what still applies from the old design and
implement skills (grounding a candidate, the decision gate for a breaking change, test-first slices,
review, the forge-facing writing rules, never deleting a branch that holds the only record of a decision).

**Blocked by:** 04

**Status:** done

- [x] At the design and at the implement point the suite looks at the target's available skills and its
      `AGENTS.md`, recommends the target's own, and falls back to its references; the choice is stored
      nowhere
- [x] The design point ends with an implementable plan on the ticket; an autonomous run that needs a human
      answer ends there with a message naming the open question
- [x] The implement point ends with a branch whose checks are green
- [x] The suite opens the merge request per **Merge requests** and **Linked merge request** unless it
      already exists; with no forge the prepared branch is handed to the human
- [x] An ADR and a glossary change are committed on the candidate's branch, and only where the target's
      domain docs say ADRs are kept
- [x] A design that finds the candidate cannot be done without changing behaviour ends as a decision
      point, not as a silent stop
- [x] A **Flagged candidate** works in a target that has no `docs/agents/triage-labels.md`: onboarding no
      longer writes that file (ticket 02), so the "waiting on you" and "ready" states are either expressed
      without triage labels or the design point proposes setting them up at a decision point; the
      glossary entry and the now unreferenced `triage-labels-template.md` are brought in line with
      whichever is chosen
- [x] No ticket mode or merge-request mode is read; the run's mode decides whether the suite asks
- [x] No test is written or changed

## Comments

### Done — what exists now

Under `skills/continuous-refactoring/references/`:

- `design-point.md` — new. Reading the ticket, who plans, the two findings that change the ending
  (behaviour change, a decision meeting the ADR bar), the plan as a comment, open questions and how a
  ticket waits, and the suite's own planning for a tooling ticket, a baseline ticket and any other ticket.
- `implement-point.md` — new. Who implements, the branch, building by kind of ticket, checks, review, and
  the slices any ticket can have (ADR, glossary, Housekeeping line).
- `reviewing-a-change.md` — new, behind a pointer from the implement point: the two review axes, the
  smell set and the test-quality rules, carried over from the old review fallback.
- `opening-a-merge-request.md` — rewritten: existing merge request, the decision point, description,
  the forge's checks, no forge. `MR-create-mode`, the cap of two and the config file are gone.
- `worklist.md` — the **waiting** row names its mark; a baseline ticket's merge requests are also found
  by search; a branch that is gone counts as merged.
- `foundational-refactoring-rules.md` — its first line no longer names the old skills.
- `refactoring-operations.md` — the fallback cell of **Comment author and time**.
- `triage-labels-template.md` — deleted.
- `../SKILL.md` — step 8's criterion and "The end of a run" name the two new endings.
- `CONTEXT.md` — **Flagged candidate**, **Decision trail**, **Plan**, one clause in **Run**.

Not touched: `skills/refactor-design/`, `skills/refactor-implement/` and the other old skills.

### The two answers ticket 04 asked for

**How a waiting ticket is marked.** By its newest comment. The suite leaves a comment opening with the
words `Open question`; the ticket is waiting while that comment is its newest one, and any newer comment
ends the wait. No label, no field, nothing to remove. At its next pick-up the design point reads the
reply: the default is confirmed (the plan stands), another way is named (plan again), or the question is
still open (ask again). Reconcile's question about a merge request closed without a reason leaves nothing
on the ticket and holds for that run only; the next run's reconcile finds it again.

**How a baseline ticket is planned.** One ticket, one merge request after another. Each run groups the
baseline's entries by root cause and plans one **part** — a group, or the named files of a large group —
as a new `Plan` comment whose last section says what stays. The part's merge request names the ticket
with the word "part" and carries no closing reference; while it is open the ticket is in review, after
its merge reconcile keeps the ticket open ("delivered a part"), and the next run plans the next part.
The merge request that empties the baseline delivers the whole ticket and closes it.

### Decided here, not stated by the spec

**Who plans, who implements**

- "The skills available in the target" are read as: every skill on offer in the conversation apart from
  the suite's two, plus what the target's `AGENTS.md` says. Recommendation: what `AGENTS.md` names, else a
  fitting skill installed in the target, else a fitting skill from elsewhere (user-level), and only then
  the suite's own. A user-level skill thus ranks above the suite's fallback.
- With no fitting skill and nothing in `AGENTS.md` there is no decision point, only one sentence.
- The choice is made twice per run (design, implement) and holds for that ticket in that run.
- In an autonomous run the suite answers a target skill's questions with its own recommendation, except
  one that meets the ADR bar.
- After a target's implement skill the suite does not review again; it reads the diff once against the
  plan and builds a missing slice itself. Its own review runs only after its own implementation.
- The old pointers to `/grilling`, `/tdd`, `/domain-modeling` and the engineering skills' implement skill
  are gone from the fallback: such a skill is now simply one of the options at the choice.

**Plan and ticket states**

- A plan the suite writes is always a comment opening with the word `Plan`, never an edit of the ticket's
  text; the newest one counts. A ticket "carries a plan" also when a human or a target's skill wrote one
  in any form.
- In an interactive run the plan is itself a decision point before it is posted.
- The triage labels are dropped entirely: no `needs-info`, no `ready-for-agent`, also where the target
  has a `docs/agents/triage-labels.md`. "Ready" is: carries a plan and is not waiting.
- Any newer comment ends the wait, whoever wrote it; the suite no longer tells its own comments from a
  human's. **Comment author and time** is therefore not needed for this, and its fallback cell in
  `refactoring-operations.md` now says so. Nothing in the new references still reads that operation.
- A reply that names another way is planned with directly. The old rule (only a plain yes is taken over,
  everything else needs a human to swap labels) is not carried over.
- A waiting ticket named in an autonomous call ends the run with the question named; it is not answered
  with the default.
- The **decision trail** is no longer a comment of its own but the `Decisions` part of the plan.

**Behaviour change**

- A design that finds the work would change behaviour is a decision point with two options: record a
  rejection (recommended, so an autonomous run does that), or leave the finding on the ticket as an open
  question. The run ends there in both cases and does not go back to selection. `SKILL.md` and the **Run**
  entry name this ending.
- The same finding during implementation leads to the same decision point; the branch stays and is named
  in the record. This is what remains of "never delete a branch that holds the only record".
- A baseline whose remaining groups all need a behaviour change: the rejection recorded is that of the
  next level's node, and the baseline ticket is closed with a note.

**Baseline ticket**

- Which part comes first: a group touching input from outside the application, else the group one fix
  removes the most entries of. The old admission tiers and the cap are gone.
- An interrupted part is recognised by the newest plan's group still having all its entries.
- One commit per file and one for the regenerated baseline; no test is written.

**Implementing**

- Branch name: the target's convention, else `refactor/<ticket reference>-<subject>`; a baseline ticket
  uses the part's name, so that two parts never share a branch. An earlier branch is continued only when
  no merge request ever came from it.
- A check outside the plan's `Done when` that was already red on the default branch is named and left.
- A smell from the review sends the work back only when its way out stays within the plan's slices;
  otherwise it is named in the merge request's description.
- ADR, glossary term and Housekeeping line are slices of the plan, built and checked like the others.
  An ADR is written only for a decision a human answered or confirmed, and only where the target's
  domain docs (`docs/agents/domain.md`, or what `AGENTS.md` names instead) name the place; the glossary
  term only where they name a glossary file. An existing `docs/adr/` folder alone is not enough.
- Without a **Housekeeping** operation the node's Housekeeping line is left out of the merge request; the
  Housekeeping Track adds it later (ticket 07).
- The implementation runs in the main conversation. Only the review may run in a subagent.
- Confirming the seams with the human before the first test is gone: the plan, which names the seam, was
  already a decision point.
- The **Outlook** comment (what a merged node unlocks, with a diagram) is not carried over: every node
  now has a ticket with its blockers, so the way ahead is in the tracker.

**Merge request**

- Opening it is a decision point of its own: push and open (recommended), change the text, or leave the
  branch for the human. Where one is already open, the decision is only about pushing.
- Without a forge, and when the branch is left for the human, one comment on the ticket names the
  branch. Without a forge that comment is the decision point of the step.
- With **Merge requests** `none`, a named branch that no longer exists counts as merged (`worklist.md`).
- CI still running when everything else is done does not hold the run: the closing report says so.
- Draft merge requests are not used.

### Red afterwards

No unit test is newly red (the same two). The validator has four new errors and loses three lines; listed
in a comment on ticket 09, together with texts that are now untrue.

### Review

Reviewed on two axes before the commit. Taken over: one owner for ADR and glossary (slices, built before
the checks), the baseline ticket's part merge requests found by search, branch names per part, the
bounded smell loop, the waiting ticket in an autonomous call, completion criteria per step. Left open on
purpose: the meaning of the waiting rule also stands in the **Flagged candidate** glossary entry.

### Changed after review

- **A behaviour-change finding is left to a human.** The recommendation at that decision point is now the
  open question; recording a rejection is the option a human may choose. An autonomous run therefore
  never rejects by its own judgement — on a baseline ticket that would have closed every level above.
- **Comment author and time** is read by nothing since this ticket; ticket 07 says whether Housekeeping
  needs it, ticket 08 removes it otherwise.
