# 04 — Triage findings into four buckets with reasons

Type: task
Status: done

Findings and signals sorted into act on / consider / noted / dismissed, each with the source and a one-line reason; a dismissal always carries its reason; independent agreement of two reviewers counts as the strongest signal.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments

### 2026-10-16 — gap check against `skills/`: partial

`reviewing-a-change.md`: every finding is one line and sends the work back; only a smell whose way out exceeds the plan is "named in the MR description and left" (an informal *noted*). No dismissed-with-reason, no agreement signal. Caution: **Finding** in `CONTEXT.md` already means the breaking-change case, so the new buckets need a different word.

### 2026-10-17 — grilled; decisions

- Applies to the suite's own review (`reviewing-a-change.md`) only; decision-point findings, scans and bot comments (ticket 10) unchanged.
- Three buckets, not four: fix / note / dismiss. No *consider*: autonomy is said in the call and never observable, and in an autonomous run it would equal the recommendation.
- Spec findings are never noted or dismissed; Standards findings can be, with a concrete reason.
- Notes go into the merge request description; dismissals with reasons go to the closing report only, so the caller can overrule.
- No "two reviewers agree" signal (one reviewer). No new glossary word, no ADR; **Finding** stays the breaking-change case.
- Built: `reviewing-a-change.md` (*Sorting the findings*), `implement-point.md` step 5, `opening-a-merge-request.md`, `SKILL.md` closing report, FAQ, changelog fragment.
