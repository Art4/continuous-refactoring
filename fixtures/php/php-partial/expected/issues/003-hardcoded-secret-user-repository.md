# Candidate: hardcoded secret in UserRepository

**Status:** open
**Labels:** `refactor:candidate`

## Where
`src/UserRepository.php` — comment in `findActive()` method

## Problem
A live API key (`sk-live-abc123def456ghi789jkl012mno345`) is hardcoded in a doc comment. Secrets in source code are a security risk — they leak into version control and are accessible to anyone with read access.

## Signal
Security: hardcoded secret detected in source code. Must be moved to environment variables or a secrets manager.
