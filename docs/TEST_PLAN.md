# Test Plan — Scientific Calculator QA Automation

| Field | Value |
|---|---|
| Document version | 1.0 |
| Date | 2026-05-07 |
| Author | Gaurav Kumar (QA Lead candidate) |
| Application under test | Scientific Calculator |
| URL | <https://rbihubcodechallenge.github.io/calculator/index.html> |
| Branch / commit | `main`, see latest commit on the repo |

## 1. Objective

Validate that the Scientific Calculator behaves to specification, surface
every functional / scientific / boundary / UX defect, and provide a
runnable, CI-ready automated regression suite that the receiving team
can adopt without rewriting.

## 2. Scope

### In scope

* All 24 calculator buttons (digits 0–9, `+ − × ÷ ( ) . = C`,
  `sin cos tan √ log`).
* Display behaviour (initial state, updates, reset semantics, error
  messages).
* Operator precedence and parenthesised expression evaluation.
* Domain-error handling for scientific functions.
* Numeric extremes (very large, very small, IEEE-754 boundary cases).
* WCAG-derived accessibility checks: keyboard operability, ARIA
  metadata, semantic landmarks, viewport readiness.
* HTML hygiene relevant to embedding (`<button type>`, etc.).

### Out of scope

* Cross-browser matrix beyond Chromium (request: Chromium-only).
* Mobile-device emulation (parked behind BUG-016 — viewport meta is
  absent so tests would be measuring CSS pixel mistakes, not user
  experience).
* Network / availability monitoring of the GitHub Pages host.
* Source-level static analysis of the calculator's JavaScript
  (the source is intentionally treated as black-box; root-cause
  *hypotheses* in bug reports are documented, not asserted on).

## 3. Test approach

* **Black-box, UI-driven.** Every test pretends to be a user pressing
  buttons. The Page Object Model in `src/pages/calculator_page.py`
  is the only DOM-aware module.
* **Oracle-driven assertions.** A small recursive-descent evaluator
  in `src/utils/math_oracle.py` computes the *expected* result
  independently. Tests never hard-code answers.
* **JS-compatible display formatting.** The oracle's output is
  formatted via `js_number_to_string` so trig results, `Infinity`,
  `NaN` and integer-valued floats compare verbatim with the
  calculator's rendered string.
* **Layered isolation.** When a function under test (e.g.
  `Math.sin`) interacts with an independently-defective input layer
  (e.g. the digit-`3` button), `set_display_value` bypasses the
  input layer to keep failure attribution clean.
* **Strict-`xfail` for known defects.** All confirmed defects are
  decorated with `pytest.mark.xfail(strict=True, reason="BUG-NNN: …")`,
  so CI exits 0 today *and* flags any silently-fixed defect as XPASS.

## 4. Test types

| Type | Marker | Folder | Purpose |
|---|---|---|---|
| Smoke | `@pytest.mark.smoke` | `tests/smoke/` | Page renders, all buttons present, trivial happy-path. Gates everything else. |
| Functional | `@pytest.mark.functional` | `tests/functional/` | Single-operator arithmetic; digit / decimal integrity; clear & error pathways. |
| Scientific | `@pytest.mark.scientific` | `tests/scientific/` | sin / cos / tan / sqrt / log correctness and domain handling. |
| Edge cases | `@pytest.mark.edge` | `tests/edge_cases/` | Parens, precedence, division-by-zero, malformed input, numeric extremes. |
| UX / a11y | `@pytest.mark.ux` | `tests/ux/` | ARIA, semantic landmarks, viewport, keyboard operability, post-`=` reset. |
| Bug-tracking | `@pytest.mark.bug` (cross-cuts) | various | Tests that exist *to demonstrate* a known defect. |
| Regression | `@pytest.mark.regression` | all but smoke-only | Default CI scope. |

Markers compose:
`pytest -m "scientific and bug"` runs only the scientific defect-tracking
tests.

## 5. Environment

| Component | Value |
|---|---|
| OS (local) | macOS 14.6 |
| OS (CI) | Ubuntu 22.04 (`ubuntu-latest`) |
| Python | 3.12 |
| Browser | Google Chrome (system) |
| Driver | chromedriver auto-managed by `webdriver-manager` |
| Network | unrestricted; GitHub Pages must be reachable |
| Display | headless (`--headless=new`) by default; `HEADLESS=false` for local debugging |

The `Settings` dataclass in `src/utils/config.py` documents every
overridable knob; `.env.example` is the canonical reference.

## 6. Entry & exit criteria

### Entry

* Page loads and renders the 24 expected buttons (smoke gate).
* Required Python deps install cleanly.
* `webdriver-manager` resolves a chromedriver matching the local
  Chrome.

### Exit

* All non-`xfail` tests pass.
* No unexpected `XPASS` (a defect was silently fixed without removing
  its xfail marker — the build *will* fail in this case).
* HTML report is generated under `reports/report.html`.
* Every previously-failing test maps to a Markdown bug report under
  `bug-reports/`.

## 7. Risks & mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Public test target (GitHub Pages) goes down | Low | Suite cannot run | `BASE_URL` is env-driven so a local mirror or staging URL can be substituted in CI. |
| Chrome auto-update breaks chromedriver compatibility | Low | CI job fails at start | `webdriver-manager` re-downloads the matching driver on each run; cached layer is keyed on `requirements.txt` so a `pip install` bump invalidates the cache. |
| Flaky network or slow CI runner times out a test | Low | False red | `pytest-rerunfailures` is wired in (currently unused); 60 s per-test timeout cap is in `pytest.ini`. |
| New defect lands without a bug report | Medium | Inventory drifts from reality | Code review checklist: any new failing test must come with a Markdown bug report and a strict-xfail marker citing it. |
| Defect silently fixed by a developer | Medium | xfail marker becomes stale | Strict-xfail XPASSes break the build automatically — exactly the alert we want. |

## 8. Reporting

* **HTML report:** `reports/report.html` (auto-generated, embeds
  failure screenshots).
* **JUnit XML:** `reports/junit.xml` for any CI dashboard.
* **CI artifacts:** the `test-reports-<run>` artifact uploads the
  whole `reports/` folder for 14 days.
* **Bug inventory:** `bug-reports/README.md` is the human-readable
  index; each `BUG-NNN.md` is self-contained.

## 9. Schedule

| Milestone | Status |
|---|---|
| Test framework scaffolding | ✅ |
| Page Object Model | ✅ |
| Smoke / functional / scientific / edge / UX suites | ✅ |
| Bug reports + traceability | ✅ |
| CI pipeline | ✅ |
| Documentation (this plan + coverage matrix + README) | ✅ |
| Visual-regression / cross-browser / a11y-scan extensions | Future sprint (see README §"What I'd do in a follow-up sprint") |
