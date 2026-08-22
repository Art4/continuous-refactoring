# Candidate: shallow UserService god service

**Status:** open
**Labels:** `refactor:candidate`

## Where
`src/UserService.php`

## Problem
UserService mixes authentication, profile management, email notification, reporting, and lifecycle management in a single class. High fan-in, low cohesion — a classic shallow module.

## Signal
Structural: god service pattern, 10+ public methods, multiple distinct responsibilities in one class. The deletion test would concentrate complexity rather than remove it.
