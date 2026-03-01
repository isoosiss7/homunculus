import time
from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from homunculus.browser_wait import wait_for


def _ensure_playwright_available() -> None:
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")
        else:
            browser.close()


def test_wait_for_selector_with_delayed_element():
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "browser_wait.html"
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")
        page = browser.new_page()
        page.goto(f"file://{fixture_path}")

        wait_for(page, selector="#late", timeout_ms=1000)

        assert page.is_visible("#late") is True
        browser.close()


def test_wait_for_url_after_history_push():
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "browser_wait.html"
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")
        page = browser.new_page()
        page.goto(f"file://{fixture_path}")
        page.evaluate(
            """
            () => {
                setTimeout(() => {
                    history.pushState({}, '', 'next');
                }, 50);
            }
            """
        )

        wait_for(page, url="**/next", timeout_ms=1000)

        assert page.url.endswith("/next")
        browser.close()


def test_wait_for_function_on_delayed_window_var():
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "browser_wait.html"
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")
        page = browser.new_page()
        page.goto(f"file://{fixture_path}")

        wait_for(page, fn="() => window.delayedFlag === true", timeout_ms=1000)

        assert page.evaluate("() => window.delayedFlag") is True
        browser.close()


def test_combined_waits_share_timeout_budget():
    _ensure_playwright_available()
    fixture_path = Path(__file__).parent / "fixtures" / "browser_wait.html"
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browsers not installed: {exc}")
        page = browser.new_page()
        page.goto(f"file://{fixture_path}")

        start = time.monotonic()
        try:
            wait_for(
                page,
                selector="#late",
                fn="() => window.delayedFlag === true",
                timeout_ms=110,
            )
        except TimeoutError:
            elapsed_ms = (time.monotonic() - start) * 1000
            assert elapsed_ms < 180
        else:
            raise AssertionError("Expected combined wait to time out")
        finally:
            browser.close()


def test_wait_for_invalid_load_state_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Invalid load state"):
        wait_for(None, load="not-a-load-state")


def test_wait_for_requires_condition() -> None:
    with pytest.raises(ValueError, match="At least one wait condition must be provided"):
        wait_for(None)
