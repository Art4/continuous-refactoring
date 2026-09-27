# Reference: issue mode — the bookkeeping document in a tracker issue

Where `refactoring-bookkeeping.md`'s Bookkeeping pointer is a URL, the bookkeeping document lives in that issue
instead of in a file. It is what lets the state be picked up from another machine without anything being
committed. Every skill still works on the same local files it always did; **load** and **save** (below) are the
only difference.

## The pointer

An issue URL on the target's own tracker: `https://github.com/<owner>/<repo>/issues/<n>` (GitHub) or
`https://<host>/<group>/<project>/-/issues/<n>` (GitLab), reached with `gh` / `glab`. Any other URL, or a
tracker other than GitHub or GitLab, isn't supported: stop with a clear message and change nothing. A local
Markdown tracker never has a URL pointer — it is always file mode.

## What lives where

- **The issue body** is the bookkeeping document. It starts with two plain sentences for a human who lands on
  the issue (what it holds, that editing it changes what the loop does), then a line `---`, then the document
  itself from its `# Refactoring Bookkeeping` title on.
- **Comments** hold the two things that don't fit a body. One comment per learned rejection, whose first line
  is `<!-- refactor:out-of-scope <slug> -->`, followed by the entry's text — the content of what would be
  `out-of-scope/<slug>.md` in file mode. One comment per remembered merge request (only when the tracker has no
  native labels), whose first line is `<!-- refactor:merge-request -->`, followed by its fields. Any other
  comment is a human talking and is ignored.
- The issue has no label of its own, and the Track sections' `Out-of-scope` lists in the body keep pointing at
  `out-of-scope/<slug>.md` exactly as in file mode — the entry simply comes from a comment.

## The working copy

The Refactoring Notes are `.scratch/refactor/`, always, in issue mode: a cache the suite rewrites on every load.
`bookkeeping.md`, `out-of-scope/` and `merge-requests.md` there are what every skill, and the parser, read and
write; none of it is authoritative and the suite never commits it. The config file (`config.md`) is not cached
state — it stays exactly as it is.

## Load

Before a pass reads any state, its entry point loads: `refactor-loop`, `continuous-housekeeping`, the
dispatcher's Track selection, and a lifecycle skill invoked on its own.

1. Read the issue's state, body and comments (`gh issue view <n> --json state,body,comments`, or the GitLab
   equivalent).
2. Can't read it (deleted, no access, no CLI, forge error) → **stop**: "the bookkeeping issue can't be read:
   <reason>". Nothing runs and nothing is created in its place.
3. Closed but readable → carry on, and say in the closing report that the issue is closed.
4. Replace the working copy: `bookkeeping.md` ← the body from its `# Refactoring Bookkeeping` line on; the
   `out-of-scope/` files and `merge-requests.md` ← the marked comments. Remove whatever the working copy held
   before, so nothing stale survives.

Never load over working-copy changes that haven't been saved — every writing skill saves before it returns
(below), so this only happens after a pass was cut short. In that case save first if the changes are the
suite's own, and ask otherwise.

## Save

Every skill that wrote the working copy saves before it returns: `refactor-learn`, and `refactor-design` for its
`Pending candidates` write.

1. Body ← the two sentences, `---`, and the working copy's `bookkeeping.md`. **The last write wins**: the suite
   doesn't reload and merge, so a human edit made while a pass runs is overwritten.
2. For each `out-of-scope/<slug>.md` and each `merge-requests.md` entry: no comment yet → add one; a comment
   whose text differs → edit it; a marked comment whose entry is gone (a rejection reversed, a merge request
   dropped) → delete it.
3. Each write is reported on its own line (`reporting-progress.md`): a comment added or changed on an issue is an
   ordinary forge write.

`Ticket-create-mode` doesn't apply: the bookkeeping issue isn't a ticket, and the loop never creates it.

## Only onboarding creates the issue

With a human present, the onboarding interview (`onboarding-setup-interview.md`) creates the bookkeeping issue
or adopts an existing one. No other skill, in any circumstance, creates a replacement — a pointer that doesn't
resolve stops the pass.

## Writing the body and comments

Both are text on the target repo's own forge, so `forge-facing-writing.md` applies: no skill file paths, no
internal vocabulary a reader of that project wouldn't know.
