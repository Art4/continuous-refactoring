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

**Status:** needs-triage

Open design questions:

- [ ] Non-native-tracker case, or a native tracker where the fold-in exception doesn't apply (a
  separate bookkeeping branch/MR still follows later, per ADR-0011/ADR-0029's non-native path) —
  does the candidate MR open as a normal (non-draft) MR there, since there's no single same-branch
  closing step to key the transition off? Working assumption from the originating memory, not yet
  settled.
- [ ] Should draft status suppress `refactor-scan` step 3's native-tracker reconciliation from
  treating the MR as a genuine open candidate-in-flight, or is it still correct to detect it
  regardless of draft state (i.e. is "draft" purely a human/reviewer signal, invisible to the
  suite's own logic)?
- [ ] Where exactly does the "mark ready for review" step live — its own explicit new step in
  `refactor-learn/SKILL.md`'s closing call, right after the fold-in commit push, or folded into the
  existing fold-in step's description?
- [ ] What happens if the closing-call fold-in commit never lands in the same pass (an interrupted
  pass, matching the tradeoff ADR-0029 already accepted for the `Pending candidates` write) — does
  the MR stay draft indefinitely until a future pass's `refactor-learn` catches up, and is that an
  acceptable steady state (a draft MR sitting open is arguably a *better* visible signal of "not
  actually done yet" than ADR-0029's silent nothing-written state)?
- [ ] Forge-specific mechanics: `gh pr create --draft` / `gh pr ready` for GitHub — confirm the
  GitLab equivalent before writing this into `opening-a-merge-request.md`.

## Comments

> **2026-09-04:** Filed from the `Art4/legacy-todo` reviewer-loop findings log (PR #114 finding) and
> the `candidate-mrs-as-draft-until-bookkeeping` memory, per the user's request to prepare "für
> später" ideas for fixing. Not yet grilled.
