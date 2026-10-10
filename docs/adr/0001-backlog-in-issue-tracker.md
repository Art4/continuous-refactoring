# Backlog lives in the issue tracker

> Extended by [ADR-0074](0074-state-lives-in-the-tracker-found-by-search.md): not only the backlog but
> all of the suite's state lives on the tracker and the forge; nothing is kept under `docs/refactoring/`
> or anywhere else.

The refactoring backlog is a set of candidate issues on the project's issue tracker, not a separate state file. Loop metadata and learned rejections live under `docs/refactoring/` in the target repo (ADR-0005); the backlog itself stays on the tracker.

Chosen so the loop's state travels with the repo and reuses the tracker every contributor already reads. A separate backlog file would duplicate the tracker and split attention between two sources of truth.