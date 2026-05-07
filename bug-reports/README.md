# Defect Inventory — Scientific Calculator

This directory contains one Markdown bug report per distinct defect
discovered while running the automated test suite against
<https://rbihubcodechallenge.github.io/calculator/index.html>.

Reports follow the schema in [`_TEMPLATE.md`](./_TEMPLATE.md) — what
you would expect to file in Jira / Linear / GitHub Issues. Every
report is fully self-contained: title, severity, steps, expected vs.
actual, evidence path, root-cause hypothesis, suggested fix, and
severity justification.

## Severity matrix

| Severity     | Count | IDs                                        |
| ------------ | ----- | ------------------------------------------ |
| **Critical** | 4     | BUG-001, BUG-002, BUG-003, BUG-007         |
| **High**     | 4     | BUG-004, BUG-008, BUG-009, BUG-019         |
| **Medium**   | 9     | BUG-005, BUG-006, BUG-010, BUG-011, BUG-012, BUG-013, BUG-014, BUG-016, BUG-018 |
| **Low**      | 2     | BUG-015, BUG-017                           |
| **TOTAL**    | **19**|                                            |

## Index — by ID

| ID | Title | Severity | Component | Failing tests |
|----|-------|----------|-----------|---------------|
| [BUG-001](./BUG-001.md) | `−` button performs division | Critical | UI | `test_minus_button_subtracts` |
| [BUG-002](./BUG-002.md) | Digit `3` button appends `0` | Critical | UI | `test_digit_button_inserts_its_own_label[digit=3]` |
| [BUG-003](./BUG-003.md) | Division operands swapped in parser | Critical | Parser | `test_division_uses_correct_operand_order` (×3); `test_basic_arithmetic_matches_oracle[div_*]` (×4) |
| [BUG-004](./BUG-004.md) | Multi-decimal silently truncates (`1.2.4`→`1.2`) | High | Lexer | `test_multiple_decimal_points_must_be_rejected`; `test_consecutive_decimal_points_must_be_rejected` |
| [BUG-005](./BUG-005.md) | Empty `=` shows `'undefined'` | Medium | calculate | `test_pressing_equals_with_empty_display_must_not_show_undefined` |
| [BUG-006](./BUG-006.md) | Leading op yields `NaN` (inconsistent with `Error`) | Medium | Parser | `test_leading_operator_must_yield_error_consistent_with_trailing` |
| [BUG-007](./BUG-007.md) | `sin(x)` ignores input, always returns `1` | Critical | sin handler | `TestSinIsConstant::*` (×3); `TestTrigFunctions::*[sin_zero,sin_pi]` (×2) |
| [BUG-008](./BUG-008.md) | sqrt/log domain errors leak `NaN`/`-Infinity` | High | func | `TestDomainErrorsAreReported::*` (×3) |
| [BUG-009](./BUG-009.md) | Parser truncates after closing `)` mid-expression | High | Parser | `TestParserTruncatesAfterClosingParen::*` (×5) |
| [BUG-010](./BUG-010.md) | Malformed parens don't reach `Error` pathway | Medium | Parser | `TestMalformedParenthesesShouldYieldError::*` (×4) |
| [BUG-011](./BUG-011.md) | Div-by-zero leaks `Infinity` / `NaN` | Medium | Arithmetic | `TestDivisionByZero::*` (×2) |
| [BUG-012](./BUG-012.md) | Display uses `disabled`, should be `readonly` | Medium | a11y | `test_display_should_be_readonly_not_disabled` |
| [BUG-013](./BUG-013.md) | Display has no `aria-label` | Medium | a11y | `test_display_should_have_aria_label` |
| [BUG-014](./BUG-014.md) | Display has no `aria-live` region | Medium | a11y | `test_display_should_be_an_aria_live_region` |
| [BUG-015](./BUG-015.md) | No `<main>` / `<h1>` landmark | Low | a11y | `test_page_has_main_landmark_or_heading` |
| [BUG-016](./BUG-016.md) | No viewport meta — broken on mobile | Medium | HTML head | `test_viewport_meta_is_present_for_mobile` |
| [BUG-017](./BUG-017.md) | Buttons default to `type="submit"` | Low | HTML | `test_all_buttons_have_explicit_type_button` |
| [BUG-018](./BUG-018.md) | No keyboard input (WCAG 2.1.1) | Medium | a11y | `test_typing_a_digit_on_keyboard_updates_the_display` |
| [BUG-019](./BUG-019.md) | Digit after `=` appends instead of resetting | High | UX/state | `test_digit_after_equals_starts_new_calculation` |

