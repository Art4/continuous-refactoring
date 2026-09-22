# 1 — Fix: cross-skill reference paths don't resolve in a symlink-installed target repo

**What to build:** Every `SKILL.md`/reference file in this suite cites other skills' reference docs
with a path prefixed `skills/<name>/references/...` (e.g. `skills/refactor-implement/SKILL.md`
citing `skills/continuous-refactoring/references/opening-a-merge-request.md`) — a path rooted at
*this suite's own repo root*. That root doesn't exist in a target repo installed per `README.md`'s
own instructions (`ln -s /path/to/continuous-refactoring/skills/* <target>/.agents/skills/`): each
skill lands as its own flat symlink directly under `.agents/skills/`, with no enclosing `skills/`
directory. The fix needs to make every such cross-reference actually resolve from a target repo, for
whichever citing skill an agent is executing at the time — without assuming the executing agent
knows to follow the citing file's own symlink back to the suite repo first.

**Why:** Verified directly against a real installed target repo:

```
$ ls <target>/skills/
ls: cannot access 'skills/': No such file or directory

$ realpath <target>/.agents/skills/refactor-implement
<suite-repo>/skills/refactor-implement
```

`<target>/skills/continuous-refactoring/references/opening-a-merge-request.md` — the path as
literally cited in `refactor-implement/SKILL.md` — does not exist relative to the target repo's own
root. It only resolves if the reading agent first resolves the *citing* file's own symlink
(`.agents/skills/refactor-implement` → the suite repo's real `skills/refactor-implement`) and then
treats the cited path as rooted at that resolved location's parent — a resolution strategy nothing
documents and no convention guarantees an executing agent will perform.

Observed live: an agent working in a target repo, told (via `refactor-implement/SKILL.md`) to consult
`opening-a-merge-request.md`, could not resolve the cited path directly and fell back to searching the
filesystem for the file ("Locate the actual `opening-a-merge-request.md` file on disk") — the exact
friction this finding is about, reproducing on the first real citation checked.

Traced to `docs/adr/0013-skill-reference-docs-live-under-skills.md`, the ADR that introduced this
convention. Its own accepted option's reasoning already contains the mismatch:

> "cross-cited by other skills via a full repo-root-relative path ... every citing skill already ships
> alongside it under the same `.agents/skills/` parent, so the cross-directory reference always
> resolves."

The stated reasoning (siblings under a shared `.agents/skills/` parent) is correct — but the path
convention it accepted (`skills/<name>/references/...`, keeping the suite-repo-root `skills/` prefix)
doesn't match that parent; the resolving path relative to `.agents/skills/` would need to drop `skills/`
entirely (or be written skill-relative, `../<name>/references/...`), not keep it.

**Scope:** this is not limited to `opening-a-merge-request.md`. `grep -rn "skills/[a-z-]*\
/references/" skills/ docs/adr/ docs/playbooks/` turns up dozens of citations across nearly every
`SKILL.md` and reference file in the suite (`refactoring-bookkeeping.md`, `track-open-processing.md`,
`safety-net-write.md`/`guardrails-write.md`, `decision-gate.md`, and more) — every one of them carries
the identical mismatch once installed via symlink into a target repo, per ADR-0013's own convention.

**Blocked by:** none.

**Priority:** high — affects nearly every cross-skill citation in the suite, in every symlink-installed
target repo (the suite's own documented, and only recommended, install method), not a single-file edge
case.

**Status:** needs-triage.

**Parked, not part of this ticket:** whether the copy-install alternative `README.md` also mentions
("Or copy") has the same problem (it likely doesn't — a flat copy of `skills/*` into `.agents/skills/`
has the identical missing-parent issue as the symlink case, so probably in scope too, but not yet
checked) — worth confirming during triage/grilling rather than assumed here.

## Comments

> **2026-09-22:** Filed after the user reported an agent working in a target repo saying "Locate the
> actual `opening-a-merge-request.md` file on disk" instead of resolving the cited path directly.
> Verified live against that target repo's actual installed symlink layout; traced the convention to
> ADR-0013 and found the mismatch between its stated reasoning and the path shape it actually
> accepted. Not yet grilled or fixed — filed for triage.
