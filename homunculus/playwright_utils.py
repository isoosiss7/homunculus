"""Helpers for Playwright usage in Homunculus."""


def launch_chromium(playwright, headless: bool = True):
    """Launch a Chromium browser with sensible defaults."""
    return playwright.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
        ],
    )


def new_anonymous_context(browser):
    """Create a fresh, anonymous browser context."""
    return browser.new_context(
        storage_state=None,
        java_script_enabled=True,
        locale="en-US",
        timezone_id="America/Chicago",
        viewport={"width": 1366, "height": 768},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
    )
