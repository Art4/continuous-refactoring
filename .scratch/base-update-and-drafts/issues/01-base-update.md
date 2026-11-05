# 01 — The base update

Type: task
Status: claimed
Blocked by: —

**What to build** (spec Q2–Q6, Q8–Q11, Q16–Q24; a new ADR)

- **The procedure.** A new reference `skills/continuous-refactoring-run/references/updating-the-base.md`:
  - **Rebase or merge** by the target's convention, read from its history. Rebase only a branch that holds the
    suite's commits alone, pushed with `--force-with-lease` pinned to the last pushed tip; a commit the suite did not
    make → merge the default branch in instead (Q3).
  - **Resolving:** tool output by running the tool again; anything else by hand. Then graded (Q5): tool rerun →
    green checks; no textual conflict → pin and checks (drift); by hand → a new review by the Driver.
  - **Cannot be resolved safely** → nothing is pushed, a comment names the files and both sides, the merge request
    goes to the human (Q6).
  - **Comment** only for a resolved conflict: the files, what it collided with, how it was resolved (Q18).
  - **No forge:** `git merge-tree` against the default branch when the run works the branch anyway (Q19).
- **The run.** `implement-point.md` step 2: the row "the ticket came with its merge request" reads the new reference
  when the merge request is blocked. `worklist.md`: the state **needs base update** (Q16's triggers), workable,
  before every Track choice; the run ends with that merge request; several → Q11's order (Q23). In an interactive
  run a decision point with update / skip / stop (Q24).
- **The Driver.** `skills/continuous-refactoring/SKILL.md`:
  - *Ready* reads the merge state of every open merge request of the suite — handed-over ones too (Q20) — and runs
    one subagent run per blocked one, naming its ticket, in Q11's order, before the round's run. No round, no
    rework, no cadence, no limit (Q4, Q8).
  - *Stops*: before **done**, **ended** and **paused**, the same pass first; not before **broken** (Q9).
  - `references/merging.md` stays as it is (Q10).
- `CONTEXT.md`: the term **Base update** (Q21).
- Docs: `docs/known-limitations.md` (*Parallel merge requests may conflict* rewritten; no forge → no detection),
  `docs/FAQ.md` (*Why is there no limit on open merge requests?*, its last paragraph; why a base update is no
  rework), `docs/playbooks/run.md` (line on side-by-side merge requests), `docs/playbooks/driver.md`, `README.md`
  and `docs/architecture.md` where they describe a round and its decision points.
- **Scenarios.** `docs/agents/evals/d12-a-conflict-after-a-human-merge.md` (`review only`; the human merged !12,
  !13 now conflicts → *Ready* updates !13 before the round's run, the round still counts once) and
  `r6-a-conflict-it-cannot-resolve.md` (a run alone; both sides changed the same method → nothing pushed, a
  comment, handed to the human). Both in the README's table.
- A changelog fragment.

**Done when** d12 and r6 pass as walk-throughs, and `python3 -m unittest discover -s scripts -p 'test_*.py'` and
`python3 scripts/validate_skills.py .` are green.

## Comments
