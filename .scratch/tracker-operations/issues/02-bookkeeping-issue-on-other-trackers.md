# 02: Remote bookkeeping anywhere the target describes

**Status:** done — PR #142

**What to build:** Issue mode is written against GitHub and GitLab: the pointer must match one of their issue URLs, and the suite spells out the body, the marked comments and the `gh`/`glab` commands. A project with Redmine tickets cannot keep its bookkeeping there. Make where the bookkeeping lives, and how it gets there, the target's.

- The suite keeps two verbs, **fetch** and **store**, and the working copy under `.scratch/refactor/` (`bookkeeping.md`, `out-of-scope/`, `merge-requests.md`): fetch before a pass, store after every write, last write wins.
- The target describes the rest in an optional **Bookkeeping** bullet under `## Refactoring operations`: where it lives, what the pointer's value means, how it is fetched and stored, and how the place is created where the suite may do that.
- The pointer is opaque. The path of a local `bookkeeping.md` is local bookkeeping; any other value is interpreted with what the target's files say. The bullet is not required by name.
- One stop remains: the bookkeeping can't be fetched. Nothing is created in its place; only onboarding creates the place.
- The former procedure moves unchanged into the **Bookkeeping** bullet of the GitHub and GitLab templates.
- Onboarding's state question gains "as this project describes it"; without a bullet the agent proposes one from the target's own files and the human confirms it.
- "Issue mode" / "file mode" become **remote bookkeeping** / **local bookkeeping**; `issue-mode.md` becomes `remote-bookkeeping.md`.

**Out of scope:** any procedure for a tracker other than GitHub and GitLab, a round-trip probe, per-write report lines, the closed-issue rule — all the target's. No new or changed tests or fixtures.

**Blocked by:** 01.
