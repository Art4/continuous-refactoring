# Candidate: unused UnusedReportingService

**Status:** open
**Labels:** `refactor:candidate`

## Where
`src/UnusedReportingService.php`

## Problem
UnusedReportingService is never instantiated or referenced anywhere in the codebase. It is dead code that adds maintenance burden without value.

## Signal
Structural: dead code. The deletion test passes — removing this class has zero impact on behaviour.
