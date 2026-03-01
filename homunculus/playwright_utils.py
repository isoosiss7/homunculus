"""Helpers for Playwright usage in Homunculus."""

import subprocess
import sys


def _is_missing_executable_error(error: Exception) -> bool:
    message = str(error).lower()
    return "executable doesn't exist" in message or "playwright install" in message


def _launch_chromium(playwright, headless: bool):
    return playwright.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
        ],
    )


def launch_chromium(playwright, headless: bool = True):
    """Launch a Chromium browser with sensible defaults."""
    try:
        return _launch_chromium(playwright, headless)
    except Exception as exc:
        if not _is_missing_executable_error(exc):
            raise

        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
        )
        return _launch_chromium(playwright, headless)


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
