# 05: Design, implement, merge request

**What to build:** A selected ticket gets a plan and an implementation, and the run ends with an open
merge request. Where the target has its own skills for planning and implementing, the suite recommends
those; otherwise it uses its own fallback references. A decision worth recording travels in the same
merge request.

Spec: `../spec.md` (sections *Design and implementation*, *The run*). The fallback references are written
new with the `writing-for-agents` skill, carrying over what still applies from the old design and
implement skills (grounding a candidate, the decision gate for a breaking change, test-first slices,
review, the forge-facing writing rules, never deleting a branch that holds the only record of a decision).

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] At the design and at the implement point the suite looks at the target's available skills and its
      `AGENTS.md`, recommends the target's own, and falls back to its references; the choice is stored
      nowhere
- [ ] The design point ends with an implementable plan on the ticket; an autonomous run that needs a human
      answer ends there with a message naming the open question
- [ ] The implement point ends with a branch whose checks are green
- [ ] The suite opens the merge request per **Merge requests** and **Linked merge request** unless it
      already exists; with no forge the prepared branch is handed to the human
- [ ] An ADR and a glossary change are committed on the candidate's branch, and only where the target's
      domain docs say ADRs are kept
- [ ] A design that finds the candidate cannot be done without changing behaviour ends as a decision
      point, not as a silent stop
- [ ] A **Flagged candidate** works in a target that has no `docs/agents/triage-labels.md`: onboarding no
      longer writes that file (ticket 02), so the "waiting on you" and "ready" states are either expressed
      without triage labels or the design point proposes setting them up at a decision point; the
      glossary entry and the now unreferenced `triage-labels-template.md` are brought in line with
      whichever is chosen
- [ ] No ticket mode or merge-request mode is read; the run's mode decides whether the suite asks
- [ ] No test is written or changed
