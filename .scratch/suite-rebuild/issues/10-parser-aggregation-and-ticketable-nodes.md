# 10: Parser computes the gates and lists only nodes that get a ticket

**What to build:** Whoever calls the tooling-tree parser hands in the state of the nodes an agent can
judge, and nothing about the aggregation nodes. The parser works out from their leaves whether
`structural-scan` and a language's safety-net node are fulfilled, says per Track whether the Track is
fulfilled, and returns backlog and node lists that hold only nodes a ticket can be filed for. The Track
choice of a run reads "is Safety Net fulfilled?" from this output instead of judging it.

Spec: `../spec.md` (sections *The parser*, *Track choice*, *Testing Decisions*). Follow-up to ticket 03,
whose comments name the two behaviours this ticket changes. Built test-first, like ticket 03.

**Blocked by:** 03

**Status:** done

- [x] The state of an aggregation node (a node others reach through `resolved` edges) is computed from
      its leaves; whatever is handed in for such a node is ignored, as for `git` and `onboarding-setup`
- [x] A rejected leaf counts as decided for its aggregation node, the way a rejected recommended parent
      already releases its child
- [x] The output states, per Track, whether the Track is fulfilled: every node of it that can get a
      ticket is fulfilled or rejected
- [x] Each Track's backlog and node list hold only nodes a ticket can be filed for; recognition-only and
      aggregation nodes (`git`, `onboarding-setup`, the recognition gate, `structural-scan`, the
      safety-net node) are left out of both, and out of the flat `backlog` and `next`
- [x] Each listed node carries search words fit for a tracker search: the node's name and its tool as
      short plain strings, without Markdown backticks and without explanatory prose; where a node's tool
      field is a sentence, the node's tree-doc entry is given a short tool name and the sentence moves to
      its Purpose
- [x] Parser tests cover the computed aggregation state, the per-Track fulfilled flag and the filtered
      lists at the parser's existing interface; the parser's own test file is green
- [x] No skill text other than the tree-doc entries named above is touched; what goes red outside the
      parser's tests is listed in a comment on ticket 09

## Comments

### Done — what changed at the parser's interface

- **Aggregation nodes are computed.** `structural-scan` and `php-safety-net` (every node others reach
  through `resolved` edges) are fulfilled once each leaf is fulfilled, rejected, or closed by a rejected
  required parent. Whatever a caller hands in for them — fulfilled or rejected, in the functions or in a
  `--seed` file — is ignored, as for `git` and `onboarding-setup`. `detected` in the output shows the
  computed state.
- **`tracks[<Track>]["fulfilled"]`** (new, boolean): every node of the Track a ticket can be filed for is
  fulfilled, rejected, or closed by a rejected required parent — the same thing as the Track's backlog
  being empty. "Is Safety Net fulfilled?" is `tracks["Safety Net"]["fulfilled"]`.
- **Only nodes a ticket can be filed for are listed** — in `tracks[...]["nodes"]`, both backlogs, the
  flat `backlog`, `next`, and `unblocked_by`. Left out: `git`, `onboarding-setup`, the aggregation nodes,
  and the recognition-only nodes (`is-php-project`, `static-code-analyzer`, `psalm`,
  `has-real-dependency`, `phpstan-baseline-empty`, `phpstan-not-psalm`). They still appear as the reason
  in `withheld` ("blocked by required parent php-safety-net") and in `detected`.
- **Consequences a caller sees:** a target that is not onboarded has an empty `next`
  (`detected["onboarding-setup"]["fulfilled"]` is false and every node is withheld behind it);
  `structural-scan` is never a candidate, whether or not its gate is open; `--unblocked-by` walks through
  the aggregation nodes to what they open (the last leaf reports `phpmd`, `semgrep`, `secret-detection`, …).
- **Search words:** each listed node is `{node, name, tool, search}`. `name` and `tool` come back without
  Markdown backticks; a `Tool: none` comes back as `null`. `search` is name and tool, each once (a tool
  that only repeats the name is dropped), e.g. `["PHP CS Fixer", "php-cs-fixer"]`, `["PHPUnit"]`.
- **Tree-doc entries shortened** (Tool now a short name, the sentence moved to the end of Purpose), each in
  the tree doc and in the node's own file: `editorconfig`, `secret-detection`, `php-minimal-version`,
  `psr-4`, `coverage-floor`, `phpstan-level-0`, `phpstan-deprecation-rules`, `psalm-taint-analysis`,
  `semgrep`, and the five `rector-*` nodes. A parser test holds every listed node to short, plain search
  words.

### Left as it was

- A target that is not a PHP project never gets a fulfilled Safety Net: its PHP leaves are neither
  fulfilled nor rejected, they sit in the backlog, and `php-safety-net` stays unfulfilled. This is the
  known gap `tooling-tree/is-php-project.md` describes; computing the gate did not change it.
- A leaf below its PHP floor is neither fulfilled nor rejected either, so it keeps `php-safety-net` and the
  Safety Net Track unfulfilled until the caller rejects it or the floor rises.
- `test-runner-if-missing` and `secret-detection` keep the tools "any test runner" / "any secret
  scanner", `ci-runner` "GitHub Actions / GitLab CI" — short, but not a single tool name. The names
  "Test Runner (fallback)" and "Semgrep (OWASP Top 10)" keep their parentheses.

### For ticket 04 to decide

- **The Track flag and the gate are two different questions.** `tracks["Safety Net"]["fulfilled"]` follows
  this ticket's wording — every Safety Net node with a ticket is fulfilled or rejected. `php-safety-net` and
  `structural-scan` (in `detected`) only need their leaves. With `php-cs-fixer` or
  `test-runner-if-missing` still undecided, the gates are fulfilled and the Guardrails nodes behind them
  open, while the Track flag is false. "Moving on to the next Track … applies once Safety Net is fulfilled"
  has to say which of the two it reads.
- `editorconfig` got the tool name "EditorConfig" (it was "none — plain-text convention file …") so that
  a ticket titled after the convention is found; `psr-4` and `php-minimal-version` stay at "none".
- A second search word shared by siblings ("Rector", "PHPStan", "PHPUnit" for `coverage-floor`) finds
  the siblings' tickets too; the name is the word that tells them apart.
