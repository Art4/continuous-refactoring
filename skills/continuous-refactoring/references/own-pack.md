# Reference: a Pack of the target's own

The call asked for a Pack of the target's own, or for a tool the suite does not know. The run builds or finishes
that Pack, checks it, and ends with one merge request. Step 1 of the run has passed. The run builds no worklist,
makes no Track choice, and files no ticket; the Stages are worked by later runs, like any other.

What a Pack holds and what it may do is in `tooling-model.md`, *A Pack* and *A target's own Pack*; read both first.

## 1. What is there

Read only.

- **What the suite knows:** the parser's seedless call (`tooling-parser.md`), with `--own-pack` where the section has
  a **Tooling Pack** bullet. It lists every Tool, Stage and Role. Exit code 2 on the target's Pack is a finding for
  step 4; call again without `--own-pack` for the list.
- **The tool is a Tool of the suite's** → no Pack is needed: the run ends, naming the Tool and the call that
  reaches it.
- **The tool:** what it does, its package, the command that proves it, the oldest runtime it ever ran on, from its
  own documentation or the target's manifest. What cannot be read there is named as unknown.
- **The Role:** one of the suite's where it fits, so the Tool competes with the suite's; a new Role only where none
  does.

*Done when* the Tool, its Role and its Stages, each with its Track and `requires`, are clear, or the run has ended.

## 2. The decision point

- **Findings:** the Pack's directory, Tool, Role and whether it is new, the Stages with Track and what they require,
  anything unknown about the tool, and for a Pack that exists what is left to do.
- **Options:** build it (the recommendation); change it; end the run.

*Done when* the answer is taken.

## 3. Build

Check the working tree (`../SKILL.md`, *A clean working tree*), then take a new branch from the default branch's
current tip, named by the target's convention, else `refactor/own-pack-<tool>`.

- **The directory:** the one the **Tooling Pack** bullet names, else a folder `tooling-pack` beside the tracker file.
- **`pack.json`:** its `"$schema"` is the relative path from the directory to `pack.schema.json`, beside this file, in
  the target's installed skills. Written in the form of `packs/generic/pack.json`: two-space indent, objects one key per
  line, lists of plain values on one line. `"scope"` names the language; `"applies_when"` is usually "Always."
- **`roles.json`**, only for a new Role: in the form of `roles.json` beside this file, its `"$schema"` pointing at
  `roles.schema.json` the same way.
- **One Tool file per Tool**, named in `details`, relative to the directory, in the form of
  `packs/generic/editorconfig.md`: for each Stage a `### <slug>` heading with **Purpose**, **Fulfilment check** and
  **MR scope**.
- **The bullet:** `- **Tooling Pack:** <directory>` in `## Refactoring operations`, relative to the repository root,
  where it is missing.

Commit all of it on the branch.

*Done when* the branch holds the Pack and the bullet, and the working tree is clean.

## 4. The check

Call the parser with `--own-pack` and the directory, relative to the target. Exit code 0, with the Pack's Stages in
`tracks`, is the pass.

Exit code 2 names the file, and for a clash both places. The suite's slug stands: rename the Pack's, along with
everything in the Pack that names it, the Tool file's heading included. Correct, commit, call again. A rename goes
into the closing report with the reason. A check that still refuses after two corrections ends the run, naming the
error.

*Done when* the parser exits 0 on the branch's last commit.

## 5. The merge request

Follow `opening-a-merge-request.md`. Handed in: the branch, its commits, the parser's check as the check that ran,
and no ticket. The description's opening says what the project gains from the Tool, and that later runs propose its
Stages.

*Done when* that reference's last step is. The run ends here, with the closing lines of `../SKILL.md`, *The end of a
run*.
