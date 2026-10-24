# 01 — Secret Detection on request, the history scan on its own

Type: task
Status: done

Follows up the point `.scratch/on-request-tools-and-bc-promise/spec.md` left open ("Not in this plan").
Grilled 2026-10-24; decided in ADR-0089 (option D).

**What to build**

- Tool `secret-detection` **on request**; its Stage stays Guardrails and gains `waits_for: ci-runner`.
- Role `secret-scanning` loses the Signal Security; `signals.md` drops the scanner from the Security signal.
- Fulfilment check: a CI job running a scanner, or the forge's push protection read through its API (unreadable counts
  as off and is said); a pre-commit hook alone does not fulfil it.
- Housekeeping's history scan: the target's scanner, else one the run executes without adding it (binary or Docker
  image); no baseline written; none can run → `not run: no secret scanner available`, tried again next cycle.
- Docs: ADR-0089 with banners on 0086/0043/0040, `CONTEXT.md`, `docs/tooling/` regenerated, `docs/FAQ.md`,
  `docs/playbooks/housekeeping.md`, `track-scan.md`'s on-request line, changelog fragment.

**Done when** the generic Pack proposes nothing in Guardrails unasked, a target asking for Secret Detection gets its
Stage after `ci-runner` is decided, and tests and validator are green.
