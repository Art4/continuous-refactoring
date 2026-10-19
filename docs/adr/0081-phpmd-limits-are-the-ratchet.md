# PHPMD's limits are the ratchet, not a baseline

> Applies the Ratchet of [ADR-0079](0079-tooling-model-roles-tools-stages-in-packs.md) to a Tool that has no level chain.

PHPMD was adopted once, with "fix what the first run reports or baseline it", and nothing afterwards made the debt
shrink. The PHPStan baseline is a Ratchet because a level waits for it to be empty. A PHPMD baseline cannot be one:
it stores the rule, the file and the method, no value and no reason, so a baselined method can get worse unseen,
and `--update-baseline` rewrites the file without any comment.

## Decision

- **The limits of the metric rules are the Ratchet.** At adoption each metric rule the code breaks gets its limit
  set to today's worst value, with a comment (`recommended`, `Current peak` and where). Limits only fall.
- **No baseline.** A deliberate exception is a suppression at the code, with a reason beside it; a metric rule is
  never suppressed. A project that has a baseline gets one merge request that moves its entries into limits and
  suppressions and deletes the file.
- **Lowering travels with structural work (way C).** A ticket whose plan touches a file named in a `Current peak`
  comment carries a Ratchet slice, a step of the Tool's details file: measure again, lower the limits the change
  made possible. The Housekeeping ticket lowers what the code reached without it. The success is that PHPMD is
  green with every other limit unchanged and the target rule's peak has fallen.
- **Rules wait, they are not given up.** A rule with more findings than one reviewable merge request can take
  is excluded with a `Not yet:` comment; the Stage stays unfulfilled and its ticket takes the rules in one at a
  time, in the shape of the PHPStan baseline ticket. Without this, a first run could only ask the human to drop
  rules (found in the first trial run on a real project).
- **A CI job** runs PHPMD once `ci-runner` is fulfilled, or the limits hold only for the suite's own runs.
- **The search for candidates** runs PHPMD at the rules' default limits, since under the ratcheted ones it reports
  nothing.
- **Rule sets:** `cleancode`, `codesize`, `design`, `naming`, `unusedcode`; a target may leave any out, with a
  comment. The Tool is installed in its newest major version, and a target on an older one stays there.

## Considered Options

- **A series of Stages or a standing ticket that lowers the limits** (the shape of the PHPStan levels). The limits
  are continuous and per rule, a chain would be arbitrary, and the work is structural refactoring the run does
  anyway. Revisit if the peaks are never picked as candidates.
- **A baseline for what is not a metric.** Keeps the file and loses the reason. Rejected for the suppression.
- **Lowering to the previous second place.** The same only if the rewritten method falls below it; measuring again
  stays right otherwise. Rejected.

## Consequences

`phpmd.md` carries the policy; the Slice *Ratchet* in the implement point is general and may serve other Tools. A
target that adopted PHPMD with a baseline is not fulfilled until it is replaced.
