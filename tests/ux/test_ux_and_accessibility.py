"""
UX & accessibility tests.

Scope
-----
This suite asserts on:

* Concrete accessibility violations the markup is *missing* (aria-label
  on the display, aria-live region for results, semantic landmarks,
  viewport meta).
* Specific UX expectations a scientific-calculator user has from any
  similar app (keyboard support, post-= digit-reset behaviour, button
  ``type`` attribute hygiene).
* Things the developer got *right* — pinned with passing tests so a
  regression flips them.

Some items here are bugs in the strict pass/fail sense (post-= reset,
``aria-live``); others are findings that may be considered
prioritisation calls (visual distinction between operator / digit
buttons). Both are documented; only the former fail the build.
"""

from __future__ import annotations

import pytest

from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from src.pages.calculator_page import CalculatorPage


pytestmark = [pytest.mark.ux, pytest.mark.regression]


# ===========================================================================
# 1. Display accessibility
# ===========================================================================
@pytest.mark.bug
class TestDisplayAccessibility:
    """The display is the calculator's primary output. It must be
    discoverable & announced by assistive tech."""

    @pytest.mark.xfail(
        strict=True,
        reason="BUG-012: display has the 'disabled' attribute; should be 'readonly'.",
    )
    def test_display_should_be_readonly_not_disabled(self, calculator_page: CalculatorPage) -> None:
        """``disabled`` removes the element from the accessibility tree
        and the tab order entirely; ``readonly`` is the correct attribute
        for "user can't edit but assistive tech and tab focus still
        work" (`WAI-ARIA Authoring Practices`).

        Today: ``<input id="display" disabled>``.
        Should be: ``<input id="display" readonly>``.
        """
        elem = calculator_page.find(CalculatorPage.DISPLAY)
        assert elem.get_attribute("disabled") is None, (
            "Display uses the wrong attribute: 'disabled' makes it invisible "
            "to screen readers and removes it from tab order. Use 'readonly'."
        )

    @pytest.mark.xfail(
        strict=True,
        reason="BUG-013: display <input> has no aria-label.",
    )
    def test_display_should_have_aria_label(self, calculator_page: CalculatorPage) -> None:
        """Without an accessible name the screen-reader announces only
        'edit' or 'text input' — completely unhelpful."""
        elem = calculator_page.find(CalculatorPage.DISPLAY)
        aria_label = elem.get_attribute("aria-label")
        assert aria_label, (
            "Display <input> has no aria-label. Screen-reader users will "
            "not know what this field represents. Suggest: "
            'aria-label="Calculator display".'
        )

    @pytest.mark.xfail(
        strict=True,
        reason="BUG-014: display is not declared aria-live; result updates "
        "are inaudible to screen-reader users.",
    )
    def test_display_should_be_an_aria_live_region(self, calculator_page: CalculatorPage) -> None:
        """When ``=`` is pressed, the display value updates without any
        focus change. Without ``aria-live``, the change is invisible to
        screen-reader users."""
        elem = calculator_page.find(CalculatorPage.DISPLAY)
        live = elem.get_attribute("aria-live")
        assert live in {"polite", "assertive"}, (
            f'Display should declare aria-live="polite" so screen-reader '
            f"users hear the result. Got aria-live={live!r}."
        )


# ===========================================================================
# 2. Page-level accessibility
# ===========================================================================
@pytest.mark.bug
class TestPageAccessibility:
    """Document-level a11y hygiene."""

    @pytest.mark.xfail(
        strict=True,
        reason="BUG-015: page has neither <main> landmark nor any heading element.",
    )
    def test_page_has_main_landmark_or_heading(self, calculator_page: CalculatorPage) -> None:
        """Screen-reader users navigate by landmarks (``<main>``) and
        headings. The page exposes neither — only the ``<title>``.
        """
        has_landmark = calculator_page.driver.execute_script(
            "return !!document.querySelector('main, [role=main], h1, h2');"
        )
        assert has_landmark, (
            "Page has neither a <main> landmark nor any heading element. "
            "Add <h1>Scientific Calculator</h1> at minimum."
        )

    @pytest.mark.xfail(
        strict=True,
        reason="BUG-016: <meta name='viewport'> is absent; mobile rendering "
        "uses default 980px width and is unusable.",
    )
    def test_viewport_meta_is_present_for_mobile(self, calculator_page: CalculatorPage) -> None:
        """No viewport meta means the page is unusable on phones (zoomed
        out by default, fixed-pixel layout)."""
        viewport = calculator_page.driver.execute_script(
            "return document.querySelector('meta[name=viewport]')?.content;"
        )
        assert viewport, (
            "No <meta name='viewport'> declared. The calculator will be "
            "unusable on mobile. Suggest: "
            'content="width=device-width, initial-scale=1".'
        )


