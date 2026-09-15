# 1 — Unify the duplicated retry-with-backoff logic

**Filed:** 2026-09-15
**Status:** needs-triage
**Labels:** refactor:candidate, ready-for-agent

`OrderRetrySender::send()` (src/OrderRetrySender.php) and
`PaymentRetryDispatcher::dispatch()` (src/PaymentRetryDispatcher.php) both
implement retry-with-backoff, independently, with different backoff shapes
(exponential doubling starting at 1s / 5 attempts vs. linear +2s starting at
2s / 4 attempts) and different sleep mechanisms (`usleep` vs `sleep`).
Please deduplicate this into one shared retry helper — this is fully
specified, go ahead.

## Comments
