import os

import pytest
from playwright.sync_api import expect, sync_playwright

from homunculus.playwright_utils import launch_chromium, new_anonymous_context
from tests.gmaps_helpers import find_search_box, open_google_maps

pytestmark = pytest.mark.skipif(
    os.getenv("HOMUNCULUS_RUN_ACCEPTANCE") != "1",
    reason="Acceptance tests require HOMUNCULUS_RUN_ACCEPTANCE=1",
)


def test_google_maps_smoke_acceptance():
    with sync_playwright() as playwright:
        browser = launch_chromium(playwright, headless=True)
        context = new_anonymous_context(browser)
        page = context.new_page()
        try:
            open_google_maps(page)

            search_box = find_search_box(page)
            expect(search_box).to_be_visible(timeout=5000)
        finally:
            context.close()
            browser.close()
