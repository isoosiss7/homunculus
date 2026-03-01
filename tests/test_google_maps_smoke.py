import os
import re

import pytest
from playwright.sync_api import expect, sync_playwright

from homunculus.google_maps import open_google_maps
from homunculus.playwright_utils import launch_chromium, new_anonymous_context

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

            search_box = page.locator("input#searchboxinput").first
            try:
                expect(search_box).to_be_visible(timeout=5000)
            except Exception:
                search_box = page.get_by_role(
                    "combobox", name=re.compile(r"search", re.I)
                ).first
                try:
                    expect(search_box).to_be_visible(timeout=5000)
                except Exception:
                    search_box = page.get_by_role(
                        "textbox", name=re.compile(r"search", re.I)
                    ).first
                    expect(search_box).to_be_visible(timeout=5000)
        finally:
            context.close()
            browser.close()
