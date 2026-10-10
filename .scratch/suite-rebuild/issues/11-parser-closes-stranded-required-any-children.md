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

**Status:** done

- [x] A node whose `required-any` group has no member left that could be fulfilled — each one rejected,
      closed by a rejection, or an unfulfilled recognition-only node — is in `closed_by_rejection`, out of
      the backlog, and counts as decided for its aggregation node
- [x] A group with one member still open, or with a recognition-only member handed in as fulfilled,
      closes nothing
- [x] The closure follows the rejection: with the rejection gone from the handed-in state, the node is
      back in the backlog; with a `php` blocker the target now meets, the rejected node is in `reversals`
      as before
- [x] On the case from ticket 04 (PHP 5.6 target, `phpstan-level-0` rejected with its PHP blocker, `psalm`
      not fulfilled) `detected["structural-scan"]["fulfilled"]` no longer waits for `rector-php-set` and
      `psalm-taint-analysis`
- [x] Parser tests cover these cases at the parser's existing interface; the parser's own test file is
      green
- [x] The rule the run's rejection reference carries for stranded nodes (recording them as rejected with
      the same blocker) is removed there, and the parser reference's description of `closed_by_rejection`
      and of the `required-any` rule for working without `python3` reads true; no other skill text is
      touched
- [x] What goes red outside the parser's tests is listed in a comment on ticket 09

## Comments

### Done — what changed at the parser's interface

- **The rule.** A node is closed by rejection when its `required-any` group has no member left that could
  be fulfilled: each one rejected, closed by a rejection, or a recognition-only node not handed in as
  fulfilled. What requires a node closed this way is closed with it, and a `recommended` child is released
  (`rector-type-coverage` no longer waits for `rector-dead-code`).
- **Output:** unchanged in shape. `closed_by_rejection`, both backlogs, `tracks[...]["fulfilled"]` and the
  aggregation nodes in `detected` follow the rule. With `phpstan-level-0` rejected and `psalm` not
  fulfilled, `closed_by_rejection` also holds `rector-php-set`, `rector-dead-code`, `rector-code-quality`,
  `php-minimal-version` and `psalm-taint-analysis`.
- **Functions:** `closed_by_rejection(tree, rejected, fulfilled=None)` takes the handed-in `{slug: bool}`
  state as a third, optional argument; without it no recognition-only node counts as fulfilled.
- **References:** `rejection.md` lost the paragraph about recording stranded nodes as rejected, and its
  table now says "no member left that could be fulfilled"; `tooling-tree-parser.md` describes
  `closed_by_rejection` and the `required-any` rule for working without `python3`.

### Decided here, not stated by the ticket

- **At least one member of the group must be rejected or closed by a rejection.** A group made only of
  unfulfilled recognition-only nodes closes nothing: nothing was rejected, so there is no rejection the
  closure could follow or come back with. No group of the current tree is built that way (both pair one
  node that gets a ticket with `psalm`); a test on a small tree of its own holds the rule.

### Left as it was

- **A closed node is still listed in `withheld`**, with "blocked — none of required-any parents
  fulfilled: …", as the child of a rejected required parent already is.
- **A node handed in as fulfilled is still listed in `closed_by_rejection`** when its group is out of
  reach, again like the child of a rejected required parent.
- **The seed read from a Track's trace does not reach this rule.** `tooling-tree-parser.md`, *Is Safety
  Net fulfilled?*, hands in every recognition-only node without an open ticket as fulfilled — `psalm`
  always, since no ticket is filed for it. On that path the group still has a fulfilled member, so the
  stranded nodes count only by their own tickets: without an open ticket they are handed in as fulfilled
  and the gate opens; with a ticket the human chose to leave open, the gate waits for it. The rule works
  where the nodes are judged (the scan). Whether the trace seed should judge the recognition-only nodes
  instead of assuming them is the run's to decide, not the parser's.

### Red afterwards

Nothing newly red; the list of texts that are now untrue is in a comment on ticket 09.
