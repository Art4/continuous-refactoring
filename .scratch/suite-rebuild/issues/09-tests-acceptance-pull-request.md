# 09: Decide the tests, accept, open the pull request

**What to build:** The rebuilt suite is accepted on a real target and goes to `main` as one pull request
with a pipeline that is green for stated reasons.

Spec: `../spec.md` (section *Testing Decisions*).

**Blocked by:** 08

**Status:** ready-for-human

- [ ] The human decides, with the list of red checks from ticket 08 in view, what happens to the
      validator's checks, the trigger-control tests and the fixture harness: deleted, adapted or rewritten
- [ ] That decision is carried out and the pipeline is green
- [ ] Acceptance from the `suite-rebuild` checkout in the target whose tracker and forge are different
      systems: onboarding again, one interactive run, one autonomous run, one Housekeeping run; what was
      observed is noted here
- [ ] The pull request from `suite-rebuild` to `main` is open
