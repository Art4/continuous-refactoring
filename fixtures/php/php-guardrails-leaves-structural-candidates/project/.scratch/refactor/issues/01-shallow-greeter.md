# Greeter mixes formatting and delivery

**Status:** open
**Labels:** refactor:candidate
**Filed:** 2026-09-15

## Where

`src/Greeter.php` — builds the greeting text and decides how it is delivered.

## Problem

Formatting and delivery change for different reasons, but sit in one class, so a wording change needs the delivery path retested.

## Signal

Change frequency: the file changes with both concerns.

## Comments

(none)
