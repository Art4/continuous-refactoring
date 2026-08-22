# Candidate: SQL injection in UserRepository::searchByName

**Status:** open
**Labels:** `refactor:candidate`

## Where
`src/UserRepository.php` — `searchByName()` method

## Problem
User input is interpolated directly into a SQL string via string concatenation (`"SELECT * FROM users WHERE name LIKE '%" . $search . "%'"`). This is an OWASP A03 injection vulnerability.

## Signal
Security: raw SQL with unparameterised user input. The fix is to use a prepared statement with bound parameters.
