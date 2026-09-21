# A Track's `Cadence` carries a unit, and may be a monthly calendar day

> Amends [ADR-0055](0055-purpose-based-fulfilment-and-scheduled-tracks.md): the per-Track `Cadence` there
> was a bare number of days. The staleness ratio, the fixed tie-break order and the one-time bootstrap
> exception are unchanged.

## Context

`Cadence` in `bookkeeping.md` was a bare number read as days (`90`, `60`, `7`). A person who wants a
Track to run every 12 hours, every 2 weeks or every quarter had to convert by hand, and nothing could say
"always on the 1st of the month". The bare number also gave a hand-editor no hint what it meant.

## Considered Options

- **Short form** (`90d`, `2w`, `1mo`): compact, but cryptic for someone editing the file by hand.
- **Timestamp in `Last scan`** (to make hours exact): a schema change for every writer of that field, for
  a loop that rarely runs more than daily.
- **A cron-like expression** for calendar days: expressive, but far more than "the 1st of the month" needs,
  and unfriendly to read in a bookkeeping file.

## Decision

`Cadence` is a number with a written-out unit (`hours`, `days`, `weeks`, `months`; singular or plural), or
`monthly on the <N>th` for N from 1 to 28. `continuous` (Investigation) stays as it is.

- Interval forms feed the existing `overdue_ratio` (`elapsed / interval`); a month counts as 30 days.
- The calendar form is due once such a day has passed since `Last scan`; its ratio is
  `max(1, elapsed / 30)`, so "due ⇔ ratio >= 1" and the Housekeeping preemption rule hold unchanged.
- `Last scan` stays a date. Hours are therefore only day-accurate; this is documented, not fixed.
- A bare number keeps reading as days, so existing files and fixtures need no migration. The loop writes
  its defaults with the unit (`90 days`, `60 days`, `7 days`).
- An unreadable value is never guessed at: the Track's default is used for that pass and the report names it.

## Consequences

Anyone can state a cadence the way they think of it, in the unit they mean, and the file explains
itself. The forms are defined once (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`,
*Cadence values*); the scheduler, the write steps and the docs point there. Weekday anchors and
sub-day precision are out of reach until `Last scan` carries a time.
