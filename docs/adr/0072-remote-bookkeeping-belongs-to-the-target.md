# Where remote bookkeeping lives, and how it gets there, belongs to the target

> Amends [ADR-0064](0064-bookkeeping-state-lives-in-an-issue-or-a-local-file.md): the place that is not a
> local file no longer has to be a GitHub or GitLab issue, and the suite no longer describes how it is
> read and written.
>
> Amends [ADR-0071](0071-tracker-through-operations-tracker-and-forge-apart.md): **Bookkeeping** joins the
> optional operations, and issue mode is no longer written against `gh`/`glab`.

ADR-0071 made the tracker a set of operations but left issue mode as it was: a pointer had to match a
GitHub or GitLab issue URL, and the suite spelled out the body, the marked comments and the commands. A
project with Redmine tickets could not keep its bookkeeping there. Generalising the procedure showed that
every part of it is a property of the place — whether a comment can be edited or deleted, whether writing
sends mail, whether the markup survives — and none of it is the loop's.

## Decision

The suite keeps its own side and nothing else. With **remote bookkeeping** the files under
`.scratch/refactor/` are a working copy; the suite **fetches** the bookkeeping before a pass and
**stores** it after every write, the last write wins, and bookkeeping that can't be fetched stops the
pass. Only onboarding creates the place.

Where the bookkeeping lives, what the pointer's value means and how fetching and storing are done are
the target's, written as an optional **Bookkeeping** bullet under `## Refactoring operations`. The
pointer is opaque: the path of a local `bookkeeping.md` is **local bookkeeping**, any other value is
read with what the target's files say about it. The agent does not require the bullet by name — a
pointer nothing explains simply can't be fetched.

The GitHub and GitLab templates carry the former issue-mode procedure unchanged in their **Bookkeeping**
bullet, so existing bookkeeping issues keep working. For any other place the onboarding agent proposes a
bullet from the target's own files and the human confirms it.

One requirement is stated and not checked: what was stored comes back unchanged at the next fetch.

## Considered

- **A fixed list of sub-operations (read body, replace body, add, edit, delete a comment).** Rejected —
  it keeps the issue-with-comments layout as the only shape and rules out a wiki page or an attachment.
- **Everything in the issue body, no comments.** Rejected — it changes the storage of existing GitHub
  and GitLab bookkeeping issues to solve a problem only other trackers have.
- **A round-trip probe during onboarding.** Rejected — whether a procedure holds is the target's to know.
- **Stop when the pointer is not a local file and no Bookkeeping bullet exists.** Rejected as too
  specific: the pointer is read and interpreted whatever the target calls its description.

## Consequences

"Issue mode" and "file mode" leave the vocabulary; `issue-mode.md` becomes `remote-bookkeeping.md`. The
parser treats a pointer as a local path only when it names a `bookkeeping.md`; every other value reads
the default working copy. A lossy procedure in a target loses state without the loop noticing —
`docs/known-limitations.md` says so. No tests or fixtures were changed.
