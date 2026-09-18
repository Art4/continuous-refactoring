- Safety Net Track: `refactor-scan` now judges a Safety Net Track node's Fulfilment check against its
  own Purpose statement (an agent walking the tree), instead of trusting `tooling_tree.py`'s raw
  dependency-name match alone — a target already running Laravel Pint is recognized as fulfilling
  `php-cs-fixer`'s Purpose and is never proposed a redundant, possibly colliding second style tool.
  `bookkeeping.md` gains a `## Safety Net` section (`Cadence`, `Last scan`, `Open`, `Out-of-scope`),
  replacing the old `Fulfilled nodes`/global `Pending candidates` fields for this Track's own nodes;
  `refactor-learn` writes into it symmetrically — merge removes an entry from `Open`, rejection removes
  it and writes both `out-of-scope/<slug>.md` and an `Out-of-scope` pointer. A repo on the old
  `bookkeeping.md` shape runs a normal pass, unaffected.
