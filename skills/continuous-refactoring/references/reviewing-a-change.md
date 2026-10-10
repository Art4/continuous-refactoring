# Reference: reviewing a change

The suite's own review of a branch before its merge request: the diff against the default branch, on two
axes, **Spec** and **Standards**, reported separately. A finding is one line — file, what is wrong, why —
and sends the work back to be fixed.

## Spec

Does the diff do what the plan on the ticket says? Go through the plan slice by slice and quote the line
each finding is checked against. Three kinds of finding: a slice missing or half done; a change the plan
does not ask for; a slice that looks done and does something else. A change in what the target observably
does is always a finding, whatever the plan says.

## Standards

Does the diff follow what the target documents — its `AGENTS.md`, `CONTRIBUTING.md`, coding standards,
domain docs? What a tool of the target already enforces is left to that tool.

On top of the documented standards, look for these **smells** in the lines the diff adds. Each is a
judgement, reported as "possible <smell>"; a documented standard of the target that endorses the pattern
wins. A smell is a finding when its way out stays within the plan's slices; one that would need more is
named in the merge request's description and left.

| Smell | In the diff | Way out |
| --- | --- | --- |
| Mysterious Name | a name that does not say what the thing does or holds | rename; no honest name to be found means the design is unclear |
| Duplicated Code | the same shape of logic in more than one hunk | extract it, call it from both |
| Feature Envy | a method that uses another object's data more than its own | move it to that data |
| Data Clumps | the same few values travelling together | one type for them |
| Primitive Obsession | a string or number standing in for a domain concept | a small type for the concept |
| Repeated Switches | the same branching on the same type in several places | polymorphism, or one shared map |
| Shotgun Surgery | one logical change spread over many files | gather what changes together |
| Divergent Change | one module edited for unrelated reasons | split by reason |
| Speculative Generality | a hook, parameter or abstraction the plan has no use for | delete it |
| Message Chains | `a.b().c().d()` | one method on the first object |
| Middle Man | a class that only passes calls on | call the target directly |
| Refused Bequest | a subclass ignoring most of what it inherits | composition |

## Tests worth keeping

Part of the Standards axis. A test added by the change is kept when it checks behaviour through a public
interface and would still pass after the code behind that interface is rewritten. Two findings:

- **Tautological** — the assertion computes the expected value the way the code does, so it can never
  disagree with the code.
- **Coupled to the implementation** — it mocks an internal collaborator, calls a private method, or
  checks through a side channel.

The review is done when every slice of the plan and every changed file was looked at on both axes.
