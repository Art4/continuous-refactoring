# r4 — Tests that run the code and check little

Played as a walk-through.

## Situation

An onboarded PHP project on GitHub, `acme/shop`, tested with PHPUnit 11. Its Safety Net is fulfilled; the Test
Coverage Floor is fulfilled at 72 %. Infection is not in place, has no ticket and no rejection; no mutation testing
runs. Housekeeping is set up, and its ticket is not due. The tracker file's **BC promise** bullet is `none`. No
ADRs, no glossary.

The open Investigation ticket #40, signal Shallow module: "`PriceCalculator` spreads discount, tax and rounding
over six public methods every caller strings together itself." `tests/PriceCalculatorTest.php` calls each of the
six methods with fixed inputs; every test ends with `$this->assertTrue(true)` or `$this->addToAssertionCount(1)`,
and none compares a returned price. The coverage report counts `PriceCalculator` at 100 %.

## Call

`/continuous-refactoring-run autonomous`

## Expected

- [ ] The plan does not take the existing tests as its pin. Its first slice is a new pin at the seam that
      compares prices.
- [ ] Under `Decisions` the plan has one Opener line, `Opener: infection — …`, naming that the tests reach the
      code and check little of it.
- [ ] The run files no tooling ticket and does not set Infection up itself.

## Results

2026-11-03, skill commit 9654c4b: pass, every line, as a walk-through, played before the situation named the BC promise
bullet; the play also wrote `Opener: bc-promise`, which a project without that bullet meets.
