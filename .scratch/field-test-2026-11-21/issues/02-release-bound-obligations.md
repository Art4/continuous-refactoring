# 02 — A one-off task due after the next release has no home

Type: task
Status: open
Blocked by: —

**What was seen**

- The target has no Housekeeping. `implement-point.md` (*Slices every kind of ticket can have*) leaves the Tool's
  Housekeeping line out then, and Housekeeping setup adds the Housekeeping lines of fulfilled Tools later. That
  covers the Roave Tool's general line ("after a release, remove each `<ignored-regex>` entry the release has made
  obsolete").
- It does not cover a one-off task tied to the next release: here, removing `--from=<sha>` from the workflow once a
  release contains the `@internal` marks (see 01). It lived first only in a workflow comment and a review note.
- The Driver then filed a ticket of its own for it, which says it cannot be done before that release. The suite has
  no way to say that a ticket waits for a release: no blocker, no state for it, so a run could pick it as workable.

**Open**

- Where such a task belongs: a ticket that waits for a release (and how its waiting is written), an entry in the
  Housekeeping template, or a Housekeeping comment.
- Whether a run must name such a task in its merge request and closing report when there is no place for it yet.

## Comments
