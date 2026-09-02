# Bookkeeping Branch Reference

How refactor-learn manages its dedicated bookkeeping branch.

## Finding the branch (deterministic, no memory required)

Bookkeeping branches are always named `refactor-learn/bookkeeping-N`, N starting at 1, numbers never reused.

1. `git symbolic-ref refs/remotes/origin/HEAD` to name default branch, then `git ls-remote --heads origin 'refactor-learn/bookkeeping-*'` to list existing branches. None found → start fresh at N=1 (step 4).
2. Take highest N. `git merge-base --is-ancestor origin/refactor-learn/bookkeeping-N origin/<default-branch>` exits 0 → merged, not reusable → step 4 with N+1.
3. Not an ancestor (still open) → **reuse it**: `git fetch origin refactor-learn/bookkeeping-N && git checkout -B refactor-learn/bookkeeping-N origin/refactor-learn/bookkeeping-N`. Skip step 4.
4. Pull default, then `git checkout -B refactor-learn/bookkeeping-<N+1> origin/<default-branch>`.

## Rules

- Never invent a different name. Never `find`/`grep` to locate "the last bookkeeping branch".
- Never let deleting a branch be the only record. Before deleting, land the record via a bookkeeping branch/MR off the default branch. Leave stale branches undeleted if no time to merge — a stale unmerged branch costs nothing.
- Never direct commit to default branch. Always via bookkeeping branch/MR.

## `loop-config` exception

Before `loop-config` merges, `config.md` doesn't exist on default branch. Write `Pending candidates` and `Create-mode` on `loop-config`'s own branch instead. After it merges, every closing call uses its own dedicated bookkeeping branch.
