# Reference: the signals

A **signal** is the named factor that makes a place in the code a genuine friction spot. Every structural
ticket names one, and Investigation orders both its tickets and what its exploration finds by them. The
catalogue says how each is recognised; recognising one is a judgement, backed by the evidence named here.

Some signals are readable from Git and the files alone (**generic**). For others a tool the target has
set up says something more precise (**from a tool**): where that tool is in place, read its output; where
it is not, the generic reading stands.

## Structural signals

- **Shallow module** — the interface is nearly as complex as what it hides. The **deletion test** decides:
  would deleting the module concentrate complexity, or just move it? "Concentrates" is the signal.
  *Generic* — reading the code.
- **Missing locality** — what changes together lives apart: pure functions were pulled out for
  testability, and the real bugs hide in how they are called. *Generic* — reading the code.
- **Low leverage** — a lot of interface surface buying little behaviour. *Generic* — reading the code.
- **Tightly-coupled seams** — modules leaking across their boundaries. *Generic* — reading the code.
- **Untested or hard to test** — no test reaches it, or its interface resists testing. *Generic* — the
  test suite, or its absence. *From a tool* — PHP: the coverage report of the coverage floor (Clover
  XML); a file well under the floor is the evidence.
- **Tooling pressure** — a place the target's own tools keep flagging, or a dependency nearing its end of
  life. *From a tool* — PHP: PHPStan's findings at the level in force, a Rector dry run, `composer
  outdated`.

## Consequence signals

- **Security** — an exposed secret, an unauthenticated path to sensitive data, an injection class left
  open. *Generic* — reading request handling and the deployment and docroot configuration. *From a
  tool* — the secret scanner's findings; PHP: Psalm's taint analysis, and Semgrep's OWASP rules for what
  taint analysis does not reach (crypto misuse, misconfiguration, logging gaps).
- **Blast radius of inaction** — the cost of leaving it alone keeps rising: a dependency that gets harder
  to migrate the longer it stays, a workaround other code starts to build on. *Generic* — the surrounding
  code and its trend over recent commits.
- **Defect density** — where bugs cluster, however often the area changes. *Generic* — the tracker's
  history, commit messages that mention fixes (`git log --grep`). *From a tool* — PHP: PHPMD's
  complexity findings, which track where defects gather.
- **Understandability** — how hard it is to follow or to change safely: cognitive load (nested
  conditionals, implicit state, unclear names) and knowledge held by one person. *Generic* — reading the
  code; `git shortlog` or blame for the second half. *From a tool* — PHP: PHPMD's cyclomatic complexity.
- **Observability** — nobody can tell when it breaks. *Generic* — reading for silent failures: swallowed
  exceptions, unchecked return values.
- **Domain criticality** — it sits on a core user journey or a revenue path, by what the target's
  glossary or README says the application must keep doing. *Generic* — comparing against those documents.
- **Timing** — a larger change, planned or just landed, resolves this for free or makes it urgent before
  more work builds on the current shape. *Generic* — recent commits and the open tickets.

## Order of signal

Used for the open Investigation tickets and for an exploration's proposals alike. Strongest first:

1. **Security**, then **Blast radius of inaction** — each day it waits makes it worse.
2. Everything else, by four questions. The more of them an item answers with yes, the stronger it is:
   - **Heat** — is it in a hot spot, an area the history shows changing again and again?
   - **Leverage** — do many modules call it, so that deepening it eases much future change?
   - **Tooling pressure** — do the target's tools flag it on every run?
   - **Low risk** — is the change easy to reverse, and narrow in what it touches?

Within either group the target's two project lines (`structural-candidate-search.md`, step 1) move an
item up: one inside a **focus area** stands before one outside, and of two that are otherwise level the
one that brings the code closer to the **refactoring goal** stands first.

Give each item its place together with the reason in a few words ("security: token in the docroot",
"hot spot, called from 14 files").
