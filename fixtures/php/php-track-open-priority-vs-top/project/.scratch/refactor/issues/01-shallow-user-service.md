# Shallow UserService

**Status:** open
**Labels:** refactor:candidate, refactor:priority, ready-for-agent
**Filed:** 2026-09-15

## Where

`src/UserService.php` — a god service mixing authentication, profile management, notifications, and reporting.

## Problem

The service has grown to handle four unrelated concerns. Every change to one concern risks breaking the others. Tests can't target one behaviour without loading the whole service.

## Plan

Extract three focused services (AuthService, ProfileService, NotificationService) behind a thin facade. Each new service owns its own seam and can be tested independently.

## Comments

(none)
