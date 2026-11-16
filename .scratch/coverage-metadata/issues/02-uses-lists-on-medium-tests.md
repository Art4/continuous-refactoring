# 02 — No `#[UsesClass]` lists on medium and large tests

Type: task
Status: open
Blocked by: —

From GitHub issue #279. A target that followed `coverage-metadata-strict` ended up with `#[UsesClass]` lists of
hundreds of lines on its integration tests. The design record of the Stage (ADR-0090) rejected exactly that:
"Integration tests list everything they use. Lists that change with every extract."

**Cause.** *Working under the metadata Stages* told every test that runs an extracted class to list it, with no
exception for medium and large tests. The *MR scope* tied the size to `tests/Integration/` and `tests/Functional/`,
so a test that runs real collaborators elsewhere was told to list them.

**Decided** (grilled 2026-11-16)

- Q1: a gap in the skill text against ADR-0090, no new ADR.
- Q2: the working rule says that a unit test lists what it uses; a medium or large test lists nothing and keeps its
  `#[CoversClass]` alone.
- Q3: the size goes by what a test does, not where it lives. `#[Medium]` marks an integration test, which runs real
  collaborators on purpose; `#[Large]` marks a functional test, which runs the application through its entry point.
  The two directories are named as the rule.
- Q4: the fulfilment check adds the following: every integration and functional test carries its size and no
  `#[UsesClass]`. The Housekeeping re-check of the tooling Tracks finds a target with lists, and files a ticket.
- Q5: a shared list on an abstract base class is rejected. PHPUnit 10.5 to 12.5 read class attributes only from the
  test class. 13.4 deprecates size and group attributes on parents. 14 inherits size and groups, never
  `#[UsesClass]`. Nothing about it goes into the skill.
- Q6: this ticket, the change and a new scenario go in one PR, which closes #279.
- Q7, Q9–Q12: a new walk-through scenario, r12, with two variants. A is an extract that must leave a `#[Medium]`
  test alone. B is the Housekeeping re-check finding the lists, one of them on a test outside `tests/Integration/`.
  One player and one judge, on the human's go.
- Q8: the analysis is posted on #279 first.

**Done when** `coverage-floor.md` says the above, r12 passes, and tests and validator are green.
