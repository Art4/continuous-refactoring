# PHPMD

The Tool for the Role Code Smell Detection in the PHP Pack.

**Why this order.** A Guardrails Stage: workable only once the Safety Net is fulfilled, and it needs Composer. Adopting it enriches the search for structural candidates; it never holds structural work up.

### `phpmd`

- **Purpose:** measure the size and complexity of the code, and keep it from growing: the limits of its metrics are a Ratchet (below). Once fulfilled, the search for structural candidates reads its real output for the Understandability factor (nested conditionals, long methods, deep coupling) and for Defect density (complexity correlates with bug rates), both in `../../signals.md`, in place of the generic recognition method. It runs there with the rules' own default limits (*Measuring*), because under the Ratchet the target's run is green and reports nothing.
- **Fulfilment check:** all of:
  - the dev dependency `phpmd/phpmd` is installed;
  - a ruleset config is committed (`phpmd.xml`, `phpmd.xml.dist` or `.phpmd.xml`). The rule sets it takes are the target's choice (*Rule sets*);
  - no baseline file (`phpmd.baseline.xml`) exists, nor does the config name one;
  - every limit the config overrides on a metric rule carries the Ratchet comment (below);
  - no rule is left out *for now*: an `<exclude>` whose comment begins `Not yet:` (*Taking in a rule*) keeps the Stage unfulfilled;
  - PHPMD runs locally without a violation;
  - once `ci-runner` is fulfilled, a CI job invokes PHPMD with that config (a self-wired CI gate, the same shape as PHPUnit's; with no CI yet, local adoption alone still fulfils the Stage).
- **Rule sets:** a fresh adoption writes `cleancode`, `codesize`, `design`, `naming` and `unusedcode`, not `controversial`: its camel-case rules overlap the code style fixer, and its superglobal rule depends on the framework. A target that does not want a rule set, or a single rule, leaves it out of the config or names it in an `<exclude>`, with a comment beside it that says why. The check accepts such a selection, with or without the comment, and the suite never proposes a rule set later that the config left out. Many findings are no reason to decline a rule: such a rule waits (*Taking in a rule*), and the human is not asked to give it up.
- **Version:** a fresh adoption installs the newest major version. A target on 2.x stays on it and uses the 2.x property names (*The Ratchet*); moving to 3.x is no part of this Stage.
- **MR scope:**
  - *A fresh adoption:* the dependency, the config and, once `ci-runner` is fulfilled, the CI job. The config is made so PHPMD runs green, in this order:
    1. Noise the stack causes is expressed in the config, not in the code: path excludes, and rule properties such as `exceptions` or `ignore-global` where the rule has them (for example static calls the framework makes idiomatic, or short method names it requires). A path exclude covers every rule, and an `exceptions` list covers its rule in every file, by name. So a name goes into `exceptions` only where the stack fixes it for the whole project (a method the framework calls, a class it makes static). A name that is only a convention of some classes (the fields a mapper fills through reflection, in the entities) is suppressed on those classes instead, or the list would silence a real finding of that name anywhere else.
    2. Every metric rule the target breaks gets its limit set to today's peak, with the Ratchet comment. The target's code is not touched for these. A name-length limit it breaks is set once to what the target uses, with no comment.
    3. Count the findings of every rule that is no metric, and take the rules in with the fewest findings first: each one's findings are fixed at their cause, and a deliberate exception is suppressed at the code (*Suppressions*). Stop at the first rule whose commit a reviewer could no longer check by one pattern (`../../principles.md`, *A merge request a person can review*): a mechanical rewrite of many places counts for little, a suppression that needs its own reason in each place counts for much. That rule and every rule after it are not taken in yet (*Taking in a rule*). The plan names the count of each rule and the rule where it stopped.
    4. Where the merge request is still too big, the plan is cut into parts (`../../design-point.md`, *Planning a tooling ticket*): the first holds the dependency, the config, the limits and the rules already green; the rest is taken in later.
  - *A target that has a baseline:* one merge request replaces it, whether the suite or the target's own hand put it there. Entries of metric rules become limits at today's peak, with the Ratchet comment; the others are fixed or suppressed as above; the baseline file is deleted. This is no ticket that stays open: nothing is repaired, only moved.
  - In both cases the merge request reads in its description what was set to which peak and what was suppressed, with the reasons.
  - Also add the Housekeeping line below to the target's Housekeeping template (`../../implement-point.md`, *Slices every kind of ticket can have*), as a commit of its own before the changelog entry. A Stage already fulfilled the very first time it is evaluated never gets a merge request of its own; its line then reaches the template through the Housekeeping Track (`../../../../continuous-housekeeping/references/housekeeping-track.md`, step 4).
- **Suppressions:** a deliberate exception is written at the code it concerns, never in a baseline, which holds only rule, file and method and has no place for a reason. On 3.x it is the attribute `#[SuppressWarnings(RuleClass::class)]` on the method or class; on 2.x the docblock annotation `@SuppressWarnings(PHPMD.RuleName)`. A comment above says why. On 3.x the rule `UnusedSuppression` reports a suppression that no longer suppresses anything. A metric rule is never suppressed: its limit is the tool for that. A suppression at adoption is judged by the merge request's review; later, a new one is an open question to the human, like an ignore rule for PHPStan.

### Taking in a rule

A rule that reports too much to take in at adoption is named in an `<exclude>` inside its rule set's `<rule ref>`, with the comment `Not yet:` and the number of findings the last measurement counted, so that the config stays green and the debt stays in sight:

```xml
<rule ref="rulesets/cleancode.xml">
    <!-- Not yet: 212 findings. -->
    <exclude name="ElseExpression"/>
</rule>
```

Every such `<exclude>` has its own comment directly above it, and no other `<exclude>` of the config carries a `Not yet:`. A metric rule whose limit is overridden, or a rule with a property set for noise, is named in an `<exclude>` of its rule set without a comment and then referenced once more on its own with the property: PHPMD does not merge a rule named twice, it runs both, and the default one would still report.

The Stage is not fulfilled while such an `<exclude>` exists. Its ticket is "PHPMD: take in the remaining rules", the same shape as a PHPStan baseline ticket and planned part by part (`../../design-point.md`, *Planning a baseline ticket*): one rule per merge request, the one with the fewest findings first; a rule too large for one merge request is cut by directory, and its `<exclude>` stays until the last part is merged. A part fixes findings at their cause, and suppresses only a deliberate exception. A suppression that merely lowers the count is no fix. Taking in a rule deletes its `<exclude>` and its comment. A finding that only a behaviour change could remove is named in the plan, and the rule is declined instead: its `<exclude>` then carries the reason, and only a human decides that.

### The Ratchet

The limits of the metric rules only ever fall. A metric rule is one with an upper bound: in `codesize` cyclomatic complexity, NPath, method length, class length, parameter count, public count, field count, method count and class complexity, and in `design` coupling, depth of inheritance and number of children. The length of a name (`naming`) is a convention, set once to what the target uses and not ratcheted.

- **The limit** of a rule is the lowest value at which PHPMD still reports nothing. In 3.x every metric rule has the property `maximum` and reports a value above it, so the limit is the peak. In 2.x the property is named differently per rule (`reportLevel`, `minimum`, `maxfields`, `maxmethods`, `maximum`) and mostly reports at the value itself, so the limit is the peak plus one; the installed version's own rule files say which. A rule the target already keeps is not overridden: it stays on the rule's default.
- **The default** is read from the installed version's own rule files (`vendor/phpmd/phpmd/rulesets/` in 3.x, `src/main/resources/rulesets/` in 2.x), not copied from here.
- **The comment** is written beside each override, as the rule's name, the default, the peak and where it is, as a class, and for a rule that measures a method the method with it (a metric of a class that spans several classes, like coupling, names the class that sets the peak):

  ```xml
  <!-- recommended: 10. Current peak: 14 (App\Billing\Invoice::total). -->
  <property name="maximum" value="14"/>
  ```

  The planning of a structural ticket reads the comment to know which method sets the peak; the comment is measured again only when it is missing or no longer matches the code.
- **Raising a limit is never a fix.** A metric that exceeds its limit is met by changing the code. A limit is set above the code only at an adoption, for a rule the merge request newly takes in, and for a rule a new PHPMD version added (*Housekeeping*).
- **Lowering**, the step the Ratchet slice carries (`../../implement-point.md`, *Slices every kind of ticket can have*): a merge request that rewrote the method or class at a `Current peak`, or any file the plan named for it, measures again (*Measuring*) and for each metric rule sets the limit to the new peak and updates the comment. A limit goes no lower than the default. The merge request is a success when PHPMD, with all other limits unchanged, runs green and the target rule's peak has fallen. A rule whose value rose in the process counts as long as it stays under its own limit; where it does not, the merge request is red and the limit does not move, because the code changes, not the limit. It may lower several limits at once.

### Measuring

Only PHPMD's own means are used; the suite adds no script, neither to itself nor to the target.

- A ruleset in a temporary directory outside the target, naming the same rule sets, with every metric limit set as low as the rule allows. A ruleset's baseline is looked up beside the first ruleset file, so there is none there, and the target's files stay as they are.
- The report in a machine-readable format. The value of each violation is in its message ("has a Cyclomatic Complexity of 14"); SARIF carries it as an argument of the message. Only values above a limit are reported, hence the low limits. The peak of a rule is the greatest value, its second place the next.
- For the search for structural candidates the same ruleset is used with the rules' default limits instead: the places above `recommended` are the evidence.

### Housekeeping

- **Housekeeping:** measure again. For each metric rule whose peak lies below its limit (the code improved without the Ratchet slice), set the limit to the peak and update the comment; only the config changes, never the code. After `composer update` run PHPMD and check for rules a new version added to the rule sets in use: a new metric rule is set to today's peak with the comment, any other new finding is fixed or suppressed, as in an adoption.
