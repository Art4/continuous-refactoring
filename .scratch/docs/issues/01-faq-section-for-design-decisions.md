# 1 — FAQ/Q&A section explaining recurring design decisions

**What to build:** A canonical, written Q&A doc answering recurring questions about the skill suite's
own design — the kind of question a newcomer (or a target-repo maintainer skeptical of the suite) asks
early, that currently gets re-explained ad hoc every time it comes up.

Two entries already drafted (captured as a memory note, never built anywhere real):

1. **Warum installiert die Skill-Suite so viele Tools statt einfach das Refactoring zu starten?**
   Weil man LLMs nicht trauen kann — die Tools führen deterministische Verbesserungen und
   Absicherungen ein, bevor ein Agent den Code verändern darf. Überspringbar, aber zulasten von
   Qualität/Abwärtskompatibilität; Reviews lassen sich darüber auch steuern/beschleunigen/lenken.
2. **Warum ist `continuous-housekeeping` ein eigener Skill statt ein wiederkehrender
   Tooling-Tree-Node?** Der Tree ist rein faktenbasiert/dateisystem-getrieben — der deterministische
   Parser hat keinen Forge-Zugriff, könnte eine Taktung nie aus Tracker-Historie ableiten, und ein
   zeitgetriebenes Fulfilment würde `structural-scan`s `resolved`-Gate-Annahme verletzen (einmal
   aufgelöste Blätter bleiben aufgelöst). Inhaltlich passt ein Sweep auch nicht in
   scan→prioritise→design→implement→learn — er liefert nicht einen gerankten Kandidaten, er arbeitet
   eine stehende Checkliste ab.

**Why:** Filed at the user's explicit request, after the second entry came up naturally while
building ticket 38 (`continuous-housekeeping`). Worth having a canonical answer rather than
re-explaining ad hoc every time a similar "why not the simpler-seeming alternative" question comes up
— and it will keep coming up, since this suite makes several deliberately non-obvious calls.

**Blocked by:** none.

**Priority:** low — pure documentation, no bug/gap it fixes.

**Status:** needs-triage

Open questions (none decided yet):

- [ ] **Where does it live?** Options: a new `docs/FAQ.md`; a section inside `README.md` directly;
  woven into `CONTEXT.md` (doesn't fit — that's vocabulary, not justification); one Q&A per relevant
  ADR's own "Consequences" section instead of a separate doc at all. The memory note this ticket comes
  from explicitly left this open for the user to decide.
- [ ] **Format:** a flat, growing Q&A list (simplest, matches the two drafted entries' own shape), or
  grouped by theme once there are enough entries to need it?
- [ ] **Audience:** newcomers deciding whether to adopt the suite (belongs near the README's own
  front door), or people already running it who hit a specific "why does it do X" moment (belongs
  closer to the relevant playbook/skill doc instead, possibly several smaller FAQs rather than one
  central one)? These pull toward different homes for the same content.
- [ ] **Growth process:** does every future ADR of a certain weight (recommended-edge-change class)
  automatically get an accompanying FAQ entry drafted alongside it, or does this stay a manually
  curated, occasionally-updated doc?

## Comments

> **2026-09-06:** Filed from a memory note (`qa-section-idea-for-skill-suite`) capturing two drafted
> entries — the first from 2026-09-04, the second from today's `continuous-housekeeping` work. Not
> designed yet; the memory note itself already flagged "where should this live" as an open question
> for the user.
