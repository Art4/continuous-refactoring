# 05 — Openers for the other Tools on request

Type: grilling
Status: open
Blocked by: 01

**The question** (ADR-0093, spec Q22)

Which situation in a run is the Opener of each other Tool on request, if it has one at all?

- **Semgrep (OWASP Top 10)** and **Psalm Taint Analysis**: for example, a plan that touches code where input from a
  request reaches a sink (SQL, shell, output) with nothing checking it.
- **Secret Detection**: something that looks like a secret is more an urgent finding than an Opener; it touches
  Housekeeping's history scan (ADR-0089).

For each: the Opener's wording in the Tool file, why it is the moment the Tool pays off, and how often it would
fire on an old codebase.

**Done when** each of the three has an Opener or the decision that it gets none, recorded in its Tool file through
a PR of its own.
