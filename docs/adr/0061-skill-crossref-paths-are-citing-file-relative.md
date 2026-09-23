# A skill's cross-reference to another skill's file is written relative to the citing file, not the suite repo's root

> Amends [ADR-0013](0013-skill-reference-docs-live-under-skills.md): the accepted option's path
> convention (`skills/<name>/references/...`) is reversed for citations *between* skills — see that
> ADR's own "Amended by" note. Its rule for where a skill-facing reference doc lives is untouched.

Every `SKILL.md`/reference file in the suite cited another skill's reference doc with a path rooted at
the suite repo's own root — `skills/continuous-refactoring/references/opening-a-merge-request.md`, for
example, cited from `refactor-implement/SKILL.md`. Install is `ln -s .../skills/* <target>/.agents/
skills/` (`README.md`): each skill lands as its own flat symlink directly under `.agents/skills/`, with
no enclosing `skills/` directory — that root simply doesn't exist in an installed target repo.

Verified live against a real installed target repo:

```
$ ls <target>/skills/
ls: cannot access 'skills/': No such file or directory

$ realpath <target>/.agents/skills/refactor-implement
<suite-repo>/skills/refactor-implement
```

`<target>/skills/continuous-refactoring/references/opening-a-merge-request.md` — the path as literally
cited — doesn't exist relative to the target repo's own root. It only resolves if the reading agent
first resolves the *citing* file's own symlink back to the suite repo and treats the cited path as
rooted at that resolved location's parent — a resolution strategy nothing documented and no convention
guaranteed an executing agent would perform. Observed live: an agent working in a target repo, told to
consult the cited file, could not resolve it directly and fell back to searching the filesystem for it
by name.

ADR-0013's own accepted-option reasoning already contained the mismatch: "every citing skill already
ships alongside it under the same `.agents/skills/` parent, so the cross-directory reference always
resolves" — true of the *parent*, but the path shape accepted (keeping the suite-repo-root `skills/`
prefix) doesn't match that parent; a path resolving relative to `.agents/skills/` has to drop `skills/`
entirely, or be written skill-relative (`../<name>/references/...`).

Before deciding, the fix itself was checked mechanically rather than assumed: a scratch copy of four
real skills, two real citations rewritten to the proposed relative form, symlink-installed into an
empty fake target exactly per the README command, and a real coding-agent subagent (OpenCode, a
different harness than this suite's own) told to follow each citation as written. Both a one-level
(`SKILL.md`-to-sibling) and a two-level (nested `references/`-to-sibling) case resolved directly on the
first `Read`, no search needed, confirming the relative form actually resolves through a real symlink
chain rather than only on paper.

## Considered Options

- **Document a resolution algorithm instead of changing the paths**: "resolve your own skill directory's
  symlink first, then treat the cited path as rooted at that location's parent." Rejected: this is
  exactly the unstated assumption that already failed live (above) — nothing enforces an executing agent
  performs it, and it depends on the agent bothering to inspect its own symlink at all.
- **Duplicate the cited content into every citing skill's own directory.** Rejected for the same reason
  ADR-0013 already rejected it for a smaller case: dozens of citing skills would each need their own
  copy of shared fact kept in sync, a worse problem than the one being fixed.
- **Write every cross-skill citation relative to the citing file itself** (`../<name>/references/...`,
  depth-correct for however deeply the citing file is nested), and simplify a *same*-skill citation the
  same way, dropping the now-redundant own-skill segment entirely (`references/...` from a `SKILL.md`,
  a shorter relative form from a nested `references/` file). Accepted: resolves identically whether a
  skill is symlink-installed or plain-copied, needs no knowledge of the parent directory's name, and
  requires no runtime resolution logic beyond what any file-reading tool already does with `../`.

## Consequences

Every `skills/**` citation of another file was migrated (292 citations across 61 files) — same-skill
ones simplified, cross-skill ones rewritten with a depth-correct `../` count, via a one-off migration
script discarded after the run rather than kept as a maintenance tool. Citations from outside
`skills/**` (`docs/adr/`, `docs/playbooks/`, `.scratch/`, `CONTEXT.md`, `README.md`) are unaffected —
those files are never installed into a target repo, so they are always read from the suite repo's own
root, where the old form already resolves correctly; rewriting them would be diff noise with no
functional benefit.

`scripts/validate_skills.py`'s local-reference check now resolves a `../`- or `references/`-prefixed
citation relative to its own citing file (a `SKILL.md`'s own directory, or a `references/` file's
parent) instead of the suite repo's root, and unconditionally flags any remaining `skills/<name>/
references/...`-shaped citation inside `skills/**` as an error — the old form must never reappear. The
orphaned-reference advisory, which used to look for a reference file's full suite-root-relative path
appearing verbatim elsewhere, now matches on the file's basename instead, since a citation no longer
repeats that full path in any form. The ADR-0004 keyword-propagation check's cross-skill-content
augmentation (pulling a cited file's text into the citing skill's own text for that check) now matches
the relative form too, resolving straight to `skills/<cited skill>/references/...` rather than walking
the literal `../` count, since that check only needs to know *which* file was pulled in.

A same-skill citation where both files sit in the exact same immediate directory now simplifies to a
fully bare filename with no `references/` or `../` prefix at all — that specific narrow shape is not
validated by the check above (a bare `word.md` is structurally indistinguishable from the suite's own,
already-established convention of citing a *target* repo's file bare, e.g. `bookkeeping.md`, `AGENTS.md`,
`tests/README.md`, which must never be checked against the suite repo). That gap is not new: a bare
same-skill citation written this way already existed throughout the suite before this fix and was never
validated either way; this fix does not shrink that pre-existing, out-of-scope gap, only closes the one
this ticket was filed for.
