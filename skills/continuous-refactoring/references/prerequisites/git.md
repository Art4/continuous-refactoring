# Git

A prerequisite of the suite, in no Pack (`../tooling-model.md`): version control. The suite reads history from it and delivers through it.

- **Fulfilment check:** the target is a git repository.
- **MR scope:** never a merge request. It is the only hard requirement; without it the suite does not run. If it is missing, a run ends at its first step with that message, and nothing is filed.
