# Coverage Matrix

This document maps every calculator feature / behaviour to the tests that
exercise it, so a reviewer can answer two questions at a glance:

1. **Is anything missing?**
2. **What test breaks if behaviour X regresses?**

Tests are grouped by suite; ✅ = covered with explicit assertions, 🐛 = the
test exists *because* the area has a known defect (xfail), ⏭ = deliberately
skipped/parked with a documented reason, — = not covered.

## Calculator feature × test file

| Feature / behaviour | smoke | functional | scientific | edge | ux |
|---|---|---|---|---|---|
| Page loads & renders | ✅ `test_smoke::TestPageRenders` | — | — | — | — |
| 24 expected buttons present | ✅ `test_smoke::TestButtonSurface` | — | — | — | — |
| Display empty on load | ✅ `test_smoke::TestPageRenders` | — | — | — | — |
| End-to-end click→display chain | ✅ `test_smoke::TestHappyPath` | — | — | — | — |
| Digits 0–9 each insert their own label | — | 🐛 `test_button_label_integrity::test_digit_button_inserts_its_own_label` (BUG-002) | — | — | — |
| `+` adds | — | ✅ `test_arithmetic` (parametrised) | — | — | — |
| `−` subtracts | — | 🐛 `test_button_label_integrity::test_minus_button_subtracts` (BUG-001) | — | — | — |
| `×` multiplies | — | ✅ `test_arithmetic` | — | — | — |
| `÷` divides | — | 🐛 `test_button_label_integrity::test_division_uses_correct_operand_order` (BUG-003) | — | — | — |
| Multi-digit composition | — | ✅ `test_digits_and_decimal::TestDigitComposition` | — | — | — |
| Decimal point — single | — | ✅ `test_digits_and_decimal::TestDecimalPoint` | — | — | — |
| Decimal point — leading dot `.5` | — | ✅ `test_digits_and_decimal::test_leading_dot_decimal_is_accepted` | — | — | — |
| Decimal point — multiple in one number | — | 🐛 `test_digits_and_decimal::test_multiple_decimal_points_must_be_rejected` (BUG-004) | — | — | — |
| Decimal point — consecutive | — | 🐛 `test_digits_and_decimal::test_consecutive_decimal_points_must_be_rejected` (BUG-004) | — | — | — |
| `C` empties the display | — | ✅ `test_digits_and_decimal::TestClearAndErrors` | — | — | — |
| Trailing operator yields `Error` | — | ✅ `test_digits_and_decimal::test_trailing_operator_yields_error` | — | — | — |
| Empty input + `=` | — | 🐛 `…::test_pressing_equals_with_empty_display_must_not_show_undefined` (BUG-005) | — | — | — |
| Leading operator | — | 🐛 `…::test_leading_operator_must_yield_error_consistent_with_trailing` (BUG-006) | — | — | — |
| `sin(x)` correctness | — | — | 🐛 `TestSinIsConstant`, `TestTrigFunctions` (BUG-007) | — | — |
| `cos(x)` correctness | — | — | ✅ `TestTrigFunctions` | — | — |
| `tan(x)` correctness | — | — | ✅ `TestTrigFunctions` | — | — |
| `sqrt(x)` positive | — | — | ✅ `TestSquareRoot` | — | — |
| `log(x)` positive | — | — | ✅ `TestLogarithm` | — | — |
| `sqrt(-x)` domain error | — | — | 🐛 `TestDomainErrorsAreReported` (BUG-008) | — | — |
| `log(0)` / `log(-x)` domain error | — | — | 🐛 `TestDomainErrorsAreReported` (BUG-008) | — | — |
| Function then arithmetic chain | — | — | ✅ `TestFunctionThenArithmetic` | — | — |
| Function on empty display → `Error` | — | — | ✅ `TestFunctionWithEmptyDisplay` | — | — |
| Parens at end of expression | — | — | — | ✅ `TestParenthesesAlone` | — |
| Parens mid-expression | — | — | — | 🐛 `TestParserTruncatesAfterClosingParen` (BUG-009) | — |
| Malformed parens (`)`, `()`, `(2+5`, `2+5)`) | — | — | — | 🐛 `TestMalformedParenthesesShouldYieldError` (BUG-010) | — |
| Operator precedence (`*` before `+`) | — | — | — | ✅ `TestOperatorPrecedenceMultiplicativeOnly` | — |
| Division by zero | — | — | — | 🐛 `TestDivisionByZero` (BUG-011) | — |
| `=` is idempotent | — | — | — | ✅ `TestEqualsIsIdempotent` | — |
| Numeric extremes | — | — | — | ✅ `TestNumericExtremes` | — |
| Display = readonly (a11y) | — | — | — | — | 🐛 `TestDisplayAccessibility` (BUG-012) |
| Display has aria-label | — | — | — | — | 🐛 `TestDisplayAccessibility` (BUG-013) |
| Display is aria-live | — | — | — | — | 🐛 `TestDisplayAccessibility` (BUG-014) |
| Page has `<main>`/`<h1>` | — | — | — | — | 🐛 `TestPageAccessibility` (BUG-015) |
| Viewport meta declared | — | — | — | — | 🐛 `TestPageAccessibility` (BUG-016) |
| Buttons declare `type="button"` | — | — | — | — | 🐛 `TestButtonAttributes` (BUG-017) |
| Keyboard input works | — | — | — | — | 🐛 `TestKeyboardInput` (BUG-018) |
| Display-not-typable | — | — | — | — | ✅ `TestKeyboardInput::test_display_field_is_not_directly_typable` |
| Digit after `=` resets | — | — | — | — | 🐛 `TestPostEqualsBehaviour` (BUG-019) |
| Focus indicator visible | — | — | — | — | ✅ `TestKeyboardFocusIndicator` |
| `<html lang>` declared | — | — | — | — | ✅ `TestPageLanguageDeclared` |

## Defect ID → failing tests

See [`bug-reports/README.md#index--by-id`](../bug-reports/README.md#index--by-id)
for the canonical mapping. Each row in the table above showing 🐛 also
links 1:1 to a Markdown bug report file.

## Coverage gaps and why

| Area | Status | Why |
|---|---|---|
| Cross-browser (Firefox / WebKit) | Not covered | Assessor request was Chrome-only. |
| Mobile / touch | Not covered | BUG-016 (no viewport meta) makes mobile rendering meaningless until fixed. |
| Visual regression | Not covered | Out of scope for v1; queued for follow-up sprint (README §"What I'd do next"). |
| Performance / animation | Not covered | Calculator has no animations; perf is bounded by `pytest-timeout` (60 s). |
| Localisation (decimal comma, RTL) | Not covered | App declares `lang="en"`; localisation is not in spec. |
| `axe-core` automated a11y scan | Not covered | We assert specific WCAG criteria explicitly; running an axe-core scan would be additive but not duplicative. Queued for follow-up sprint. |
