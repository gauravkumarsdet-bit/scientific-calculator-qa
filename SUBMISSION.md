# QA Lead Assessment — Submission Note

**Candidate:** Gaurav Kumar
**Repository:** <https://github.com/gauravkumarsdet-bit/scientific-calculator-qa>
**Target under test:** <https://rbihubcodechallenge.github.io/calculator/index.html>
**CI status:** ![CI](https://github.com/gauravkumarsdet-bit/scientific-calculator-qa/actions/workflows/ci.yml/badge.svg?branch=main)
**Tag for review:** `v1.0`

---

## 30-second tour for the reviewer

| You want to see…                                  | Open this                                                                  |
| ------------------------------------------------- | -------------------------------------------------------------------------- |
| **How to run the suite**                          | [`README.md` → Quick start](./README.md#quick-start)                       |
| **Test plan, scope, entry/exit criteria**         | [`docs/TEST_PLAN.md`](./docs/TEST_PLAN.md)                                 |
| **Feature × test-type coverage matrix**           | [`docs/COVERAGE_MATRIX.md`](./docs/COVERAGE_MATRIX.md)                     |
| **All 19 bug reports (severity, repro, fix)**     | [`bug-reports/README.md`](./bug-reports/README.md)                         |
| **Suggested fix order + cascade map**             | [`bug-reports/README.md` → Suggested fix order](./bug-reports/README.md#suggested-fix-order-highest-leverage-first) |
| **CI pipeline definition**                        | [`.github/workflows/ci.yml`](./.github/workflows/ci.yml)                   |
| **Latest green CI run**                           | <https://github.com/gauravkumarsdet-bit/scientific-calculator-qa/actions>  |
| **Page Object**                                   | [`src/pages/calculator_page.py`](./src/pages/calculator_page.py)           |
| **Math oracle (independent expected-value source)** | [`src/utils/math_oracle.py`](./src/utils/math_oracle.py)                 |

## At-a-glance numbers

| Metric                              | Value                                            |
| ----------------------------------- | ------------------------------------------------ |
| **Tests collected**                 | 148                                              |
| **Passed**                          | 101                                              |
| **xfailed (known defects, tracked)**| 43                                               |
| **Skipped (not applicable yet)**    | 4                                                |
| **Unexpected failures / errors**    | 0                                                |
| **Distinct defects filed**          | 19 (4 Critical · 4 High · 9 Medium · 2 Low)      |
| **Lint (black + flake8)**           | clean                                            |
| **CI**                              | green on Ubuntu, parallel headless Chrome        |

## What was prioritised, and why

1. **Coverage breadth before depth.** Six layered suites — smoke,
   functional, scientific, edge, UX/a11y, and bug-tracking — so a
   single `pytest` run gives signal on every dimension of the product.
2. **Oracle-driven assertions.** Every numeric expectation comes from
   a *separately-implemented* recursive-descent evaluator
   ([`src/utils/math_oracle.py`](./src/utils/math_oracle.py)),
   not from hand-written constants. This caught BUG-003 (operand
   swap) and BUG-009 (token truncation) that a "type 2+3, expect 5"
   suite would have missed.
3. **Strict-xfail discipline.** Every known defect is tied to its
   bug ID via `@pytest.mark.xfail(strict=True, reason="BUG-NNN: …")`.
   Strict mode means **the day a developer fixes a bug, CI immediately
   reports an XPASS and forces the marker to be removed** — defects
   cannot silently regress in either direction.
4. **CI-readiness from day one.** No hand-installed driver binaries
   (webdriver-manager), parallel execution (`pytest-xdist`), HTML +
   JUnit reports archived as artifacts on every run, lint and tests
   in separate jobs so a formatting nit never blocks a real failure
   from being seen.

## Commit history (16 incremental commits, no squashes)

```
b0525e6  ci: harden screenshot pipeline so artifact upload no longer fails CI
78c08f9  docs: final README, formal test plan and coverage matrix
ebda4ac  ci: add GitHub Actions workflow (lint + parallel headless E2E)
b5bd211  test(bugs): wire strict xfail markers tying every failing test to its bug ID
7589ee9  docs(bugs): file 19 bug reports + index + cascade map (no code changes)
b3d3a4e  test(ux): UX & accessibility coverage (8 failures, 8 new findings)
7ed9021  test(edge): parens, precedence, div-by-zero, malformed input (11 failures expose 3 new defects)
8131113  test(scientific): sin/cos/tan/sqrt/log coverage (8 failures expose 2 new defects)
6677551  test(functional): digit composition, decimals, clear & error semantics (4 new defects surfaced)
71ca9cc  test(functional): basic arithmetic + button label-integrity (12 failures surface 3 distinct defects)
e73fe71  test(smoke): add smoke / sanity test suite (29 tests, all green)
adad836  feat(data): math oracle, JS-compatible display formatter, parametrised data
3e187e5  feat(pages): add Page Object Model for the Scientific Calculator
df541cf  feat(framework): add config, logger, WebDriver fixture and package skeleton
e26038e  build: add Python tooling, dependencies and quality config
0e07bd2  chore: initial project scaffolding
```

Each commit is independently reviewable: scaffolding → tooling →
framework → page objects → data/oracles → progressively wider test
suites → bug reports → defect-tracking markers → CI → docs → CI
hardening. No bulk dumps; nothing is squashed.

## Mapping to the assessment criteria

| Evaluation criterion                                                            | Where it lives                                                                                            |
| ------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Depth of exploration, precision of repro steps, accuracy of severity judgement  | [`bug-reports/`](./bug-reports/) — 19 reports, every one with steps / expected / actual / root-cause / fix / severity justification |
| Clarity & professionalism of written findings                                   | [`bug-reports/_TEMPLATE.md`](./bug-reports/_TEMPLATE.md) + every BUG-NNN.md                              |
| Logical coverage thinking, boundary awareness, sanity vs. regression distinction | [`docs/TEST_PLAN.md`](./docs/TEST_PLAN.md), [`docs/COVERAGE_MATRIX.md`](./docs/COVERAGE_MATRIX.md), pytest markers (`smoke` / `regression` / `bug`) |
| Code structure, readability, scalability                                        | [`src/pages/`](./src/pages/) (POM), [`src/utils/`](./src/utils/) (config, logger, oracle, formatter), [`src/data/`](./src/data/) (parametrised tables) |
| CI-readiness                                                                    | [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) — green on push & PR, lint and tests separated, artifacts uploaded |
| Constructive, specific, forward-looking                                         | [Suggested fix order](./bug-reports/README.md#suggested-fix-order-highest-leverage-first) — ordered by leverage, with cascade analysis showing 7 fixes clear ~38 of 43 failures |

## Forward-looking sprint plan (next iteration)

- Extend the oracle to cover precedence with parentheses *and*
  unary minus once BUG-009 is fixed, so the parens suite can be
  promoted from regression-tracking to true equivalence checking.
- Add visual-regression on the calculator at three breakpoints
  (mobile / tablet / desktop) once BUG-016 lands.
- Add a Firefox + WebKit matrix to CI; today the suite is
  Chrome-only, intentionally, to keep the first cut focused.
- Promote `pytest-xdist` to `--dist=loadfile` once the suite has
  enough per-file tests to benefit from file-level scheduling.

## How to run, quickly

```bash
git clone https://github.com/gauravkumarsdet-bit/scientific-calculator-qa.git
cd scientific-calculator-qa
python3 -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
pytest                  # full suite (~6-7 min serial, ~2 min with -n auto)
open reports/report.html
```

CI runs the same command on every push / PR — no manual driver
install, no manual config.
