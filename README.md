# Scientific Calculator — QA Automation Suite

End-to-end automated test suite for the Scientific Calculator hosted at
<https://rbihubcodechallenge.github.io/calculator/index.html>, authored as
part of the **QA Lead Assessment**.

> **Status:** scaffolding in progress — full suite, bug reports and CI
> pipeline land in subsequent commits. Each commit represents a logical,
> reviewable step (setup → page objects → tests → bug reports → CI).

## Tech stack

| Concern              | Choice                                     |
| -------------------- | ------------------------------------------ |
| Language             | Python 3.10+                               |
| Test runner          | pytest                                     |
| Browser automation   | Selenium WebDriver                         |
| Driver management    | webdriver-manager (zero manual setup)      |
| Reporting            | pytest-html + JUnit XML                    |
| Parallel execution   | pytest-xdist                               |
| Flake handling       | pytest-rerunfailures                       |
| Code quality         | black, flake8                              |
| CI                   | GitHub Actions (headless Chromium)         |

## Repository layout (target)

```
scientific-calculator-qa/
├── .github/workflows/      # CI pipeline (GitHub Actions)
├── bug-reports/            # One Markdown bug report per defect found
├── docs/                   # Test plan, coverage matrix
├── src/
│   ├── pages/              # Page Object Model
│   ├── data/               # Test data / fixtures
│   └── utils/              # Shared helpers (math oracles, logging)
├── tests/
│   ├── smoke/              # Sanity — does the page even load?
│   ├── functional/         # Core arithmetic, decimal, digit integrity
│   ├── scientific/         # sin / cos / tan / sqrt / log
│   ├── edge_cases/         # Parens, precedence, div-by-zero, empty input
│   └── ux/                 # Keyboard, accessibility, display behaviour
├── conftest.py             # Pytest fixtures (driver, page objects)
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Python dependencies (pinned)
└── README.md
```

## Quick start (local)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

Detailed run instructions, command-line flags and CI execution notes will
be added in the final documentation commit.

## Author

**Gaurav Kumar** &nbsp;·&nbsp;
[github.com/gauravkumarsdet-bit](https://github.com/gauravkumarsdet-bit) &nbsp;·&nbsp;
gauravkumar.sdet@gmail.com
