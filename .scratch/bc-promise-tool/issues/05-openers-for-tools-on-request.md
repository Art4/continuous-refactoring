# 05 — Openers for the other Tools on request

Type: grilling
Status: done
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

**Decided** (2026-11-03)

- Infection belongs here too: every Tool on request is settled.
- **Semgrep / Psalm Taint Analysis:** the Opener is a plan for a ticket whose signal is Security, read from the code
  because no tool for it is in place. An injection goes to `psalm-taint-analysis` where PHPStan Level 4 or Psalm is
  fulfilled, otherwise to `semgrep`; every other class goes to `semgrep`. One line per finding.
- **Infection:** a plan whose existing tests reach the code but check little of it, and which writes a new pin.
- **Secret Detection:** no Opener; Housekeeping's history scan finds a committed secret.
- A design that ends on a change of behaviour carries the Opener line in its open question; the line names the
  Tool's key. Scenarios r3–r5.
