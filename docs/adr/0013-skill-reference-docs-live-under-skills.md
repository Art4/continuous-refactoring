# Skill reference docs live under `skills/*/references/`, not `docs/playbooks/`

Manual testing that found the unresolvable ADR self-citations (bookkeeping-branch/MR fix era) surfaced a sibling bug: `docs/playbooks/refactoring-config.md` is cited inline, as something the executing agent should consult, from four `SKILL.md` files — but `docs/playbooks/` never ships. Install is `ln -s .../skills/* <target>/.agents/skills/` (`README.md`): an entire `skills/<name>/` directory ships as a unit, and nothing outside `skills/` reaches the target repo. Every citation of `docs/playbooks/refactoring-config.md` from skill prose pointed at a file the agent could never resolve, the exact same class of gap the ADR self-citation fix closed for `docs/adr/`.

Not every file under `docs/playbooks/` has this problem, though. `docs/playbooks/loop.md` is a human-facing steering guide referenced only from `README.md` — no skill instructs the agent to consult it mid-run, so it has nothing to ship and stays exactly where it is.

## Considered Options

- **Leave `refactoring-config.md` under `docs/playbooks/`, status quo.** Rejected: this is the bug — it doesn't ship, so the citation can never resolve at skill-runtime.
- **Duplicate the file into each of the four citing skills' own directories.** Rejected: four copies of one fact (the shape of `docs/refactoring/config.md`) to keep in sync is worse than the shared-file problem ADR-0003 was solving for *optional* global-skill fallbacks — and this isn't that case: all six suite skills always ship together as one `skills/*` glob, never a subset, so there's no "what if the other skill isn't installed" risk to guard against here.
- **Single copy in the owning skill's `references/` folder, cross-cited by other skills via a full repo-root-relative path.** Accepted: one source of truth, and every citing skill already ships alongside it under the same `.agents/skills/` parent, so the cross-directory reference always resolves.

## Consequences

`docs/playbooks/refactoring-config.md` moves to `skills/continuous-refactoring/references/refactoring-config.md` — the orchestrator owns the "Loop state" concept this doc describes. `continuous-refactoring`, `refactor-scan`, `refactor-design`, and `refactor-implement` all cite it by that path. `docs/playbooks/loop.md` is unaffected and stays under `docs/playbooks/`.

This establishes the general rule for future skill-facing reference docs in this suite: if a `SKILL.md` instructs the agent to consult it, it lives under `skills/<owning-skill>/references/`; if it's written for a human reading the repo, it stays under `docs/playbooks/`. As with the ADR self-citation fix, no skill cites this ADR by number — the rule is a plain pointer to the reference file, nothing more.
