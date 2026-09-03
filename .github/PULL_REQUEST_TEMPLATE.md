## What this changes

<!-- Short description of the change and why. -->

## Checklist

- [ ] Branched off `main`, no direct commits to it
- [ ] Ran the relevant tests locally before pushing (see [CONTRIBUTING.md](../CONTRIBUTING.md)):
      `python3 -m unittest discover -s scripts -p 'test_*.py'` and
      `python3 scripts/validate_skills.py .` for any `skills/**`/`docs/**` change, plus the
      relevant `fixtures/harness/run.sh` tier for tooling-tree/fixture changes
- [ ] CI is green
