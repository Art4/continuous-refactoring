# 01: Worklist and reconcile scope when the call names a ticket

**Status:** done — option 1, ADR-0085

## Observation

A run called with "diy zu #68" (autonomous, ticket #68 — Rector Code Quality Set) answered:
"Worklist, Reconcile und Pick-up-Check zuerst, nur lesend." That follows the skill text exactly:

- `SKILL.md`, *The call*: a named ticket answers Track choice and selection — nothing more. Steps 1–3
  of *The run* have no shortcut for it.
- `references/worklist.md` §1 takes "the ticket the call names, whatever it carries" **in addition to**
  every Stage's open tickets: the full worklist is built.
- `references/reconcile.md` collects findings for **every** open ticket's merge request and every
  recorded rejection.
- `references/track-choice.md` lays out nothing for a named ticket; `references/selection.md` puts only
  the named ticket in the list but still runs its pick-up check.

A named ticket is not a **restriction** (its own row in *The call*), so nothing narrows steps 2–3.

## The question

Should a named ticket narrow the worklist and reconcile to that ticket?

What the run needs for the named ticket alone: its Track, its state, its merge request (worklist §2–3,
*A ticket's merge request*), reconcile of that ticket's merge request, and the pick-up check.

Today's cost of not narrowing:

- One **Search** per Stage (or a full listing) and a merge-request lookup per open ticket, for a run
  that will work one ticket.
- In an autonomous run, reconcile may close or reject **other** tickets the human did not mention —
  writes the call did not ask for.

Arguments for keeping it as is:

- The suite keeps no state; every run is the chance to bring tracker and forge into agreement.
- The blocked state of the named ticket can depend on another ticket (`Blocked by`), which is read
  either way.

## Options

1. **Narrow both** — a named ticket acts as a restriction to itself (plus what its `Blocked by` names)
   for worklist and reconcile.
2. **Narrow the worklist, keep reconcile whole** — cheaper lookup, tracker still reconciled.
3. **Keep as is, state it** — say in *The call* that a named ticket does not narrow worklist and
   reconcile, so the behaviour is intended rather than incidental.

## Done when

- The chosen option is in `SKILL.md` (*The call*) and the affected references.
- `docs/playbooks/run.md` and `CONTEXT.md` read true against it; a changelog fragment exists.

## Comments

- 2026-10-23: Option 2 dropped while implementing — reconcile reads the worklist, so keeping reconcile
  whole needs the full worklist and saves almost nothing. Option 1 chosen instead.
