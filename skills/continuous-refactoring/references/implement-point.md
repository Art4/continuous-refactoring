# Reference: the implement point

Ends with a **branch whose checks are green**, holding the planned change and nothing else. Handed in: the
ticket with its plan, its Track, the run's mode, for a tooling ticket the node's slug and tree-doc file,
and for a ticket in review its merge request with the review's comments. Every slice keeps
`foundational-refactoring-rules.md`.

## 1. Who implements

Decided as `design-point.md` step 2 decides who plans, with two differences: a skill fits here when its
description says it builds a planned ticket, and the `AGENTS.md` sentences that count are those on how
work is implemented, tested and reviewed. The suite's own way is steps 3 to 5 below.

*Done when* it is said who implements.

## 2. The branch

The first row that applies:

| Found | The branch |
| --- | --- |
| the ticket came with its merge request | that merge request's branch, checked out and up to date; the review's comments are findings for step 3 |
| a branch for this ticket — named in one of its comments, or carrying its reference — holds commits the default branch lacks, and no merge request ever came from it | that branch; read its commits before adding to them |
| neither | a new one from the default branch's current tip, named by the target's convention, else `refactor/<ticket reference>-<subject in two or three words>`; for a baseline ticket the subject is the part's name |

A new branch always starts from the default branch, also when another open merge request holds work this
ticket builds on: a forge closes a merge request whose base branch is deleted.

*Done when* the branch is checked out and the working tree is clean.

## 3. Build

**The target's skill** → run it with this brief: the ticket and its plan, the branch, the review's
comments where the ticket came with them, `foundational-refactoring-rules.md`, and the outcome wanted —
the plan's slices committed on this branch, its `Done when` commands passing. Whether it also opens the
merge request is its own matter. Then go to step 4.

**The suite's own**, by the kind of ticket:

- **A tooling ticket** → make the change the plan's slices name: a dependency, configuration, a CI job.
  Where the tool rewrites code (Rector, a code-style fixer), the tool's own run is one commit and holds
  nothing typed by hand. No test is written.
- **A baseline ticket** → fix file by file, one commit per file, following the tool's diagnosis. Then
  regenerate the baseline with the command the plan names and commit it by itself. No test is written:
  the existing suite is what notices a behaviour change.
- **Any other ticket** → slice by slice, test-first at the plan's seam: write one failing test through the
  seam's public interface, watch it fail for the expected reason, write the code that makes it pass,
  commit. Tests go where the target's `tests/README.md` puts them; where that file is missing, the
  target's language may have a layout among the tree docs (`tooling-tree-parser.md` says where they are;
  PHP: `phpunit.md`, *Test layout*). Which tests are kept: `reviewing-a-change.md`, *Tests worth
  keeping*.

**The work turns out to need a behaviour change** → stop building. The branch stays as it is, and the run
goes to `design-point.md`, the first of the *Two findings*.

*Done when* every slice of the plan is committed on the branch.

## 4. Checks

Run all of these on the branch, after the last commit:

- the plan's `Done when` commands — for a tooling ticket the node's Fulfilment check, for a baseline
  ticket the regenerated baseline without the part's entries;
- the target's whole test suite;
- every tool the target already runs as a check — static analysis, code style, the ones its CI file
  calls — over the files this branch touched.

A red check → fix it on the branch and run them all again. A check outside the plan's `Done when` that
was already red on the default branch is named as such and left alone.

*Done when* every command above ran after the last commit and passed, or is named as red before this
work.

## 5. Review

The diff of the branch against the default branch is reviewed on two axes, per `reviewing-a-change.md`.
The review may run in a subagent handed that reference, the diff and the plan; it returns findings.
A finding → back to step 3 for it, then steps 4 and 5 again.

A target's skill that built the branch has reviewed it its own way. The suite then reads the diff once
against the plan; a slice found missing is built the suite's own way (step 3) and checked (step 4).

*Done when* the final diff holds every slice of the plan and no finding is left.

## Slices every kind of ticket can have

The plan lists them where they apply; they are built in step 3 like any slice, each as one commit.

- **ADR** — for each entry of the plan's `Decisions` that a human answered or confirmed, where the
  target's domain docs (`docs/agents/domain.md`, or what its `AGENTS.md` names in its place) say where
  ADRs are kept: one ADR in the form and numbering of the newest one there. Where they name no such
  place, the decision stays in the plan and goes into the merge request's description.
- **Glossary** — where those docs name a glossary file: a term the work introduced, added as a definition
  and nothing else.
- **Housekeeping line** — a node with a **Housekeeping** field adds that line, as a recurring task, to
  the Housekeeping template the target's **Housekeeping** operation names, the first where it names
  several. Where the target has no such
  operation the line is left out, and the Housekeeping Track adds it once its mechanism exists.

## Hand on

To the merge-request step, which names what it needs.

The implement point is done when the branch holds every slice and step 4's checks are green on its last
commit.
