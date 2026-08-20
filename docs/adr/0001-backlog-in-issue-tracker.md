# Backlog lives in the issue tracker

The refactoring backlog is a set of candidate issues on the project's issue tracker, not a separate state file. Loop metadata (config, cadence, last-run marker) lives in `docs/agents/refactoring.md`; learned rejections live in `.out-of-scope/`.

Chosen so the loop's state travels with the repo and reuses the tracker every contributor already reads. A separate backlog file would duplicate the tracker and split attention between two sources of truth.