# ===========================================================================
# 3. Button hygiene
# ===========================================================================
@pytest.mark.bug
class TestButtonAttributes:
    """Buttons must declare ``type="button"`` to avoid implicit submit
    behaviour if the calculator is ever embedded in a ``<form>``."""

    @pytest.mark.xfail(
        strict=True,
        reason="BUG-017: 24 buttons rely on the HTML default <button type='submit'>.",
    )
    def test_all_buttons_have_explicit_type_button(self, calculator_page: CalculatorPage) -> None:
        bad = calculator_page.driver.execute_script(
            """
            return [...document.querySelectorAll('.buttons button')]
              .filter(b => b.getAttribute('type') !== 'button')
              .map(b => b.textContent.trim());
            """
        )
        assert not bad, (
            f"{len(bad)} button(s) lack type='button': {bad}. "
            "HTML default for <button> is type='submit', which would "
            "submit a parent <form> if the calculator is ever embedded."
        )


# ===========================================================================
# 4. Keyboard input
# ===========================================================================
@pytest.mark.bug
class TestKeyboardInput:
    """A scientific calculator that cannot be typed into is hostile to
    productivity users (and a WCAG keyboard-operability violation)."""

    @pytest.mark.xfail(
        strict=True,
        reason="BUG-018: no keydown handler; calculator is mouse-only "
        "(WCAG 2.1.1 Keyboard violation).",
    )
    def test_typing_a_digit_on_keyboard_updates_the_display(
        self, calculator_page: CalculatorPage
    ) -> None:
        body = calculator_page.driver.find_element(By.TAG_NAME, "body")
        body.send_keys("7")
        assert calculator_page.read_display() == "7", (
            "Typing '7' on the keyboard had no effect on the display. "
            "The calculator has no keydown handlers, so it is operable "
            "by mouse only — a WCAG 2.1.1 (Keyboard) violation."
        )

    def test_display_field_is_not_directly_typable(self, calculator_page: CalculatorPage) -> None:
        """The display being a non-interactive output is itself fine, but
        Selenium's ``ElementNotInteractableException`` confirms users
        also cannot click into it and edit. Pin this so the regression
        story is clear when the team enables keyboard input."""
        elem = calculator_page.find(CalculatorPage.DISPLAY)
        with pytest.raises(ElementNotInteractableException):
            elem.click()
            elem.send_keys("5")


# ===========================================================================
# 5. Post-equals UX (functional + UX)
# ===========================================================================
@pytest.mark.bug
class TestPostEqualsBehaviour:
    """After ``=``, pressing a digit should *replace* the result, not
    append to it. Every desktop / mobile / OS calculator behaves this
    way; users will be surprised otherwise."""

    @pytest.mark.xfail(
        strict=True,
        reason="BUG-019: pressing a digit after '=' appends to the result "
        "instead of starting a fresh calculation.",
    )
    def test_digit_after_equals_starts_new_calculation(
        self, calculator_page: CalculatorPage
    ) -> None:
        # 7+2 = 9 — clean path (no '3', no '-')
        calculator_page.evaluate("7+2")
        assert calculator_page.read_display() == "9"
        calculator_page.click_digit(5)
        result = calculator_page.read_display()
        assert result == "5", (
            f"After pressing '=', a digit must start a new calculation. "
            f"Pressing '5' on a display showing '9' yielded {result!r} "
            "(the digit was appended). Severity: High (functional)."
        )


# ===========================================================================
# 6. Working behaviour pinned — focus indicator & contrast
# ===========================================================================
class TestKeyboardFocusIndicator:
    """The user agent default focus ring is present — pin it so a
    later 'outline: none' regression breaks loudly."""

    def test_focused_button_has_a_visible_outline(self, calculator_page: CalculatorPage) -> None:
        body = calculator_page.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.TAB)
        outline = calculator_page.driver.execute_script(
            "return getComputedStyle(document.activeElement).outline;"
        )
        # User agent default has non-zero width; assert nothing has
        # explicitly disabled it (e.g. 'rgb(0,0,0) none 0px').
        assert "none 0px" not in outline, (
            f"Focused element has no visible outline ({outline!r}); "
            "keyboard users cannot tell where focus is."
        )


class TestPageLanguageDeclared:
    """``<html lang>`` aids screen-reader pronunciation. The developer
    correctly set ``lang='en'`` — pin it."""

    def test_html_lang_is_declared(self, calculator_page: CalculatorPage) -> None:
        lang = calculator_page.driver.execute_script("return document.documentElement.lang;")
        assert lang, "<html> is missing a 'lang' attribute."
