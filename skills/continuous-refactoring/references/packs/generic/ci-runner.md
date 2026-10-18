# CI Runner

The Tool for the Role Continuous Integration in the generic Pack: GitHub Actions or GitLab CI. A pipeline is useful whatever languages the target has, so it is in the generic Pack and nothing waits for a language first.

**Why this order.** Quality jobs need somewhere to run. Tools whose job belongs in the pipeline (Composer Audit, Semgrep) wait until this Stage is decided. PHPUnit and PHPStan Level 0 do not get a ticket for their job: once this Stage is fulfilled, each wires its own CI gate as part of its own Fulfilment check.

### `ci-runner`

- **Purpose:** an existing pipeline that later hosts quality jobs.
- **Fulfilment check:** a CI config file is present; the forge is determined from `git remote`. An unknown CI is a question to the human, never a recorded rejection.
- **MR scope:** the pipeline file only.
