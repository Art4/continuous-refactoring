# p1 — A tool the suite does not know, on an onboarded target

Played live.

## Situation

A copy of the fixture `php-own-pack`, without a Pack: delete `docs/agents/tooling-pack/` and the **Tooling Pack**
bullet from `docs/agents/issue-tracker.md`, then commit. The tracker file has `## Refactoring operations`, and
**Merge requests** says the prepared branch goes to the human.

## Call

`/<run skill> a Pack of its own for Deptrac, to check the dependencies between the layers, do it yourself`

## Expected

- [ ] It says back in one sentence that it builds a Pack, for Deptrac.
- [ ] It builds no worklist, makes no Track choice and files no ticket.
- [ ] A new directory holds `pack.json` with a `"$schema"` line and the two-space form of the suite's Packs.
- [ ] The Tool has one details file, named relative to the directory, with Fulfilment check and MR scope for each
      Stage.
- [ ] A Role the suite does not have sits in a `roles.json` beside it. A Role the suite has is reused, not added.
- [ ] Every slug is new: no Tool, Stage, Role or Pack of the suite's is redefined.
- [ ] `## Refactoring operations` gains the **Tooling Pack** bullet, naming the directory relative to the repository
      root.
- [ ] It calls the parser with `--own-pack`, and that call exits 0 before anything is handed on.
- [ ] One branch holds all of it, and the tree is clean afterwards.
- [ ] The branch goes to the human, as **Merge requests** says. Its description reads without a ticket and names
      no file of the suite.
- [ ] The run ends there with the **Status** and **Next** lines, and starts no other work.
- [ ] A later parser call on that branch, with the Pack's directory, lists the Pack's Stages.

## Results

2026-11-01, skill commit d53ce5f: pass, every line. Fixture copy with the skills linked in, no forge, so the branch went to the human and no merge request description was written: the line on the description holds for the closing report only. The agent could not read Deptrac's documentation, named that as unknown and said so in the Tool file. `pack.json` and `roles.json` are valid against the schemas and in the fixed form; `$schema` resolves.
