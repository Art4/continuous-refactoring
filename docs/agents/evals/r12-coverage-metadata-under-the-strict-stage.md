# r12 — Coverage metadata under the strict Stage

Played as a walk-through, once per variant.

Covers: `skills/continuous-refactoring-run/references/packs/php/coverage-floor.md`, `skills/continuous-refactoring-run/references/implement-point.md`, `skills/continuous-refactoring-run/references/track-scan.md`, `skills/continuous-housekeeping/references/housekeeping-track.md`

## Situation

An onboarded PHP application on GitHub, `acme/shop`, as the fixture `fixtures/php/php-app-onboarded/project`
holds it, with what its later tickets added: every Stage of both tooling Tracks that applies has a closed ticket
whose merge request was merged, and what it set up is in the repository and runs in CI. Among them are
`coverage-floor`, `coverage-metadata-required` and `coverage-metadata-strict`: PHPUnit 11 runs with
`requireCoverageMetadata="true"`, `beStrictAboutCoverageMetadata="true"` and `failOnRisky="true"`, the coverage
job is green, and `tests/README.md` holds the two metadata rules. `roave-bc-check` does not apply, and no Tool on
request was asked for. No rejection is recorded.

The tests that matter here:

- `tests/Unit/CartTest.php`: `#[CoversClass(Cart::class)]`, no size, no `#[UsesClass]`; it builds a `Cart`, which
  has grown a `total()` with price and discount logic since the fixture, and checks the total.
- `tests/Integration/CheckoutTest.php`: `#[Medium]`, `#[CoversClass(Checkout::class)]`; it runs a `Checkout` with a
  real `Cart`, a real `OrderRepository` on SQLite and a real `Mailer` writing to a file.

**Variant A.** Open Investigation ticket #60, "Extract the price calculation from Cart", carries the suite's plan as
its newest comment: move `Cart::total()`'s price and discount logic into a new `PriceCalculator`, which `Cart` gets
in its constructor; the pin is `CartTest` and `CheckoutTest`, both green. No merge request, no blocker, no open
question.

**Variant B.** No refactoring ticket is open. The Housekeeping ticket #70 is due today, with the fixture's template's
tasks. The secret scan and the dependency audit find nothing. `CheckoutTest` carries, beside its `#[Medium]`, 40
`#[UsesClass]` lines for every class a checkout reaches. `tests/Unit/OrderFlowTest.php` builds a real `Checkout`,
`Cart`, `OrderRepository` on SQLite and `Mailer`, and asserts on the stored order and the written mail; it carries
no size, `#[CoversClass(Checkout::class)]` and 38 `#[UsesClass]` lines. The coverage job is still green.

## Call

Variant A: `/continuous-refactoring-run autonomous #60`

Variant B: `/continuous-housekeeping autonomous`

## Expected

- [ ] Variant A: the design point finds #60's plan standing and goes on to the implement point.
- [ ] Variant A: the extract's slices give `PriceCalculator` a test of its own with
      `#[CoversClass(PriceCalculator::class)]`.
- [ ] Variant A: `CartTest`, a unit test that now runs `PriceCalculator` without covering it, gains
      `#[UsesClass(PriceCalculator::class)]`.
- [ ] Variant A: `CheckoutTest` gains no `#[UsesClass]` line: as a medium test it keeps its `#[CoversClass]` alone.
- [ ] Variant B: the re-check of the tooling Tracks judges `coverage-metadata-strict` not fulfilled, naming
      `CheckoutTest`'s `#[UsesClass]` lines and `OrderFlowTest` as an integration test with neither size nor an
      empty list.
- [ ] Variant B: one ticket is filed for `coverage-metadata-strict`; its proposal says to delete `CheckoutTest`'s
      list, to give `OrderFlowTest` `#[Medium]` and delete its list, and to leave `CartTest` as it is.
- [ ] Variant B: no other Stage is judged not fulfilled, and the run reaches the remaining tasks of #70.

## Results
