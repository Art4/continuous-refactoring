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

**Status:** done — this PR.

**Parked, not part of this ticket:** whether the copy-install alternative `README.md` also mentions
("Or copy") has the same problem — confirmed during implementation: no, the accepted fix (paths
relative to the citing file) resolves identically under either install method, since both produce the
same flat-sibling directory shape under `.agents/skills/`. Nothing further to do there.

## Comments

> **2026-09-22:** Filed after the user reported an agent working in a target repo saying "Locate the
> actual `opening-a-merge-request.md` file on disk" instead of resolving the cited path directly.
> Verified live against that target repo's actual installed symlink layout; traced the convention to
> ADR-0013 and found the mismatch between its stated reasoning and the path shape it actually
> accepted. Not yet grilled or fixed — filed for triage.

> **2026-09-22 (grilling):** Settled via `/grilling` (6 questions, one round). **Q1 — scope**: migrate
> only the 292 citations inside `skills/**` (the only tree that ships); the other 55 citations
> elsewhere (`docs/adr/`, `docs/playbooks/`, `.scratch/`, `CONTEXT.md`, `README.md`) are never
> installed, so the old form already resolves correctly there — left untouched. **Q2 — same-skill vs.
> cross-skill**: simplified separately — a same-skill citation drops the now-redundant own-skill
> segment (shortest relative form); a real cross-skill citation gets a depth-correct `../` count. **Q3
> — migration mechanism**: one-off script, discarded after the run, not kept as a maintenance tool.
> **Q4 — new ADR**: yes, amending ADR-0013. **Q5 — `scripts/validate_skills.py`**: updated to resolve
> the new form relative to the citing file and to flag any reappearance of the old
> `skills/<name>/references/...` form as an error. **Q6 — testing**: the extended static check plus the
> existing `unittest` suite is sufficient; no separate symlink-fixture integration test.
>
> Before committing to the direction, the proposed relative-path format was checked empirically, not
> just reasoned about: a scratch copy of four real skills, two real citations rewritten to the proposed
> form, symlink-installed into an empty fake target exactly per `README.md`'s own command, and a real
> coding-agent subagent (OpenCode) told to follow each citation as written. Both a one-level
> (`SKILL.md`-to-sibling) and a two-level (nested `references/`-to-sibling) citation resolved directly
> on the first `Read`, no search needed.

> **2026-09-23 (implement):**
> [ADR-0061](/docs/adr/0061-skill-crossref-paths-are-citing-file-relative.md) added, amending ADR-0013.
> All 292 in-scope citations migrated via a one-off script (discarded after the run): same-skill ones
> simplified, cross-skill ones rewritten `../<skill>/references/...` with a depth-correct `../` count.
> Two citations the script's plain substring approach couldn't reach — each split across a line by
> prose reflow — fixed by hand. `scripts/validate_skills.py`: `local_ref_issues` now resolves a
> `../`-/`references/`-prefixed citation relative to its own citing file and unconditionally flags any
> remaining `skills/<name>/references/...` citation inside `skills/**` as an error; the orphaned-
> reference advisory now matches a reference file's basename instead of its full former path (a
> citation no longer repeats that full path in any form); the ADR-0004 keyword-propagation check's
> cross-skill-content augmentation now resolves the new relative form too. New unit tests for all three.
> Incidentally found and fixed along the way: `outlook-comment.md` used backtick-quoted
> `references/tooling_tree.py`/`references/tree-walk-prompt.md` descriptively (another skill's own
> installed location, not a literal citation from this file) — dropped the backticks so it no longer
> reads as a path the new check should validate. Full test suite green (229 tests), `validate_skills.py`
> clean (same pre-existing warning-only baseline as before this change, zero new errors).

> **2026-09-23 (follow-up):** A second session test-ran the fixed suite live against a real symlink-
> installed target repo — every citation resolved directly except one: `safety-net-track.md`/
> `guardrails-track.md` (2 occurrences each) described a node's tree-doc entry with the placeholder
> `php-tooling-tree/<node>.md`, implying a 1:1 slug→filename derivation that doesn't hold for a
> multi-node file (`rector.md` covers five `rector-*` nodes, `psalm.md` covers two) — the agent had to
> `find` its way to `rector.md`. Not a regression of this ticket's own fix (a separate, narrower
> documentation-accuracy gap, unrelated to the citing-root problem this ticket closed) but folded in
> here rather than filed separately, since it's the same class of "agent has to search instead of being
> told exactly where to look." Fixed: all 4 occurrences reworded to point at `php-tooling-tree.md`'s own
> per-node *Full definition* pointer (which already names the correct file for every node, multi-node
> ones included) instead of implying direct slug-to-filename derivation.
