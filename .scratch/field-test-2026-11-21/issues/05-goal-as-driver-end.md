# 05 — A content goal as the Driver's End

Type: task
Status: open
Blocked by: —

**What was seen**

- The maintainer started the Driver with a content goal: go on until the library is compatible with PHP 7.4 through
  8.5. The settings table of `continuous-refactoring/SKILL.md` allows as End only a number of rounds, of merged merge
  requests, a time, or "until nothing is workable".
- The Driver read the goal back correctly and worked toward it, which the maintainer wanted to see. No Stage of the
  PHP Pack leads there (nothing widens a CI matrix), so the work came from tickets outside the tooling tree: extend
  the CI matrix, then a fix for the PHPStan deprecation that blocked it.
- It stopped when the merge request for the matrix was mergeable, before the human merged it. With `review only`
  that is the last point the Driver can reach; whether that counts as "goal reached" or "waiting for the human" is
  not written anywhere.

**Open**

- Whether a goal becomes an End form of its own, and what it takes: how a run gets the goal (through the Call?),
  where work toward it comes from when no Stage leads there, and when the goal counts as reached under
  `review only` versus `merge`.
- Which Stop it ends with (`ended`?) and what the report says about the open merge request.

## Comments
