# Finding the bookkeeping branch

**Doesn't run at all** when `refactor-learn/SKILL.md`'s native-tracker in-flight fold-in exception applies — the writes ride the candidate's own already-open branch instead, no dedicated branch to find or create. Only relevant when that exception doesn't apply: no candidate MR opened this pass, or the tracker has no native labels.

Deterministic, no memory required, never search for a name. Named `refactor-learn/bookkeeping-N`, N starting at 1, numbers never reused even once merged or deleted.

1. `git symbolic-ref refs/remotes/origin/HEAD` (or equivalent) for the default branch, then `git ls-remote --heads origin 'refactor-learn/bookkeeping-*'` for every bookkeeping branch that exists remotely. None found → start fresh at N=1 (step 4).
2. Otherwise take the highest N. `git merge-base --is-ancestor origin/refactor-learn/bookkeeping-N origin/<default-branch>` exits `0` → already merged, not reusable → step 4 with N+1.
3. Not an ancestor (still open) → **reuse it**: `git fetch origin refactor-learn/bookkeeping-N && git checkout -B refactor-learn/bookkeeping-N origin/refactor-learn/bookkeeping-N`. Skip step 4.
4. Pull the default branch's latest, `git checkout -B refactor-learn/bookkeeping-<N+1> origin/<default-branch>`.

Never invent a different name, never `find`/`grep`/browse history to locate "the last bookkeeping branch" — the listing above is authoritative and cheap for a fresh subagent with no memory of earlier passes.
