import os

import pytest
from playwright.sync_api import sync_playwright

from homunculus.playwright_utils import launch_chromium, new_anonymous_context

pytestmark = pytest.mark.skipif(
    os.getenv("HOMUNCULUS_RUN_ACCEPTANCE") != "1",
    reason="Acceptance tests require HOMUNCULUS_RUN_ACCEPTANCE=1",
)


def test_google_maps_midterm_acceptance():
    with sync_playwright() as playwright:
        browser = launch_chromium(playwright, headless=True)
        context = new_anonymous_context(browser)
        page = context.new_page()
        try:
            page.goto("https://www.google.com/maps", wait_until="domcontentloaded")
            title = page.title()
            assert "google maps" in title.lower()
        finally:
            context.close()
            browser.close()
