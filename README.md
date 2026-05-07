# Scientific Calculator — QA Automation Suite

[![CI](https://github.com/gauravkumarsdet-bit/scientific-calculator-qa/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/gauravkumarsdet-bit/scientific-calculator-qa/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Selenium 4.25](https://img.shields.io/badge/selenium-4.25-43B02A.svg)](https://www.selenium.dev/)
[![pytest 8.3](https://img.shields.io/badge/pytest-8.3-009384.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

End-to-end automated test suite for the Scientific Calculator hosted at
<https://rbihubcodechallenge.github.io/calculator/index.html>, authored as the
**QA Lead Assessment** submission.

> **The headline:** the suite catches **19 distinct defects** across smoke,
> functional, scientific-function, edge-case and UX/accessibility coverage.
> Every failing test is mapped 1:1 to a self-contained Markdown bug report
> in [`bug-reports/`](./bug-reports/), and every defect is wired through a
> strict-`xfail` marker so CI exits **0** today and **automatically alerts**
> the team the moment any defect is fixed (XPASS → build break).

| Stat | Value |
|---|---|
| Distinct defects identified | **19** (4 Critical · 4 High · 9 Medium · 2 Low) |
| Test cases authored | **148** (101 passing · 43 xfail · 4 skipped) |
| Suites | smoke · functional · scientific · edge_cases · ux |
| Wall time, sequential headless | ~7 min |
| Wall time, CI parallel (`-n auto`) | ~3–4 min |
| Final pytest exit code | **0** (CI green) |

---

## Why these tools

| Concern | Choice | Rationale |
|---|---|---|
| Language | **Python 3.12** | Lowest cognitive overhead for QA engineers; rich standard library (`math`, `re`, `dataclasses`) covers everything we need with no extra deps. |
| Test runner | **pytest** | Best-in-class parametrisation, plugin ecosystem, fixture model. Markers give us a free coverage matrix. |
| Browser | **Selenium 4.25** | Explicit user request. Modern Selenium handles waits cleanly via `WebDriverWait` and supports CDP for any future advanced needs. |
| Driver | **webdriver-manager** | Zero-touch driver binary management. CI just runs `pip install` and works — no `apt-get install chromedriver`, no manual versioning. |
| Reporting | **pytest-html + JUnit XML** | HTML for humans (with screenshots auto-attached on failure); JUnit for any CI dashboard the team plugs in later. |
| Parallelism | **pytest-xdist** | `-n auto` halves wall time. `--dist=loadscope` keeps related tests on the same worker for clean failure attribution. |
| Flake handling | **pytest-rerunfailures** | Wired-in but not yet used; we have zero flaky tests today. Available the moment any are introduced. |
| Hard timeouts | **pytest-timeout** | Per-test 60 s ceiling so a hung browser never wedges CI. |
| Code quality | **black, flake8, isort** | Formatter > linter > debate. Industry default. |
| CI | **GitHub Actions** | Free, native, fast. Two jobs (`lint` ≈30 s, `test` ≈4 min). |

### Architectural decisions worth flagging

* **Page Object Model.** `src/pages/calculator_page.py` is the *only* place
  that knows the calculator's DOM. Tests speak in user actions
  (`click_digit`, `click_operator`, `evaluate("(2+5)*4")`).
* **Locate buttons by their visible text, not their `onclick` attribute.**
  Locating by visible glyph is exactly how a real user finds a button —
  and it is the only strategy that *also* surfaces the label-vs-handler
  mismatches that turn out to be the calculator's most damaging defects
  (BUG-001, BUG-002).
* **Math oracle, not hand-coded numbers.** `src/utils/math_oracle.py` is a
  small recursive-descent evaluator. Tests assert against
  `oracle.expected("8/2") == "4"`, never `assert result == "4"`. If the
  spec ever changes (e.g. trig-in-degrees) the oracle is the *single*
  audit point.
* **JS-compatible display formatting.** `src/utils/display_format.py`
  replicates `Number.prototype.toString` so trig results, `Infinity`,
  `NaN`, and integer-valued floats compare exactly the way the calculator
  prints them — no false-negative comparisons.
* **Strict `xfail` for known defects.** Every defect-tracking test is
  decorated with `@pytest.mark.xfail(strict=True, reason="BUG-NNN: …")`.
  The build is green today; the moment a defect is fixed, the test
  flips to **XPASS** which (because of `strict=True`) breaks the build
  and tells the developer "your fix landed, please remove the marker".
  This is the canonical regression-vs-fix-progress signal.
* **Layered isolation in scientific tests.** When the *function* under
  test (e.g. `Math.sin`) and the *input path* (e.g. clicking digits)
  contain independent defects, mixing them produces misleading failure
  attributions. The page object exposes a deliberately-named
  `set_display_value` helper that bypasses the input layer for trig
  tests, isolating the function itself.

---

## Repository layout

```
scientific-calculator-qa/
├── .github/workflows/ci.yml       # 2-job CI (lint + parallel headless E2E)
├── bug-reports/                   # 19 Markdown bug reports + index + cascade map
│   ├── README.md                  # severity matrix, full ID→test traceability
│   ├── _TEMPLATE.md               # canonical template
│   └── BUG-001.md … BUG-019.md
├── docs/
│   ├── TEST_PLAN.md               # Scope, approach, exit criteria, risks
│   └── COVERAGE_MATRIX.md         # feature × test-type matrix
├── reports/                       # HTML report + JUnit + screenshots (gitignored)
├── src/
│   ├── data/expressions.py        # parametrised data tables
│   ├── pages/
│   │   ├── base_page.py           # reusable explicit-wait wrappers
│   │   └── calculator_page.py     # the only DOM-aware module
│   └── utils/
│       ├── config.py              # env-driven, immutable settings
│       ├── display_format.py      # JS-compatible number-to-string
│       ├── logger.py              # idempotent logger factory
│       └── math_oracle.py         # recursive-descent expected-value oracle
├── tests/
│   ├── smoke/                     # 29 sanity assertions (all green)
│   ├── functional/
│   │   ├── test_arithmetic.py
│   │   ├── test_button_label_integrity.py
│   │   └── test_digits_and_decimal.py
│   ├── scientific/
│   │   └── test_scientific_functions.py
│   ├── edge_cases/
│   │   └── test_edge_cases.py
│   └── ux/
│       └── test_ux_and_accessibility.py
├── conftest.py                    # WebDriver fixture, screenshot-on-failure hook
├── pytest.ini                     # discovery, markers, default flags, reporters
├── pyproject.toml                 # black + isort config
├── .flake8                        # PEP8 with black-compat tweaks
├── .env.example                   # documents every supported override
├── Makefile                       # make install / test / smoke / functional / lint
├── requirements.txt               # runtime deps (pinned)
├── requirements-dev.txt           # +linters/formatter
├── README.md                      # ← you are here
└── LICENSE                        # MIT
```

---

## Quick start (local, 90 seconds)

Prerequisites: Python ≥ 3.10 and Google Chrome installed.

```bash
git clone https://github.com/gauravkumarsdet-bit/scientific-calculator-qa.git
cd scientific-calculator-qa

python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

pytest                           # full suite — exits 0 (101 pass, 43 xfail)
open reports/report.html         # rich HTML report with screenshots
```

Or, with the included `Makefile`:

```bash
make install-dev                 # creates venv + installs everything
make test                        # full suite
make smoke                       # smoke only (~75 s)
make functional                  # functional only
make scientific
make edge
make ux
make lint                        # black + flake8
make format                      # auto-format
```

### Targeted runs

```bash
pytest -m smoke                  # one marker
pytest -m "functional and bug"   # bug-tracking tests within a marker
pytest -k "division"             # by name substring
pytest tests/scientific          # one folder
pytest -n auto --dist=loadscope  # parallel — what CI does
pytest --lf                      # last failed only
```

### Environment overrides (see `.env.example`)

| Variable | Default | Purpose |
|---|---|---|
| `BASE_URL` | the GitHub Pages URL | point the suite at a different deployment |
| `BROWSER` | `chrome` | only `chrome` is supported today |
| `HEADLESS` | `true` | flip to `false` to watch the browser locally |
| `WINDOW_WIDTH` / `WINDOW_HEIGHT` | 1280 × 800 | viewport size |
| `EXPLICIT_WAIT` | `10` | seconds for `WebDriverWait` |
| `PAGE_LOAD_TIMEOUT` | `30` | seconds before page-load failure |
| `SCREENSHOT_ON_FAILURE` | `true` | toggle the on-failure hook |

---

## CI

[`.github/workflows/ci.yml`](./.github/workflows/ci.yml) runs on every push
to `main` and every pull request. It has two jobs:

1. **Lint** (~30 s) — `black --check` + `flake8`. Fails fast.
2. **Test** (~3–4 min) — `pytest -n auto --dist=loadscope` headless. Reports
   uploaded as a build artifact (HTML + JUnit + screenshots; 14-day retention)
   so reviewers can inspect failures without cloning.

Concurrency: a new commit on the same branch cancels the previous in-flight
run to save runner minutes.

The badge at the top of this README links to live CI.

---

## Defect inventory

A full, navigable inventory lives at
[`bug-reports/README.md`](./bug-reports/README.md). Quick summary:

| Severity | Count | Highlights |
|---|---|---|
| **Critical** | 4 | minus button performs division (BUG-001) · digit `3` appends `0` (BUG-002) · division operands swapped (BUG-003) · `sin(x)` always returns `1` (BUG-007) |
| **High** | 4 | silent multi-decimal truncation (BUG-004) · domain errors leak `NaN`/`-Infinity` (BUG-008) · parser drops tokens after `)` (BUG-009) · digit after `=` appends instead of resetting (BUG-019) |
| **Medium** | 9 | empty-input shows `'undefined'` (BUG-005) · inconsistent error pathway (BUG-006) · malformed parens leak `NaN` (BUG-010) · div-by-zero leaks `Infinity` (BUG-011) · 4 a11y issues (BUG-012/013/014/018) · viewport meta missing (BUG-016) |
| **Low** | 2 | no `<main>`/`<h1>` landmark (BUG-015) · buttons default `type="submit"` (BUG-017) |

### Recommended fix order (highest leverage first)

After applying items **1–7** below — together a ~10-line patch across 5 files —
the suite drops from 43 xfail entries to under 5.

1. **BUG-002** — change `append('0')` to `append('3')` on the `3` button.
2. **BUG-003** — flip the operand order in the parser's division step.
3. **BUG-001** — change `append('/')` to `append('-')` on the minus button.
4. **BUG-007** — replace `display.value = 434563^434562` with `Math.sin(value)`.
5. **BUG-006/008/011 (one fix)** — normalise non-finite results to `'Error'`.
6. **BUG-009** — re-author parser's `expr`/`term` rules as proper loops.
7. **BUG-019** — add a `justEvaluated` flag and reset on next digit.

---

## Mapping to the assessment's evaluation criteria

| Criterion | Where it shows up |
|---|---|
| **Depth of exploration** | 19 distinct defects across 5 categories (functional, scientific, lexical, parser, a11y, UX). 35+ test scenarios per category before the curated subset was committed. |
| **Precision of reproduction steps** | Every bug report includes verbatim button presses *and* the exact failing test path. Tests are runnable single-line repros. |
| **Severity judgement** | Severity is defended explicitly in each bug report (data loss vs. cosmetic vs. accessibility). Cascade map prevents inflating cascade-failures into separate "Critical" bugs. |
| **Clarity & professionalism of findings** | Each report uses the same template you would file in Jira/Linear. Suggested-fix sections include 1–3 line diffs. |
| **Coverage thinking** | Test markers map to coverage axes; smoke vs. regression are clearly distinct ([`docs/TEST_PLAN.md`](./docs/TEST_PLAN.md), [`docs/COVERAGE_MATRIX.md`](./docs/COVERAGE_MATRIX.md)). |
| **Boundary awareness** | Edge tests cover empty input, leading/trailing operators, mismatched parens, division by zero, IEEE-754 quirks (`0.1+0.2`), `Number.MAX_SAFE_INTEGER`. |
| **Sanity vs. regression distinction** | `smoke` marker = sanity; `regression` marker = everything else. CI runs both; a failed smoke alone exits the build at the first bad sign. |
| **Code structure / readability / scalability** | Page Object Model, environment-driven config, frozen dataclass test data, tiny pure-function utilities — every concern lives in exactly one place, named after what it does. |
| **CI-readiness** | GitHub Actions workflow runs the full suite headless without manual setup; reports are CI artifacts. |
| **Constructive & forward-looking** | Each bug report has a *Suggested Fix* section. README has a "what I'd do next" sprint plan (below). |

---

## What I'd do in a follow-up sprint

* **Visual regression.** Screenshot the calculator at known states and
  diff with `pixelmatch` or Percy. The current grid layout is fragile;
  any future CSS change is a guaranteed regression risk.
* **`axe-core` accessibility scan.** Pipe the page through axe-core
  via Selenium CDP to get an authoritative WCAG report. Manual
  assertions (BUG-012/13/14) are useful but not exhaustive.
* **Cross-browser matrix.** Add Firefox + WebKit (Safari) to the CI
  matrix. Trivial for Selenium 4 with `webdriver-manager`.
* **Mobile / responsive tests.** Once BUG-016 is fixed, add device
  emulation tests (iPhone 14, Pixel 7) verifying tap targets ≥ 44 px.
* **Performance budget.** A scientific calculator should answer in
  < 100 ms per click; add a soft assertion using `performance.timing`
  via CDP.
* **Property-based tests for the parser.** Once BUG-009 is fixed, drive
  `evaluate(arbitrary_well_formed_expression)` against the Python
  oracle via Hypothesis. The shape we already have makes this a
  ~30-line addition.
* **Fail-fast for data-loss defects.** Promote BUG-002, BUG-004 (silent
  data-loss class) to a `@pytest.mark.critical` smoke-style fail-fast
  group so CI bails the moment they reproduce.
* **i18n smoke.** Trig in radians vs. degrees, decimal separator
  comma vs. dot — a globally-deployed calculator must declare which
  it is.

---

## Author

**Gaurav Kumar** — QA Lead candidate
[github.com/gauravkumarsdet-bit](https://github.com/gauravkumarsdet-bit) ·
gauravkumar.sdet@gmail.com

Project commit history is intentionally **un-squashed** so each logical
step (scaffolding → tooling → POM → suites → bug reports → CI →
documentation) reads as its own reviewable unit.
