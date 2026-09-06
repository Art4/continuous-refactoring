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

**Status:** done

Open questions, settled via `/grill-me`:

- [x] **Where does it live?** `docs/FAQ.md` — the direct structural sibling of the existing
  `docs/known-limitations.md` (same shape: flat, one H2 per topic, plain-text answer), linked from
  `README.md` at the same spot as "Known limitations".
- [x] **Format:** a flat list, one H2 per question — matches `known-limitations.md` exactly. With 37
  ADRs in the repo and zero FAQ entries before this ticket, grouping by theme would be premature
  structure with no content yet to justify it.
- [x] **Audience:** both — a single central doc serves newcomers deciding whether to adopt and
  people already running the suite who hit a specific "why does it do X" moment; no reader needs to
  know in advance which category their question falls into.
- [x] **Growth process:** manual/occasion-driven, not automatic. Both existing entries came from a
  question actually recurring in practice (a user question, a grilling session), not from a rule —
  and 37 ADRs have produced zero automatic FAQ entries so far, so there's no evidence a
  weight-triggered rule would add value rather than noise.

## Comments

> **2026-09-06:** Filed from a memory note (`qa-section-idea-for-skill-suite`) capturing two drafted
> entries — the first from 2026-09-04, the second from today's `continuous-housekeeping` work. Not
> designed yet; the memory note itself already flagged "where should this live" as an open question
> for the user.

> **2026-09-06 (grilled):** Grilled (`/grill-me`, German, two rounds). Settled: `docs/FAQ.md`, flat
> list matching `docs/known-limitations.md`'s own shape exactly, serves both audiences from one place,
> grows manually/occasion-driven rather than automatically off ADRs. Implemented same session: new
> `docs/FAQ.md` with both drafted entries, `README.md` linked next to "Known limitations".
