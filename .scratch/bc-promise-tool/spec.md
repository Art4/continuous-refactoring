# bc-promise-tool

The BC promise moves out of onboarding into a Tool on request, proposed through a new mechanism, the **Opener**.
Grilled on 2026-11-02 (`/grill-with-docs`); the decision is ADR-0093, which amends ADR-0088 and ADR-0086. The
research behind the Tool file's questions is `research.md` in this folder.

## Why

- **The question comes too early.** Onboarding asks for the BC promise before anything about the project is known;
  for a new project it is a surprise.
- **It comes back on every run.** An autonomous run that finds no single document asks again each time, and the
  Driver does not show the question as open.
- **It asks for a document without helping.** The options are a found document, another one, `none`, or ask again.
- **Nothing waits on it.** Until it is settled the suite is careful (Strangler Fig only, the BC-safe Rector path).
  The question starts to cost only when a plan takes the careful way because of it.

## Decided

| # | Decision |
|---|---|
| Q1 | Tool and Stage `bc-promise` in the generic Pack, new Role `compatibility-policy` without Signal, Safety Net, `requires: []`, `waits_for: []`; status on request (Q15) |
| Q2 | Fulfilled when the tracker file's **BC promise** bullet is there: a path that exists, a URL (Q8), `none`, or a list (Q16). A document without the bullet does not count |
| Q3 | A rejection is not `none`: the careful default stays for good, nothing asks again, Roave does not apply |
| Q4 | Superseded by Q17: no review that always asks the human |
| Q5 | The draft answers the Tool file's questions from evidence, each answer with its evidence; a question without evidence stays open (typically the window, exceptions, support); practice is described, the merge or answer makes it a promise; consumer part only; the Tool file lists the questions, no model text |
| Q6 | The question leaves the onboarding interview (step 2, the summary line, step 5) and *The BC promise alone* leaves the run's step 1 and its *Done when*; *Finding the BC promise* moves into the Tool file |
| Q7 | A single document found still goes through ticket and merge request; the merge request adds only the bullet and names the questions the document leaves open. The autonomous "exactly one document is taken" rule goes |
| Q8 | The bullet may name an `https://` URL; not fetched to judge the Stage; read where the promise is needed, and an unreadable URL makes that run careful, with a finding; a promise found on a website gets the bullet only; versioned docs: the link to the current line, kept current by a Housekeeping line |
| Q9 | A draft goes to `docs/bc-promise.md` where `docs/` exists, else `BC-PROMISE.md`; a recognisable docs convention of the project wins |
| Q10 | Evidence that nothing outside relies on the project (`type: project`, no published package, no plugin or hook API) → the merge request proposes the bullet `none`, evidence in its description, no document |
| Q11 | The ticket carries the scan's findings; an answer there is an ordinary answer at the design point; the merge request follows it with an ordinary review (Q17) |
| Q12 | Superseded by Q17 |
| Q13 | Superseded by Q18 |
| Q14 | A new ADR amending ADR-0088 → ADR-0093 |
| Q15 | On request, proposed through an Opener (Q19–Q23) at the point where the open promise costs |
| Q16 | The bullet may list parts, each with a scope (an area of code, or a surface: PHP API, HTTP API, CLI); the stricter promise wins on overlap; uncovered code keeps the careful default; a single `none` only for the whole repository; the default branch's release line only |
| Q17 | An autonomous run opens no merge request for `bc-promise`: the draft goes on the ticket as a proposal with the open question, the ticket waits, the run goes on careful. The human's answer leads to the merge request in a later run, reviewed like any other; `merge` mode may merge it. An interactive run asks directly |
| Q18 | Roave gets no `requires: bc-promise` (it would hold `rector-type-coverage` and the Safety Net through `waits_for`); it keeps `applies_when` with "an unsettled promise does not count", applied to the parts that follow SemVer |
| Q19 | The Opener is recorded as a line `Opener: <tool> — <why>` under the plan's `Decisions`, found through **Search**; the run does not file the ticket itself |
| Q20 | A Stage on request with an Opener found counts as not known: its Track's scan is due, the Stage in its scope. Used up by a ticket of the Tool in any state, or a recorded rejection of the Tool, Stage or Role; after a rejection no Opener proposes it again, a call naming it still can |
| Q21 | A ticket filed from an Opener waits for a human's yes, autonomous runs too: the question "Set up <Tool>?", the Opener with a link to its plan, for `bc-promise` the draft (Q17). Not workable before the answer |
| Q22 | The mechanism is built in general now, with `bc-promise`'s Opener only; Semgrep, Psalm Taint Analysis and Secret Detection get theirs in a follow-up ticket |
| Q23 | The term **Opener** in `CONTEXT.md`, with *Avoid*: trigger (Rector's "Re-triggering" is a Stage becoming unfulfilled again); on request becomes "proposed only when a human asks for it, or as a question once an Opener was seen" |
| Q24 | Spec and tickets here; terms ride into `CONTEXT.md` with each ticket's PR |
| Q25 | Two walk-through scenarios with a new prefix `r` (the run): `r1-opener-seen`, `r2-opener-after-rejection` |

## Facts

- `track-scan.md`: a Stage on request is in scope only when the call names it, a scan including on-request Tools is
  asked for, or a ticket of it exists; otherwise only its first Stage is judged, to say whether it fills a Role. Every
  scan report ends with "Available on request: …", which will list `bc-promise` without a new rule.
- `worklist.md`, *A Track's trace*: a Stage on request never counts as not known today, so it never makes a scan due.
- `packs/php/pack.json`: `rector-type-coverage` (Safety Net) has `waits_for: [..., "roave-bc-check"]`; `phpstan-level-5`
  waits for `rector-type-coverage`. Hence Q18.
- `rector.md`, `rector-type-coverage`: a promise not settled already takes the BC-safe path (`art4/rector-bc-library`).
- The suite keeps no state of its own: whatever the next run is to see must be findable through **Search**.

## Not in this plan

- Openers for Semgrep, Psalm Taint Analysis and Secret Detection (ticket 05).
- Promises of maintained branches other than the default branch.

## Tickets

1. `01-opener` — the mechanism
2. `02-bc-promise-tool` — the Tool, onboarding without the question (blocked by 01)
3. `03-bc-promise-bullet` — URL and several promises (blocked by 02)
4. `04-roave-and-rector` — Roave per part, the Opener on the Rector path (blocked by 02, 03)
5. `05-openers-for-tools-on-request` — design of the other Openers (blocked by 01)

Every ticket keeps the docs in sync in its own PR (`AGENTS.md`, *Docs stay in sync*), regenerates `docs/tooling/`
with `python3 scripts/tooling_docs.py` where the Packs change, adds a changelog fragment, and runs
`python3 -m unittest discover -s scripts -p 'test_*.py'` and `python3 scripts/validate_skills.py .` green before
pushing.
