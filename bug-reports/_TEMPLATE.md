# BUG-NNN — <One-line title in active voice>

| Field        | Value                                              |
| ------------ | -------------------------------------------------- |
| **ID**       | BUG-NNN                                            |
| **Status**   | Open / In Progress / Fixed / Won't fix             |
| **Severity** | Critical / High / Medium / Low                     |
| **Priority** | P0 / P1 / P2 / P3                                  |
| **Component**| Parser / UI / Accessibility / Function (sin/…)     |
| **Reporter** | Gaurav Kumar (QA)                                  |
| **Reported** | YYYY-MM-DD                                         |
| **Affects**  | <branch / commit / version under test>             |

## Summary

Two-to-three-sentence executive description: what is wrong, what should
happen instead, and the user-facing impact.

## Environment

| | |
|--|--|
| URL | <https://rbihubcodechallenge.github.io/calculator/index.html> |
| Browser | Chromium (chromedriver auto-managed) |
| OS | macOS 14.6 / Ubuntu 22.04 (CI)                            |
| Test commit | <git short SHA>                                       |

## Steps to reproduce

1. Open the calculator URL above.
2. …
3. …

## Expected behaviour

What the spec / user expectation says should happen.

## Actual behaviour

What was observed, verbatim. Quote the displayed string exactly.

## Evidence

| Type | Path |
|--|--|
| Failing test | `tests/<suite>/test_<file>.py::Test<Class>::test_<name>` |
| Screenshot   | `reports/screenshots/<file>.png` (auto-captured on failure) |

## Root cause hypothesis

Best-guess of the underlying defect, citing the specific JS / DOM
construct in `index.html` where reasonable.

## Suggested fix

Concrete, minimal patch that would resolve the issue.

## Severity justification

Why this rating? What is the user-visible impact (data loss vs. cosmetic),
how often will it be hit, and what workarounds exist?

## Notes / related bugs

Cross-references to other bug IDs that share a root cause or interact
with this one (e.g. cascades).
