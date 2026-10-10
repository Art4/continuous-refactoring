# 08: Remove the old, bring the docs in line

**What to build:** The repository holds two skills and their references, and nothing of the nine removed
skills. A human reading the README, the architecture page, the playbooks, the FAQ and the known
limitations learns the suite as it now works, including how to install it and how to move a target over
from 0.6.0.

Spec: `../spec.md` (sections *Shape of the suite*, *Onboarding and existing targets*, user stories 45–49).

**Blocked by:** 05, 06, 07

**Status:** ready-for-agent

- [ ] The skills `refactor-loop`, `refactor-scan`, `refactor-prioritize`, `refactor-design`,
      `refactor-implement`, `refactor-learn`, `continuous-safety-net`, `continuous-guardrails`,
      `continuous-investigation` are gone; the tooling-tree files and the parser live under a skill that
      remains
- [ ] No remaining skill text or reference points to a removed file, to bookkeeping, a config file, a
      cadence or a cap
- [ ] The **Comment author and time** operation is removed from the operations reference, its templates,
      the onboarding interview and the glossary, unless ticket 07's comments say Housekeeping reads it
- [ ] `README.md`, `docs/architecture.md`, `docs/playbooks/`, `docs/FAQ.md`, `docs/known-limitations.md`
      and `CONTRIBUTING.md` read true against the rebuilt suite, in their own words, citing no ADR, ticket
      or scratch path
- [ ] The install instructions name two symlinks
- [ ] The known limitations state: a freely written ticket on a large tracker is found only through a
      **Candidate** hint or by being named; parallel merge requests may conflict and resolving that is the
      developer's; a target that is not a PHP project never gets a fulfilled Safety Net gate, so an
      autonomous run stops there; on a tracker strangers can write to, an autonomous Housekeeping run
      weighs a stranger's comment as a proposal like anyone's, carries it out only as a behaviour-keeping
      refactoring, and delivers it in a merge request a human reviews; with a daily rhythm the re-check
      of the tooling Tracks runs daily unless the human moves that task into a rarer template
- [ ] `AGENTS.md`'s description of the suite matches the two skills
- [ ] A changelog fragment marks the rebuild as breaking for 0.7.0 and lists the steps for an onboarded
      target: run onboarding again, delete the old files under the suite's scratch folder (or name the old
      rejections folder under **Rejected**), remove the symlinks of the removed skills
- [ ] No test is written or changed; which checks are red afterwards is listed in a comment on ticket 09
