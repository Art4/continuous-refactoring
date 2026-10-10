# 11: Parser closes a node whose whole required-any group is out of reach

**What to build:** When every member of a node's `required-any` group is rejected, closed by a rejection,
or a recognition-only node that is not fulfilled, the parser reports the node as closed by rejection, the
same way it already closes the child of a rejected required parent. A caller who rejects one node below
the PHP floor gets an open gate without having to find and reject the nodes stranded behind it, and those
nodes come back by themselves when the rejection is reversed.

Spec: `../spec.md` (sections *The parser*, *Rejections*, *Testing Decisions*). Follow-up to ticket 04,
whose comment "Rejecting the floor-blocked node alone does not open the gate" describes the case: a
PHP 5.6 target with `phpstan-level-0` rejected leaves `rector-php-set` and `psalm-taint-analysis`
neither fulfillable nor closed, and `structural-scan` unfulfilled. Built test-first, like tickets 03
and 10.

**Blocked by:** 10

**Status:** ready-for-agent

- [ ] A node whose `required-any` group has no member left that could be fulfilled — each one rejected,
      closed by a rejection, or an unfulfilled recognition-only node — is in `closed_by_rejection`, out of
      the backlog, and counts as decided for its aggregation node
- [ ] A group with one member still open, or with a recognition-only member handed in as fulfilled,
      closes nothing
- [ ] The closure follows the rejection: with the rejection gone from the handed-in state, the node is
      back in the backlog; with a `php` blocker the target now meets, the rejected node is in `reversals`
      as before
- [ ] On the case from ticket 04 (PHP 5.6 target, `phpstan-level-0` rejected with its PHP blocker, `psalm`
      not fulfilled) `detected["structural-scan"]["fulfilled"]` no longer waits for `rector-php-set` and
      `psalm-taint-analysis`
- [ ] Parser tests cover these cases at the parser's existing interface; the parser's own test file is
      green
- [ ] The rule the run's rejection reference carries for stranded nodes (recording them as rejected with
      the same blocker) is removed there, and the parser reference's description of `closed_by_rejection`
      and of the `required-any` rule for working without `python3` reads true; no other skill text is
      touched
- [ ] What goes red outside the parser's tests is listed in a comment on ticket 09
