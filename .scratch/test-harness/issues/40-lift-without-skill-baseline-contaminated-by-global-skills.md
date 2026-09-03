# 40 — `lift`'s "without-skill" baseline is contaminated by globally-installed skills

**Type:** bug

**What to build:** `fixtures/harness/run.sh lift <fixture> --opencode` (ticket 27) is supposed to compare
a with-skill opencode run against a without-skill baseline by mounting `skills/` into the fixture's
`.agents/skills` for the first run and omitting it for the second (`run_opencode_advisory`'s
`mount_skills` flag). On any machine where this repo's skills are also installed **globally** —
e.g. `~/.agents/skills/continuous-refactoring` → `.../skills/continuous-refactoring`, the layout
`/setup-matt-pocock-skills` produces — the "without-skill" run finds and uses the exact same skills
anyway, via that global path, regardless of whether the fixture's own `.agents/skills` symlink exists.
The comparison the whole command exists to produce is invalid on any such machine.

**Why:** Found running `lift php-partial --opencode` for real (ticket 27's own verification pass,
2026-08-30). The "without-skill" transcript opens with `→ Skill "continuous-refactoring"` and goes on to
read `~/.agents/skills/refactor-scan/SKILL.md`, `.../refactor-design/SKILL.md`, etc. — full
process fidelity, not a naive baseline. `ls -la ~/.agents/skills` on that machine confirms all six of this
repo's skills are symlinked there permanently. `fixtures/README.md`'s existing isolation language ("only
skills from this repo, no global `~/.config/opencode/skills`") only accounts for one global path and
turns out to be incomplete — `~/.agents/skills` is a second one it never considered.

No CLI flag currently avoids this: `opencode run --pure` ("run without external plugins") does **not**
disable skill discovery — verified directly, it still lists the full skill set including
`continuous-refactoring`. `opencode run --help` has no `--no-skills`/`--skills-dir` equivalent as of
version 1.18.23.

**Blocked by:** none — self-contained fix in `fixtures/harness/run.sh`'s opencode-subprocess plumbing.

**Status:** needs-triage

- [ ] Find a real isolation mechanism — candidates worth checking before picking one:
  - Override `$HOME` for the subprocess (e.g. a throwaway `$HOME` with only `~/.local/share/opencode/auth.json`
    copied in, so auth still works but `~/.agents/skills` isn't visible) — needs confirming opencode doesn't
    read anything else from `$HOME` that would break the run.
  - Check for an opencode project/global config key that disables or overrides the skill-discovery path
    (`opencode.json`/`opencode.jsonc` schema — not established from `--help` alone; needs the actual docs).
  - Ask upstream / file a request if no existing mechanism covers this.
- [ ] Until a real fix lands, `lift`'s output and `fixtures/README.md`'s description of it should say
  plainly that the without-skill baseline is unreliable on a machine with the skills installed globally,
  rather than silently presenting a contaminated comparison as clean.
- [ ] Re-check whether `roadmap --opencode` / `tier4 --opencode`'s "isolated" framing needs the same
  caveat — those aren't comparing with vs. without, so global availability doesn't invalidate their
  *result* (the global symlinks point at this exact repo's files, so content is identical either way),
  but the "isolated" claim in their own comments/README language is equally inaccurate and worth
  correcting for the same reason.

## Comments

> **2026-08-30:** Filed while running ticket 27's `--opencode` checks for real for the first time
> (`roadmap`/`judge`/`lift` across the fixture set, model `opencode/big-pickle`) — not fixed inline to
> keep that verification pass from turning into an unplanned harness redesign. Two smaller, in-scope bugs
> found in the same pass (opencode model never pinned; `judge`'s prompt pointed at a path unreachable from
> the isolated fixture workdir) were fixed directly, since they were narrow and clearly this harness's own
> defects rather than an environment-dependent gap like this one.
