import os
import re

import pytest
from playwright.sync_api import expect, sync_playwright

from homunculus.google_maps import open_google_maps, search_location
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
            open_google_maps(page)
            search_location(page, "Cross Creek Ranch community center, Fulshear TX")
            title = page.title()
            assert "google maps" in title.lower()

            panel = page.get_by_role("region", name=re.compile(r"results for", re.I))
            expect(panel).to_contain_text(
                re.compile(r"(Cross Creek|Fulshear)", re.I), timeout=15000
            )
        finally:
            context.close()
            browser.close()
