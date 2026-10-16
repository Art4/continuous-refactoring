# 04 — Triage findings into four buckets with reasons

Type: task
Status: open

Findings and signals sorted into act on / consider / noted / dismissed, each with the source and a one-line reason; a dismissal always carries its reason; independent agreement of two reviewers counts as the strongest signal.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments

### 2026-10-16 — gap check against `skills/`: partial

`reviewing-a-change.md`: every finding is one line and sends the work back; only a smell whose way out exceeds the plan is "named in the MR description and left" (an informal *noted*). No dismissed-with-reason, no agreement signal. Caution: **Finding** in `CONTEXT.md` already means the breaking-change case, so the new buckets need a different word.
