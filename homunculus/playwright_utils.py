"""Helpers for Playwright usage in Homunculus."""


def launch_chromium(playwright, headless: bool = True):
    """Launch a Chromium browser with sensible defaults."""
    return playwright.chromium.launch(headless=headless)


def new_anonymous_context(browser):
    """Create a fresh, anonymous browser context."""
    return browser.new_context(storage_state=None, java_script_enabled=True)
