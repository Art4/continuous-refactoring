# Playbook: Continuous Housekeeping

The playbook for humans. `continuous-housekeeping`'s own `SKILL.md` covers the step-by-step; this document explains how you steer it as a person — opting in, reading a sweep, and what a housekeeping mention on an ordinary refactoring merge request means.

## What it is, and why it's separate

A periodic maintenance sweep — dependency currency, tooling-deprecation fixes, documentation sync — on its own cadence, deliberately **not** part of the continuous-refactoring loop's own scan → prioritise → design → implement → learn pass. That pipeline ranks and delivers one candidate at a time; housekeeping works through a standing checklist instead, and its own trigger is a calendar interval, not a proposal competing for priority. See ADR-0037 for the full reasoning.

## Opting in

Nothing runs until you run `/continuous-housekeeping` yourself, at least once. That first run asks one question — how often (default weekly) — and records the answer. Nobody is signed up for this without asking; the main loop's own regular passes never trigger that interview on their own.

Once opted in, you get it for free from the loop's own trigger too: any later `/continuous-refactoring` pass checks whether a sweep is due and runs it first, automatically, before its own ordinary work — one scheduler covers both. Running `/continuous-housekeeping` directly, on its own, still works any time — useful if you want a sweep without a full refactoring pass alongside it.

## If you haven't opted in yet

Some tooling-tree nodes register a recurring check the moment they're adopted (`composer` → run `composer update`; `composer-audit` → review the audit report between CI runs; and others — see a node's own `Housekeeping` field, `CONTEXT.md`'s **Tooling tree** entry). If any of those were already adopted before you ever ran `/continuous-housekeeping`, a regular `/continuous-refactoring` pass's closing report names it — "N adopted tool(s) have registered housekeeping checks nobody's using yet" — until you either opt in or the pass stops finding anything to mention.

## Reading a sweep

Each due cycle is one issue, titled `Housekeeping — <date>`, its checklist assembled from whatever's accumulated in the Refactoring Notes' `housekeeping-template.md` plus one standing item (an AGENTS.md/skills/rules sync check, every cycle, tied to no single tool). Review it like any other merge request: CI green, the reported findings actually addressed or explicitly escalated back to you — not silently decided — for anything without a clean fix.

## Housekeeping mentions on ordinary merge requests

An unrelated tooling-adoption merge request (say, adopting `composer-audit` for the first time) may also mention that it registered a housekeeping check — that's the node's own `Housekeeping` field reaching `housekeeping-template.md`, described in the merge request's own plain-facts section. Nothing to review differently there; it's a factual note about what else that merge request touched, not a second decision to make.

## Common mistakes

- **Expecting a stored "last run" date somewhere.** There isn't one — due-ness comes from the tracker's own history (the most recent `Housekeeping — <date>` issue), the same way in-flight suite merge requests are already tracked without a duplicate ledger field.
- **Treating a housekeeping finding with no clean fix as something to force through.** Document it on the issue and let the human decide — same bar the rest of this suite already holds itself to.
