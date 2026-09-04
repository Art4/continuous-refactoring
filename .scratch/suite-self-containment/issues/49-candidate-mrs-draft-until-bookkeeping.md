# 49 — Candidate MRs open as draft until the fold-in bookkeeping commit lands

**What to build:** `refactor-implement` opens its candidate merge request as a **draft** on a
native-label tracker where ADR-0028's in-flight fold-in exception applies; only once
`refactor-learn`'s closing-call fold-in bookkeeping commit lands on that same branch does something
mark the MR **ready for review** (`gh pr ready`/GitLab equivalent) — undrafting it becomes the
mechanical signal that a candidate's full cycle (implementation + bookkeeping) is actually complete,
rather than a reviewer having to notice and infer it by hand.

**Why:** Directly motivated by a reviewer-loop finding (`Art4/legacy-todo` PR #114, Round 4,
2026-09-04 — `.scratch/legacy-todo-loop-observation/findings.md`): the reviewer caught a candidate
PR mid-pass — implementation commit present, bookkeeping/fold-in commit not yet landed, CI still
pending — and had to notice this manually and wait a few minutes before reviewing. A draft state
would make this self-evident: draft = don't look yet, ready-for-review = the actual, unambiguous
"this candidate's cycle is complete" signal.

**Blocked by:** none, but only applies where ADR-0028's fold-in exception applies (native-label
tracker, same-pass implement+learn) — ADR-0028 already merged
(`Art4/continuous-refactoring` PR #40).

**Priority:** medium — not a bug (the reviewer already handled it correctly by waiting), but a real
ergonomics gap that will recur every time a reviewer (human or automated) catches a candidate mid
fold-in.

**Status:** done

- [x] Non-native-tracker / no-fold-in case → normal (non-draft) MR, confirmed as the working
  assumption.
- [x] `refactor-scan` step 3 needs no logic change for reconciliation — "still open, nothing
  changed → no finding" already treats a draft the same as any other quiet open MR. Added a
  clarifying line anyway.
- [x] "Mark ready for review" lives as the last bullet of `refactor-learn`'s closing-call write
  list — after every other fold-in write, since undrafting should only happen once everything is
  actually pushed.
- [x] **Solved directly in this ticket, not spun out**: an interrupted pass leaving a candidate
  stuck in draft forever turned out to be a real, previously-invisible gap — nothing in
  `refactor-scan`'s existing reconciliation would ever resume it, since it requires reviewer
  activity that a correctly-draft, unreviewed MR will never get. Fixed with a new finding type
  ("fold-in still owed"): `refactor-scan` step 3 checks reviewer activity first (regardless of
  draft status — a human comment always wins), then draft status; `refactor-learn`'s early call
  checks out the stale branch and finishes the fold-in, same writes as the closing call.
- [x] Forge mechanics confirmed and written into `opening-a-merge-request.md`: `gh pr create
  --draft` / `gh pr ready` (GitHub), `glab mr create --draft` / `glab mr update <n> --ready`
  (GitLab).
- [x] `docs/playbooks/reviewer-loop.md` gets a rule: skip a draft MR, don't treat it as a hang;
  escalate only if it stays draft across several rounds with no new commits.
- [x] `CONTEXT.md`'s **Findings** definition broadened to include the new "fold-in still owed"
  outcome.
- [x] New ADR-0031, amending ADR-0028. `refactor-learn/SKILL.md`'s `Fulfilled nodes`/`Skip streak`
  write procedure extracted to its own reference file along the way (word-count advisory).
  `python3 -m unittest discover -s scripts -p 'test_*.py'` (240/240) and
  `python3 scripts/validate_skills.py` (same 5 pre-existing advisory warnings) both green.

## Comments

> **2026-09-04:** Filed from the `Art4/legacy-todo` reviewer-loop findings log (PR #114 finding) and
> the `candidate-mrs-as-draft-until-bookkeeping` memory, per the user's request to prepare "für
> später" ideas for fixing.

> **2026-09-04 (later):** Design settled via a `/grill-me` session (in German). Researched GitHub's
> and GitLab's CLI draft-mechanics directly rather than guessing. The user pushed back on one
> recommendation (Q7): reviewer activity is checked *before* draft status, not the other way
> round — a human comment on a draft still wins over the mechanical fold-in-owed default. The user
> also chose to solve the interrupted-pass steady-state question directly in this ticket rather
> than spinning it into a separate one, once it became clear nothing in the existing suite would
> ever resume a permanently-stuck draft on its own. Implemented in the same session on branch
> `tickets/49-draft-candidate-mrs-until-fold-in`.
