# 02 — The Tool `bc-promise`

Type: task
Status: open
Blocked by: 01

**What to build** (ADR-0093, spec Q1–Q3, Q5–Q7, Q9–Q11, Q17)

- **Pack.** `packs/generic/pack.json`: Tool `bc-promise`, name "BC promise", status `on-request`, Role
  `compatibility-policy`, one Stage `bc-promise`, Safety Net, `requires: []`, `waits_for: []`. `roles.json`: the Role's
  Purpose ("the project's promise to code outside it is written down and recorded, so a run knows what it may
  change"), no Signal.
- **Tool file** `packs/generic/bc-promise.md`:
  - **Fulfilment check:** the tracker file's **BC promise** bullet is there — a path that exists, or `none` (URL and
    lists come with ticket 03). A document without the bullet does not count.
  - **Finding the BC promise**, moved here from `onboarding-setup-interview.md`.
  - **The questions** a draft answers, from `research.md` section 7: who relies on the project; versioning; what is
    covered; what is excluded; what use, extend and implement may rely on; changes per release type; how a
    deprecation is marked; its minimum window; experimental parts; exceptions; support; where changes are announced;
    surfaces beyond code; how the promise is checked. Each with the evidence to read. No model text.
  - **MR scope:** no document → a draft at `docs/bc-promise.md` (where `docs/` exists, else `BC-PROMISE.md`; a docs
    convention of the project wins), consumer part only, each answer with its evidence, each question without
    evidence left open, practice described as practice; plus the bullet. One document found → the bullet only, the
    questions it leaves open named in the description. Evidence that nothing outside relies on the project → the
    bullet `none`, evidence in the description.
  - **Autonomous:** no merge request; the draft goes on the ticket as a proposal with the open question, the ticket
    waits (ticket 01's waiting ticket). The answer leads to the merge request in a later run; its review is ordinary.
  - **Opener:** a plan that takes the careful way only because the promise is not settled — Strangler Fig where
    *Migrate callers, then delete* would apply to code with no caller outside the repository.
  - **Rejection:** the careful default stays for good.
- **Onboarding without the question.** `onboarding-setup-interview.md`: drop the question in step 2, the "BC promise:"
  summary line, the step 5 clause, *Finding the BC promise* (moved) and *The BC promise alone*. `SKILL.md` step 1: drop
  the sentence that calls it and the BC promise from *Done when*.
- `refactoring-operations.md`: the **BC promise** row's fallback — not settled: code outside the repository could reach
  counts as covered, and the Tool `bc-promise`, on request, settles it.
- `principles.md`, *Strangler Fig*: the unsettled case names the Opener.
- `CONTEXT.md`: **BC promise** — settled by the Tool on request, not asked in onboarding; **Refactoring operations** —
  the absence of the bullet still means not settled.
- Docs: `docs/playbooks/run.md` (onboarding no longer asks), `docs/playbooks/tracks.md` (Safety Net row: the BC
  promise on request), `docs/FAQ.md` (what the suite does with a BC promise, and when it asks), `docs/known-limitations.md`
  (a target with an open promise stays careful), `docs/tooling/` regenerated, `README.md` where it names the onboarding
  question.
- Changelog fragment: onboarding no longer asks for the BC promise; a Tool on request drafts it from the project's
  evidence, proposed when a plan takes the careful way because of it.

**Done when** a walk-through of r1 with `bc-promise` passes (a plan on an unsettled target writes the Opener; the
next scan files a waiting ticket with a draft; an answer `none` leads to a merge request with the bullet only), an
onboarding on a fixture asks nothing about a promise, and tests and validator are green.