## Suggested fix order (highest leverage first)

1. **BUG-002** — replace `append('0')` with `append('3')` on the `3`
   button. *One-line change. Removes an entire class of cascading
   wrong answers across the suite.*
2. **BUG-003** — flip the operand order in the parser's division
   step. *One-line change. Fixes ~6 failing tests directly and
   another ~3 cascade failures.*
3. **BUG-001** — replace `append('/')` with `append('-')` on the
   minus button. *One-line change.*
4. **BUG-007** — replace `display.value = 434563^434562` with
   `display.value = Math.sin(value)`. *One-line change.*
5. **BUG-006 / BUG-008 / BUG-011 (single fix)** — normalise the
   final result in `calculate()` and `func()` to coerce
   `undefined` / `NaN` / non-finite values into `'Error'`. *Three
   bug reports, one ~3-line change.*
6. **BUG-009** — re-author the parser's `expr`/`term` rules as
   loops so tokens after a closing `)` are no longer dropped. The
   project's own oracle implementation in
   [`src/utils/math_oracle.py`](../src/utils/math_oracle.py) is a
   working reference for the exact same grammar.
7. **BUG-019** — add a `justEvaluated` flag and reset on next
   digit / decimal append.
8. **BUG-018** — add a `keydown` document-level listener.
9. **BUG-012 / BUG-013 / BUG-014 (one diff)** — change the
   display element to `<input type="text" id="display" readonly
   aria-label="Calculator display" aria-live="polite">`.
10. **BUG-016** — add `<meta name="viewport" content="width=device-width,
    initial-scale=1">`.
11. **BUG-004** — track `seenDot` while tokenising numbers, throw
    on the second `.`.
12. **BUG-010** — make the closing `)` mandatory in the parser
    (or assert "all tokens consumed" at the end of `evaluate`).
13. **BUG-017** — add `type="button"` to the 24 buttons.
14. **BUG-015** — wrap the calculator in `<main>` and add an
    `<h1>` (visually hidden if necessary).

After items 1-7 are applied, the suite is expected to drop from 43
failing tests to under 5; the remaining a11y/UX items are cosmetic
and can ship in the following sprint.

## Cascade map

Several defects interact and double-cause failures. The dependency
graph below explains why some inputs surface multiple bug numbers
in their reasoning section:

```
BUG-002 (digit 3 -> 0)
  └─ cascades into → many functional, edge tests
                     (e.g. "13+1" silently becomes "10+1")

BUG-001 (minus -> /)  +  BUG-003 (div swap)
  └─ together → "9-4" entered as "9/4" then evaluated as "4/9 = 0.444"
  └─ together → "(0-5)/0" entered as "(0/5)/0" = "0/0 = NaN"…

BUG-006, BUG-008, BUG-011  -- all cured by a single normalise-to-Error
                              line in calculate() / func().
BUG-012, BUG-013, BUG-014  -- all cured by a single attribute change
                              on <input id="display">.
```

## How to reproduce all defects locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pytest                       # full suite, 43 expected failures (xfail today)
pytest -m bug                # only the defect-tracking tests
pytest tests/functional      # one suite at a time
```

The HTML report at `reports/report.html` includes a screenshot of
the failing display state for every red test (auto-captured by
`conftest.py::pytest_runtest_makereport`).
