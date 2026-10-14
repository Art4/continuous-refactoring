# `## Investigation`'s `Open` supports more than one in-flight candidate

> Superseded by [ADR-0074](0074-state-lives-in-the-tracker-found-by-search.md): there is no `Open` list;
> the open tickets are the worklist.

> Amends [ADR-0065](0065-investigation-gets-its-own-open.md): `Open` is no longer single-entry. Every
> other decision in that ADR — a candidate's own entry set by `refactor-design`, cleared by
> `refactor-learn`, read only when Investigation is the Track selected — is unchanged; only the
> assumption that exactly one entry can ever exist at once is dropped.

Observed live in `Art4/legacy-todo`: a structural candidate (#290) was in flight with an open,
unmerged pull request (#291) — its `## Investigation` `Open` entry correctly named it. Separately, a
human directly invoked `/refactor-design` on a second, independently-filed externally-labeled
candidate (#293) while #290's own entry was still current. `refactor-design`'s own rule
(ADR-0065: *"adds an entry to `## Investigation`'s own `Open`"*) fired as documented — except the field
it was writing to was defined as holding *at most one entry* (ADR-0065's own **Decision**), so the
write landed as a second bullet line, silently violating that shape. The `Open` entry for #268 (a
separate candidate delivered and merged in between) was, by the same underlying gap, left stale in the
field rather than cleared, since nothing had re-checked it before the new entry was appended.

The single-entry assumption was reasonable when ADR-0065 was written — Investigation had only ever been
observed to have one candidate move through design → implement → merge at a time. It was never actually
guaranteed, though: `refactor-loop`'s own suite-wide two-merge-request cap
(`docs/playbooks/tracks.md`'s *"Two merge requests at most"*) has always permitted **two** candidates
in flight simultaneously, suite-wide, and nothing about that cap restricts both slots to different
Tracks. The moment two Investigation candidates land in that state together — as they did here — a
single-entry `Open` has exactly two ways to respond, both wrong: silently drop whichever candidate it
doesn't name (losing track of it entirely, until the tracker's own PR-linkage happens to be checked by
some other step), or grow a second line despite being documented as holding only one, which is what
was actually observed.

## Decision

**`## Investigation`'s `Open` becomes a list, one line per in-flight candidate** —
`- <issue title> (#<issue>)` per entry, `- none` when empty — matching `## Safety Net`'s/`## Guardrails`'
own shape (though not their semantics: it's still never a backlog of un-filed work the way a tree node's
list is, only ever candidates already past design).

- **`refactor-design` appends an entry** the moment it writes a structural, baseline-shrink, or
  externally-labeled candidate's plan — never overwriting whatever is already there.
- **`refactor-learn` removes exactly one entry** — the one naming the candidate that just merged, was
  rejected, or was found to need a breaking change — leaving every other entry untouched.
- **A resuming pass reads every entry**, applying the existing per-entry status logic
  (`refactor-scan/SKILL.md` step 2: plan + `ready-for-agent` → implement; plan + `needs-info` → flagged,
  checked for a newer human comment) to whichever entry still has design/implement work outstanding, and
  advances **at most one entry per pass** — the same "one candidate per pass" discipline already implied
  by the two-merge-request cap. An entry already past design and implement, sitting on an open, unmerged
  PR with no reviewer activity, has nothing to advance; step 3's own merge/close reconciliation is what
  watches it, unchanged.
- **Still gated the same way**: `Open` non-empty → no fresh scan (step 4/3b) this pass, regardless of how
  many entries it holds — resuming existing work still comes before proposing new work.

No new cap is introduced here — `Open` can in principle hold more entries than two if, say, a candidate
sits designed-but-not-yet-implemented behind the cap; the two-merge-request limit
(`refactor-loop/SKILL.md` step 5) already governs how many can actually be *implementing* at once, and
this ADR doesn't duplicate that check into `Open`'s own shape.

## Considered Options

- **Keep `Open` single-entry; make the suite-wide two-merge-request cap Track-aware** (never let two
  Investigation candidates be in flight at once, even though two suite-wide is fine). Rejected — it
  would special-case one Track inside a limit that's deliberately suite-wide and Track-agnostic
  (`refactor-loop`'s own stated design, never branching on a Track's name), just to preserve a bookkeeping
  field's shape; the cap exists to bound total review load, not to enforce one-candidate-per-Track.
- **Keep `Open` single-entry; refuse to add a second entry, forcing the second candidate to wait.**
  Rejected — that candidate already has a plan and `ready-for-agent` by the time `Open` would be written;
  refusing to record it doesn't stop `refactor-implement` from working it (the cap gate, not `Open`, is
  what actually blocks a new MR), it just makes the record wrong the moment that happens anyway.
- **A dedicated second field for "the second candidate," rather than a real list.** Rejected — it just
  moves the same shape problem one field over and stops working the moment three-in-flight ever occurs for
  any reason (even a manual override, as happened here); a list has no such ceiling to rediscover later.

## Consequences

- `skills/refactor-scan/references/investigation-track.md`'s resume section, `skills/refactor-scan/SKILL.md`
  step 2's Investigation-`Open` paragraph, `skills/refactor-design/SKILL.md`'s two "set `Open`" bullets, and
  `skills/refactor-learn/references/investigation-write.md`'s merge/rejection/set sections are all rewritten
  around a list rather than a single value.
- `skills/continuous-refactoring/references/refactoring-bookkeeping.md`'s `Open` field description and its
  *Why single-entry* rationale are replaced with *Why more than one entry*.
- `docs/playbooks/tracks.md` and `CONTEXT.md`'s **Self-tracking** entry drop their "at most one"/"single-entry"
  wording.
- No migration needed: an existing single-line `Open` is already valid as a one-entry list; nothing about
  the on-disk format changes for the common case.
